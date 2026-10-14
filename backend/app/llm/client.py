import os
import logging
import json
import re
import httpx
from typing import List, Dict, Any, Optional, Tuple
from openai import AsyncOpenAI
from ..config import settings

logger = logging.getLogger("ragul_llm_client")

class LLMClient:
    def __init__(self):
        self._async_openai_client: Optional[AsyncOpenAI] = None

    def _get_openai_client(self) -> AsyncOpenAI:
        api_key = (
            settings.JARVISLABS_API_KEY 
            or settings.OPENAI_API_KEY 
            or os.environ.get("JARVISLABS_API_KEY", "") 
            or os.environ.get("OPENAI_API_KEY", "")
            or "sk-jarvislabs-placeholder"
        )
        base_url = settings.LLM_API_BASE.rstrip("/")
        return AsyncOpenAI(base_url=base_url, api_key=api_key)

    async def chat(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        max_tokens: int = 250,
        temperature: float = 0.2
    ) -> Tuple[Dict[str, Any], Optional[List[Dict[str, Any]]]]:
        """
        Executes JarvisLabs.ai, OpenAI-compatible, or Ollama chat completions with native tool-calling.
        Returns: (assistant_message_dict, tool_calls_list_or_None)
        """
        provider = settings.LLM_PROVIDER.lower()
        model_name = settings.LLM_MODEL_NAME
        api_base = settings.LLM_API_BASE

        # Mode A: JarvisLabs / OpenAI / Groq / vLLM (AsyncOpenAI SDK)
        if provider in ["jarvislabs", "openai", "groq", "vllm"] or "jarvislabs" in api_base or "openai" in api_base or "groq" in api_base:
            try:
                client = self._get_openai_client()
                logger.info(f"[LLMClient] Calling JarvisLabs/OpenAI endpoint ({model_name}) at {api_base} (Tools: {bool(tools)})")

                kwargs: Dict[str, Any] = {
                    "model": model_name,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
                if tools:
                    kwargs["tools"] = tools
                    kwargs["tool_choice"] = "auto"

                response = await client.chat.completions.create(**kwargs)
                choice = response.choices[0]
                message = choice.message

                content = message.content or ""
                # Strip reasoning tags if present
                clean_content = re.sub(r'<think>[\s\S]*?</think>', '', content).strip()

                tool_calls = None
                if message.tool_calls:
                    tool_calls = [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in message.tool_calls
                    ]
                
                # Secondary parser: if model generated special tokens or function call syntax in text content
                if not tool_calls and clean_content:
                    # Match known tool names even if slightly clipped or prefixed
                    known_tools = [
                        "send_whatsapp_notification",
                        "veterinary_and_products_rag",
                        "get_workers_and_staff_data",
                        "get_daily_farm_comprehensive_summary",
                        "get_feed_and_nutrition",
                        "get_cow_health_summary",
                        "analyze_mastitis_risk",
                        "get_breeding_and_estrus_status",
                        "get_milk_production_trends",
                        "get_herd_health_and_anomalies",
                        "get_monthly_historical_metrics"
                    ]
                    
                    found_tool = None
                    for t in known_tools:
                        if f"functions.{t}" in clean_content or f'"{t}"' in clean_content or f"'{t}'" in clean_content or f"to=functions.{t[:15]}" in clean_content:
                            found_tool = t
                            break
                    
                    if not found_tool:
                        match_fn = re.search(r'functions\.([a-zA-Z0-9_]+)', clean_content)
                        if match_fn:
                            extracted = match_fn.group(1)
                            for t in known_tools:
                                if t.startswith(extracted) or extracted.startswith(t[:10]):
                                    found_tool = t
                                    break
                            if not found_tool:
                                found_tool = extracted

                    if found_tool:
                        tool_calls = [{"function": {"name": found_tool, "arguments": {}}}]
                        clean_content = ""

                    elif "{" in clean_content and "}" in clean_content:
                        match = re.search(r'\{[\s\r\n]*"(?:name|tool)"\s*:\s*"(\w+)"[\s\S]*?\}', clean_content)
                        if match:
                            try:
                                parsed = json.loads(match.group(0))
                                t_name = parsed.get("name") or parsed.get("tool")
                                t_args = parsed.get("arguments") or parsed.get("parameters", {})
                                if t_name:
                                    tool_calls = [{"function": {"name": t_name, "arguments": t_args}}]
                                    clean_content = ""
                            except Exception:
                                pass

                # Clean any special tokens, channel commentary, and function artefacts from content
                clean_content = re.sub(r'<\|[\s\S]*?\|>', '', clean_content)
                clean_content = re.sub(r'assistant\s*commentary[\s\S]*', '', clean_content, flags=re.IGNORECASE)
                clean_content = re.sub(r'to=functions\.[\w_]+', '', clean_content)
                clean_content = clean_content.strip()
                logger.info(f"[LLMClient] JarvisLabs response received: {len(clean_content)} chars, Tool Calls: {bool(tool_calls)}")
                return {"role": "assistant", "content": clean_content}, tool_calls

            except Exception as e:
                logger.warning(f"[LLMClient] JarvisLabs API call failed: {e}. Falling back to direct HTTP or local fallback...")

        # Mode B: Direct HTTP Fallback (Ollama / Local HTTP)
        try:
            is_ollama = "11434" in api_base or provider == "ollama"
            base_clean = api_base.replace("/v1", "").rstrip("/")
            target_url = f"{base_clean}/api/chat" if is_ollama else f"{api_base}/chat/completions"

            payload: Dict[str, Any] = {
                "model": model_name,
                "messages": messages,
                "stream": False,
                "options": {
                    "num_ctx": 1024,
                    "num_predict": max_tokens,
                    "temperature": temperature
                }
            }
            if tools:
                payload["tools"] = tools

            async with httpx.AsyncClient(timeout=8.0) as http_client:
                response = await http_client.post(target_url, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    msg = data.get("message") or (data.get("choices", [{}])[0].get("message", {}))
                    raw_content = msg.get("content") or ""
                    clean_content = re.sub(r'<think>[\s\S]*?</think>', '', raw_content).strip()
                    msg["content"] = clean_content
                    return msg, msg.get("tool_calls")

        except Exception as e2:
            logger.error(f"[LLMClient] Fallback HTTP call failed: {e2}")

        err_msg = "LLM service temporarily offline. Using direct database telemetry."
        return {"role": "assistant", "content": err_msg}, None

llm_client = LLMClient()
