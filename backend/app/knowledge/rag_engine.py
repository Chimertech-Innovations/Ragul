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
        
        self.vet_qa_data: List[Dict[str, Any]] = []
        self.products_data: List[Dict[str, Any]] = []
        self.scenarios_data: List[Dict[str, Any]] = []
        self.load_knowledge_base()

    def load_knowledge_base(self):
        """Loads both veterinary Q&A and Chimertech product knowledge bases from JSON."""
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
        except Exception as e:
            logger.error(f"[RAG] Error loading knowledge bases: {e}")

    def _calculate_match_score(self, query: str, target_texts: List[str], keywords: List[str]) -> float:
        """Computes a semantic relevance score between user query and knowledge base record."""
        q_words = set(re.findall(r'\w+', query.lower()))
        if not q_words:
            return 0.0

        score = 0.0
        
        # 1. Keyword overlap
        kw_set = set(k.lower() for k in keywords)
        kw_matches = q_words.intersection(kw_set)
        score += len(kw_matches) * 3.0

        # 2. Phrase matching against question variants
        lower_q = query.lower()
        for t in target_texts:
            lt = t.lower()
            if lt in lower_q or lower_q in lt:
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

        # If no clinical or product match exceeds confidence threshold
        if best_vet_score < 2.0 and best_scenario_score < 2.0:
            return None

        # Build combined response
        matched_products = []
        if best_scenario:
            matched_products = best_scenario.get("recommended_products", [])
            if not matched_products and "recommended_product_ids" in best_scenario:
                p_ids = set(best_scenario["recommended_product_ids"])
                matched_products = [
                    {"name": p["name"], "purpose": p.get("safe_answer", p.get("role", ""))}
                    for p in self.products_data if p["product_id"] in p_ids
                ]

        # Clinical synthesis
        topic = best_vet.get("topic", "Cattle Health") if best_vet else (best_scenario.get("primary_disease", "Cattle Health") if best_scenario else "Cattle Health")
        answer_friendly = best_vet.get("answer_farmer_friendly", "") if best_vet else (best_scenario.get("clinical_explanation", "") if best_scenario else "")
        action = best_vet.get("immediate_action", "") if best_vet else (best_scenario.get("action_steps", "") if best_scenario else "")
        prevention = best_vet.get("prevention", "") if best_vet else ""
        
        # Build Voice-Ready Spoken Answer
        spoken_parts = []
        
        # 1. Clinical Analysis
        if any(w in cleaned_query.lower() for w in ["what is mastitis", "meaning of mastitis", "explain mastitis", "so what is mastitis"]):
            spoken_parts.append("Sir, Mastitis is an inflammation and infection of the mammary gland and udder tissue, primarily caused by bacterial invasion (such as Staphylococcus or Streptococcus) entering through the teat canal.")
        elif "swollen" in cleaned_query.lower() or "mastitis" in cleaned_query.lower():
            spoken_parts.append("Sir, a swollen udder is a strong indication of Mastitis (udder inflammation caused by bacterial infection entering through the teat canal).")
        elif "bloat" in cleaned_query.lower() or "gas" in cleaned_query.lower() or "belly" in cleaned_query.lower():
            spoken_parts.append("Sir, abnormal gas accumulation on the left side of the abdomen indicates Bloat in the rumen.")
        elif "calving" in cleaned_query.lower() or "down" in cleaned_query.lower() or "cannot stand" in cleaned_query.lower():
            spoken_parts.append("Sir, a cow unable to stand after calving indicates potential Milk Fever (acute hypocalcemia).")
        elif "heat" in cleaned_query.lower() or "estrus" in cleaned_query.lower() or "mount" in cleaned_query.lower():
            spoken_parts.append("Sir, standing to be mounted and clear mucus discharge indicate active Estrus (standing heat).")
        elif "tick" in cleaned_query.lower():
            spoken_parts.append("Sir, tick infestation on cattle causes severe anemia and can transmit deadly Theileriosis tick fever.")
        elif answer_friendly:
            spoken_parts.append(f"Sir, regarding {topic}: {answer_friendly}")

        # 2. Immediate Action & Prevention
        if action:
            spoken_parts.append(f"Immediate action: {action}")
        if prevention:
            spoken_parts.append(f"Prevention: {prevention}")

        # 3. Chimertech Product Recommendations
        if matched_products:
            prod_names = [f"{p.get('name')} ({p.get('purpose')})" for p in matched_products[:2]]
            spoken_parts.append(f"To test and manage this, use {'; and '.join(prod_names)}, available on chimertech.shop.")
        else:
            spoken_parts.append("Screening tools and teat hygiene dips are available on chimertech.shop.")

        # 4. Red flag
        spoken_parts.append("If high fever or severe worsening occurs, call your veterinarian promptly.")

        full_spoken_text = " ".join(spoken_parts)

        return {
            "topic": topic,
            "clinical_answer": answer_friendly,
            "action": action,
            "prevention": prevention,
            "products": matched_products,
            "store_url": "https://chimertech.shop/",
            "spoken_response": full_spoken_text,
            "score": max(best_vet_score, best_scenario_score)
        }

rag_engine = VeterinaryRAGEngine()
