
import os
import json
import re
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("ragul_rag_engine")

class VeterinaryRAGEngine:
    def __init__(self):
        self.kb_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "knowledge_base")
        self.vet_qa_path = os.path.join(self.kb_dir, "veterinary_qa.json")
        self.products_path = os.path.join(self.kb_dir, "products_catalog.json")
        
        self.nasem_rules_path = os.path.join(self.kb_dir, "nasem_feed_nutrition_rules.json")
        
        self.vet_qa_data: List[Dict[str, Any]] = []
        self.products_data: List[Dict[str, Any]] = []
        self.scenarios_data: List[Dict[str, Any]] = []
        self.nasem_rules_data: Dict[str, Any] = {}
        self.load_knowledge_base()

    def load_knowledge_base(self):
        """Loads veterinary Q&A, products, and NASEM 2021 dairy nutrition knowledge bases from JSON."""
        try:
            if os.path.exists(self.vet_qa_path):
                with open(self.vet_qa_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.vet_qa_data = data.get("qa", [])
                    logger.info(f"[RAG] Loaded {len(self.vet_qa_data)} veterinary QA records.")
            else:
                logger.warning(f"[RAG] Veterinary QA file not found at {self.vet_qa_path}")

            if os.path.exists(self.products_path):
                with open(self.products_path, "r", encoding="utf-8") as f:
                    pdata = json.load(f)
                    self.products_data = pdata.get("products", [])
                    self.scenarios_data = pdata.get("recommendation_scenarios", [])
                    logger.info(f"[RAG] Loaded {len(self.products_data)} products and {len(self.scenarios_data)} scenarios.")
            else:
                logger.warning(f"[RAG] Products catalog file not found at {self.products_path}")

            if os.path.exists(self.nasem_rules_path):
                with open(self.nasem_rules_path, "r", encoding="utf-8") as f:
                    self.nasem_rules_data = json.load(f)
                    logger.info(f"[RAG] Loaded NASEM 2021 Dairy Nutrition ruleset: {self.nasem_rules_data.get('ruleset_id')}")
            else:
                logger.warning(f"[RAG] NASEM rules file not found at {self.nasem_rules_path}")
        except Exception as e:
            logger.error(f"[RAG] Error loading knowledge bases: {e}")

    def _calculate_match_score(self, query: str, target_texts: List[str], keywords: List[str]) -> float:
        """Computes a semantic relevance score between user query and knowledge base record."""
        normalized_q = query.lower()
        normalized_q = re.sub(r'\b(diasese|desease|diseas|deseas)\b', 'disease', normalized_q)
        normalized_q = re.sub(r'\bhowto\b', 'how to', normalized_q)

        q_words = set(re.findall(r'\w+', normalized_q))
        if not q_words:
            return 0.0

        # Expand domain acronyms for rich recall
        if "fmd" in q_words:
            q_words.update(["foot", "mouth", "disease"])
        if "cmt" in q_words:
            q_words.update(["mastitis", "california", "test"])

        score = 0.0
        
        # 1. Keyword overlap
        kw_set = set(k.lower() for k in keywords)
        kw_matches = q_words.intersection(kw_set)
        score += len(kw_matches) * 3.0

        # 1.5. Primary Disease Boost: If query explicitly mentions the disease acronym or name
        PRIMARY_DISEASES = {"fmd", "mastitis", "bloat", "theileriosis", "brucella", "scour", "hypocalcemia", "lumpy"}
        if q_words.intersection(PRIMARY_DISEASES).intersection(kw_set):
            score += 6.0

        # 2. Phrase matching against question variants
        for t in target_texts:
            lt = t.lower()
            if lt in normalized_q or normalized_q in lt:
                score += 5.0
            # Token overlap
            t_words = set(re.findall(r'\w+', lt))
            overlap = q_words.intersection(t_words)
            score += len(overlap) * 1.5

        return score

    def search(self, user_query: str) -> Optional[Dict[str, Any]]:
        """
        Dual RAG Retrieval:
        1. Finds best matching veterinary clinical QA record.
        2. Finds matching Chimertech product recommendations and scenarios.
        3. Returns combined synthesized evidence.
        """
        if not self.vet_qa_data and not self.scenarios_data:
            self.load_knowledge_base()

        cleaned_query = user_query.strip()
        if not cleaned_query:
            return None

        best_vet = None
        best_vet_score = 0.0

        for item in self.vet_qa_data:
            targets = [item.get("question", ""), item.get("topic", "")] + item.get("question_variants", [])
            kws = item.get("keywords", [])
            score = self._calculate_match_score(cleaned_query, targets, kws)
            lower_cq = cleaned_query.lower()
            intent = item.get("intent", "")
            if any(w in lower_cq for w in ["check", "inspect", "sign", "symptom", "identify", "look for", "notice"]) and intent == "signs":
                score += 15.0
            elif any(w in lower_cq for w in ["prevent", "prevention", "protect", "avoid", "stop"]) and intent == "prevention":
                score += 15.0
            elif any(w in lower_cq for w in ["do", "action", "step", "first step", "treatment", "manage", "suspect"]) and intent == "what_to_do":
                score += 15.0

            if score > best_vet_score:
                best_vet_score = score
                best_vet = item

        best_scenario = None
        best_scenario_score = 0.0

        for sc in self.scenarios_data:
            targets = sc.get("farmer_questions", []) + sc.get("trigger_keywords", []) + [sc.get("intent", "")]
            kws = sc.get("trigger_keywords", [])
            score = self._calculate_match_score(cleaned_query, targets, kws)
            if score > best_scenario_score:
                best_scenario_score = score
                best_scenario = sc

        lower_q = cleaned_query.lower()
        # Strictly guard against routing clinical disease, veterinary symptom, or biosecurity questions to NASEM
        is_disease_q = any(re.search(rf"\b{w}\b", lower_q) for w in [
            "disease", "diseases", "prevent", "prevention", "spread", "spreading",
            "infection", "infectious", "biosecurity", "quarantine", "sick", "symptom",
            "symptoms", "fever", "mastitis", "fmd", "bloat", "treatment", "medicine", "vaccine", "isolate"
        ])
        is_explicit_nasem = any(re.search(rf"\b{w}\b", lower_q) for w in [
            "nasem", "dmi", "fwi", "nel", "me", "mp", "dry matter intake", "free water intake",
            "water requirement", "ration optimization", "single source of truth", "deprecated formula"
        ])
        if is_explicit_nasem and not is_disease_q:
            nasem_match = self.search_nasem_nutrition(cleaned_query)
            if nasem_match:
                return nasem_match

        # If no clinical or product match exceeds confidence threshold, provide reliable general veterinary guidance
        if best_vet_score < 5.0 and best_scenario_score < 5.0:
            return {
                "topic": "General Cattle Health & Veterinary Guidance",
                "clinical_answer": "To prevent disease transmission and protect your herd, standard veterinary protocols advise isolating any sick animal immediately, maintaining strict barn hygiene, and ensuring clean feed and water.",
                "action": "Isolate the affected cow immediately in a clean, quiet, shaded pen with abundant fresh water. Contact your qualified veterinarian for professional diagnosis and medical treatment.",
                "prevention": "Maintain strict herd biosecurity: isolate new arrivals for 21-30 days, disinfect equipment and sheds regularly, and keep vaccinations up to date.",
                "prevention_tips": [
                    "Isolate sick animals immediately from the main herd in a dedicated sick stall",
                    "Quarantine all newly introduced or returning cattle for 21 to 30 days before mixing",
                    "Provide constant access to clean drinking water and clean feeding troughs",
                    "Consult a licensed veterinarian for diagnosis, medication, or vaccination protocols"
                ],
                "products": [
                    {
                        "name": "Chimertech Bovine Herd Health Diagnostic Solutions",
                        "url": "https://chimertech.shop",
                        "purpose": "Early cow-side diagnostic screening and infection surveillance"
                    }
                ],
                "store_url": "https://chimertech.shop/",
                "spoken_response": "Sir, for cattle health and disease control, isolate any sick animal immediately, maintain clean feed and water, and arrange a veterinarian assessment for diagnosis and prescription medication.",
                "score": 5.0
            }

        # Build combined response
        matched_products = []
        is_mastitis_relevant = any(w in cleaned_query.lower() for w in ["mastitis", "udder", "teat", "swollen", "cmt", "milk clot", "subclinical", "மடிநோய்", "quadmastest"])
        
        if is_mastitis_relevant and best_scenario:
            matched_products = best_scenario.get("recommended_products", [])
            if not matched_products and "recommended_product_ids" in best_scenario:
                p_ids = set(best_scenario["recommended_product_ids"])
                matched_products = [
                    {"name": p["name"], "purpose": p.get("safe_answer", p.get("role", ""))}
                    for p in self.products_data if p["product_id"] in p_ids
                ]

        # Clinical synthesis
        topic = best_vet.get("topic", "Cattle Health") if best_vet else (best_scenario.get("primary_disease", "Cattle Health") if best_scenario else "Cattle Health")
        topic_id = best_vet.get("topic_id", "") if best_vet else ""
        answer_friendly = best_vet.get("answer_farmer_friendly", "") if best_vet else (best_scenario.get("clinical_explanation", "") if best_scenario else "")
        action = best_vet.get("immediate_action", "") if best_vet else (best_scenario.get("action_steps", "") if best_scenario else "")
        prevention = best_vet.get("prevention", "") if best_vet else ""

        # Retrieve comprehensive prevention tips for this disease if not in current record
        if not prevention and topic_id:
            for item in self.vet_qa_data:
                if item.get("topic_id") == topic_id and item.get("intent") == "prevention":
                    prevention = item.get("prevention") or item.get("answer_farmer_friendly", "")
                    break

        # Standardize structured prevention checklist for the specific disease
        prevention_tips: List[str] = []
        lower_topic = (topic + " " + topic_id + " " + cleaned_query).lower()

        if any(w in lower_topic for w in ["mastitis", "udder", "teat", "மடிநோய்"]):
            prevention_tips = [
                "Follow a consistent clean milking routine (strip, pre-dip, wipe dry)",
                "Keep corral bedding clean, dry, and regularly limed to stop bacteria",
                "Practice proper post-milking teat barrier dip immediately after clusters detach",
                "Monitor cows regularly with quarter-wise cow-side screening tests"
            ]
        elif any(w in lower_topic for w in ["estrus", "heat", "breeding", "insemination", "ai gun", "mounting", "standing heat", "சினை", "பருவம்"]):
            prevention_tips = [
                "Observe herd for standing heat signs 2 to 3 times daily (early morning and late evening)",
                "Follow the AM-PM rule: cows in standing heat in the morning should be bred in the evening (12-18 hr window)",
                "Inspect clear, stringy cervical mucus discharge before proceeding with artificial insemination",
                "Use visual inspection tools to avoid cervical trauma and ensure precise deep-uterine semen placement"
            ]
        elif any(w in lower_topic for w in ["bloat", "tympanites", "rumen gas"]):
            prevention_tips = [
                "Introduce lush green legumes and young pastures gradually over 7–10 days",
                "Always feed dry roughage, straw, or hay before letting cows graze lush green grass",
                "Avoid sudden shifts to high-starch or finely milled concentrate rations",
                "Ensure unrestricted access to fresh drinking water and rumen buffering salts"
            ]
        elif any(w in lower_topic for w in ["milk fever", "hypocalcemia", "downer"]):
            prevention_tips = [
                "Feed a low-calcium, DCAD-balanced mineral ration during the late dry period (last 3 weeks)",
                "Administer oral prophylactic calcium gel within 12 hours before and after calving",
                "Avoid high-potassium forages (e.g. fresh lucerne) during the transition dry period",
                "Ensure adequate dietary magnesium to maintain parathyroid calcium mobilization"
            ]
        elif any(w in lower_topic for w in ["theileriosis", "tick", "fever", "tick fever"]):
            prevention_tips = [
                "Apply regular acaricide pour-on or dip treatments to eliminate external ticks",
                "Seal and whitewash shed wall crevices where ticks hide and lay eggs",
                "Quarantine and inspect newly introduced cattle for tick vectors before mixing",
                "Vaccinate crossbred dairy cattle against Theileriosis where approved vaccines exist"
            ]
        elif any(w in lower_topic for w in ["calf scours", "diarrhea", "scour"]):
            prevention_tips = [
                "Feed 3 to 4 liters of clean maternal colostrum within 2 to 4 hours of birth",
                "House newborn calves in clean, elevated, well-ventilated pens with dry bedding",
                "Sanitize calf feeding buckets and teats thoroughly after every milk feeding",
                "Provide immediate oral rehydration electrolytes at the earliest sign of loose manure"
            ]
        elif any(w in lower_topic for w in ["fmd", "foot and mouth", "foot-and-mouth", "கோமாரி"]):
            prevention_tips = [
                "Follow mandatory government FMD vaccination schedules (every 6 months)",
                "Strictly isolate and quarantine newly purchased cattle for at least 21 to 30 days",
                "Install vehicle tire disinfection dip baths and footwear disinfectant footbaths at farm gate",
                "Immediately restrict visitors, vehicles, and animal movement if any blister sores appear"
            ]
        elif any(w in lower_topic for w in ["biosecurity", "prevent disease", "disease spread", "spreading", "quarantine", "transmission", "contagious"]):
            prevention_tips = [
                "Quarantine all newly purchased or returning cattle for 21 to 30 days before mixing with the herd",
                "Immediately isolate sick cattle in a separate stall with dedicated feeding buckets and tools",
                "Maintain disinfectant footbaths at shed entrances and sanitize milking gear between animals",
                "Control vectors (ticks and flies) and follow a timely vaccination schedule supervised by your veterinarian"
            ]
        elif prevention:
            parts = re.split(r'[,;.]\s*(?:and\s*)?', prevention)
            prevention_tips = [p.strip().capitalize() for p in parts if len(p.strip()) > 8][:4]

        # Disease-specific screening & supportive prevention products from Chimertech catalog
        matched_products: List[Dict[str, Any]] = []

        if any(w in lower_topic for w in ["mastitis", "udder", "teat", "மடிநோய்"]):
            matched_products = [
                {
                    "name": "Chimertech Quadmastest Mastitis Screening Device",
                    "url": "https://chimertech.shop",
                    "purpose": "Early 4-quarter subclinical mastitis detection"
                },
                {
                    "name": "Chimertech CMT Kit 500 ml with paddle",
                    "url": "https://chimertech.shop",
                    "purpose": "Cow-side somatic cell subclinical mastitis screening"
                }
            ]
        elif any(w in lower_topic for w in ["estrus", "heat", "breeding", "insemination", "ai gun", "artificial insemination", "mounting", "standing heat", "சினை", "பருவம்"]):
            matched_products = [
                {
                    "name": "Chimertech Visual AI Insemination Gun with HD Camera",
                    "url": "https://chimertech.shop",
                    "purpose": "Visual cervical inspection, heat mucus verification, and precise non-traumatic artificial insemination"
                },
                {
                    "name": "Chimertech Smart Bovine Estrus Detection Kit",
                    "url": "https://chimertech.shop",
                    "purpose": "Accurate standing heat detection and tracking the optimal 12-18 hour breeding window"
                }
            ]
        elif any(w in lower_topic for w in ["fmd", "foot and mouth", "foot-and-mouth", "கோமாரி"]):
            matched_products = [
                {
                    "name": "Chimertech Bovine Foot and Mouth Disease (FMD) Antibody Rapid Test Kit",
                    "url": "https://chimertech.shop",
                    "purpose": "Rapid cow-side antibody screening & herd surveillance for Foot-and-Mouth Disease (FMD)"
                }
            ]
        elif any(w in lower_topic for w in ["bloat", "tympanites", "rumen"]):
            matched_products = [
                {
                    "name": "Anti-Bloat Carminative Rumen Liquid",
                    "url": "https://chimertech.shop",
                    "purpose": "Rapid rumen gas dispersion and frothy bloat relief"
                }
            ]
        elif any(w in lower_topic for w in ["milk fever", "hypocalcemia", "downer"]):
            matched_products = [
                {
                    "name": "Calci-Boost High-Potency Oral Calcium Gel",
                    "url": "https://chimertech.shop",
                    "purpose": "Post-calving calcium restoration and milk fever prevention"
                }
            ]
        elif any(w in lower_topic for w in ["theileriosis", "tick"]):
            matched_products = [
                {
                    "name": "Chimertech Ectoparasiticide Pour-On",
                    "url": "https://chimertech.shop",
                    "purpose": "External tick, lice, and fly infestation control"
                }
            ]
        elif any(w in lower_topic for w in ["scour", "calf", "diarrhea"]):
            matched_products = [
                {
                    "name": "Oral Electrolyte Rehydration Formula (ORS)",
                    "url": "https://chimertech.shop",
                    "purpose": "Calf dehydration reversal and gut electrolyte replenishment"
                }
            ]
        elif any(w in lower_topic for w in ["biosecurity", "prevent disease", "disease spread", "spreading", "quarantine", "transmission"]):
            matched_products = [
                {
                    "name": "Chimertech Bovine Herd Health Rapid Screening Kits",
                    "url": "https://chimertech.shop",
                    "purpose": "Cow-side herd screening and early infection surveillance"
                }
            ]

        # Build Voice-Ready Spoken Answer with Structured Formatting
        spoken_parts = []
        if answer_friendly:
            spoken_parts.append(f"Sir, regarding {topic}: {answer_friendly}")
        if action:
            spoken_parts.append(f"Immediate action: {action}")
        if prevention_tips:
            spoken_parts.append(f"Prevention: {'; '.join(prevention_tips[:2])}.")
        if matched_products:
            prod_names = [f"{p.get('name')} ({p.get('purpose')})" for p in matched_products[:2]]
            spoken_parts.append(f"To test and manage this, use {'; and '.join(prod_names)}, available on chimertech.shop.")
        spoken_parts.append("If high fever or severe worsening occurs, call your veterinarian promptly.")

        full_spoken_text = " ".join(spoken_parts)

        return {
            "topic": topic,
            "clinical_answer": answer_friendly,
            "action": action,
            "prevention": prevention,
            "prevention_tips": prevention_tips,
            "products": matched_products,
            "store_url": "https://chimertech.shop/",
            "spoken_response": full_spoken_text,
            "score": max(best_vet_score, best_scenario_score)
        }

    def search_nasem_nutrition(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Specialized RAG retriever for NASEM 2021 Dairy Nutrition, Feed, DMI, Water, Energy,
        Minerals, and Ration Optimization rules.
        """
        try:
            from app.knowledge.nasem_calculator import nasem_calculator
            rules_res = nasem_calculator.query_nasem_rules(query)
            if not rules_res or not rules_res.get("matches"):
                return None

            matches = rules_res.get("matches", [])
            matched_cats = [m.get("category", "") for m in matches if m.get("category")]
            cat_label = ", ".join(matched_cats[:2]) if matched_cats else "Dairy Feed & Nutrition"

            overview = (
                "According to NASEM 2021 (Nutrient Requirements of Dairy Cattle, 8th Revised Edition), "
                "dairy feeding, water intake, energy, and minerals must follow unified, traceable scientific equations. "
                "Key principles: 1) Single source of truth across all farm tables; 2) Lactating DMI follows NASEM Eq 2-1; "
                "3) Free Water Intake follows Eq 9-1/9-3 without extra 1.44 heat multipliers; 4) Adult energy uses NEL while heifers use ME; "
                "5) Minerals use factorial requirements (Ca Eq 7-1, P system) with mineral mixture prescribed strictly based on calculated deficits."
            )

            return {
                "topic": f"NASEM 2021 Dairy Nutrition ({cat_label})",
                "clinical_answer": overview,
                "action": "Apply authoritative NASEM 2021 equations. Never apply arbitrary multipliers or generic category mineral averages.",
                "prevention": "Prevent metabolic disorders (acidosis, milk fever, ketosis) by balancing rations joint-farm wide with hard inventory limits.",
                "prevention_tips": [
                    "Single source of truth: all animal and herd tables must consume identical calculated result objects",
                    "Water intake: use NASEM Eq 9-1 (lactating) or Eq 9-3 (dry) - do not apply extra 1.44 heat multiplier",
                    "Minerals: calculate natural feed supply, subtract from factorial requirement, and dose mineral mix only to bridge deficits",
                    "Ration balance: DMI adequacy alone never equals BALANCED - all energy, protein, mineral, and inventory checks must pass"
                ],
                "rules_data": rules_res,
                "products": [],
                "store_url": "https://chimertech.shop/",
                "spoken_response": f"Sir, under NASEM 2021 standards for {cat_label}, all calculations are strictly standardized. Lactating DMI follows Equation 2-1, water intake uses Equation 9-1 without double-counting temperature, and mineral mixtures must be dosed strictly based on calculated nutritional deficits.",
                "score": 25.0
            }
        except Exception as e:
            logger.error(f"[RAG] Error in search_nasem_nutrition: {e}")
            return None

rag_engine = VeterinaryRAGEngine()
