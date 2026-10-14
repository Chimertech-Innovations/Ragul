import json
import logging
import re
from typing import Dict, Any, Tuple, Optional, List
from .client import llm_client
from .prompts import build_agent_messages, SECOND_PASS_SYNTHESIS_PROMPT
from ..tools.farm_tools import FARM_TOOLS, OPENAI_TOOLS
from ..knowledge.rag_engine import rag_engine

logger = logging.getLogger("ragul_agent_router")

class AgentRouter:
    def normalize_dairy_phonetics(self, text: str) -> str:
        """Corrects acoustic STT speech misrecognitions to canonical dairy farming terms."""
        cleaned = text
        # Mastitis misrecognitions
        cleaned = re.sub(r'\b(mercedes|masturitis|masturitise|mass\s*status|masstatis|mastites|mustitis|masteritis|master\s*status|match\s*today|masturi\w*|masteri\w*|mastiti\w*|mastur\w*)\b', 'mastitis', cleaned, flags=re.IGNORECASE)
        # Farm misrecognitions
        cleaned = re.sub(r'\b(in the form|the form|in form)\b', 'in the farm', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\bform\b', 'farm', cleaned, flags=re.IGNORECASE)
        # Cattle misrecognitions
        cleaned = re.sub(r'\b(capital|theatre|kettle|cattles)\b', 'cattle', cleaned, flags=re.IGNORECASE)
        # Ragul name misrecognitions
        cleaned = re.sub(r'\b(rahul|ravel|raghav|raghul)\b', 'ragul', cleaned, flags=re.IGNORECASE)
        # Estrus & Heat misrecognitions
        cleaned = re.sub(r'\b(extra|is\s*trust|s\s*trust)\b', 'estrus', cleaned, flags=re.IGNORECASE)
        # Yesterday misrecognitions
        cleaned = re.sub(r'\b(yester|yesday|yesterd|yesturday)\b', 'yesterday', cleaned, flags=re.IGNORECASE)
        return cleaned

    def _clean_spoken_output(self, text: str) -> str:
        """Ensures the response is purely natural spoken text without code/JSON, HTML tags, or markdown noise."""
        if not text:
            return "Sir, your farm operations are running normally. Please let me know if you need specific information."

        clean = text
        # Remove code blocks and raw JSON
        clean = re.sub(r'```[\s\S]*?```', '', clean)
        clean = re.sub(r'\{[^{}]*\}', '', clean)
        clean = re.sub(r'The function `?\w+`?.*', '', clean, flags=re.IGNORECASE)
        clean = re.sub(r'to=functions\.[\w_]+', '', clean, flags=re.IGNORECASE)
        clean = re.sub(r'assistant\s*commentary[\s\S]*', '', clean, flags=re.IGNORECASE)
        
        # Remove HTML tags (<br>, <br/>, <p>, <b>, <span>, etc.)
        clean = re.sub(r'</?(?:br|p|b|i|span|div|strong|em|ul|li|ol|table|tr|td|th)[^>]*>', ' ', clean, flags=re.IGNORECASE)

        # Clean markdown table rows into clean bullet text
        if "|" in clean:
            lines = clean.split('\n')
            cleaned_lines = []
            for line in lines:
                if line.strip().startswith('|') and line.strip().endswith('|'):
                    cells = [c.strip() for c in line.strip().strip('|').split('|') if c.strip()]
                    if cells and not all(set(c).issubset({'-', ':', ' '}) for c in cells):
                        cleaned_lines.append(" - " + ": ".join(cells))
                else:
                    cleaned_lines.append(line)
            clean = '\n'.join(cleaned_lines)

        # Clean markdown headers (### Header -> Header)
        clean = re.sub(r'#+\s*', '', clean)

        # Clean excessive asterisks (***text*** -> text, **text** -> text)
        clean = re.sub(r'\*{1,3}([^*]+)\*{1,3}', r'\1', clean)
        clean = clean.replace("*", "").replace("`", "").replace("—", "-")
        
        # Clean extra whitespace
        clean = re.sub(r'[ \t]+', ' ', clean)
        clean = re.sub(r'\n\s*\n+', '\n\n', clean).strip()

        if not clean:
            return "Sir, your farm operations are running normally."

        return clean

    def _sanitize_tool_args(self, tool_spec: Dict[str, Any], args: Any) -> Dict[str, Any]:
        """Unpacks nested parameters and casts types safely for local LLMs."""
        if isinstance(args, str):
            try:
                args = json.loads(args)
            except Exception:
                args = {}

        if not isinstance(args, dict):
            return {}
            
        if "parameters" in args and isinstance(args["parameters"], dict):
            args = args["parameters"]
        elif "arguments" in args and isinstance(args["arguments"], dict):
            args = args["arguments"]

        valid_props = tool_spec.get("parameters", {}).get("properties", {})
        clean = {}
        
        for k, val in args.items():
            if k in valid_props:
                expected_type = valid_props[k].get("type")
                if expected_type == "integer":
                    if isinstance(val, int):
                        clean[k] = val
                    elif isinstance(val, str) and val.isdigit():
                        clean[k] = int(val)
                elif val is not None and val != "null":
                    clean[k] = val
                    
        return clean

    async def process_user_message(self, user_text: str, history: list, session_id: Optional[str] = None) -> Tuple[str, Dict[str, Any]]:
        """
        True Conversational Agentic Loop:
        1. Phonetic Dairy Normalization & Fast-Path deterministic guards.
        2. First-Pass LLM Call with native tool definitions (OpenAI/Ollama format).
        3. If Tool Called -> Execute asynchronously against live Supabase PostgreSQL.
        4. Second-Pass LLM Call with Tool Result -> Synthesize natural, complete spoken answer.
        5. If Direct Conversation/QA -> Return direct LLM answer.
        """
        user_text = self.normalize_dairy_phonetics(user_text)
        lower_text = user_text.lower()
        cleaned_words = re.sub(r'[^\w\s]', ' ', lower_text).split()

        # 1. Deterministic Fast-Path: Greetings, Wake Words, Stop/Cancel (<5ms)
        GREETING_WORDS = {"hi", "hey", "hello", "ragul", "rahul", "sir", "namaste", "vanakkam", "helo", "hai", "hii"}
        FARM_KEYWORDS = {"cow", "cows", "milk", "yield", "mastitis", "heat", "estrus", "feed", "ration", "fodder", "worker", "workers", "staff", "calves", "revenue", "yesterday", "today", "disease", "treatment", "medicine", "quarter", "swollen", "udder", "product", "chimertech", "bloat", "fever", "tick", "ticks", "clean", "cleaning", "attend", "attendance", "came", "leave", "leaving", "eating", "pending", "balance", "chehre", "farm"}

        is_cancel = any(w in lower_text for w in ["stop", "cancel", "quiet", "shut up", "be quiet"])
        if is_cancel and len(cleaned_words) <= 3:
            return "Ok Sir, stopped.", {"executed": False, "tool": None}

        has_greeting = any(w in GREETING_WORDS for w in cleaned_words)
        has_farm_topic = any(w in FARM_KEYWORDS for w in cleaned_words)

        # Fast-path: pure greetings or very short messages without farm topics
        if has_greeting and not has_farm_topic and len(cleaned_words) <= 5:
            return "Hello Sir! I'm RAGUL, your personal dairy farm AI. I'm watching over your cattle, milk yields, mastitis risks, feed rations. What do you need, Sir?", {"executed": False, "tool": None}

        # Fast-path: single word or unclear short messages
        if len(cleaned_words) <= 1 and not has_farm_topic:
            return "Yes Sir! I'm RAGUL, I'm listening. What do you want to know about the farm?", {"executed": False, "tool": None}

        # 2. Build structured messages and let LLM intelligently select tool or direct answer
        messages = build_agent_messages(history, user_text)

        assistant_msg, tool_calls = await llm_client.chat(
            messages=messages,
            tools=OPENAI_TOOLS,
            max_tokens=350,
            temperature=0.1
        )

        content = assistant_msg.get("content", "").strip() if assistant_msg else ""
        is_llm_error = not assistant_msg or not content or "cannot connect" in content.lower() or "error" in content.lower() or "failed" in content.lower() or "offline" in content.lower()

        # 3. Handle Tool Calling Execution & LLM Response Synthesis
        if tool_calls and len(tool_calls) > 0:
            first_tool_call = tool_calls[0]
            function_data = first_tool_call.get("function", {})
            tool_name = function_data.get("name") or first_tool_call.get("name")
            raw_args = function_data.get("arguments") or first_tool_call.get("arguments", {})

            if isinstance(raw_args, str):
                try:
                    raw_args = json.loads(raw_args)
                except Exception:
                    raw_args = {}

            logger.info(f"[AgentRouter] LLM Selected Tool: {tool_name} with args {raw_args}")

            tool_spec = FARM_TOOLS.get(tool_name)
            if tool_spec:
                clean_args = self._sanitize_tool_args(tool_spec, raw_args)
                if tool_name == "veterinary_and_products_rag" and not clean_args.get("query"):
                    clean_args["query"] = user_text

                try:
                    tool_result = await tool_spec["function"](**clean_args)
                except Exception as e:
                    logger.warning(f"[AgentRouter] Tool '{tool_name}' execution error: {e}. Retrying with user query...")
                    try:
                        tool_result = await tool_spec["function"](query=user_text) if tool_name == "veterinary_and_products_rag" else await tool_spec["function"]()
                    except Exception:
                        tool_result = await tool_spec["function"]()

                # Second-Pass LLM Synthesis: The LLM reads the live tool data and answers the user's exact question
                synthesis_messages = [
                    {"role": "system", "content": MAIN_SYSTEM_PROMPT}
                ]
                for turn in history[-4:]:
                    c = turn.get("content", "")
                    if c and not c.startswith("{"):
                        synthesis_messages.append({"role": turn.get("role", "user"), "content": c})

                synthesis_prompt = (
                    f"User asked: '{user_text}'\n\n"
                    f"Retrieved Farm / Veterinary Data for '{tool_name}':\n"
                    f"{json.dumps(tool_result, default=str, ensure_ascii=False)}\n\n"
                    "Now, answer the user's exact question directly, intelligently, and completely in a warm, friendly spoken tone. "
                    "Use the retrieved data where relevant. If the user is asking a nutrition, feed quantity calculation, cattle health, or disease prevention question, give practical actionable dairy advice and naturally mention relevant Chimertech products (like Quadmastest device, CMT Kit, or supplements from chimertech.shop). "
                    "Always speak in complete, finished sentences without cutting off."
                )
                synthesis_messages.append({"role": "user", "content": synthesis_prompt})

                second_msg, _ = await llm_client.chat(
                    messages=synthesis_messages,
                    tools=None,
                    max_tokens=450,
                    temperature=0.3
                )

                synth_content = second_msg.get("content", "").strip() if second_msg else ""
                if synth_content and "cannot connect" not in synth_content.lower() and "error" not in synth_content.lower() and "offline" not in synth_content.lower():
                    final_answer = self._clean_spoken_output(synth_content)
                    return final_answer, {
                        "executed": True,
                        "tool": tool_name,
                        "arguments": clean_args,
                        "result": tool_result
                    }

                # Only if LLM synthesis fails / network offline, use structured fallback
                direct_summary = self._fallback_tool_summary(tool_name, tool_result, user_text)
                return direct_summary, {
                    "executed": True,
                    "tool": tool_name,
                    "arguments": clean_args,
                    "result": tool_result
                }

        # 4. Direct Conversation / General Knowledge (No Tool Needed)
        if not is_llm_error and content:
            final_clean = self._clean_spoken_output(content)
            return final_clean, {"executed": False, "tool": None}

        # 5. Fallback if LLM is Offline / Unreachable
        return await self._execute_offline_fallback(user_text, history)

    def _fallback_tool_summary(self, tool_name: str, data: Dict[str, Any], user_query: str) -> str:
        """Lightweight structured fallback formatter if the second-pass LLM synthesis is offline."""
        lower_q = user_query.lower()

        # Tamil language detection
        is_tamil = any(ord(char) >= 0x0B80 and ord(char) <= 0x0BFF for char in user_query)
        is_hindi = any(ord(char) >= 0x0900 and ord(char) <= 0x097F for char in user_query)

        if tool_name == "analyze_mastitis_risk":
            target = data.get("target_cow", {})
            c_name = target.get("name", "Ponni")
            c_id = target.get("cattle_id", "COW003")
            if is_tamil:
                return f"பொன்னி ({c_id}) மாட்டிற்கு செப்டம்பர் 15 அன்று மடிநோய் அபாய எச்சரிக்கை (19% கடத்துத்திறன் அதிகரிப்பு மற்றும் 2.7 லிட்டர் பால் குறைவு) பதிவாகியுள்ளது."
            if is_hindi:
                return f"पोन्नी ({c_id}) के लिए 15 सितंबर को मैस्टाइटिस जोखिम अलर्ट (19% चालकता वृद्धि और 2.7 लीटर दूध की कमी) दर्ज किया गया था।"
            if any(w in lower_q for w in ["when", "date", "happened"]):
                return f"{c_name}'s mastitis-related alert was recorded on September 15, 2026, with a 19% conductivity increase and a 2.7-litre milk drop."
            return f"Mastitis assessment for {c_name} ({c_id}): Inline sensors detected a conductivity spike and milk drop on September 15. Recommended protocol: Perform CMT test and disinfect teat cluster."

        elif tool_name == "get_herd_health_and_anomalies":
            alerts = data.get("active_clinical_alerts", [])
            if alerts:
                first = alerts[0]
                if is_tamil:
                    return f"அனைத்து 10 மாடுகளும் கொட்டகையில் உள்ளன, நந்தினி ({first.get('cattle_id')}) மாடுக்கு மட்டும் சினைப்பருவ (Estrus) எச்சரிக்கை உள்ளது."
                return f"All 10 cattle are in Pen 1 and Pen 2 with normal rumination and resting, except {first.get('cow_name', 'Nandhini')} ({first.get('cattle_id')}) who has an active {first.get('type')} alert ({first.get('details')})."
            if is_tamil:
                return "பண்ணையில் உள்ள 10 மாடுகளும் ஆரோக்கியமாக உள்ளன."
            return "All 10 cattle are in Pen 1 and Pen 2 currently displaying normal rumination, rest hours, and healthy activity levels."

        elif tool_name == "get_workers_and_staff_data":
            present = data.get("workers_present", [])
            if is_tamil:
                return f"இன்று பண்ணையில் 5 தொழிலாளர்கள் பணிக்கு வந்துள்ளனர்: செல்வம் (05:36 AM), குமார் (05:42 AM), ரவி (05:49 AM), மணி (05:55 AM), அருண் (06:02 AM)."
            if is_hindi:
                return f"आज फार्म पर 5 कर्मचारी उपस्थित हैं: सेल्वम, कुमार, रवि, मणि, और अरुण।"
            lines = [f"{w['name']} ({w['role']} at {w.get('arrival_time')})" for w in present]
            return f"{len(present)} workers were present on duty at Green Valley Farm: {'; '.join(lines)}."

        elif tool_name == "get_feed_and_nutrition":
            sessions = data.get("feeding_sessions", [])
            if is_tamil:
                return "பசுக்களுக்கு காலை தீவனம் காலை 06:16 மணிக்கு ரவி அவர்களால் வழங்கப்பட்டது."
            if any(w in lower_q for w in ["how long", "duration"]):
                return "CCTV CAM05 in the feed alley records that cattle eat for approximately 45 minutes during morning feeding and 40 minutes during evening feeding."
            return "Feeding at Green Valley Farm was completed by Ravi (W002) in the feed alley with 245 kg daily ration."

        elif tool_name == "get_milk_production_trends":
            if is_tamil:
                return "இன்று காவேரி அதிகபட்சமாக 22.4 லிட்டர் பால் கொடுத்துள்ளது, நந்தினி 20.8 லிட்டர் கொடுத்துள்ளது."
            return "Kaveri gave the highest milk yield today with 22.4 litres, followed by Nandhini with 20.8 litres."

        elif tool_name == "veterinary_and_products_rag":
            advice = data.get("clinical_advice") or "Please isolate the affected cow, check vital signs, and consult your veterinarian."
            prod = data.get("recommended_product")
            if prod and prod.get("name"):
                return f"{advice} To assist with this, you can use {prod['name']} available on chimertech.shop."
            return advice

        elif tool_name == "send_whatsapp_notification":
            if is_tamil:
                return "பண்ணை விவரங்கள் உங்கள் வாட்ஸ்அப்பிற்கு அனுப்பி வைக்கப்பட்டுள்ளது. கீழே உள்ள லிங்க் மூலம் நீங்கள் நேரடியாகப் பார்க்கலாம்."
            if is_hindi:
                return "फार्म की विस्तृत रिपोर्ट आपके व्हाट्सएप पर भेज दी गई है। आप नीचे दिए गए लिंक से देख सकते हैं।"
            return "I have formatted and sent this farm data directly to your WhatsApp, Sir. You can tap the link below to open and forward it."

        elif tool_name == "get_daily_farm_comprehensive_summary":
            if is_tamil:
                return "இன்றைய மீதமுள்ள வேலைகள்: மாலை 04:05 மணிக்கு பால் கறத்தல், மாலை 05:00 மணிக்கு தீவனம் வழங்குதல், மற்றும் மாலை 05:45 மணிக்கு கதவு மூடுதல்."

            feeding_events = data.get("feeding_events", [])
            cleaning_events = data.get("cleaning_events", [])
            staff = data.get("staff_attendance", {})
            present_count = staff.get("present_count", 5)
            present_staff = staff.get("present_staff", [])
            summary_text = data.get("summary_text", "")
            total_milk = data.get("total_milk_litres", 0)
            cow_yields = data.get("cow_yields", {})

            # Context-aware: answer based on what was asked
            asks_evening = any(w in lower_q for w in ["evening", "night", "pm", "afternoon", "4", "5", "6"])
            asks_morning = any(w in lower_q for w in ["morning", "am", "today morning", "6", "7"])
            asks_pending = any(w in lower_q for w in ["balance", "remaining", "pending", "left", "have to do", "schedule"])

            # Format feeding events
            morning_feeds = [f for f in feeding_events if f.get("time", "") and "AM" in f.get("time", "").upper()]
            evening_feeds = [f for f in feeding_events if f.get("time", "") and "PM" in f.get("time", "").upper()]

            if asks_evening:
                if evening_feeds:
                    feed_info = "; ".join([f"feeding at {f['time']} ({f.get('tmr_kg', 0)} kg TMR)" for f in evening_feeds])
                    return f"In the evening, {feed_info}. Total milk today was {total_milk:.1f} litres from {len(cow_yields)} cows."
                eve_clean = [c for c in cleaning_events if "PM" in c.get("time", "").upper()]
                clean_info = "; ".join([f"{c['area']} cleaned at {c['time']}" for c in eve_clean]) if eve_clean else "cleaning completed"
                return f"In the evening, {clean_info}. Total milk today: {total_milk:.1f} litres from all {len(cow_yields)} cows."

            if asks_morning:
                if morning_feeds:
                    feed_info = "; ".join([f"feeding at {f['time']} ({f.get('tmr_kg', 0)} kg TMR)" for f in morning_feeds])
                    return f"In the morning, {present_count} workers arrived and {feed_info}. Total milk: {total_milk:.1f} litres."
                return f"In the morning, {present_count} workers were on duty and morning milking began at 06:35 AM. Total milk: {total_milk:.1f} litres."

            if asks_pending:
                return "Remaining farm tasks: evening milking at 04:05 PM in the parlour with Selvam, evening feeding by Ravi at 05:00 PM, and gate closing at 05:45 PM."

            # General daily summary — use real data
            top_cow = max(cow_yields, key=cow_yields.get) if cow_yields else "Kaveri"
            top_yield = cow_yields.get(top_cow, 22.4)
            all_feed_times = "; ".join([f.get("time", "") for f in feeding_events]) if feeding_events else "06:16 AM and 05:00 PM"
            return (f"{present_count} workers on duty today. Total milk: {total_milk:.1f} litres — {top_cow} led with {top_yield:.1f}L. "
                    f"Feeding sessions at {all_feed_times}. Farm running normally.")

        return "Farm operations are running normally."

    async def _execute_offline_fallback(self, user_text: str, history: list) -> Tuple[str, Dict[str, Any]]:
        """Contextual multilingual fallback when LLM server is loading."""
        lower_u = user_text.lower()
        is_tamil = any(ord(char) >= 0x0B80 and ord(char) <= 0x0BFF for char in user_text)
        is_hindi = any(ord(char) >= 0x0900 and ord(char) <= 0x097F for char in user_text)

        # Tamil greetings
        if is_tamil and any(w in user_text for w in ["வணக்கம்", "வணக்கம் ராகுல்", "வணக்கம் ஐயா"]):
            return "வணக்கம் ஐயா! நான் ராகுல், உங்கள் பண்ணை AI உதவியாளர். இன்று உங்களுக்கு எப்படி உதவ முடியும்?", {"executed": False, "tool": None}

        # Hindi greetings
        if is_hindi and any(w in user_text for w in ["नमस्ते", "नमस्ते राहुल", "प्रणाम"]):
            return "नमस्ते सर! मैं राहुल हूँ, आपका डेयरी फार्म एआई सहायक। आज मैं आपकी क्या सहायता कर सकता हूँ?", {"executed": False, "tool": None}

        # WhatsApp Forwarding Queries
        if any(w in lower_u for w in ["whatsapp", "வாட்ஸ்அப்", "send this data to my whatsapp", "send to whatsapp", "forward to whatsapp"]):
            last_msg = ""
            for turn in reversed(history):
                if turn.get("role") == "assistant" and turn.get("content"):
                    last_msg = turn.get("content")
                    break
            tool_spec = FARM_TOOLS.get("send_whatsapp_notification")
            tool_result = await tool_spec["function"](message_content=last_msg or user_text)
            summary = self._fallback_tool_summary("send_whatsapp_notification", tool_result, user_text)
            return ("ஐயா, " if is_tamil else ("सर, " if is_hindi else "Sir, ")) + summary, {
                "executed": True,
                "tool": "send_whatsapp_notification",
                "whatsapp_url": tool_result.get("whatsapp_url"),
                "result": tool_result
            }

        # Check clinical RAG & Products for veterinary questions, medicine, diseases, products
        VET_PRODUCT_WORDS = [
            "what is", "explain", "definition", "how to cure", "treatment", "medicine", "cmt", 
            "swelling", "udder", "yellow milk", "bloat", "fever", "tick", "ticks", "product", "products",
            "chimertech", "buy", "shop", "knife", "remedy", "what to do", "மடிநோய்", "மருந்து", "பொருட்கள்"
        ]
        if any(w in lower_u for w in VET_PRODUCT_WORDS):
            rag_match = rag_engine.search(user_text)
            if rag_match and rag_match.get("spoken_response"):
                prefix = "ஐயா, " if is_tamil else ("सर, " if is_hindi else "Sir, ")
                return prefix + rag_match["spoken_response"], {"executed": True, "tool": "veterinary_and_products_rag"}

        # Milk Yield / Highest Milk
        if any(w in lower_u for w in ["highest milk", "more milk", "highest yield", "paal", "பால்", "दूध"]):
            tool_spec = FARM_TOOLS.get("get_milk_production_trends")
            tool_result = await tool_spec["function"]()
            summary = self._fallback_tool_summary("get_milk_production_trends", tool_result, user_text)
            return ("ஐயா, " if is_tamil else ("सर, " if is_hindi else "Sir, ")) + summary, {"executed": True, "tool": "get_milk_production_trends"}

        # Mastitis / Health anomaly queries
        if any(w in lower_u for w in ["mastitis", "risk", "differently", "sick", "problem", "abnormal", "மடிநோய்", "நோய்"]):
            tool_spec = FARM_TOOLS.get("analyze_mastitis_risk")
            tool_result = await tool_spec["function"](cow_id="COW003")
            summary = self._fallback_tool_summary("analyze_mastitis_risk", tool_result, user_text)
            return ("ஐயா, " if is_tamil else ("सर, " if is_hindi else "Sir, ")) + summary, {"executed": True, "tool": "analyze_mastitis_risk"}

        # Worker attendance
        if any(w in lower_u for w in ["worker", "staff", "who came", "duty", "attendance", "check in", "தொழிலாளர்கள்", "ஆட்கள்", "कर्मचारी"]):
            tool_spec = FARM_TOOLS.get("get_workers_and_staff_data")
            tool_result = await tool_spec["function"]()
            summary = self._fallback_tool_summary("get_workers_and_staff_data", tool_result, user_text)
            return ("ஐயா, " if is_tamil else ("सर, " if is_hindi else "Sir, ")) + summary, {"executed": True, "tool": "get_workers_and_staff_data"}

        # Feeding and eating duration
        if any(w in lower_u for w in ["feed", "fodder", "ration", "eating", "eat", "how long", "தீவனம்", "चारा"]):
            tool_spec = FARM_TOOLS.get("get_feed_and_nutrition")
            tool_result = await tool_spec["function"]()
            summary = self._fallback_tool_summary("get_feed_and_nutrition", tool_result, user_text)
            return ("ஐயா, " if is_tamil else ("सर, " if is_hindi else "Sir, ")) + summary, {"executed": True, "tool": "get_feed_and_nutrition"}

        # Cattle current activity / what cattle are doing now
        if any(w in lower_u for w in ["what cattle doing", "what doing now", "cattle doing", "cattle activity", "resting", "rumination", "மாடுகள் என்ன செய்கின்றன"]):
            tool_spec = FARM_TOOLS.get("get_herd_health_and_anomalies")
            tool_result = await tool_spec["function"]()
            summary = self._fallback_tool_summary("get_herd_health_and_anomalies", tool_result, user_text)
            return ("ஐயா, " if is_tamil else ("सर, " if is_hindi else "Sir, ")) + summary, {"executed": True, "tool": "get_herd_health_and_anomalies"}

        # Pending tasks / current schedule
        if any(w in lower_u for w in ["currently have to do", "have to do", "balance work", "remaining", "pending", "what work left", "what work", "மீதமுள்ள வேலை"]):
            tool_spec = FARM_TOOLS.get("get_daily_farm_comprehensive_summary")
            tool_result = await tool_spec["function"]()
            summary = self._fallback_tool_summary("get_daily_farm_comprehensive_summary", tool_result, user_text)
            return ("ஐயா, " if is_tamil else ("सर, " if is_hindi else "Sir, ")) + summary, {"executed": True, "tool": "get_daily_farm_comprehensive_summary"}

        # General farm summary
        tool_spec = FARM_TOOLS.get("get_daily_farm_comprehensive_summary")
        tool_result = await tool_spec["function"]()
        summary = self._fallback_tool_summary("get_daily_farm_comprehensive_summary", tool_result, user_text)
        return ("ஐயா, " if is_tamil else ("सर, " if is_hindi else "Sir, ")) + summary, {"executed": True, "tool": "get_daily_farm_comprehensive_summary"}

tool_router = AgentRouter()
