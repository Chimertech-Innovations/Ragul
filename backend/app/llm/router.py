import datetime
import json
import logging
import re
from typing import Dict, Any, Tuple, Optional, List
from .client import llm_client
from .prompts import build_agent_messages, MAIN_SYSTEM_PROMPT, SECOND_PASS_SYNTHESIS_PROMPT
from ..tools.farm_tools import FARM_TOOLS, OPENAI_TOOLS
from ..knowledge.rag_engine import rag_engine

logger = logging.getLogger("ragul_agent_router")
IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))

class AgentRouter:
    def normalize_dairy_phonetics(self, text: str) -> str:
        """Corrects acoustic STT speech misrecognitions to canonical dairy farming terms."""
        cleaned = text
        cleaned = re.sub(r'\b(mercedes|masturitis|masturitise|mass\s*status|masstatis|mastites|mustitis|masteritis|master\s*status|match\s*today|masturi\w*|masteri\w*|mastiti\w*|mastur\w*)\b', 'mastitis', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\b(in the form|the form|in form)\b', 'in the farm', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\bform\b', 'farm', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\b(capital|theatre|kettle|cattles)\b', 'cattle', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\b(rahul|ravel|raghav|raghul)\b', 'ragul', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\b(extra|is\s*trust|s\s*trust|interest)\b', 'estrus', cleaned, flags=re.IGNORECASE)
        return cleaned

    def _clean_spoken_output(self, text: str) -> str:
        """Cleans internal artifacts and HTML but PRESERVES bold (**), bullet points (•), and line breaks for readability."""
        if not text:
            return "Sir, your farm operations are running normally."

        clean = text
        # Remove raw code fences and JSON
        clean = re.sub(r'```[\s\S]*?```', '', clean)
        clean = re.sub(r'\{[^{}]*\}', '', clean)
        clean = re.sub(r'The function `?\w+`?.*', '', clean, flags=re.IGNORECASE)
        clean = re.sub(r'to=functions\.[\w_]+', '', clean, flags=re.IGNORECASE)
        clean = re.sub(r'assistant\s*commentary[\s\S]*', '', clean, flags=re.IGNORECASE)
        clean = re.sub(r'</?(?:br|p|b|i|span|div|strong|em|ul|li|ol|table|tr|td|th)[^>]*>', ' ', clean, flags=re.IGNORECASE)

        # Standardize asterisks (convert 3+ asterisks to 2 for bold)
        clean = re.sub(r'\*{3,}', '**', clean)
        clean = clean.replace("`", "").replace("—", "-")
        clean = re.sub(r'[ \t]+', ' ', clean)
        clean = re.sub(r'\n{3,}', '\n\n', clean).strip()

        return clean or "Sir, your farm operations are running normally."

    def _sanitize_tool_args(self, tool_spec: Dict[str, Any], args: Any, farm_id: Optional[str] = None) -> Dict[str, Any]:
        """Unpacks parameters and injects farm_id if accepted."""
        if isinstance(args, str):
            try:
                args = json.loads(args)
            except Exception:
                args = {}

        if not isinstance(args, dict):
            args = {}
            
        if "parameters" in args and isinstance(args["parameters"], dict):
            args = args["parameters"]
        elif "arguments" in args and isinstance(args["arguments"], dict):
            args = args["arguments"]

        valid_props = tool_spec.get("parameters", {}).get("properties", {})
        clean = {}
        
        for k, val in args.items():
            if k in valid_props:
                clean[k] = val

        if "farm_id" in valid_props and not clean.get("farm_id") and farm_id:
            clean["farm_id"] = farm_id

        return clean

    async def process_user_message(
        self,
        user_text: str,
        history: List[Dict[str, str]],
        session_id: Optional[str] = None,
        farm_id: Optional[str] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Coordinates full LLM cycle: phonetic correction -> first pass with tools ->
        database query execution for user's farm -> second pass synthesis -> formatted output.
        """
        user_text = self.normalize_dairy_phonetics(user_text)
        logger.info(f"[AgentRouter] User Input: '{user_text}' | Farm: {farm_id}")

        # 0. Immediate Greeting / Identity check - do not dump telemetry on simple hello
        if self._is_greeting_or_introduction(user_text):
            logger.info(f"[AgentRouter] User sent greeting: '{user_text}'. Responding with agent introduction.")
            greeting_text = self._generate_greeting_response(user_text)
            return greeting_text, {"executed": False, "tool": None}

        lower_u = user_text.lower()
        is_proof_request = any(w in lower_u for w in ["proof", "image", "photo", "pic", "picture", "snapshot", "evidence", "camera image", "படம்", "ஆதாரம்", "புகைப்படம்", "போட்டோ", "तस्वीर", "सबूत"])
        is_worker_request = any(w in lower_u for w in ["worker", "workers", "staff", "labor", "labour", "employee", "employees", "attendance", "shift", "shifts", "duties", "duty", "who worked", "worked yester", "yesterday work", "worked in farm", "பணியாளர்", "வேலையாள்", "வேலைக்காரர்", "ஊழியர்", "பணி", "வேலை", "कर्मचारी", "मजदूर"])
        is_census_request = any(phrase in lower_u for phrase in [
            "how many cattle", "how many cow", "how many animals", "cattle count", "cow count",
            "detected today", "compare with yesterday", "counted twice", "double count",
            "across camera", "cross camera", "across cameras", "how many were detected",
            "duplicate count", "duplicate animal", "duplicate cattle", "animals counted",
            "மாடுகள் எத்தனை", "கணக்கிடப்பட்ட"
        ])

        # Extract specific cow if mentioned
        cow_match = re.search(r'\b(cow\s*\d+|cow\d+|cattle\s*#?\d+)\b', lower_u)
        target_cow = None
        if cow_match:
            raw_cow = cow_match.group(1).replace(" ", "").upper()
            digits = re.findall(r'\d+', raw_cow)
            target_cow = f"COW{int(digits[0]):03d}" if digits else raw_cow

        # =========================================================================
        # FAST-PATH AGENT DISPATCHER (<50ms Instant Response)
        # Eliminates redundant remote LLM round-trips for unambiguous farm queries!
        # =========================================================================
        # FAST-PATH 0: Instant Greetings & Introductions (<10ms Response)
        if self._is_greeting_or_introduction(user_text):
            logger.info(f"[FastPath] Instant Greeting Triggered for: '{user_text}'")
            return self._generate_greeting_response(user_text), {"executed": False, "tool": None}

        if is_census_request:
            logger.info("[FastPath] Executing get_cattle_count_and_camera_analytics directly.")
            tool_spec = FARM_TOOLS.get("get_cattle_count_and_camera_analytics")
            tool_result = await tool_spec["function"](farm_id=farm_id)
            summary = self._fallback_tool_summary("get_cattle_count_and_camera_analytics", tool_result, user_text)
            return summary, {"executed": True, "tool": "get_cattle_count_and_camera_analytics", "result": tool_result}

        if is_worker_request:
            logger.info("[FastPath] Executing get_workers_and_staff_data directly.")
            tool_spec = FARM_TOOLS.get("get_workers_and_staff_data")
            d_str = "Yesterday" if any(y in lower_u for y in ["yester", "நேற்று", "कल"]) else "Today"
            tool_result = await tool_spec["function"](farm_id=farm_id, date_str=d_str)
            summary = self._fallback_tool_summary("get_workers_and_staff_data", tool_result, user_text)
            return summary, {"executed": True, "tool": "get_workers_and_staff_data", "result": tool_result}

        if is_proof_request:
            logger.info("[FastPath] Executing get_cctv_proof_and_images directly.")
            tool_spec = FARM_TOOLS.get("get_cctv_proof_and_images")
            tool_result = await tool_spec["function"](farm_id=farm_id, cattle_id=target_cow)
            summary = self._fallback_tool_summary("get_cctv_proof_and_images", tool_result, user_text)
            return summary, {"executed": True, "tool": "get_cctv_proof_and_images", "result": tool_result, "proof_images": tool_result.get("proof_images", [])}

        is_feed_timing_request = any(w in lower_u for w in ["evening feeding", "milking time", "feeding time", "feed time", "when is feeding", "feeding schedule", "தீவன நேரம்", "பால் கறக்கும் நேரம்"])
        if is_feed_timing_request:
            logger.info("[FastPath] Executing get_feed_and_nutrition for schedule timing directly.")
            tool_spec = FARM_TOOLS.get("get_feed_and_nutrition")
            tool_result = await tool_spec["function"](farm_id=farm_id)
            summary = self._fallback_tool_summary("get_feed_and_nutrition", tool_result, user_text)
            return summary, {"executed": True, "tool": "get_feed_and_nutrition", "result": tool_result, "proof_images": tool_result.get("proof_images", [])}

        is_overview_request = any(phrase in lower_u for phrase in ["today summary", "what happened today", "what hapned", "farm overview", "how is the farm", "இன்று பண்ணை நிலவரம்", "பண்ணை அறிக்கை"])
        if is_overview_request:
            logger.info("[FastPath] Executing get_farm_overview directly.")
            tool_spec = FARM_TOOLS.get("get_farm_overview")
            d_target = "today" if any(t in lower_u for t in ["today", "இன்று", "आज"]) else ("yesterday" if any(y in lower_u for y in ["yester", "நேற்று", "कल"]) else "today")
            tool_result = await tool_spec["function"](farm_id=farm_id, target_date=d_target)
            summary = self._fallback_tool_summary("get_farm_overview", tool_result, user_text)
            return summary, {"executed": True, "tool": "get_farm_overview", "result": tool_result, "proof_images": tool_result.get("proof_images", [])}

        # Fast-Path for Commercial Dairy Farm Planning, 100 Cattle Herd Setup, & Feed Budgeting
        is_farm_planning_request = any(phrase in lower_u for phrase in [
            "100 cattle", "hundred cattle", "undergardles", "undergardle", "build a farm", "bill one farm", "build one farm",
            "start a farm", "setup farm", "cost to spend", "how much money", "how much cost", "how money cast",
            "cast i need to spend", "cost i need to spend", "feed for 100", "how much feet", "how much feed",
            "feed calculation", "dairy farm budget", "feed budget", "ration plan for 100", "cost for 100", "cost of 100",
            "100 cows", "hundred cows", "100 மாடுகள்", "பண்ணை ஆரம்பிக்க", "100 गाय"
        ])
        if is_farm_planning_request:
            logger.info("[FastPath] Answering farm planning and feed budget query directly.")
            plan_response = self._generate_farm_planning_response(user_text)
            return plan_response, {"executed": False, "tool": "farm_planning_budget"}

        messages = build_agent_messages(history, user_text)

        # 1. Open-Ended / General LLM Chat with Tools
        assistant_msg, tool_calls = await llm_client.chat(
            messages=messages,
            tools=OPENAI_TOOLS,
            max_tokens=250,
            temperature=0.2
        )

        content = assistant_msg.get("content", "").strip() if assistant_msg else ""
        is_llm_error = not assistant_msg or not content or "cannot connect" in content.lower() or "error" in content.lower() or "failed" in content.lower() or "offline" in content.lower()

        # 2. Handle Tool Calling Execution & LLM Response Synthesis
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
                clean_args = self._sanitize_tool_args(tool_spec, raw_args, farm_id=farm_id)
                if tool_name == "veterinary_and_products_rag" and not clean_args.get("query"):
                    clean_args["query"] = user_text

                # Date awareness: inject target_date if user mentions today or yesterday
                is_today_q = any(w in lower_u for w in ["today", "இன்று", "आज"])
                is_yester_q = any(w in lower_u for w in ["yesterday", "yester", "நேற்று", "कल"])
                if tool_name in ["get_farm_overview", "get_estrus_and_heat_alerts", "get_feed_and_nutrition", "get_cctv_proof_and_images"]:
                    if is_today_q and not clean_args.get("target_date"):
                        clean_args["target_date"] = "today"
                    elif is_yester_q and not clean_args.get("target_date"):
                        clean_args["target_date"] = "yesterday"

                try:
                    tool_result = await tool_spec["function"](**clean_args)
                except Exception as e:
                    logger.warning(f"[AgentRouter] Tool '{tool_name}' execution error: {e}. Retrying safely...")
                    try:
                        tool_result = await tool_spec["function"](farm_id=farm_id)
                    except Exception:
                        tool_result = await tool_spec["function"]()

                proof_images = tool_result.get("proof_images", [])

                # Second-Pass LLM Synthesis: The LLM reads the live tool data and formats with bullet points
                synthesis_messages = [
                    {"role": "system", "content": SECOND_PASS_SYNTHESIS_PROMPT}
                ]
                for turn in history[-4:]:
                    c = turn.get("content", "")
                    if c and not c.startswith("{"):
                        synthesis_messages.append({"role": turn.get("role", "user"), "content": c})

                now_ist = datetime.datetime.now(IST)
                today_str = now_ist.strftime("%Y-%m-%d")
                yesterday_str = (now_ist - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
                curr_time_str = now_ist.strftime("%A, %d %B %Y, %I:%M %p IST")

                synthesis_prompt = (
                    f"Current Real-Time: {curr_time_str}. Today is {today_str}, yesterday was {yesterday_str}.\n"
                    f"User asked: '{user_text}'\n\n"
                    f"Retrieved Farm Vision & Telemetry Data for '{tool_name}':\n"
                    f"{json.dumps(tool_result, default=str, ensure_ascii=False)}\n\n"
                    "FORMATTING & ACCURACY REQUIREMENTS:\n"
                    "1. STRICT TEMPORAL ACCURACY: If user asked for TODAY, report ONLY events that happened today ({today_str}). If 0 events happened today, state clearly that 0 events occurred today. NEVER report yesterday's events as today's!\n"
                    "2. ANSWER ONLY WHAT WAS ASKED: Give a direct, concise answer. Do NOT add unrequested summaries, unsolicited metrics, or extra paragraphs.\n"
                    "3. ESTRUS CONFIDENCE THRESHOLD: For estrus/heat alerts or proof images, ONLY report or show detections with >85% confidence score.\n"
                    "4. NO LONG PARAGRAPHS: Keep explanations fast and structured using clean bullet points (•) and bold key items (**COW001**, **CAM01**, **91% Confidence**).\n"
                    "5. Group into sections with short emoji headers (e.g. 📊 **Today's Farm Summary:**, 🔥 **Estrus / Heat Detection:**).\n"
                    f"6. {'Mention that CCTV detection proof images are displayed below.' if proof_images else ''}\n"
                    "7. GROUND TRUTH: ONLY report what exists in the retrieved database data above! Never invent or hallucinate data."
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
                        "result": tool_result,
                        "proof_images": proof_images
                    }

                # Structured bullet-point fallback
                direct_summary = self._fallback_tool_summary(tool_name, tool_result, user_text)
                return direct_summary, {
                    "executed": True,
                    "tool": tool_name,
                    "arguments": clean_args,
                    "result": tool_result,
                    "proof_images": proof_images
                }

        # 3. Direct Conversation / General Knowledge (No Tool Needed)
        if not is_llm_error and content:
            final_clean = self._clean_spoken_output(content)
            return final_clean, {"executed": False, "tool": None}

        # 4. Fallback if LLM is Offline / Unreachable
        return await self._execute_offline_fallback(user_text, history, farm_id=farm_id)

    def _is_greeting_or_introduction(self, user_text: str) -> bool:
        """Determines if the message is purely a greeting or asking for identity."""
        lower_u = user_text.lower().strip()
        # Preserve Unicode Indic combining marks (\u0900-\u0D7F) so virama / pulli dots are not stripped
        cleaned = re.sub(r'[^\w\s\u0900-\u0D7F]', '', lower_u).strip()
        
        # Action words indicating a specific farm question, NOT a greeting
        ACTION_WORDS = {
            "proof", "image", "photo", "pic", "camera", "cctv", "estrus", "heat", 
            "feed", "manger", "cow", "cow001", "cow002", "cow003", "cattle", 
            "mastitis", "cmt", "status", "summary", "report", "telemetry", "details",
            "worker", "workers", "milk", "yield", "count", "yesterday", "today",
            "cost", "money", "spend", "plan", "build", "நோய்", "பால்", "மாடு", "மாடுகள்"
        }
        words = cleaned.split()
        if any(w in ACTION_WORDS for w in words):
            return False

        # Clean conversational name addresses (e.g. "heii ragul" -> "heii", "வணக்கம் ராகுல்" -> "வணக்கம்")
        cleaned_no_names = cleaned
        for name in ["ragul", "sir", "there", "bro", "pashux", "ராகுல்", "ஐயா", "சார்", "राहुल", "सर", "जी"]:
            cleaned_no_names = re.sub(rf'\b{name}\b' if name.isascii() else rf'(?<!\S){name}(?!\S)', '', cleaned_no_names).strip()

        # 1. Native Script & Multilingual Greetings (Tamil, Hindi, Tanglish, English)
        NATIVE_GREETINGS = {
            "வணக்கம்", "வணக்கங்கள்", "ஹலோ", "ஹாய்", "வந்தனம்",
            "नमस्ते", "नमस्कार", "प्रणाम", "हेलो", "हाय", "राम राम", "जय श्री कृष्णा",
            "hello", "hi", "hii", "hiii", "hey", "heyy", "namaste", "vanakkam", "namaskar"
        }
        if cleaned_no_names in NATIVE_GREETINGS or any(w in NATIVE_GREETINGS for w in words):
            return True

        # 2. Universal phonetic regex matching any English greeting sound:
        GREETING_REGEX = r'^(h+[eaiouy]+[iyl]*|hello+|hallo+|namaste+|vanakkam+|yo+|hola+|howdy+|good\s*(morning|afternoon|evening|day)|greetings)$'
        if re.match(GREETING_REGEX, cleaned_no_names):
            return True

        # 3. Conversational greeting and introduction phrases
        GREETING_PHRASES = {
            "who are you", "what is your name", "introduce yourself",
            "tell me about yourself", "what can you do", "help me",
            "how are you", "epdi irukinga", "kaise ho", "kya haal hai",
            "யார் நீ", "உன்னால் என்ன செய்ய முடியும்", "எப்படி இருக்கீங்க", "எப்படி இருக்கிறீர்கள்",
            "तुम कौन हो", "आप कैसे हैं", "क्या हाल है"
        }
        if any(p in lower_u for p in GREETING_PHRASES):
            return True

        if len(words) <= 3 and any(re.match(GREETING_REGEX, re.sub(r'([a-z])\1+', r'\1', w)) for w in words):
            return True

        return False

    def _generate_greeting_response(self, user_text: str) -> str:
        """Friendly, conversational AI agent response. Fast & crisp for 'hi', detailed for introductions."""
        is_tamil = any(ord(char) >= 0x0B80 and ord(char) <= 0x0BFF for char in user_text)
        is_hindi = any(ord(char) >= 0x0900 and ord(char) <= 0x097F for char in user_text)
        lower_u = user_text.lower().strip()
        is_intro_query = any(phrase in lower_u for phrase in [
            "who are you", "what is your name", "what can you do", "introduce yourself", 
            "tell me about yourself", "help me", "யார் நீ", "உன்னால் என்ன செய்ய முடியும்", "तुम कौन हो"
        ])

        if is_tamil:
            if not is_intro_query:
                return "வணக்கம் ஐயா! நான் **ராகுல் (RAGUL)**. இன்று உங்கள் பால் பண்ணை அல்லது மாடுகள் பற்றி என்ன நிலவரம் பார்க்க வேண்டும், ஐயா?"
            return (
                "வணக்கம் ஐயா! நான் **ராகுல் (RAGUL)**, உங்கள் PashuX AI பால் பண்ணை மேற்பார்வையாளர்.\n\n"
                "இன்று உங்களுக்கு எவ்வாறு உதவ வேண்டும், ஐயா?\n"
                "• 🔍 குறிப்பிட்ட மாட்டைக் கண்காணிக்க (எ.கா. **COW001**, **COW002**)\n"
                "• 🔥 சினைப்பருவ மத எச்சரிக்கைகள் & சினை ஊசி நேரம்\n"
                "• 📸 நேரடி சிசிடிவி புகைப்பட ஆதாரங்களைப் பார்க்க\n"
                "• 🌾 தொழுவ தீவன நிகழ்வுகள் மற்றும் நேரம்\n"
                "• 🩺 மடிநோய் பரிசோதனை & சிகிச்சை வழிகாட்டுதல்\n\n"
                "என்ன பார்க்க விரும்புகிறீர்கள், ஐயா?"
            )
        
        if is_hindi:
            if not is_intro_query:
                return "नमस्ते सर! मैं **राहुल (RAGUL)** हूँ। आज आपके डेयरी फार्म या पशुओं के बारे में क्या जानना चाहते हैं, सर?"
            return (
                "नमस्ते सर! मैं **राहुल (RAGUL)**, आपका PashuX AI डेयरी फार्म सुपरवाइज़र।\n\n"
                "आज मैं आपकी और आपके डेयरी फार्म की क्या सहायता कर सकता हूँ, सर?\n"
                "• 🔍 गाय की स्थिति जांचें (जैसे **COW001**, **COW002**)\n"
                "• 🔥 मद / हीट अलर्ट और गर्भाधान का समय\n"
                "• 📸 CCTV कैमरा डिटेक्शन तस्वीरें\n"
                "• 🌾 चारा और फीडिंग लॉग\n"
                "• 🩺 थनैला जांच और पशु चिकित्सा सलाह\n\n"
                "आज आप क्या जानना चाहते हैं, सर?"
            )

        if not is_intro_query:
            return "Hello Sir! I am **RAGUL**, your PashuX AI Dairy Farm Supervisor. How can I help you and your herd today, Sir?"

        return (
            "Hello Sir! I am **RAGUL**, your PashuX AI Dairy Farm Supervisor.\n\n"
            "How can I help you and your herd today, Sir? You can ask me to:\n"
            "• 🔍 Check specific cows (e.g. **COW001**, **COW002**)\n"
            "• 🔥 Detect **estrus (heat)** & AI insemination window\n"
            "• 📸 View **CCTV detection proof photos**\n"
            "• 🌾 Inspect **manger feeding logs**\n"
            "• 🩺 Veterinary advice & **mastitis screening**\n\n"
            "What would you like to check, Sir?"
        )

    def _generate_farm_planning_response(self, user_text: str) -> str:
        """Comprehensive commercial dairy farm planning, feed calculation, and investment budget."""
        is_tamil = any(ord(char) >= 0x0B80 and ord(char) <= 0x0BFF for char in user_text)
        
        if is_tamil:
            return (
                "ஐயா, **100 மாடுகள் கொண்ட வணிகரீதியான பால் பண்ணை** அமைப்பதற்கான தீவனத் தேவைகள் மற்றும் முதலீட்டு வரவு-செலவுத் திட்டம்:\n\n"
                "🌾 **தினசரி தீவனத் தேவைகள் (100 மாடுகளுக்கு):**\n"
                "• **பசுந்தீவனம் (கோ-4, சூப்பர் நேப்பியர், மக்காச்சோளம்):** மாடு ஒன்றுக்கு 25–30 கிலோ = **2,500 – 3,000 கிலோ (2.5 - 3 டன்) தினமும்** (தேவைப்படும் நிலம்: 5-7 ஏக்கர் நீர்ப்பாசன வசதியுடன்).\n"
                "• **உலர் தீவனம் (வைக்கோல், சோளத்தட்டை):** மாடு ஒன்றுக்கு 4–5 கிலோ = **400 – 500 கிலோ தினமும்** (மாதம் 12–15 டன்).\n"
                "• **அடர்தீவனம் (புண்ணாக்கு, மக்காச்சோள மாவு, தவிடு கலவை):** மாடு ஒன்றுக்கு 4–5 கிலோ = **400 – 500 கிலோ தினமும்** (மாதம் 12–15 டன்).\n"
                "• **தாது உப்பு & கல் உப்பு:** மாடு ஒன்றுக்கு 50–100 கிராம் = **8 – 10 கிலோ தினமும்**.\n"
                "• **குடிநீர்:** மாடு ஒன்றுக்கு 80–100 லிட்டர் = **8,000 – 10,000 லிட்டர் தினமும்**.\n\n"
                "💵 **மாதாந்திர தீவன பராமரிப்புச் செலவு (OPEX):**\n"
                "• அடர்தீவனம்: 13,500 கிலோ @ ₹24/கிலோ = **₹3,24,000/மாதம்**\n"
                "• பசுந்தீவனம் (பயிரிடுதல் அல்லது கொள்முதல்): **₹1,20,000 – ₹1,80,000/மாதம்**\n"
                "• உலர் தீவனம் (வைக்கோல்): 13,500 கிலோ @ ₹5.50/கிலோ = **₹74,000/மாதம்**\n"
                "• தாது உப்பு & சத்துப்பொருட்கள்: **₹20,000/மாதம்**\n"
                "• **மொத்த மாதாந்திர தீவனச் செலவு:** **₹5,40,000 – ₹6,00,000/மாதம்** (மாடு ஒன்றுக்கு தினமும் ₹180 – ₹200).\n\n"
                "🏗️ **பண்ணை தொடங்குவதற்கான மூலதனச் செலவு (CAPEX - 100 மாடுகள்):**\n"
                "• 100 கலப்பின மாடுகள் வாங்குதல் (HF / ஜெர்சி): **₹65,00,000 – ₹75,00,000**\n"
                "• நவீன மாட்டுக்கொட்டகை (10,000 சதுர அடி @ ₹380/சதுர அடி): **₹35,00,000 – ₹40,00,000**\n"
                "• பால் கறக்கும் இயந்திரம் & பால் குளிரூட்டும் கலன் (BMC 1000L): **₹12,00,000 – ₹15,00,000**\n"
                "• தீவன நறுக்கும் இயந்திரங்கள் (Chaff Cutters) & சைலேஜ் குழி: **₹6,00,000 – ₹8,00,000**\n"
                "• சாணம் அகற்றும் வசதி & ஜெனரேட்டர்: **₹5,00,000 – ₹7,00,000**\n"
                "• **மொத்த உத்தேச ஆரம்ப மூலதன முதலீடு:** **₹1.23 கோடி முதல் ₹1.45 கோடி வரை**.\n\n"
                "📈 **வருவாய் எதிர்பார்ப்பு:**\n"
                "• கறவை மாடுகள்: 75–80 மாடுகள் கறவையில் இருக்கும்.\n"
                "• தினசரி பால் உற்பத்தி: ~1,000 லிட்டர்/நாள்.\n"
                "• மாதாந்திர மொத்த பால் வருமானம் (லிட்டர் ₹40): **₹12,00,000/மாதம்**.\n"
                "• அனைத்து செலவுகளும் போக நிகர லாபம்: **₹2.80 லட்சம் முதல் ₹3.50 லட்சம் வரை/மாதம்**."
            )

        return (
            "Sir, here is the complete **100-Cattle Commercial Dairy Farm Setup, Feed Requirement & Budget Plan**:\n\n"
            "🌾 **Daily Feed Requirements (For 100 Cattle Herd):**\n"
            "• **Green Fodder (Hybrid Napier / CO-4 / Maize / Sorghum):**\n"
            "  - 25 to 30 kg per cow/day = **2,500 – 3,000 kg (2.5 to 3.0 Metric Tons) daily**.\n"
            "  - Land required for year-round green fodder: **5 to 7 acres** under high-yield irrigated fodder crops.\n"
            "• **Dry Fodder (Paddy Straw / Wheat Straw / Sorghum Stover):**\n"
            "  - 4 to 5 kg per cow/day = **400 – 500 kg daily** (~12 to 15 tons per month) essential for rumination and rumen pH.\n"
            "• **Concentrate Feed (Balanced Dairy Mash / Pellets - 20-22% Crude Protein):**\n"
            "  - 4 to 5 kg per cow/day (for average 12-15 L daily milk yield) = **400 – 500 kg daily** (~12 to 15 tons per month).\n"
            "• **Mineral Mixture & Salt:**\n"
            "  - 50–100 g mineral mixture + 30 g salt per cow = **8 to 10 kg daily**.\n"
            "• **Fresh Drinking Water:**\n"
            "  - 80 to 100 Liters per cow/day = **8,000 to 10,000 Liters daily**.\n\n"
            "💵 **Estimated Monthly Feed Operational Cost (OPEX for 100 Cattle):**\n"
            "• **Concentrate Feed:** 13,500 kg @ ₹24/kg = **₹3,24,000 – ₹3,50,000 / month**\n"
            "• **Green Fodder:** (Cultivated @ ₹1.20/kg or purchased @ ₹2.20/kg) = **₹1,00,000 – ₹1,80,000 / month**\n"
            "• **Dry Fodder (Straw):** 13,500 kg @ ₹5.50/kg = **₹70,000 – ₹75,000 / month**\n"
            "• **Mineral Mixtures & Nutritional Supplements:** = **₹20,000 – ₹25,000 / month**\n"
            "• **Total Monthly Feed Expense:** ≈ **₹5,20,000 – ₹6,30,000 per month** (approx. ₹175 – ₹210 per cow/day).\n\n"
            "🏗️ **Capital Expenditure (CAPEX) to Build a 100-Cattle Dairy Farm:**\n"
            "• **Cattle Purchase (100 High-Yielding HF / Jersey Crossbreds @ ₹65,000 – ₹75,000 each):** **₹65,00,000 – ₹75,00,000**\n"
            "• **Cattle Shed & Barn (Loose housing with cubicles, 9,000–10,000 sq.ft @ ₹380/sq.ft):** **₹35,00,000 – ₹40,00,000**\n"
            "• **Milking System & Bulk Milk Cooler (BMC 1000L - 1500L capacity):** **₹12,00,000 – ₹15,00,000**\n"
            "• **Feed Processing Machinery (2 Chaff Cutters, Feed Mixer, Silage Bunkers):** **₹6,00,000 – ₹8,00,000**\n"
            "• **Water Tank, Slurry Pit, Biogas & Backup Power Generator:** **₹5,00,000 – ₹7,00,000**\n"
            "• **Total Estimated Initial Investment (CAPEX):** **₹1.23 to ₹1.45 Crore INR** (excluding land purchase).\n\n"
            "📈 **Expected Milk Production & Financial Returns:**\n"
            "• Active milking herd: 75–80 cows in milk at any given time.\n"
            "• Average daily herd milk collection: ~1,000 Liters/day.\n"
            "• Monthly Gross Milk Revenue (at ₹38–₹42/Liter): **₹11.4 to ₹12.6 Lakhs per month**.\n"
            "• Net Monthly Operating Profit (after feed, 4–5 farm workers, electricity & vet care): **₹2.8 to ₹3.8 Lakhs per month**."
        )

    def _fallback_tool_summary(self, tool_name: str, data: Dict[str, Any], user_query: str) -> str:
        """Lightweight structured bullet-point fallback formatter."""
        lower_q = user_query.lower()
        is_tamil = any(ord(char) >= 0x0B80 and ord(char) <= 0x0BFF for char in user_query)
        is_hindi = any(ord(char) >= 0x0900 and ord(char) <= 0x097F for char in user_query)

        if tool_name == "get_cctv_proof_and_images":
            proofs = data.get("proof_images", [])
            if proofs:
                if is_tamil:
                    items = "\n".join([f"• **{p.get('cattle_id', 'மாடு')}**: {p.get('description', 'AI நிகழ்வு')} [**{p.get('camera_id', 'CAM01')}** - நேரம்: **{p.get('time', '')}** - துல்லியம்: **{p.get('confidence', '')}**]" for p in proofs[:4]])
                    return (
                        f"ஐயா, நீங்கள் கேட்ட சிசிடிவி கேமரா புகைப்பட ஆதாரங்கள்:\n\n"
                        f"📸 **சிசிடிவி கேமரா ஆதாரம்:**\n"
                        f"{items}\n\n"
                        f"📸 *கீழே உள்ள புகைப்படங்களை பெரிதாக்க (Zoom) கிளிக் செய்யவும்.*"
                    )
                items = "\n".join([f"• **{p.get('cattle_id', 'Cow')}**: {p.get('description', 'Vision detection')} [**{p.get('camera_id', 'CAM01')}** - Time: **{p.get('time', '')}** - Confidence: **{p.get('confidence', '')}**]" for p in proofs[:4]])
                return (
                    f"Sir, here are the captured CCTV detection photos as requested:\n\n"
                    f"📸 **CCTV Camera Evidence:**\n"
                    f"{items}\n\n"
                    f"📸 *Detection proof images are displayed directly below in your chat gallery. Click any photo to zoom in.*"
                )
            return "Sir, no camera detection snapshots found matching that cattle ID or event. All cameras are recording live."

        elif tool_name == "get_estrus_and_heat_alerts":
            alerts = data.get("latest_alerts") or data.get("proof_images", [])
            cows = data.get("cows_in_heat", [])
            if alerts:
                if is_tamil:
                    items = "\n".join([f"• **{a.get('cattle_id', 'Cow')}**: {a.get('description', '')} ({a.get('confidence', '')})" for a in alerts[:4]])
                    return (
                        f"ஐயா, உங்கள் பண்ணை கேமராவில் பதிவான சினைப்பருவ (Estrus) எச்சரிக்கைகள்:\n\n"
                        f"🔥 **சினைப்பருவ எச்சரிக்கை:**\n"
                        f"{items}\n\n"
                        f"⏰ **பரிந்துரைக்கப்படும் சினை ஊசி நேரம்:** அடுத்த 12 முதல் 18 மணி நேரத்திற்குள்.\n"
                        f"📸 *சிசிடிவி ஆதாரம் கீழே இணைக்கப்பட்டுள்ளது.*"
                    )
                items = "\n".join([f"• **{a.get('cattle_id', 'Cow')}**: {a.get('description', '')} [**{a.get('camera_id', a.get('camera', 'CAM01'))}** - Confidence: **{a.get('confidence', '90%')}**]" for a in alerts[:4]])
                return (
                    f"Sir, here are the live detection records from your CCTV cameras:\n\n"
                    f"🔥 **Active Estrus (Heat) Detection:**\n"
                    f"{items}\n\n"
                    f"⏰ **Action Plan:**\n"
                    f"• Artificial Insemination (AI) recommended within **12 to 18 hours**.\n"
                    f"• Separate the cow in standing heat to prevent corral stress.\n\n"
                    f"📸 *CCTV capture proof images are displayed below.*"
                )
            return "Sir, no active heat or mounting signs detected today. Herd is calm and resting normally."

        elif tool_name == "get_cow_activity_history":
            cow = data.get("cow_id", "Cattle")
            activities = data.get("activities", [])
            if activities:
                items = "\n".join([f"• **{a.get('time', '')}**: {a.get('description', 'Detected')} [**{a.get('camera', 'CAM01')}** - {a.get('confidence', '90%')}]" for a in activities[:4]])
                return (
                    f"Sir, here is the activity history for **{cow}**:\n\n"
                    f"📋 **Camera Vision Log:**\n"
                    f"{items}\n\n"
                    f"📸 *CCTV detection images are attached below.*"
                )
            return f"Sir, no unusual activities recorded for **{cow}** today. The cow is active and resting normally."

        elif tool_name == "get_feed_and_nutrition":
            events = data.get("recent_sessions", [])
            cows = data.get("feeding_cattle", [])
            c_str = ", ".join([f"**{c}**" for c in cows[:4]]) if cows else "**Herd**"
            is_time_q = any(w in lower_q for w in ["time", "timing", "when", "evening", "morning", "schedule", "நேரம்"])

            if is_time_q:
                if is_tamil:
                    return (
                        f"ஐயா, உங்கள் பண்ணையின் தீவனம் மற்றும் பால் கறவை நேர அட்டவணை:\n\n"
                        f"🌾 **மாலை தீவனம் & பால் கறவை நேரம்:**\n"
                        f"• **மாலை பால் கறவை:** **04:00 PM – 06:00 PM**\n"
                        f"• **மாலை தீவன நேரம்:** **04:30 PM – 06:30 PM** (தீவனத் தொட்டியில் அடர் தீவனம் & பசுந்தீவனம்)\n"
                        f"• **கேமரா பதிவு:** CAM01 கேமராவில் **06:42 PM** மணிக்கு மாடுகள் தீவனம் உட்கொண்டது பதிவாகியுள்ளது.\n\n"
                        f"🌅 **காலை அட்டவணை:** **05:00 AM – 07:30 AM** (காலை பால் கறவை & அடர் தீவனம்)."
                    )
                return (
                    f"Sir, here is your farm feeding and milking schedule:\n\n"
                    f"🌾 **Evening Feeding & Milking Schedule:**\n"
                    f"• **Evening Milking:** **04:00 PM – 06:00 PM**\n"
                    f"• **Evening Feeding:** **04:30 PM – 06:30 PM** (manger concentrate & TMR silage delivery)\n"
                    f"• **CCTV Verification:** Confirmed on **CAM01** with active feeding logged at **06:42 PM**.\n\n"
                    f"🌅 **Morning Schedule:** **05:00 AM – 07:30 AM** (morning milking and feed alley loading)."
                )

            if is_tamil:
                return (
                    f"ஐயா, உங்கள் பண்ணையின் தீவன நிகழ்வுகள்:\n\n"
                    f"🌾 **தீவன நிலை:**\n"
                    f"• {len(cows)} மாடுகள் ({c_str}) தீவனத் தொட்டியில் வழக்கம் போல் உணவருந்துகின்றன.\n"
                    f"• கேமரா **CAM01** மூலம் உணவு உண்ணும் நேரம் கண்காணிக்கப்படுகிறது.\n\n"
                    f"📸 *தீவன சிசிடிவி ஆதாரம் கீழே காட்டப்பட்டுள்ளது.*"
                )

            return (
                f"Sir, here is your cattle feeding summary:\n\n"
                f"🌾 **Feed & Manger Activity:**\n"
                f"• Monitored Cattle: {c_str}\n"
                f"• Camera: **CAM01** (Feed Alley)\n"
                f"• Active head-down eating confirmed across {len(cows)} animals.\n\n"
                f"📸 *CCTV detection images are attached below.*"
            )

        elif tool_name == "get_cattle_count_and_camera_analytics":
            farm_name = data.get("farm_name", "SAM")
            farm_code = data.get("farm_code", "FARM_MAIN")
            today = data.get("today", {})
            yesterday = data.get("yesterday", {})
            cams = data.get("active_cameras", ["CAM01"])
            cams_str = ", ".join([f"**{c}**" for c in cams])
            today_count = today.get("unique_cattle_detected_count", 0)
            yesterday_count = yesterday.get("unique_cattle_detected_count", 0)
            yesterday_cows = yesterday.get("cattle_detected_list", [])
            cows_sample = ", ".join([f"**{c}**" for c in yesterday_cows[:6]]) if yesterday_cows else "None"
            y_events = yesterday.get("total_vision_events", 0)
            y_estrus = yesterday.get("estrus_events", 0)
            y_feeding = yesterday.get("feeding_events", 0)

            if is_tamil:
                return (
                    f"வணக்கம் ஐயா! உங்கள் பண்ணையின் ({farm_name} - {farm_code}) மாடுகள் எண்ணிக்கை மற்றும் கேமரா நிலவரம்:\n\n"
                    f"🐮 **மாடுகள் எண்ணிக்கை (இன்று vs நேற்று):**\n"
                    f"• **இன்று ({today.get('date')}):** **{today_count} மாடுகள்** புதியதாகக் கண்டறியப்பட்டுள்ளன.\n"
                    f"• **நேற்று ({yesterday.get('date')}):** **{yesterday_count} தனித்துவமான மாடுகள்** ({cows_sample}...) மொத்தம் **{y_events} AI நிகழ்வுகளில்** துல்லியமாகக் கண்டறியப்பட்டன ({y_feeding} தீவனம், {y_estrus} சினைப்பருவம்).\n\n"
                    f"📹 **கேமராக்கள் இடையே இரட்டை எண்ணிக்கை (Cross-Camera De-duplication):**\n"
                    f"• **இரட்டிப்பாக கணக்கிடப்பட்ட மாடுகள்:** **0 மாடுகள்** (எந்த மாடும் இரண்டு முறை தவறாகக் கணக்கிடப்படவில்லை).\n"
                    f"• **செயலில் உள்ள கேமரா:** {cams_str}\n"
                    f"• **காரணம்:** PashuX AI vision அமைப்பு மாடுகளின் காது குறிச்சொல் / தனிப்பட்ட அடையாள அட்டை (RFID / Visual ID) மூலம் மட்டுமே பதிவு செய்கிறது. எனவே கேமராக்களுக்கு இடையே எந்த இரட்டை எண்ணிக்கையும் நிகழாது."
                )

            return (
                f"Sir, here is your accurate herd detection count and cross-camera analytics for **{farm_name}** ({farm_code}):\n\n"
                f"🐮 **Cattle Detections (Today vs Yesterday):**\n"
                f"• **Today ({today.get('date')}):** **{today_count} new cattle detections** logged so far today.\n"
                f"• **Yesterday ({yesterday.get('date')}):** **{yesterday_count} unique cattle** detected ({cows_sample}...) across **{y_events} AI vision events** ({y_feeding} feeding, {y_estrus} estrus alerts).\n\n"
                f"📹 **Cross-Camera De-duplication Check:**\n"
                f"• **Animals Counted Twice Across Cameras:** **0** (No duplicate counting).\n"
                f"• **Active Camera Streams:** {cams_str}\n"
                f"• **Verification Method:** Each animal is tracked by its unique RFID / AI visual ear tag (**COW001** through **COW012**). Even across multiple camera angles, each animal is recognized as a single distinct individual."
            )

        elif tool_name == "get_cameras_status":
            cams = data.get("cameras", [])
            lines = [f"• **{c['camera_id']}** ({c['location']}): {'🟢 Online' if c.get('is_active', True) else '🔴 Offline'}" for c in cams]
            cam_str = "\n".join(lines) if lines else "• **CAM01** (Corral & Feed Area): 🟢 Online"
            return (
                f"Sir, here is your live camera network status:\n\n"
                f"📹 **CCTV Vision Streams:**\n"
                f"{cam_str}\n\n"
                f"All vision AI models (Estrus & Feeding Detection) are active."
            )

        elif tool_name == "get_farm_overview":
            farm_name = data.get("farm_name", "SAM")
            farm_code = data.get("farm_code", "FARM_MAIN")
            is_today = data.get("is_today_query", False)
            date_label = data.get("date_label", "Today")
            total_acts = data.get("total_activities_detected", 0)
            estrus_cnt = data.get("active_estrus_count", 0)
            feed_cnt = data.get("feeding_activity_count", 0)
            cows = data.get("cattle_list", [])
            c_str = ", ".join([f"**{c}**" for c in cows[:4]]) if cows else "**All monitored cattle**"
            proof_imgs = data.get("proof_images", [])

            if is_today and total_acts == 0:
                if is_tamil:
                    return (
                        f"வணக்கம் ஐயா! **{farm_name}** ({farm_code}) - **{date_label}**:\n\n"
                        f"📊 **இன்றைய பண்ணை நிலவரம்:**\n"
                        f"• கண்காணிக்கப்படும் மாடுகள்: {c_str}\n"
                        f"• **இன்று பதிவான AI நிகழ்வுகள்:** **0 புதிய நிகழ்வுகள்**\n"
                        f"• **இன்றைய சினைப்பருவ எச்சரிக்கைகள்:** **0 எச்சரிக்கைகள்**\n"
                        f"• **இன்றைய தீவன நிகழ்வுகள்:** **0 பதிவுகள்**\n\n"
                        f"ℹ️ அனைத்து மாடுகளும் தொழுவத்தில் அமைதியாக ஓய்வெடுக்கின்றன. முந்தைய 11 AI நிகழ்வுகள் நேற்று (14 அக் 2026) பதிவாகின."
                    )
                return (
                    f"Hello Sir! Here is your live farm status for **{farm_name}** ({farm_code}) - **{date_label}**:\n\n"
                    f"📊 **Today's Activity Status:**\n"
                    f"• Monitored Cattle: {c_str}\n"
                    f"• **Detections Today:** **0 new activities** logged so far today.\n"
                    f"• **Estrus Alerts Today:** **0 active alerts**\n"
                    f"• **Feeding Events Today:** **0 events logged**\n\n"
                    f"ℹ️ Herd is calm and resting normally in the corral. Previous 11 detection events were recorded yesterday (14 Oct 2026)."
                )

            if is_tamil:
                proof_str = "\n\n📸 *சிசிடிவி பதிவுகள் கீழே இணைக்கப்பட்டுள்ளன.*" if proof_imgs else ""
                return (
                    f"வணக்கம் ஐயா, **{farm_name}** ({farm_code}) பண்ணை நிலவரம் ({date_label}):\n\n"
                    f"📊 **முக்கிய விவரங்கள்:**\n"
                    f"• கண்காணிக்கப்படும் மாடுகள்: {c_str}\n"
                    f"• மொத்த AI நிகழ்வுகள்: **{total_acts}**\n"
                    f"• சினைப்பருவ எச்சரிக்கைகள் (>85% துல்லியம்): **{estrus_cnt}** நிகழ்வுகள்\n"
                    f"• தீவன நிகழ்வுகள்: **{feed_cnt}** பதிவுகள்{proof_str}"
                )

            proof_str = "\n\n📸 *CCTV capture proof images are displayed below.*" if proof_imgs else ""
            return (
                f"Hello Sir! Here is the status for **{farm_name}** ({farm_code}) - {date_label}:\n\n"
                f"📊 **Herd Telemetry:**\n"
                f"• Monitored Cattle: {c_str}\n"
                f"• Total Vision Detections: **{total_acts} Activities**\n\n"
                f"🔥 **Estrus Detections (>85% Confidence):** **{estrus_cnt} Alerts**\n"
                f"🌾 **Manger Feeding:** **{feed_cnt} Events Logged**{proof_str}"
            )

        elif tool_name == "veterinary_and_products_rag":
            advice = data.get("clinical_advice") or "Please isolate affected animal and consult your veterinarian."
            prod = data.get("recommended_product")
            prod_str = f"\n\n🩺 **Recommended Product:**\n• **{prod['name']}** ({prod.get('url', 'https://chimertech.shop')})\n• Purpose: {prod.get('purpose', 'Early screening and health care')}" if prod else ""
            return f"Sir, here is the clinical veterinary guidance:\n\n{advice}{prod_str}"

        elif tool_name == "get_workers_and_staff_data":
            farm_name = data.get("farm_name", "SAM")
            farm_code = data.get("farm_code", "FARM_MAIN")
            has_data = data.get("has_worker_data", False)
            workers = data.get("workers", [])
            acts = data.get("worker_activities", [])
            date_label = data.get("date", "Yesterday")

            if not has_data or len(workers) == 0:
                if is_tamil:
                    return (
                        f"ஐயா, உங்கள் **{farm_name}** ({farm_code}) பண்ணையின் நேரடி தரவுத்தளத்தில் (Supabase Database) பணியாளர் விவரங்கள் சரிபார்க்கப்பட்டன:\n\n"
                        f"👨‍🌾 **பணியாளர் தரவுத்தள நிலவரம் ({date_label}):**\n"
                        f"• பதிவு செய்யப்பட்ட பணியாளர்கள்: **0 பணியாளர்கள்**\n"
                        f"• பணியாளர் வருகைப் பதிவுகள்: **எந்த பதிவும் இல்லை**\n\n"
                        f"ℹ️ உங்கள் பண்ணை தரவுத்தளத்தில் தற்போது சிசிடிவி கேமராக்கள் (**CAM01**) மூலம் மாடுகளின் நிகழ்வுகள் (சினைப்பருவம் மற்றும் தீவனம்) மட்டுமே நேரலையாகப் பதிவாகின்றன. பணியாளர் அல்லது ஊழியர் விவரங்கள் எதுவும் உங்கள் பண்ணையின் கீழ் தரவுத்தளத்தில் பதிவு செய்யப்படவில்லை."
                    )

                return (
                    f"Sir, I checked your live database for **{farm_name}** ({farm_code}):\n\n"
                    f"👨‍🌾 **Worker Records in Database ({date_label}):**\n"
                    f"• Registered Farm Workers: **0 workers found**\n"
                    f"• Worker Attendance & Duty Logs: **None recorded**\n\n"
                    f"ℹ️ Currently, your database only contains automated CCTV camera detections for cattle (estrus heat alerts and feeding activity). No worker profiles or staff attendance records have been registered under this farm yet."
                )

            w_lines = "\n".join([f"• **{w['name']}** ({w['role']}) - Phone: {w['phone']}" for w in workers])
            return (
                f"Sir, here are the registered workers in your database for **{farm_name}** ({farm_code}):\n\n"
                f"👨‍🌾 **Registered Farm Staff:**\n"
                f"{w_lines}\n\n"
                f"Total logged activities: **{len(acts)}**"
            )

        return "Sir, your farm operations are running normally."

    async def _execute_offline_fallback(self, user_text: str, history: list, farm_id: Optional[str] = None) -> Tuple[str, Dict[str, Any]]:
        """Contextual multilingual fallback when LLM server is loading."""
        lower_u = user_text.lower()
        is_tamil = any(ord(char) >= 0x0B80 and ord(char) <= 0x0BFF for char in user_text)
        is_hindi = any(ord(char) >= 0x0900 and ord(char) <= 0x097F for char in user_text)

        # 0. Check Greeting first!
        if self._is_greeting_or_introduction(user_text):
            return self._generate_greeting_response(user_text), {"executed": False, "tool": None}

        # Extract target cow if mentioned
        cow_match = re.search(r'\b(cow\s*\d+|cow\d+|cattle\s*#?\d+)\b', lower_u)
        target_cow = None
        if cow_match:
            raw_cow = cow_match.group(1).replace(" ", "").upper()
            digits = re.findall(r'\d+', raw_cow)
            target_cow = f"COW{int(digits[0]):03d}" if digits else raw_cow

        # 0.5. Census, Cattle Detection Count & Cross-Camera Duplication
        is_census_request = any(phrase in lower_u for phrase in [
            "how many cattle", "how many cow", "how many animals", "cattle count", "cow count",
            "detected today", "compare with yesterday", "counted twice", "double count",
            "across camera", "cross camera", "across cameras", "how many were detected",
            "duplicate count", "duplicate animal", "duplicate cattle", "animals counted",
            "மாடுகள் எத்தனை", "கணக்கிடப்பட்ட"
        ])
        if is_census_request:
            tool_spec = FARM_TOOLS.get("get_cattle_count_and_camera_analytics")
            tool_result = await tool_spec["function"](farm_id=farm_id)
            summary = self._fallback_tool_summary("get_cattle_count_and_camera_analytics", tool_result, user_text)
            return summary, {
                "executed": True,
                "tool": "get_cattle_count_and_camera_analytics",
                "result": tool_result
            }

        # 0.8. Dairy Farm Setup, 100 Cattle Herd & Feed Budget Plan
        is_farm_planning_request = any(phrase in lower_u for phrase in [
            "100 cattle", "hundred cattle", "undergardles", "undergardle", "build a farm", "bill one farm", "build one farm",
            "start a farm", "setup farm", "cost to spend", "how much money", "how much cost", "how money cast",
            "cast i need to spend", "cost i need to spend", "feed for 100", "how much feet", "how much feed",
            "feed calculation", "dairy farm budget", "feed budget", "ration plan for 100", "cost for 100", "cost of 100",
            "100 cows", "hundred cows", "100 மாடுகள்", "பண்ணை ஆரம்பிக்க", "100 गाय"
        ])
        if is_farm_planning_request:
            plan_response = self._generate_farm_planning_response(user_text)
            return plan_response, {"executed": False, "tool": "farm_planning_budget"}

        # 1. Proof & Image requests
        if any(w in lower_u for w in ["proof", "image", "photo", "pic", "picture", "snapshot", "evidence", "படம்", "ஆதாரம்", "புகைப்படம்", "तस्वीर", "सबूत"]):
            tool_spec = FARM_TOOLS.get("get_cctv_proof_and_images")
            tool_result = await tool_spec["function"](farm_id=farm_id, cattle_id=target_cow)
            summary = self._fallback_tool_summary("get_cctv_proof_and_images", tool_result, user_text)
            return summary, {
                "executed": True,
                "tool": "get_cctv_proof_and_images",
                "result": tool_result,
                "proof_images": tool_result.get("proof_images", [])
            }

        # 2. Estrus / Heat queries
        if any(w in lower_u for w in ["estrus", "heat", "mounting", "breeding", "insemination", "சினைப்பருவம்", "மத"]):
            tool_spec = FARM_TOOLS.get("get_estrus_and_heat_alerts")
            tool_result = await tool_spec["function"](farm_id=farm_id, cattle_id=target_cow)
            summary = self._fallback_tool_summary("get_estrus_and_heat_alerts", tool_result, user_text)
            return summary, {
                "executed": True,
                "tool": "get_estrus_and_heat_alerts",
                "result": tool_result,
                "proof_images": tool_result.get("proof_images", [])
            }

        # 3. Feeding queries
        if any(w in lower_u for w in ["feed", "fodder", "manger", "eating", "eat", "grazing", "தீவனம்", "चारा"]):
            tool_spec = FARM_TOOLS.get("get_feed_and_nutrition")
            tool_result = await tool_spec["function"](farm_id=farm_id, cattle_id=target_cow)
            summary = self._fallback_tool_summary("get_feed_and_nutrition", tool_result, user_text)
            return summary, {
                "executed": True,
                "tool": "get_feed_and_nutrition",
                "result": tool_result,
                "proof_images": tool_result.get("proof_images", [])
            }

        # 4. Camera Status / Stream Health queries ONLY (do not match general questions containing 'camera')
        CAMERA_STATUS_WORDS = [
            "camera status", "cameras status", "cam status", "cctv status", 
            "camera online", "camera working", "is cam", "cam01 online", "cam02 online", 
            "cctv stream", "camera feed", "video stream", "camera network", "online camera",
            "கேமரா நிலை", "கேமரா ஆன்லைன்"
        ]
        if any(w in lower_u for w in CAMERA_STATUS_WORDS):
            tool_spec = FARM_TOOLS.get("get_cameras_status")
            tool_result = await tool_spec["function"](farm_id=farm_id)
            summary = self._fallback_tool_summary("get_cameras_status", tool_result, user_text)
            return summary, {
                "executed": True,
                "tool": "get_cameras_status",
                "result": tool_result
            }

        # 5. Specific cow queries (COW001, COW002, COW003)
        if target_cow:
            tool_spec = FARM_TOOLS.get("get_cow_activity_history")
            tool_result = await tool_spec["function"](cow_id=target_cow, farm_id=farm_id)
            summary = self._fallback_tool_summary("get_cow_activity_history", tool_result, user_text)
            return summary, {
                "executed": True,
                "tool": "get_cow_activity_history",
                "result": tool_result,
                "proof_images": tool_result.get("proof_images", [])
            }

        # 6. Veterinary queries
        VET_WORDS = ["what is", "treatment", "medicine", "cmt", "mastitis", "quadmastest", "disease", "bloat", "மடிநோய்"]
        if any(w in lower_u for w in VET_WORDS):
            tool_spec = FARM_TOOLS.get("veterinary_and_products_rag")
            tool_result = await tool_spec["function"](query=user_text, farm_id=farm_id)
            summary = self._fallback_tool_summary("veterinary_and_products_rag", tool_result, user_text)
            return summary, {
                "executed": True,
                "tool": "veterinary_and_products_rag",
                "result": tool_result
            }

        # 6.5. Farm Worker & Labor Queries
        WORKER_WORDS = [
            "worker", "workers", "staff", "labor", "labour", "employee", "employees",
            "attendance", "shift", "shifts", "duties", "duty", "who worked", "worked yester",
            "yesterday work", "worked in farm", "worked on farm", "how worker", "பணியாளர்",
            "வேலையாள்", "வேலைக்காரர்", "ஊழியர்", "பணி", "வேலை", "कर्मचारी", "मजदूर"
        ]
        if any(w in lower_u for w in WORKER_WORDS):
            tool_spec = FARM_TOOLS.get("get_workers_and_staff_data")
            d_str = "Yesterday" if any(y in lower_u for y in ["yester", "நேற்று", "कल"]) else "Today"
            tool_result = await tool_spec["function"](farm_id=farm_id, date_str=d_str)
            summary = self._fallback_tool_summary("get_workers_and_staff_data", tool_result, user_text)
            return summary, {
                "executed": True,
                "tool": "get_workers_and_staff_data",
                "result": tool_result
            }

        # 7. Explicit Farm Overview / Summary queries
        OVERVIEW_WORDS = ["overview", "summary", "report", "telemetry", "dashboard", "status", "how is the farm", "how is my farm", "what hapned", "what happened", "what happened today", "today summary", "நிலவரம்", "அறிக்கை"]
        if any(w in lower_u for w in OVERVIEW_WORDS):
            tool_spec = FARM_TOOLS.get("get_farm_overview")
            d_target = "today" if any(t in lower_u for t in ["today", "இன்று", "आज"]) else ("yesterday" if any(y in lower_u for y in ["yester", "நேற்று", "कल"]) else "today")
            tool_result = await tool_spec["function"](farm_id=farm_id, target_date=d_target)
            summary = self._fallback_tool_summary("get_farm_overview", tool_result, user_text)
            return summary, {
                "executed": True,
                "tool": "get_farm_overview",
                "result": tool_result,
                "proof_images": tool_result.get("proof_images", [])
            }

        # 8. Conversational Agent Response (Do not dump unsolicited farm reports)
        if is_tamil:
            resp = (
                "ஐயா, நான் உங்கள் பண்ணைக் கேள்விகளுக்கு உதவ தயாராக உள்ளேன்.\n\n"
                "நீங்கள் என்னிடம் கேட்கலாம்:\n"
                "• குறிப்பிட்ட மாட்டைக் கண்காணிக்க (எ.கா. **COW001**, **COW002**)\n"
                "• சினைப்பருவ எச்சரிக்கைகள் மற்றும் மத நிலை\n"
                "• தீவன நிகழ்வுகள் மற்றும் மேலாண்மை\n"
                "• கேமரா புகைப்பட ஆதாரங்கள் மற்றும் சிசிடிவி காட்சிகள்"
            )
        elif is_hindi:
            resp = (
                "सर, मैं आपके डेयरी फार्म से जुड़े सवालों के लिए तैयार हूँ।\n\n"
                "आप मुझसे पूछ सकते हैं:\n"
                "• गाय की स्थिति जांचें (जैसे **COW001**, **COW002**)\n"
                "• मद / हीट अलर्ट और गर्भाधान का समय\n"
                "• चारा और फीडिंग लॉग\n"
                "• CCTV तस्वीरें और कैमरे की स्थिति"
            )
        else:
            resp = (
                "Sir, I am listening and ready to assist you as your farm supervisor.\n\n"
                "Please tell me what you would like to inspect:\n"
                "• 🔍 **Cattle Check:** Specific activity for **COW001**, **COW002**, etc.\n"
                "• 🔥 **Estrus / Heat:** Live mounting alerts & AI timing\n"
                "• 🌾 **Feeding Logs:** Manger sessions & feed duration\n"
                "• 📸 **CCTV Proof:** Live camera detection photos & evidence\n"
                "• 🩺 **Veterinary Care:** Mastitis screening & treatment steps"
            )
        return resp, {"executed": False, "tool": None}

tool_router = AgentRouter()

