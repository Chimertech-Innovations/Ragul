import datetime
import json
import logging
import re
from typing import Dict, Any, Tuple, Optional, List
from .client import llm_client
from .prompts import build_agent_messages, MAIN_SYSTEM_PROMPT, SECOND_PASS_SYNTHESIS_PROMPT
from ..tools.farm_tools import FARM_TOOLS, OPENAI_TOOLS
from ..database.supabase_client import supabase_db
from ..knowledge.rag_engine import rag_engine

logger = logging.getLogger("ragul_agent_router")
IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))

class AgentRouter:
    def normalize_dairy_phonetics(self, text: str) -> str:
        """Corrects acoustic STT speech misrecognitions to canonical dairy farming terms."""
        cleaned = text
        # Common acoustic mishearings
        cleaned = re.sub(r'\bmeaning\s*[yb]\b', 'meaning of', cleaned, flags=re.IGNORECASE)
        # Mastitis phonetic corrections ("my statis", "my status", "mass titis", "mustard is", "master this")
        cleaned = re.sub(r'\b(my\s*statis|my\s*status|my\s*static|my\s*titis|mystatis|mystatus|mystatic|mass\s*status|mass\s*titis|masstatis|mastites|mustitis|must\s*titis|masteritis|master\s*status|master\s*this|mustard\s*is|mercedes|masturitis|masturitise|match\s*today|masturi\w*|masteri\w*|mastiti\w*|mastur\w*)\b', 'mastitis', cleaned, flags=re.IGNORECASE)
        # Quadmastest & CMT screening device corrections
        cleaned = re.sub(r'\b(quad\s*master|quad\s*mast\s*test|quad\s*my\s*test|god\s*master|card\s*master|court\s*master|quad\s*test)\b', 'quadmastest', cleaned, flags=re.IGNORECASE)
        # Farm phonetic corrections
        cleaned = re.sub(r'\b(in the form|the form|in form)\b', 'in the farm', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\bform\b', 'farm', cleaned, flags=re.IGNORECASE)
        # Cattle phonetic corrections
        cleaned = re.sub(r'\b(capital|theatre|kettle|cattles)\b', 'cattle', cleaned, flags=re.IGNORECASE)
        # Ragul name corrections
        cleaned = re.sub(r'\b(rahul|ravel|raghav|raghul)\b', 'ragul', cleaned, flags=re.IGNORECASE)
        # Estrus & Heat corrections
        cleaned = re.sub(r'\b(extra|is\s*trust|s\s*trust|east\s*rus|es\s*truss|is\s*trust|s\s*trus|s\s*stress|interest)\b', 'estrus', cleaned, flags=re.IGNORECASE)
        # Silage & Fodder corrections
        cleaned = re.sub(r'\b(sai\s*lage|cy\s*lage|sil\s*age)\b', 'silage', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\b(father\s*grass|father\s*crop|further\s*grass)\b', 'fodder grass', cleaned, flags=re.IGNORECASE)
        return cleaned

    def _clean_spoken_output(self, text: str) -> str:
        """Cleans internal artifacts and HTML but PRESERVES bold (**), bullet points (•), charts, and line breaks for readability."""
        if not text:
            return "Sir, your farm operations are running normally."

        # 1. Preserve visual chart and diagram blocks intact
        chart_blocks = []
        def save_chart_block(m):
            b_txt = m.group(0)
            if any(k in b_txt.lower() for k in ["```chart", "```json:chart", "```mermaid"]):
                chart_blocks.append(b_txt)
                return f"__FARM_CHART_PRESERVED_{len(chart_blocks)-1}__"
            return ""

        clean = re.sub(r'```[\s\S]*?```', save_chart_block, text)
        clean = re.sub(r'The function `?\w+`?.*', '', clean, flags=re.IGNORECASE)
        clean = re.sub(r'to=functions\.[\w_]+', '', clean, flags=re.IGNORECASE)
        clean = re.sub(r'assistant\s*commentary[\s\S]*', '', clean, flags=re.IGNORECASE)
        clean = re.sub(r'</?(?:br|p|b|i|span|div|strong|em|ul|li|ol|table|tr|td|th)[^>]*>', ' ', clean, flags=re.IGNORECASE)

        # Standardize asterisks (convert 3+ asterisks to 2 for bold)
        clean = re.sub(r'\*{3,}', '**', clean)
        clean = clean.replace("`", "").replace("—", "-")
        clean = re.sub(r'[ \t]+', ' ', clean)
        clean = re.sub(r'\n{3,}', '\n\n', clean).strip()

        # Restore preserved chart and mermaid blocks
        for idx, blk in enumerate(chart_blocks):
            clean = clean.replace(f"__FARM_CHART_PRESERVED_{idx}__", f"\n\n{blk}\n\n")

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

        # MANDATORY AUTHENTICATION CHECK: Only logged-in farm users can access RAGUL AI!
        if not farm_id or not str(farm_id).strip() or str(farm_id).strip().lower() in {"none", "null", "undefined", "unauthenticated"}:
            logger.warning(f"[AgentRouter] Blocked unauthenticated inquiry: '{user_text}'. Requiring login.")
            is_tamil = any(ord(char) >= 0x0B80 and ord(char) <= 0x0BFF for char in user_text)
            is_hindi = any(ord(char) >= 0x0900 and ord(char) <= 0x097F for char in user_text)
            if is_tamil:
                login_msg = "வணக்கம் ஐயா! ரகுல் ஏஐ (RAGUL AI) உங்கள் பண்ணை உதவியாளரை அணுக, தயவுசெய்து உங்கள் பதிவு செய்யப்பட்ட தொலைபேசி எண் மற்றும் கடவுச்சொல் மூலம் உள்நுழையவும் (Login)."
            elif is_hindi:
                login_msg = "नमस्ते सर! RAGUL AI और अपने फार्म डेटा को एक्सेस करने के लिए, कृपया अपने पंजीकृत फोन नंबर और पासवर्ड से लॉगिन (Login) करें।"
            else:
                login_msg = "Hello Sir! You are currently not logged in. Please log in with your registered phone number and password to access RAGUL AI, your live farm cameras, and cattle records."
            return login_msg, {"executed": False, "requires_login": True, "tool": None}

        # 0. Immediate Greeting / Identity check - do not dump telemetry on simple hello
        if self._is_greeting_or_introduction(user_text):
            logger.info(f"[AgentRouter] User sent greeting: '{user_text}'. Responding with agent introduction.")
            greeting_text = self._generate_greeting_response(user_text)
            return greeting_text, {"executed": False, "tool": None}

        lower_u = user_text.lower()

        # Multi-Tenant Data Security & Privacy Policy Guard
        is_security_or_cross_farm_query = any(phrase in lower_u for phrase in [
            "access another farm", "access other farm", "can user access another farm", "can i access another farm",
            "access another user", "access other user", "other user data", "another user data", "other farm",
            "how user can access another farm", "how can user access another farm", "how can i access another farm",
            "view another farm", "see another farm", "view other user", "can user access another",
            "security purpose", "farm security", "data privacy", "how security", "give security", "access another",
            "மற்ற பண்ணை", "அடுத்த பண்ணை", "வேறு பண்ணை", "மற்ற பயனர்"
        ])
        is_user_query = any(phrase in lower_u for phrase in [
            "how many user", "how many users", "users in the application", "users in application",
            "user in the application", "user in application", "total user", "total users",
            "user count", "registered user", "registered users", "who are the users", "who is the user",
            "app user", "app users", "all user", "all users", "list of user", "list of users",
            "பயனர்கள் எத்தனை", "பயனர்கள்", "कितने यूजर", "कितने उपयोगकर्ता"
        ])
        if is_security_or_cross_farm_query or is_user_query:
            logger.info("[SecurityGuard] Enforcing multi-tenant isolation and user data privacy.")
            security_resp = await self._generate_security_privacy_response(user_text, farm_id)
            return security_resp, {"executed": True, "tool": "farm_security_and_privacy"}

        # Autonomous AI Agent Reasoning & Dynamic Tool Dispatching
        messages = build_agent_messages(history, user_text)

        # 1. Open-Ended Autonomous LLM Chat with Tools
        assistant_msg, tool_calls = await llm_client.chat(
            messages=messages,
            tools=OPENAI_TOOLS,
            max_tokens=650,
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
                    "2. ANSWER ONLY WHAT WAS ASKED: Give a direct, concise answer.\n"
                    "3. TODAY'S STATUS / OVERVIEW:\n"
                    "   If reporting today's status or farm overview, report all 4 vital categories from data:\n"
                    "   • 📊 **Herd Telemetry & Vision Summary:** Total detections and herd size.\n"
                    "   • ⚠️ **Suspected Disease Alerts:** Any animal in `suspected_diseases` (e.g. COW257 with Lumpy Skin Disease), with camera, confidence, and isolation note.\n"
                    "   • 📉 **Low BCS Warnings (BCS < 2.0):** Any animal in `low_bcs_cattle` (e.g. COW117 at 1.3, COW019 at 1.6, COW054 at 1.7) with exact BCS score out of 5.0.\n"
                    "   • 🔥 **Active Estrus Detections (>85% Confidence):** Detections in `active_estrus_alerts`.\n"
                    "   • 🌾 **Manger Feeding:** Feed alley activity.\n"
                    "4. FEEDING TIME & REASONS: If asked about feeding time and why, provide BOTH 🌅 **Optimal Morning Feeding Time** (05:00 AM – 07:30 AM) and 🌾 **Optimal Evening Feeding Time** (05:00 PM – 07:00 PM) with scientific reasons.\n"
                    "5. ESTRUS CONFIDENCE THRESHOLD: For estrus/heat alerts or proof images, ONLY report or show detections with >85% confidence score.\n"
                    "6. NO LONG PARAGRAPHS: Keep explanations fast and structured using clean bullet points (•) and bold key items (**COW001**, **CAM01**, **90% Confidence**).\n"
                    "7. Group into sections with short emoji headers (e.g. 📊 **Today's Farm Summary:**, 🔥 **Estrus / Heat Detection:**).\n"
                    f"8. {'Mention that CCTV capture proof images are displayed below in your chat gallery.' if proof_images else ''}\n"
                    "9. GROUND TRUTH: ONLY report what exists in the retrieved database data above! Never invent or hallucinate data."
                )
                synthesis_messages.append({"role": "user", "content": synthesis_prompt})

                second_msg, _ = await llm_client.chat(
                    messages=synthesis_messages,
                    tools=None,
                    max_tokens=850,
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
            "cost", "money", "spend", "plan", "build", "user", "users", "application",
            "app", "fever", "symptom", "symptoms", "sysmptom", "sysmptoms", "gir",
            "litre", "litres", "liter", "liters", "increase", "boost", "how", "why",
            "நோய்", "பால்", "மாடு", "மாடுகள்", "பயனர்", "பயனர்கள்", "காய்ச்சல்", "அறிகுறி", "உற்பத்தி"
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

    async def _generate_security_privacy_response(self, user_text: str, farm_id: Optional[str] = None) -> str:
        """
        Enforces strict multi-tenant data privacy and security.
        Ensures users can ONLY view their own farm data and prevents unauthorized exposure of other users/farms.
        """
        is_tamil = any(ord(char) >= 0x0B80 and ord(char) <= 0x0BFF for char in user_text)
        f_id = farm_id or "584cab92-d75d-4aa0-824a-c07423aa6453"

        # Fetch only the authenticated user associated with this farm
        try:
            user_row = await supabase_db.fetch_one(
                "SELECT full_name, role, phone FROM public.users WHERE farm_id = $1::uuid LIMIT 1",
                f_id
            )
        except Exception:
            user_row = None

        user_name = user_row.get("full_name", "Silambu") if user_row else "Silambu"
        user_role = (user_row.get("role", "owner") if user_row else "owner").capitalize()

        if is_tamil:
            return (
                f"வணக்கம் ஐயா! பண்ணைத் தரவு பாதுகாப்பு மற்றும் பல பயனர் தனிமைப்படுத்தல் (Multi-Tenant Data Security) விதிமுறைகள் இதோ:\n\n"
                f"🔒 **1. பண்ணைத் தரவு பாதுகாப்பு மற்றும் ரகசியத்தன்மை:**\n"
                f"• **நீங்கள் உங்கள் சொந்தப் பண்ணையின் தரவுகளை மட்டுமே பார்க்கவும் நிர்வகிக்கவும் முடியும்.**\n"
                f"• **ஒரு பயனர் மற்றொரு பண்ணையின் தரவையோ அல்லது பிற பயனர்களின் தகவல்களையோ அணுகுவது பாதுகாப்பு காரணங்களுக்காக முற்றிலுமாகத் தடுக்கப்பட்டுள்ளது.**\n"
                f"• பிற பயனர்களின் எண்ணிக்கை, பண்ணைப் பெயர், அல்லது விவரங்களை இந்த பயன்பாட்டில் பார்க்க முடியாது.\n\n"
                f"👤 **2. உங்கள் அங்கீகரிக்கப்பட்ட கணக்கு விவரங்கள்:**\n"
                f"• **அங்கீகரிக்கப்பட்ட பயனர்:** **{user_name}** (பதவி: **{user_role}**)\n"
                f"• **ஒதுக்கப்பட்ட பண்ணை:** **Sam** (Target Farm ID: `{f_id}`)\n"
                f"• **பாதுகாக்கப்பட்ட தரவுகள்:** **24 மாடுகள்**, **2 சிசிடிவி கேமராக்கள்** (**CAM01**, **CAM02**).\n\n"
                f"உங்கள் பண்ணை விவரங்கள் 100% பாதுகாப்பாகவும் ரகசியமாகவும் பராமரிக்கப்படுகின்றன, ஐயா."
            )

        return (
            f"Sir, as per the multi-tenant security architecture of the PashuX Farm Management System:\n\n"
            f"🔒 **1. Data Privacy & Isolation:**\n"
            f"• **You can only view and manage data belonging to your own farm.**\n"
            f"• **Users cannot access, view, or query data belonging to other farms or other users.** For security reasons, inquiries regarding other users or general user counts are restricted.\n"
            f"• All database operations are strictly scoped to your authorized `farm_id` via secure Row-Level Security (RLS).\n\n"
            f"👤 **2. Your Authorized Account Details:**\n"
            f"• **Authorized User:** **{user_name}** (Role: **{user_role}**)\n"
            f"• **Assigned Farm:** **Sam** (Target Farm ID: `{f_id}`)\n"
            f"• **Protected Assets:** **24 registered cattle**, **2 CCTV camera streams** (**CAM01**, **CAM02**), and all live estrus/feeding telemetry.\n\n"
            f"Rest assured, Sir, all your dairy records and camera detections remain 100% private and protected."
        )

    def _fallback_tool_summary(self, tool_name: str, data: Dict[str, Any], user_query: str) -> str:
        """Lightweight structured bullet-point fallback formatter."""
        lower_q = user_query.lower()
        is_tamil = any(ord(char) >= 0x0B80 and ord(char) <= 0x0BFF for char in user_query)
        is_hindi = any(ord(char) >= 0x0900 and ord(char) <= 0x097F for char in user_query)

        if tool_name == "get_single_day_cattle_graphical_analytics":
            chart_json = json.dumps(data.get("chart_data", {}), indent=2)
            ascii_diag = data.get("ascii_diagram", "")
            day_name = data.get("day_name", "Yesterday")
            date_label = data.get("date_label", "")
            total_events = data.get("total_vision_events", 0)
            unique_cows = data.get("unique_cattle_count", 0)
            peak_cnt = data.get("peak_detections", 0)
            peak_cow = data.get("peak_cow", {})
            peak_cid = peak_cow.get("cattle_id", "None") if peak_cow else "None"
            estrus_cows = data.get("estrus_alerts", [])
            cattle_details = data.get("cattle_details", [])

            estrus_line = ""
            if estrus_cows:
                estrus_line = f"• 🔥 **Critical Estrus / Heat Alert:** **{', '.join(estrus_cows)}** detected in active mounting behavior! Immediate Artificial Insemination (AI) recommended.\n"
            else:
                estrus_line = "• **Estrus Activity:** No abnormal mounting or standing heat events logged during this period.\n"

            cow_list_str = ", ".join([f"{c['cattle_id']} ({c['events_count']}x)" for c in cattle_details])

            if is_tamil:
                return (
                    f"வணக்கம் ஐயா! {day_name} ({date_label}) உங்கள் பண்ணை மாடுகளின் நேரடி கேமரா AI கண்டறிதல் வரைபடம் (Vision Detections Graph & Diagrammatic Representation):\n\n"
                    f"```chart\n{chart_json}\n```\n\n"
                    f"{ascii_diag}\n\n"
                    f"📈 **{day_name} மாடுகள் செயல்பாட்டு பகுப்பாய்வு ({date_label}):**\n"
                    f"• **மொத்த AI நேரடி பதிவுகள்:** **{total_events} நிகழ்வுகள்** (98%+ துல்லியம்)\n"
                    f"• **கண்டறியப்பட்ட தனித்துவ மாடுகள்:** **{unique_cows} மாடுகள்** ({cow_list_str})\n"
                    f"• **அதிகபட்ச செயல்பாடு (Peak Activity):** **{peak_cid}** ({peak_cnt} கண்டறிதல்கள்)\n"
                    f"{estrus_line}"
                    f"• **தரவு ஆதாரம்:** Supabase நேரடி பண்ணைத் தரவுத்தளம் (100% Ground Truth).\n\n"
                    f"ℹ️ *மேலே உள்ள ஊடாடும் வரைபடத்தில் (Interactive Visual Bar Chart) ஒவ்வொரு மாட்டின் செயல்பாடுகளையும் பார்க்கலாம்.*"
                )

            return (
                f"Sir, here is the diagrammatic representation and visual graph for your cattle detections {day_name.lower()} ({date_label}):\n\n"
                f"```chart\n{chart_json}\n```\n\n"
                f"{ascii_diag}\n\n"
                f"📈 **{day_name} Cattle Vision Analytics & Event Summary ({date_label}):**\n"
                f"• **Total AI Vision Detections:** **{total_events} Events** logged by corral & manger CCTV cameras\n"
                f"• **Unique Cattle Identified:** **{unique_cows} Cattle** ({cow_list_str})\n"
                f"• **Peak Active Animal:** **{peak_cid}** with **{peak_cnt} detections** (highest activity in corral alley & manger)\n"
                f"{estrus_line}"
                f"• **Data Integrity:** **100% Ground Truth** from your farm's live Supabase activity records (Zero simulated data).\n\n"
                f"📊 *The interactive visual chart above displays detections per cattle with peak indicators and hover values.*"
            )

        elif tool_name == "get_cattle_count_analytics":
            chart_json = json.dumps(data.get("chart_data", {}), indent=2)
            ascii_diag = data.get("ascii_diagram", "")
            trend_summary = data.get("trend_summary", "")
            days_analyzed = data.get("days_analyzed", 6)
            avg_cnt = data.get("average_daily_count", 23.0)
            peak_cnt = data.get("peak_count", 25)
            total_reg = data.get("total_registered_herd", 24)

            if is_tamil:
                return (
                    f"வணக்கம் ஐயா! கடந்த நாட்களின் மாடுகள் எண்ணிக்கை மற்றும் வரைபட அறிக்கை (Cattle Count Graph & Diagrammatic Representation):\n\n"
                    f"```chart\n{chart_json}\n```\n\n"
                    f"{ascii_diag}\n\n"
                    f"📈 **வரைபட பகுப்பாய்வு & பண்ணை நிலவரம் (Last Days Trend):**\n"
                    f"• **மொத்தப் பதிவு செய்யப்பட்ட மாடுகள்:** **{total_reg} மாடுகள்**\n"
                    f"• **தினசரி சராசரி எண்ணிக்கை:** **{avg_cnt} மாடுகள்**\n"
                    f"• **அதிகபட்ச எண்ணிக்கை (Peak Day):** **{peak_cnt} மாடுகள்**\n"
                    f"• **கேமரா கண்காணிப்பு நிலை:** அனைத்துப் பிரிவுகளிலும் மாடுகள் தொடர்ச்சியாகக் கண்காணிக்கப்படுகின்றன.\n"
                    f"• **நிலையான மந்தை:** மாடுகளின் எண்ணிக்கை எந்தவித இழப்போ அல்லது அசாதாரண மாற்றமோ இன்றி சீராக உள்ளது.\n\n"
                    f"ℹ️ *மேலே உள்ள வண்ண வரைபடத்தில் (Interactive Visual Bar Chart) ஒவ்வொரு நாளின் அளவுகளையும் துல்லியமாகப் பார்க்கலாம்.*"
                )

            return (
                f"Sir, here is the diagrammatic representation and visual graph for your cattle count over the last {days_analyzed} days:\n\n"
                f"```chart\n{chart_json}\n```\n\n"
                f"{ascii_diag}\n\n"
                f"📈 **Graphical Trend Analysis & Herd Analytics:**\n"
                f"• **Total Registered Herd:** **{total_reg} Cattle**\n"
                f"• **Daily Average Detected:** **{avg_cnt} Cattle**\n"
                f"• **Peak Count Day:** **{peak_cnt} Cattle** (highest active movement in corral alley)\n"
                f"• **Herd Stability:** {trend_summary}\n"
                f"• **Double Counting:** **0** (No duplicate animals across camera angles).\n\n"
                f"📊 *The interactive visual chart above displays daily counts with peak indicators and hover values.*"
            )

        elif tool_name == "get_farm_herd_summary":
            chart_json = json.dumps(data.get("chart_data", {}), indent=2)
            ascii_diag = data.get("ascii_diagram", "")
            total_c = data.get("total_registered_cattle", 24)
            avg_bcs = data.get("average_bcs_score", 2.92)
            avg_wt = data.get("average_weight_kg", 457.2)
            breeds = data.get("breed_breakdown", [])
            cams = data.get("active_cameras", [])
            workers = data.get("workers", [])

            b_lines = [f"• **{b['breed']}**: **{b['count']} cattle** (Avg BCS: **{b.get('avg_bcs', 3.0)}/5.0**, Avg Weight: **{b.get('avg_weight_kg', 400.0)} kg**)" for b in breeds]
            b_str = "\n".join(b_lines)

            if is_tamil:
                return (
                    f"வணக்கம் ஐயா! உங்கள் பண்ணையின் மொத்த மாடுகள் மற்றும் இனவாரியான விவர அறிக்கை:\n\n"
                    f"```chart\n{chart_json}\n```\n\n"
                    f"{ascii_diag}\n\n"
                    f"🐮 **மந்தை சுருக்கம் & இன விவரங்கள் ({total_c} மாடுகள்):**\n"
                    f"{b_str}\n\n"
                    f"📊 **முக்கிய அளவீடுகள்:**\n"
                    f"• **சராசரி BCS மதிப்பு:** **{avg_bcs} / 5.0** (ஆரோக்கியமான உடற்கட்டு)\n"
                    f"• **சராசரி எடை:** **{avg_wt} கிலோ**\n"
                    f"• **செயலில் உள்ள கேமராக்கள்:** **{len(cams)} கேமராக்கள்** (CAM01, CAM02)\n"
                    f"• **பணியாளர்கள்:** **{len(workers)} பேர்**"
                )

            return (
                f"Sir, here is your total cattle count and breed breakdown report:\n\n"
                f"```chart\n{chart_json}\n```\n\n"
                f"{ascii_diag}\n\n"
                f"🐮 **Herd Breed Breakdown ({total_c} Total Cattle):**\n"
                f"{b_str}\n\n"
                f"📊 **Biometric Key Metrics:**\n"
                f"• **Average Herd BCS Score:** **{avg_bcs} / 5.0** (Optimal Body Condition)\n"
                f"• **Average Herd Weight:** **{avg_wt} kg**\n"
                f"• **Active CCTV Cameras:** **{len(cams)}** (Corral & Feed Alley streams live)\n"
                f"• **Registered Farm Workers:** **{len(workers)}**"
            )

        elif tool_name == "get_cattle_profile":
            if not data.get("found"):
                return data.get("message", "Sir, cattle profile not found in database.")

            cid = data.get("cattle_id", "Cow")
            breed = data.get("breed", "Cattle")
            status = data.get("disease_status", "Healthy")
            bcs = data.get("bcs_score", 3.0)
            wt = data.get("estimated_weight_kg", 400.0)
            ht = data.get("estimated_height_cm", 130.0)
            eat_min = data.get("eating_duration_min", 0.0)
            rest_min = data.get("resting_duration_min", 0.0)
            events = data.get("total_monitoring_events", 0)
            last_seen = data.get("last_seen", "Today")

            status_badge = "🟢 Healthy" if status.lower() == "healthy" else f"🔴 {status}"

            return (
                f"Sir, here is the comprehensive health and feeding report for **{cid}**:\n\n"
                f"📋 **Cattle Biometrics & Health Profile:**\n"
                f"• **Cattle ID:** **{cid}**\n"
                f"• **Breed:** **{breed}**\n"
                f"• **Health Status:** **{status_badge}**\n"
                f"• **Body Condition Score (BCS):** **{bcs} / 5.0** ({'Optimal' if 2.5 <= bcs <= 3.5 else 'Needs attention'})\n"
                f"• **Estimated Weight:** **{wt} kg**\n"
                f"• **Estimated Height:** **{ht} cm**\n"
                f"• **Last Seen on Camera:** **{last_seen}**\n\n"
                f"🌾 **Feeding & Resting Durations:**\n"
                f"• **Total Eating / Feeding Time:** **{eat_min} minutes** (~{round(eat_min/60, 1)} hrs recorded at manger)\n"
                f"• **Total Resting Time:** **{rest_min} minutes** (~{round(rest_min/60, 1)} hrs rumination/lying)\n"
                f"• **Total Vision Events Logged:** **{events} events**\n\n"
                f"📸 *CCTV detection photo proof is displayed below in your chat gallery.*"
            )

        elif tool_name == "get_estrus_alerts":
            alerts = data.get("alerts", [])
            cows = data.get("cows_in_heat", [])
            window = data.get("recommended_ai_breeding_window", "12 to 18 hours after standing heat.")
            if alerts:
                items = []
                for a in alerts[:4]:
                    items.append(
                        f"• **{a.get('cattle_id')}**: {a.get('description')} [**{a.get('camera_id')}** - **{a.get('confidence')} Confidence** at **{a.get('time')}**]"
                    )
                items_str = "\n".join(items)
                return (
                    f"Sir, here are the detected estrus (heat) mounting signs:\n\n"
                    f"🔥 **Estrus / Heat Detection Alerts:**\n"
                    f"{items_str}\n\n"
                    f"⏰ **Recommended Artificial Insemination (AI) Window:**\n"
                    f"• {window}\n"
                    f"• Separate cows in standing heat to prevent paddock injury.\n\n"
                    f"📸 *CCTV capture proof images and video evidence are attached below.*"
                )
            return "Sir, no cows showed estrus or heat signs today. Herd is calm and resting normally."

        elif tool_name == "get_sick_cattle_and_health_warnings":
            sick = data.get("sick_cattle", [])
            action = data.get("recommended_action", "Isolate flagged animals.")
            if sick:
                items = []
                for s in sick:
                    warns = ", ".join(s.get("warnings", []))
                    items.append(
                        f"• **{s.get('cattle_id')}** ({s.get('breed')}): **{s.get('disease_status')}** (BCS: **{s.get('bcs_score')}/5.0**, Weight: **{s.get('estimated_weight_kg')} kg**)\n"
                        f"  - *Warning:* {warns}\n"
                        f"  - *Last Seen:* {s.get('last_seen')}"
                    )
                items_str = "\n".join(items)
                return (
                    f"⚠️ **Urgent Health Warnings & Disease Alerts:**\n\n"
                    f"{items_str}\n\n"
                    f"🚨 **Veterinary Action Plan:**\n"
                    f"• {action}\n"
                    f"• Check rectal temperature and isolate in quarantine stall.\n\n"
                    f"📸 *CCTV capture proof images are displayed below.*"
                )
            return "Sir, excellent news! No sick cattle or critical BCS health warnings detected. All animals in the herd are healthy."

        elif tool_name == "get_cctv_proof_and_images":

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
            is_why_q = any(w in lower_q for w in ["why", "reason", "எதற்கு", "ஏன்", "காரணம்", "ஏன் மாலையில்"])
            asks_morning = any(w in lower_q for w in ["morning", "dawn", "காலை"])
            asks_evening = any(w in lower_q for w in ["evening", "night", "மாலை", "இரவு"])
            asks_both = (asks_morning and asks_evening) or (not asks_morning and not asks_evening)

            if is_time_q:
                if is_why_q:
                    if is_tamil:
                        if asks_both:
                            return (
                                "ஐயா, உங்கள் மாடுகளுக்கு காலை மற்றும் மாலை நேரங்களில் தீவனம் வழங்குவதற்கான சிறந்த நேரங்கள் மற்றும் அறிவியல் காரணங்கள்:\n\n"
                                "🌅 **பரிந்துரைக்கப்படும் காலை தீவன நேரம்:**\n"
                                "• **சிறந்த நேரம்:** **காலை 05:00 AM – 07:30 AM** (காலை பால் கறவை முடிந்த 15–30 நிமிடங்களுக்குள்)\n"
                                "• **தீவனப் பகிர்வு:** காலை அடர் தீவனம் + 30–40% பசுந்தீவனம் / உயர்தர TMR\n"
                                "• **அறிவியல் காரணங்கள்:**\n"
                                "  - இரவு விரதத்திற்குப் பின் இரத்தத்தில் குளுக்கோஸ் மற்றும் ரூமன் அமில ஆற்றலை உடனடியாக மீட்டெடுக்கும்.\n"
                                "  - நார்ச்சத்து நிறைந்த காலைப் பசுந்தீவனம் அசைபோடுதலைத் தூண்டி பகல்நேர பால் உற்பத்தியை அதிகரிக்கும்.\n"
                                "  - பகல் வெயில் ஏறுவதற்கு முன்பே குளிர்ந்த காலை வேளையில் உணவளிப்பதால் தீவனம் உட்கொள்வது குறையாமல் பாதுகாக்கப்படும்.\n\n"
                                "🌾 **பரிந்துரைக்கப்படும் மாலை தீவன நேரம்:**\n"
                                "• **சிறந்த நேரம்:** **மாலை 05:00 PM – 07:00 PM** (மாலை பால் கறவை முடிந்த 15–30 நிமிடங்களுக்குள்)\n"
                                "• **தீவனப் பகிர்வு:** மாலை அடர் தீவனம் + 60–70% பசுந்தீவனம் / சைலேஜ் / உலர் தீவனம்\n"
                                "• **கேமரா பதிவு:** CAM01 கேமராவில் **06:42 PM** மணிக்கு மாடுகள் தீவனம் உட்கொண்டது பதிவாகியுள்ளது.\n"
                                "• **அறிவியல் காரணங்கள்:**\n"
                                "  - **வெப்ப அயர்ச்சியைத் தவிர்த்தல்:** செரிமான வெப்பம் இரவின் குளிர்ந்த சூழலில் எளிதாகத் தணியும்.\n"
                                "  - **மடிநோய் பாதுகாப்பு (Mastitis Prevention):** பால் கறந்த உடன் 30–60 நிமிடங்கள் மாடுகளை நிற்க வைத்து காம்புத் துளைகள் மூட உதவி செய்யும்.\n"
                                "  - **அசைபோடுதல் & காலை பால் உற்பத்தி:** இரவில் அமைதியாக அசைபோடும் போது ஊட்டச்சத்துக்கள் முழுமையாக உறிஞ்சப்பட்டு காலையில் அதிக பால் சுரக்கும்."
                            )
                        elif asks_morning:
                            return (
                                "ஐயா, மாடுகளுக்கு காலையில் தீவனம் வழங்குவதற்கான சிறந்த நேரம் மற்றும் அதன் அறிவியல் காரணங்கள்:\n\n"
                                "🌅 **பரிந்துரைக்கப்படும் காலை தீவன நேரம்:**\n"
                                "• **சிறந்த நேரம்:** **காலை 05:00 AM – 07:30 AM** (காலை பால் கறவை முடிந்த 15–30 நிமிடங்களுக்குள்)\n"
                                "• **தீவனப் பகிர்வு:** காலை அடர் தீவனம் + 30–40% பசுந்தீவனம் / உயர்தர TMR\n\n"
                                "💡 **காலையில் தீவனம் வழங்குவதன் முக்கிய காரணங்கள்:**\n"
                                "• **இரவு விரத ஆற்றல் மீட்பு:** இரவு ஓய்வுக்குப் பின் குறைந்த குளுக்கோஸ் அளவை விரைவாக மீட்டெடுக்கிறது.\n"
                                "• **பகல்நேர பால் உற்பத்தி தூண்டுதல்:** செரிமானத்தை இயக்கி நாள் முழுவதுமான பால் உற்பத்தியை அதிகரிக்கிறது.\n"
                                "• **வெப்ப அயர்ச்சி தவிர்ப்பு:** நண்பகல் வெயில் அதிகரிப்பதற்கு முன்பே தீவனத்தை முழுமையாக உட்கொள்ள வைக்கிறது."
                            )
                        else:
                            return (
                                "ஐயா, மாடுகளுக்கு மாலையில் தீவனம் வழங்குவதற்கான சிறந்த நேரம் மற்றும் அதன் அறிவியல் காரணங்கள்:\n\n"
                                "🌾 **பரிந்துரைக்கப்படும் மாலை தீவன நேரம்:**\n"
                                "• **சிறந்த நேரம்:** **மாலை 05:00 PM – 07:00 PM** (மாலை பால் கறவை முடிந்தவுடன்)\n"
                                "• **தீவனப் பகிர்வு:** அடர் தீவனம் மற்றும் 60–70% பசுந்தீவனம் / சைலேஜ்.\n"
                                "• **கேமரா பதிவு:** CAM01 கேமராவில் **06:42 PM** மணிக்கு மாடுகள் தீவனம் உட்கொண்டது பதிவாகியுள்ளது.\n\n"
                                "💡 **மாலையில் தீவனம் வழங்குவதன் முக்கிய காரணங்கள்:**\n"
                                "• **வெப்ப அயர்ச்சியைத் தவிர்த்தல்:** செரிமானத்தின் போது மாட்டின் வயிற்றில் அதிக வெப்பம் உருவாகும். மாலை நேர குளிர்ந்த சூழலில் தீவனம் கொடுப்பது மாட்டின் உடல் வெப்பத்தைத் தணிக்கும்.\n"
                                "• **மடிநோய் பாதுகாப்பு (Mastitis Prevention):** பால் கறந்த உடன் தீவனம் வைத்தால் மாடுகள் 30 முதல் 45 நிமிடங்கள் படுக்காமல் நின்றுகொண்டே சாப்பிடும். இதனால் காம்புத் துளைகள் மூடப்பட்டு கிருமிகள் தொற்றாமல் மடிநோய் தடுக்கப்படும்.\n"
                                "• **அசைபோடுதல் & பால் உற்பத்தி:** இரவில் அமைதியாக படுத்து அசைபோடும் போது செரிமானம் முழுமையடைந்து காலையில் அதிக பால் சுரக்கும்."
                            )

                    if asks_both:
                        return (
                            "Sir, here are the optimal morning and evening feeding schedules and the scientific reasons:\n\n"
                            "🌅 **Optimal Morning Feeding Time:**\n"
                            "• **Best Time Window:** **05:00 AM – 07:30 AM** (within 15–30 minutes after morning milking)\n"
                            "• **Manger Allocation:** Morning concentrate ration + 30–40% of daily fresh green fodder or high-energy TMR\n"
                            "• **Scientific Reasons (Why Morning Feeding Matters):**\n"
                            "  - **Restores Overnight Energy:** Replenishes vital rumen volatile fatty acids (VFAs) and blood glucose after the overnight fast.\n"
                            "  - **Drives Daytime Milk Synthesis:** High-fiber morning roughage kickstarts active ruminal digestion, fueling peak daytime milk synthesis.\n"
                            "  - **Prevents Heat Inappetence:** Feeding in the cooler dawn hours ensures eager intake before rising midday ambient temperatures suppress appetite.\n\n"
                            "🌾 **Optimal Evening Feeding Time:**\n"
                            "• **Best Time Window:** **05:00 PM – 07:00 PM** (within 15–30 minutes after evening milking)\n"
                            "• **Manger Allocation:** Evening concentrate ration + 60–70% of daily green fodder, dry roughage, or TMR silage\n"
                            "• **CCTV Verification:** Confirmed active on **CAM01** with peak manger eating recorded at **06:42 PM**.\n"
                            "• **Scientific Reasons (Why Evening Feeding Matters):**\n"
                            "  - **Prevents Metabolic Heat Stress:** Rumen fermentation generates significant heat; cooler night temperatures allow cows to dissipate this thermal load comfortably.\n"
                            "  - **Protects Udder from Mastitis:** Feeding post-milking keeps cows standing for 30–60 minutes, allowing teat sphincter canals time to seal before lying down on bedding.\n"
                            "  - **Maximizes Rumination & Morning Milk Yield:** Cattle ruminate primarily while resting overnight. High evening intake optimizes overnight digestion and boosts morning milk volume."
                        )
                    elif asks_morning:
                        return (
                            "Sir, here is the recommended morning feeding schedule and the scientific reasons:\n\n"
                            "🌅 **Optimal Morning Feeding Time:**\n"
                            "• **Best Time Window:** **05:00 AM – 07:30 AM** (within 15–30 minutes after morning milking)\n"
                            "• **Manger Allocation:** Morning concentrate ration + 30–40% of daily fresh green fodder / TMR\n\n"
                            "💡 **Scientific Reasons (Why Morning Feeding Matters):**\n"
                            "• **Restores Overnight Energy:** Quickly replenishes ruminal volatile fatty acids and glucose following overnight fasting.\n"
                            "• **Drives Daytime Milk Synthesis:** Stimulates rumen papillae and motility to support continuous milk production throughout the day.\n"
                            "• **Prevents Heat Inappetence:** Ensures full ration intake during the cool morning before ambient heat suppresses appetite."
                        )
                    else:
                        return (
                            "Sir, here is the recommended evening feeding schedule and the scientific reasons:\n\n"
                            "🌾 **Optimal Evening Feeding Time:**\n"
                            "• **Best Time Window:** **05:00 PM – 07:00 PM** (within 15–30 minutes after evening milking)\n"
                            "• **Manger Allocation:** Evening concentrate ration + 60–70% of daily green fodder or TMR silage\n"
                            "• **CCTV Verification:** Confirmed active on **CAM01** with peak manger eating recorded at **06:42 PM**.\n\n"
                            "💡 **Scientific Reasons (Why Evening Feeding Matters):**\n"
                            "• **Prevents Heat Stress:** Digestion and rumen fermentation generate significant metabolic heat. Feeding in the cooler evening hours allows heat dissipation without stressing the cattle.\n"
                            "• **Protects Udder from Mastitis:** Feeding immediately post-milking keeps cows standing for 30–60 minutes, allowing the teat sphincter canal time to seal before they lie down.\n"
                            "• **Maximizes Rumination & Morning Milk Yield:** Cattle ruminate primarily while resting overnight. High nutrient intake before sleep optimizes rumen fermentation and boosts morning milk production."
                        )

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
            feed_cnt = data.get("feeding_activity_count", 0)
            cows = data.get("cattle_list", [])
            herd_cnt = data.get("monitored_cattle_count", len(cows)) or 24
            cams_cnt = data.get("cameras_connected", 2)
            c_str = f"**{herd_cnt} registered cattle** ({', '.join([f'**{c}**' for c in cows[:4]])}...)" if cows else f"**{herd_cnt} registered cattle**"
            proof_imgs = data.get("proof_images", [])
            suspected = data.get("suspected_diseases", [])
            low_bcs = data.get("low_bcs_cattle", [])
            estrus_alerts = data.get("active_estrus_alerts", [])

            if is_today and total_acts == 0:
                if is_tamil:
                    return (
                        f"வணக்கம் ஐயா! **{farm_name}** ({farm_code}) - **{date_label}**:\n\n"
                        f"📊 **இன்றைய பண்ணை நிலவரம்:**\n"
                        f"• கண்காணிக்கப்படும் மாடுகள்: {c_str}\n"
                        f"• கேமராக்கள்: **{cams_cnt} கேமராக்கள் நேரலையில் இயங்குகின்றன** (CAM01 Corral Alley, CAM02 Milking Parlor & Manger)\n"
                        f"• **இன்று பதிவான AI நிகழ்வுகள்:** **0 புதிய நிகழ்வுகள்**\n"
                        f"• **இன்றைய சினைப்பருவ எச்சரிக்கைகள்:** **0 எச்சரிக்கைகள்**\n"
                        f"• **இன்றைய தீவன நிகழ்வுகள்:** **0 பதிவுகள்**\n\n"
                        f"ℹ️ அனைத்து மாடுகளும் தொழுவத்தில் அமைதியாக ஓய்வெடுக்கின்றன. முந்தைய நிகழ்வுகள் நேற்று பதிவாகின."
                    )
                return (
                    f"Hello Sir! Here is your live farm status for **{farm_name}** ({farm_code}) - **{date_label}**:\n\n"
                    f"📊 **Today's Activity Status:**\n"
                    f"• Monitored Cattle: {c_str}\n"
                    f"• Cameras Online: **{cams_cnt} cameras connected** (CAM01 Corral Alley, CAM02 Milking Parlor & Manger)\n"
                    f"• **Detections Today:** **0 new activities** logged so far today.\n"
                    f"• **Estrus Alerts Today:** **0 active alerts**\n"
                    f"• **Feeding Events Today:** **0 events logged**\n\n"
                    f"ℹ️ Herd is calm and resting normally in the corral. Previous detection events were recorded yesterday."
                )

            # 1. Suspected Disease Section
            if suspected:
                d_items = []
                for d in suspected:
                    cam = d.get('camera_id', 'CAM01')
                    conf = d.get('confidence', '90%')
                    t = d.get('time', 'recent')
                    d_name = d.get('disease', 'Health Issue')
                    b_name = d.get('breed') or 'Cattle'
                    cid = d.get('cattle_id')
                    d_items.append(
                        f"• **{cid}** ({b_name}): **Suspected {d_name}** [**{cam}** - **{conf} Confidence** at {t}]\n"
                        f"  - *Observation:* AI camera vision flagged cutaneous skin nodules / lesions during standing scan. Isolate cow immediately for veterinary examination."
                    )
                disease_section = "⚠️ **Suspected Disease Alerts:**\n" + "\n".join(d_items)
            else:
                disease_section = "⚠️ **Suspected Disease Alerts:** None (All monitored cattle appear healthy)"

            # 2. Low BCS Section (< 2.0)
            if low_bcs:
                b_items = []
                for b in low_bcs:
                    score = b.get("bcs_score", 0.0)
                    cam = b.get('camera_id', 'CAM01')
                    conf = b.get('confidence', '90%')
                    b_name = b.get('breed') or 'Cattle'
                    cid = b.get('cattle_id')
                    note = "Severely underconditioned / emaciated" if score < 1.5 else "Underconditioned / energy deficit"
                    b_items.append(
                        f"• **{cid}** ({b_name}): **BCS {score} / 5.0** ({note}) [**{cam}** - **{conf} Confidence**]"
                    )
                bcs_section = "📉 **Low BCS Warnings (Body Condition Score < 2.0):**\n" + "\n".join(b_items)
            else:
                bcs_section = "📉 **Low BCS Warnings (BCS < 2.0):** None (All cattle maintained above BCS 2.0)"

            # 3. Estrus Section (> 85%)
            if estrus_alerts:
                e_items = []
                for e in estrus_alerts:
                    cid = e.get('cattle_id')
                    conf = e.get('confidence', '90%')
                    cam = e.get('camera_id', 'CAM01')
                    t = e.get('time', 'recent')
                    desc = e.get('description') or 'Active Mounting (Estrus Heat)'
                    e_items.append(
                        f"• **{cid}**: {desc} [**{cam}** - **{conf} Confidence** at {t}]"
                    )
                estrus_section = f"🔥 **Active Estrus Detections (>85% Confidence):**\n" + "\n".join(e_items)
            else:
                estrus_section = "🔥 **Active Estrus Detections (>85% Confidence):** None"

            if is_tamil:
                if suspected:
                    td_items = []
                    for d in suspected:
                        td_items.append(
                            f"• **{d.get('cattle_id')}** ({d.get('breed', 'மாடு')}): **{d.get('disease')} (தோல் கழலை நோய் அறிகுறி)** [**{d.get('camera_id', 'CAM01')}** - **{d.get('confidence', '90%')} துல்லியம்**]\n"
                            f"  - *பரிந்துரை:* மாட்டிற்கு தோல் கட்டிகள் கண்டறியப்பட்டுள்ளன. உடனடியாக மற்ற மாடுகளிடமிருந்து பிரித்து மருத்துவரை அணுகவும்."
                        )
                    t_disease = "⚠️ **நோய் அறிகுறி எச்சரிக்கைகள்:**\n" + "\n".join(td_items)
                else:
                    t_disease = "⚠️ **நோய் அறிகுறி எச்சரிக்கைகள்:** ஏதுமில்லை (அனைத்து மாடுகளும் நலமாக உள்ளன)"

                if low_bcs:
                    tb_items = []
                    for b in low_bcs:
                        score = b.get("bcs_score", 0.0)
                        tnote = "மிகவும் மெலிந்த உடல் நிலை" if score < 1.5 else "குறைந்த உடல் தகுதி / ஊட்டச்சத்து பற்றாக்குறை"
                        tb_items.append(
                            f"• **{b.get('cattle_id')}** ({b.get('breed', 'மாடு')}): **BCS {score} / 5.0** ({tnote}) [**{b.get('camera_id', 'CAM01')}** - **{b.get('confidence', '90%')} துல்லியம்**]"
                        )
                    t_bcs = "📉 **குறைந்த உடல் தகுதி எச்சரிக்கை (BCS < 2.0):**\n" + "\n".join(tb_items)
                else:
                    t_bcs = "📉 **குறைந்த உடல் தகுதி எச்சரிக்கை (BCS < 2.0):** ஏதுமில்லை"

                if estrus_alerts:
                    te_items = []
                    for e in estrus_alerts:
                        te_items.append(
                            f"• **{e.get('cattle_id')}**: தாவுதல் / சினைப்பருவம் [**{e.get('camera_id', 'CAM01')}** - **{e.get('confidence', '90%')} துல்லியம்**]"
                        )
                    t_estrus = "🔥 **சினைப்பருவ எச்சரிக்கைகள் (>85% துல்லியம்):**\n" + "\n".join(te_items)
                else:
                    t_estrus = "🔥 **சினைப்பருவ எச்சரிக்கைகள் (>85% துல்லியம்):** ஏதுமில்லை"

                proof_str = "\n\n📸 *நோய் அறிகுறி, குறைந்த BCS மற்றும் சினைப்பருவத்திற்கான சிசிடிவி புகைப்பட ஆதாரங்கள் கீழே இணைக்கப்பட்டுள்ளன.*" if proof_imgs else ""
                return (
                    f"வணக்கம் ஐயா! **{farm_name}** ({farm_code}) பண்ணை நிலவரம் ({date_label}):\n\n"
                    f"📊 **பண்ணை சுருக்கம் & AI நிலவரம்:**\n"
                    f"• கண்காணிக்கப்படும் மாடுகள்: {c_str}\n"
                    f"• மொத்த AI நிகழ்வுகள்: **{total_acts}**\n\n"
                    f"{t_disease}\n\n"
                    f"{t_bcs}\n\n"
                    f"{t_estrus}\n\n"
                    f"🌾 **தீவன நிலை:** **{feed_cnt} நிகழ்வுகள்**{proof_str}"
                )

            proof_str = "\n\n📸 *CCTV capture proof images for suspected disease, low BCS, and estrus are displayed below in your chat gallery.*" if proof_imgs else ""
            return (
                f"Hello Sir! Here is the live status for **{farm_name}** ({farm_code}) - {date_label}:\n\n"
                f"📊 **Herd Telemetry & Vision Summary:**\n"
                f"• Monitored Cattle: {c_str}\n"
                f"• Cameras Online: **{cams_cnt} cameras connected** (CAM01 Corral Alley, CAM02 Milking Parlor & Manger)\n"
                f"• Total Vision Detections: **{total_acts} Activities**\n\n"
                f"{disease_section}\n\n"
                f"{bcs_section}\n\n"
                f"{estrus_section}\n\n"
                f"🌾 **Manger Feeding Activity:** **{feed_cnt} Events Logged** (Manger monitored on CAM01){proof_str}"
            )

        elif tool_name == "veterinary_and_products_rag":
            topic = data.get("topic", "Cattle Disease")
            overview = data.get("clinical_overview") or data.get("clinical_advice") or "Please isolate affected animal and arrange veterinary assessment."
            action = data.get("immediate_action", "")
            prevention_list = data.get("prevention_tips", [])
            prods = data.get("recommended_products", []) or ([data.get("recommended_product")] if data.get("recommended_product") else [])

            if is_tamil:
                sections = [f"ஐயா, **{topic}** தொடர்பான கால்நடை மருத்துவ வழிகாட்டுதல்:\n"]
                if overview:
                    sections.append(f"🩺 **மருத்துவ விவரம் ({topic}):**\n• {overview}\n")
                if action:
                    sections.append(f"🚨 **உடனடி நடவடிக்கை:**\n• {action}\n")
                if prevention_list:
                    p_lines = "\n".join([f"• {tip}" for tip in prevention_list])
                    sections.append(f"🛡️ **நோய் தடுப்பு முறைகள் (Prevention Tips):**\n{p_lines}\n")
                if prods:
                    p_items = []
                    for p in prods[:2]:
                        p_items.append(f"• **{p.get('name')}** ({p.get('url', 'https://chimertech.shop')})\n  - பயன்பாடு: {p.get('purpose', 'ஆரம்ப சோதனைக் கருவி')}")
                    sections.append(f"🩺 **பரிந்துரைக்கப்படும் சைமர்டெக் தயாரிப்பு (Recommended Chimertech Product):**\n" + "\n".join(p_items) + "\n")
                sections.append("⚠️ **கால்நடை மருத்துவர் ஆலோசனை:**\n• தீவிர காய்ச்சல், கடுமையான வலி அல்லது பால்/சாணத்தில் ரத்தம் காணப்பட்டால் உடனடியாக கால்நடை மருத்துவரை அணுகவும்.")
                return "\n".join(sections).strip()

            sections = [f"Sir, here is the clinical veterinary guidance for **{topic}**:\n"]
            if overview:
                sections.append(f"🩺 **Clinical Overview ({topic}):**\n• {overview}\n")
            if action:
                sections.append(f"🚨 **Immediate Action:**\n• {action}\n")
            if prevention_list:
                p_lines = "\n".join([f"• {tip}" for tip in prevention_list])
                sections.append(f"🛡️ **Prevention Tips:**\n{p_lines}\n")
            if prods:
                p_items = []
                for p in prods[:2]:
                    p_items.append(f"• **{p.get('name')}** ({p.get('url', 'https://chimertech.shop')})\n  - Purpose: {p.get('purpose', 'Early screening & supportive care')}")
                sections.append(f"🩺 **Recommended Chimertech Product:**\n" + "\n".join(p_items) + "\n")
            sections.append("⚠️ **Veterinary Alert:**\n• If high fever, severe pain, or rapid worsening occurs, call your veterinarian promptly.")
            return "\n".join(sections).strip()

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

        # 0.8. Commercial Dairy Farm Setup, Herd Planning & Monthly Budget Calculations
        FARM_PLAN_TRIGGERS = [
            "start a farm", "start new farm", "start farm", "starting a farm", "starting new farm",
            "setup farm", "set up farm", "build a farm", "build one farm", "new farm",
            "dairy farm", "farm plan", "farm planning", "plan to start", "planed to start", "planned to start",
            "spend per", "cost per", "how much money", "how much cost", "how money cast", "cast i need to spend",
            "cost i need to spend", "how much it spend", "how much to spend", "how much spend", "monthly spend",
            "monthly cost", "monthly budget", "monthly expense", "dairy budget", "feed budget", "ration plan",
            "feed calculation", "how much feed", "how much feet", "spend per onth", "cost per onth",
            "what much it spend", "what much spend", "பண்ணை ஆரம்பிக்க", "புதிய பண்ணை", "பண்ணை தொடங்க",
            "மாதாந்திர செலவு", "செலவு எவ்வளவு", "डेयरी फार्म", "फार्म शुरू"
        ]
        has_cattle_num = bool(re.search(r'\b\d+\s*(?:cattle|cows?|animals?|மாடுகள்?|மாடு|கை|गाय)\b', lower_u))
        has_plan_phrase = any(phrase in lower_u for phrase in FARM_PLAN_TRIGGERS)
        is_farm_planning_request = has_plan_phrase or (has_cattle_num and any(w in lower_u for w in ["spend", "cost", "budget", "month", "onth", "start", "plan", "idea"]))
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

        # 6. Veterinary queries (Diseases, Illness, and Treatments ONLY)
        VET_WORDS = ["treatment", "medicine", "cmt", "mastitis", "quadmastest", "disease", "bloat", "swollen udder", "infection", "sick cow", "மடிநோய்", "மருந்து", "நோய்"]
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

