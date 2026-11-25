import os
import json
import re
import time
import logging
import datetime
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional

from dotenv import load_dotenv
from openai import OpenAI

from app.knowledge.retrieval import hybrid_search
from app.knowledge.guardrails import check_guardrails

BACKEND_ENV = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=BACKEND_ENV if BACKEND_ENV.exists() else None, override=True)

logger = logging.getLogger("ragul_rag_engine")

IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "").strip()
API_KEY = os.getenv("JARVISLABS_API_KEY")
BASE_URL = os.getenv("LLM_API_BASE")
MODEL = os.getenv("LLM_MODEL_NAME") or "glm-5.3-flash"
SYNTHESIS_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0"))
COMBINED_MAX_TOKENS = int(os.getenv("COMBINED_MAX_TOKENS", "4000"))
REQUEST_TIMEOUT_SECONDS = float(os.getenv("RAG_REQUEST_TIMEOUT_SECONDS", "45.0"))
MIN_RERANK_SCORE = float(os.getenv("RAG_MIN_RERANK_SCORE", "-1.5"))
LLM_MAX_RETRIES = max(0, int(os.getenv("RAG_LLM_MAX_RETRIES", "2")))
RETRY_BASE_DELAY_SECONDS = float(os.getenv("RAG_RETRY_BASE_DELAY_SECONDS", "0.75"))
DB_SCHEMA_CACHE_TTL_SECONDS = float(os.getenv("RAG_DB_SCHEMA_CACHE_TTL_SECONDS", "300.0"))
DB_QUERY_TIMEOUT_SECONDS = float(os.getenv("RAG_DB_QUERY_TIMEOUT_SECONDS", "8.0"))
CHIMERTECH_STORE_URL = os.getenv("CHIMERTECH_STORE_URL", "https://chimertech.shop/").strip()

RAGUL_SYNTHESIS_SYSTEM_PROMPT = """
You are RAGUL, the friendly, practical conversational AI supervisor for PashuX Dairy Farms, speaking naturally and directly to the farmer.

1. AUTOMATIC LANGUAGE RECOGNITION & STRICT RELEVANCE:
- Automatically recognize the user's language and script (Tamil script, Tanglish/Romanized Tamil, Hindi/Devanagari script, Hinglish/Romanized Hindi, English, or any other language) and ALWAYS reply 100% in that EXACT language and script—even when the retrieved evidence is in English or when a record is not found.
- Speak naturally and directly to the farmer without forcing titles or honorifics like "Sir", "Sam Sir", "சாம் சர்", or "सैम सर".
- Understand and autocorrect typos, misspellings, irregular grammar, phonetic/spoken phrasing, and code-switching gracefully without mentioning or pointing out the user's mistakes.
- ALWAYS directly answer what the user asked first. Do NOT include unwanted words, filler, conversational padding, unrequested background notes, or closing remarks.
- Never mention internal tools, search results, database lookups, knowledge-base limitations, or meta-commentary.
- Voice-synthesis friendly: spoken_response must use complete, natural sentences with no raw JSON, markdown tables, asterisks, bullet symbols, or citation codes.

2. COMPLIANCE, ACCURACY & WELFARE GUARDRAILS:
- Respect the real-time IST date and time provided in context. Never confuse TODAY with YESTERDAY.
- Enforce DairyNZ BCS thresholds when supported by context: alert if lactating cow BCS < 4.0 (palpation) or < 3.0 (visual scale); alert if dry cow < 4.5.
- Never diagnose an individual animal or prescribe antibiotics, prescription medicines, or exact dosages for a specific animal. If the user asks for an individualized treatment, antibiotic choice, or exact dosage for their animal, refuse the prescription clearly in the user's language and advise immediate consultation with a qualified veterinarian.
- When Chimertech catalog products or general supportive/nutritional items appear in context, only reference items explicitly present in the supplied catalog/excerpts without inventing medical claims, clinical cures, or dosages, and follow label directions or veterinarian guidance.
- Do not fabricate facts, symptoms, dosages, citations, or animal records not present in the retrieved veterinary excerpts or live farm database context.
- If a requested cow/cattle ID or tag is not found in the live farm database (`"found": false`), state clearly in the user's exact language that no record for that ID or tag exists in the farm database, and offer to check another ID/tag or recent herd records.
""".strip()


def _log_event(event: str, **fields: Any) -> None:
    payload = {"event": event, **fields}
    logger.info("[RAG_OBS] %s", json.dumps(payload, default=str))


class VeterinaryRAGEngine:

    def __init__(self, lazy_load: bool = True):
        self.kb_dir = os.path.join(
            os.path.dirname(
                os.path.dirname(
                    os.path.dirname(
                        os.path.abspath(__file__)
                    )
                )
            ),
            "data",
            "knowledge_base"
        )

        self.products_path = os.path.join(
            self.kb_dir,
            "products_catalog.json"
        )

        self.nasem_rules_path = os.path.join(
            self.kb_dir,
            "nasem_feed_nutrition_rules.json"
        )

        self.products_data: List[Dict[str, Any]] = []
        self.scenarios_data: List[Dict[str, Any]] = []
        self.nasem_rules_data: Dict[str, Any] = {}
        self._kb_loaded: bool = False
        self._client: Optional[OpenAI] = None
        self._schema_cache: Optional[Dict[str, List[Dict[str, str]]]] = None
        self._schema_cache_ts: float = 0.0

        if not lazy_load:
            self.warmup()

    def warmup(self) -> None:
        self._ensure_kb_loaded()
        self._get_llm_client()
        try:
            _ = hybrid_search("mastitis", top_k=1, verbose=False)
            _log_event("warmup_complete", kb_loaded=self._kb_loaded)
        except Exception as exc:
            _log_event("warmup_partial", error_type=type(exc).__name__)

    def _get_llm_client(self) -> Optional[OpenAI]:
        if self._client is not None:
            return self._client
        if API_KEY and BASE_URL:
            self._client = OpenAI(
                api_key=API_KEY,
                base_url=BASE_URL,
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
        else:
            _log_event(
                "llm_client_unconfigured",
                has_api_key=bool(API_KEY),
                has_base_url=bool(BASE_URL),
            )
        return self._client

    def _ensure_kb_loaded(self) -> None:
        if not self._kb_loaded:
            self.load_knowledge_base()

    # =====================================================
    # KNOWLEDGE BASE LOADING
    # =====================================================

    def load_knowledge_base(self) -> None:
        t0 = time.perf_counter()
        try:
            if os.path.exists(self.products_path):
                with open(self.products_path, "r", encoding="utf-8") as f:
                    pdata = json.load(f)
                    self.products_data = pdata.get("products", [])
                    self.scenarios_data = pdata.get("recommendation_scenarios", [])
            else:
                _log_event("products_catalog_missing", path=self.products_path)

            if os.path.exists(self.nasem_rules_path):
                with open(self.nasem_rules_path, "r", encoding="utf-8") as f:
                    self.nasem_rules_data = json.load(f)
            else:
                _log_event("nasem_rules_missing", path=self.nasem_rules_path)

            self._kb_loaded = True
            _log_event(
                "kb_loaded",
                products_count=len(self.products_data),
                scenarios_count=len(self.scenarios_data),
                nasem_ruleset=self.nasem_rules_data.get("ruleset_id"),
                elapsed_ms=round((time.perf_counter() - t0) * 1000, 2),
            )
        except Exception as e:
            _log_event(
                "kb_load_failed",
                error_type=type(e).__name__,
                elapsed_ms=round((time.perf_counter() - t0) * 1000, 2),
            )

    # =====================================================
    # LANGUAGE DETECTION, CHRONOLOGY & RESPONSE HELPERS
    # =====================================================

    @staticmethod
    def _detect_script_language(text: str) -> Optional[str]:
        """Fast Unicode script detector for non-Latin scripts."""
        s = text or ""
        if re.search(r"[\u0B80-\u0BFF]", s):
            return "Tamil (Tamil script)"
        if re.search(r"[\u0900-\u097F]", s):
            return "Hindi (Devanagari script)"
        if re.search(r"[\u0C00-\u0C7F]", s):
            return "Telugu"
        if re.search(r"[\u0C80-\u0CFF]", s):
            return "Kannada"
        if re.search(r"[\u0D00-\u0D7F]", s):
            return "Malayalam"
        return None

    @staticmethod
    def _localized_fallback(lang_label: str) -> str:
        low = (lang_label or "").lower()
        if "tamil" in low and "tanglish" not in low:
            return (
                "இந்தக் கேள்விக்கான சரிபார்க்கப்பட்ட தகவல் உள்ளூர் கால்நடை தரவுத்தளத்தில் "
                "கண்டறியப்படவில்லை. தயவுசெய்து தகுதிவாய்ந்த கால்நடை மருத்துவரை அணுகவும் அல்லது "
                "மாடு பற்றிய கூடுதல் விவரங்களைப் பகிரவும்."
            )
        if "tanglish" in low:
            return (
                "Indha kelvikkaana verified information namma local veterinary knowledge base la "
                "kidaikkala. Dayavu seidhu qualified veterinarian-ai consult pannunga illana animal details share pannunga."
            )
        if "hindi" in low and "hinglish" not in low:
            return (
                "इस प्रश्न से संबंधित सत्यापित जानकारी स्थानीय पशु चिकित्सा ज्ञानकोश में उपलब्ध नहीं है। "
                "कृपया किसी योग्य पशु चिकित्सक से परामर्श लें या पशु के बारे में अधिक विवरण साझा करें।"
            )
        if "hinglish" in low:
            return (
                "Is sawal se judi verified jaankari local veterinary knowledge base mein uplabdh nahi hai. "
                "Kripya kisi qualified veterinarian se salah lein ya pashu ke baare mein aur jaankari share karein."
            )
        return (
            "I couldn't find sufficiently relevant information in the veterinary "
            "knowledge base for this question. Please consult a qualified veterinarian "
            "or share more details about the animal and its condition."
        )

    @staticmethod
    def _build_ist_chronology_block() -> str:
        now_ist = datetime.datetime.now(IST)
        curr_time_str = now_ist.strftime("%A, %d %B %Y, %I:%M %p IST")
        today_str = now_ist.strftime("%Y-%m-%d")
        yesterday_dt = now_ist - datetime.timedelta(days=1)
        yesterday_str = yesterday_dt.strftime("%Y-%m-%d")
        return (
            f"Current Date & Time: {curr_time_str}\n"
            f"Today: {today_str} ({now_ist.strftime('%d %B %Y')})\n"
            f"Yesterday: {yesterday_str} ({yesterday_dt.strftime('%d %B %Y')})"
        )

    @staticmethod
    def _format_history_block(history: Optional[List[Dict[str, str]]]) -> str:
        if not history:
            return ""
        lines: List[str] = []
        for turn in history[-6:]:
            role = (turn.get("role") or "user").upper()
            content = (turn.get("content") or "").strip()
            if content and not content.startswith("{"):
                lines.append(f"{role}: {content}")
        return "\n".join(lines)

    @staticmethod
    def _make_response(
        *,
        topic: str = "Veterinary Information",
        clinical_answer: str = "",
        action: str = "",
        prevention: str = "",
        prevention_tips: Optional[List[str]] = None,
        products: Optional[List[Dict[str, Any]]] = None,
        store_url: str = CHIMERTECH_STORE_URL,
        spoken_response: str = "",
        score: float = 0.0,
        sources: Optional[List[str]] = None,
        grounded: bool = False,
        extra: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "topic": topic,
            "clinical_answer": clinical_answer,
            "action": action,
            "prevention": prevention,
            "prevention_tips": prevention_tips if prevention_tips is not None else [],
            "products": products if products is not None else [],
            "store_url": store_url,
            "spoken_response": spoken_response or clinical_answer,
            "score": score,
            "sources": sources if sources is not None else [],
            "grounded": grounded,
        }
        if extra:
            payload.update(extra)
        return payload

    # =====================================================
    # DYNAMIC LIVE DATABASE SCHEMA & READ-ONLY QUERYING
    # =====================================================

    @staticmethod
    def _quote_ident(ident: str) -> str:
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", ident or ""):
            raise ValueError(f"Unsafe SQL identifier: {ident!r}")
        return f'"{ident}"'

    def _get_live_schema(
        self,
        dsn: str,
        force_refresh: bool = False,
    ) -> Dict[str, List[Dict[str, str]]]:
        now = time.monotonic()
        if (
            not force_refresh
            and self._schema_cache is not None
            and (now - self._schema_cache_ts) < DB_SCHEMA_CACHE_TTL_SECONDS
        ):
            return self._schema_cache

        import asyncpg

        async def _fetch_cols() -> Dict[str, List[Dict[str, str]]]:
            conn = await asyncpg.connect(
                dsn,
                statement_cache_size=0,
                timeout=DB_QUERY_TIMEOUT_SECONDS,
            )
            try:
                rows = await conn.fetch(
                    """
                    SELECT table_schema, table_name, column_name, data_type
                    FROM information_schema.columns
                    WHERE table_schema = 'public'
                    ORDER BY table_name, ordinal_position
                    """
                )
                schema: Dict[str, List[Dict[str, str]]] = {}
                for r in rows:
                    fq_tbl = f"{r['table_schema']}.{r['table_name']}"
                    schema.setdefault(fq_tbl, []).append(
                        {"name": r["column_name"], "type": r["data_type"]}
                    )
                return schema
            finally:
                await conn.close()

        loop = asyncio.new_event_loop()
        try:
            schema = loop.run_until_complete(_fetch_cols())
            self._schema_cache = schema
            self._schema_cache_ts = time.monotonic()
            _log_event("db_schema_refreshed", table_count=len(schema))
            return schema
        finally:
            loop.close()

    def _plan_dynamic_read(
        self,
        query: str,
        schema: Dict[str, List[Dict[str, str]]],
    ) -> Optional[Dict[str, Any]]:
        if not schema:
            return None

        devanagari_map = str.maketrans("०१२३४५६७८९", "0123456789")
        norm_query = (query or "").translate(devanagari_map)
        q_lower = norm_query.lower()
        q_tokens = set(re.findall(r"[a-z0-9_]+", q_lower))

        num_match = re.search(
            r"\b(?:(?:cow|cattle|animal)\s+)?(?:id|tag|no|number|cattle[\s_-]?id|camera[\s_-]?id|cow[\s_-]?id|cow|cattle|animal)\s*[:#-]?\s*([A-Za-z0-9_-]*\d[A-Za-z0-9_-]*)\b",
            q_lower,
        )
        if not num_match:
            num_match = re.search(
                r"(?:गाय|गौ|पशु|மாடு|பசு)\s*[:#-]?\s*([A-Za-z0-9_-]*\d[A-Za-z0-9_-]*)",
                norm_query,
            )
        if not num_match:
            num_match = re.search(r"\b(\d{1,6})\b", q_lower)

        raw_code: Optional[str] = num_match.group(1) if num_match else None
        id_val: Optional[int] = int(raw_code) if (raw_code and raw_code.isdigit()) else None

        ranked_tables: List[tuple[float, str]] = []
        for fq_tbl, cols in schema.items():
            tbl_short = fq_tbl.split(".", 1)[-1].lower()
            tbl_parts = set(tbl_short.split("_"))
            col_names_lower = [c["name"].lower() for c in cols]

            score = 0.0
            score += len(q_tokens.intersection(tbl_parts)) * 3.0
            for cname in col_names_lower:
                if cname in q_tokens:
                    score += 2.5
                elif any(part in q_tokens for part in cname.split("_") if len(part) > 2):
                    score += 1.0

            if any(tag in tbl_short for tag in ("analytics", "cattle", "herd", "cow", "milk", "bcs")):
                score += 0.5

            if raw_code or id_val is not None:
                if any(re.search(r"(tag|ear)", c) and c != "tag_id" for c in col_names_lower):
                    score += 4.0
                if any(c in ("cattle_id", "cow_id", "animal_id", "id") for c in col_names_lower):
                    score += 1.5

            if "users" in tbl_short and not any(
                k in q_tokens for k in ("user", "users", "farmer", "village", "phone")
            ):
                score -= 2.0

            ranked_tables.append((score, fq_tbl))

        ranked_tables.sort(key=lambda x: x[0], reverse=True)
        best_table = ranked_tables[0][1]

        candidate_plans: List[Dict[str, Any]] = []
        for _, fq_tbl in ranked_tables:
            cols_meta = schema[fq_tbl]
            col_names = [c["name"] for c in cols_meta]
            selected_cols = col_names[:14]

            id_col: Optional[str] = None
            if id_val is not None:
                for candidate in ("cattle_id", "cow_id", "tag_id", "animal_id", "id"):
                    if candidate in col_names:
                        id_col = candidate
                        break

            tag_col: Optional[str] = None
            if raw_code:
                for cname in col_names:
                    cl = cname.lower()
                    if re.search(r"(tag|ear)", cl) and cl not in ("tag_id",):
                        tag_col = cname
                        break

            order_col: Optional[str] = None
            for candidate in ("created_at", "updated_at", "timestamp", "recorded_at", "id"):
                if candidate in col_names:
                    order_col = candidate
                    break

            if (raw_code or id_val is not None) and not id_col and not tag_col:
                continue

            candidate_plans.append(
                {
                    "table": fq_tbl,
                    "columns": selected_cols,
                    "id_col": id_col,
                    "id_val": id_val,
                    "tag_col": tag_col,
                    "raw_code": raw_code,
                    "order_col": order_col,
                }
            )

        return {
            "primary_table": best_table,
            "id_val": id_val,
            "raw_code": raw_code,
            "plans": candidate_plans,
        }

    def _retrieve_farm_db_context(self, query: str) -> Optional[Dict[str, Any]]:
        dsn = os.getenv("DATABASE_URL")
        if not dsn:
            return None

        t0 = time.perf_counter()

        def _run_dynamic_query(force_refresh: bool = False) -> Optional[Dict[str, Any]]:
            import asyncpg

            schema = self._get_live_schema(dsn, force_refresh=force_refresh)
            plan_bundle = self._plan_dynamic_read(query, schema)
            if not plan_bundle:
                return None

            async def _exec() -> Optional[Dict[str, Any]]:
                conn = await asyncpg.connect(
                    dsn,
                    statement_cache_size=0,
                    timeout=DB_QUERY_TIMEOUT_SECONDS,
                )
                try:
                    plans: List[Dict[str, Any]] = plan_bundle["plans"]
                    id_val: Optional[int] = plan_bundle["id_val"]
                    raw_code: Optional[str] = plan_bundle.get("raw_code")

                    if id_val is not None or raw_code:
                        checked_tables: List[str] = []
                        for p in plans:
                            _, tbl_name = p["table"].split(".", 1)
                            q_tbl = f"public.{self._quote_ident(tbl_name)}"
                            q_cols = ", ".join(self._quote_ident(c) for c in p["columns"])
                            order_clause = (
                                f" ORDER BY {self._quote_ident(p['order_col'])} DESC"
                                if p["order_col"]
                                else ""
                            )

                            if p["id_col"] and id_val is not None:
                                checked_tables.append(p["table"])
                                q_id = self._quote_ident(p["id_col"])
                                sql = f"SELECT {q_cols} FROM {q_tbl} WHERE {q_id} = $1{order_clause} LIMIT 5"
                                rows = await conn.fetch(sql, id_val)
                                if rows:
                                    return {
                                        "table": p["table"],
                                        "matched_by": p["id_col"],
                                        "found": True,
                                        "queried_id": id_val,
                                        "records": [dict(r) for r in rows],
                                    }

                            if p["tag_col"] and raw_code:
                                if p["table"] not in checked_tables:
                                    checked_tables.append(p["table"])
                                q_tag = self._quote_ident(p["tag_col"])
                                sql = (
                                    f"SELECT {q_cols} FROM {q_tbl} "
                                    f"WHERE CAST({q_tag} AS TEXT) = $1{order_clause} LIMIT 5"
                                )
                                rows = await conn.fetch(sql, str(raw_code))
                                if rows:
                                    matched_records = [dict(r) for r in rows]
                                    resolved_cattle_id: Optional[int] = None
                                    for rec in matched_records:
                                        for k in ("cattle_id", "cow_id", "id"):
                                            v = rec.get(k)
                                            if isinstance(v, int):
                                                resolved_cattle_id = v
                                                break
                                        if resolved_cattle_id is not None:
                                            break

                                    related_data: Dict[str, Any] = {}
                                    if resolved_cattle_id is not None:
                                        for rel_p in plans:
                                            if rel_p["table"] == p["table"]:
                                                continue
                                            rel_cols = schema.get(rel_p["table"], [])
                                            rel_col_names = [c["name"] for c in rel_cols]
                                            for fk in ("cattle_id", "cow_id", "animal_id"):
                                                if fk in rel_col_names:
                                                    _, r_tbl_name = rel_p["table"].split(".", 1)
                                                    q_r_tbl = f"public.{self._quote_ident(r_tbl_name)}"
                                                    q_r_cols = ", ".join(
                                                        self._quote_ident(c) for c in rel_p["columns"]
                                                    )
                                                    r_order = (
                                                        f" ORDER BY {self._quote_ident(rel_p['order_col'])} DESC"
                                                        if rel_p["order_col"]
                                                        else ""
                                                    )
                                                    r_sql = (
                                                        f"SELECT {q_r_cols} FROM {q_r_tbl} "
                                                        f"WHERE {self._quote_ident(fk)} = $1{r_order} LIMIT 3"
                                                    )
                                                    r_rows = await conn.fetch(r_sql, resolved_cattle_id)
                                                    if r_rows:
                                                        related_data[rel_p["table"]] = [dict(rr) for rr in r_rows]
                                                    break

                                    payload_out: Dict[str, Any] = {
                                        "table": p["table"],
                                        "matched_by": p["tag_col"],
                                        "found": True,
                                        "queried_tag": raw_code,
                                        "records": matched_records,
                                    }
                                    if resolved_cattle_id is not None:
                                        payload_out["resolved_cattle_id"] = resolved_cattle_id
                                    if related_data:
                                        payload_out["related_records"] = related_data
                                    return payload_out

                        return {
                            "table": checked_tables[0] if checked_tables else plan_bundle["primary_table"],
                            "checked_tables": checked_tables,
                            "found": False,
                            "queried_id": id_val if id_val is not None else raw_code,
                            "records": [],
                        }

                    p0 = plans[0]
                    _, tbl_name = p0["table"].split(".", 1)
                    q_tbl = f"public.{self._quote_ident(tbl_name)}"
                    q_cols = ", ".join(self._quote_ident(c) for c in p0["columns"])
                    order_clause = (
                        f" ORDER BY {self._quote_ident(p0['order_col'])} DESC"
                        if p0["order_col"]
                        else ""
                    )
                    sql = f"SELECT {q_cols} FROM {q_tbl}{order_clause} LIMIT 10"
                    rows = await conn.fetch(sql)
                    if not rows:
                        return None
                    return {
                        "table": p0["table"],
                        "found": True,
                        "records": [dict(r) for r in rows],
                    }
                finally:
                    await conn.close()

            loop = asyncio.new_event_loop()
            try:
                return loop.run_until_complete(_exec())
            finally:
                loop.close()

        try:
            payload = _run_dynamic_query(force_refresh=False)
            if not payload:
                return None
            _log_event(
                "farm_db_context_loaded",
                table=payload.get("table"),
                found=payload.get("found", True),
                row_count=len(payload.get("records") or []),
                elapsed_ms=round((time.perf_counter() - t0) * 1000, 2),
            )
            return payload
        except Exception as exc:
            err_name = type(exc).__name__
            if err_name in ("UndefinedTableError", "UndefinedColumnError"):
                try:
                    payload = _run_dynamic_query(force_refresh=True)
                    if payload:
                        _log_event(
                            "farm_db_context_loaded_after_refresh",
                            table=payload.get("table"),
                            found=payload.get("found", True),
                            row_count=len(payload.get("records") or []),
                            elapsed_ms=round((time.perf_counter() - t0) * 1000, 2),
                        )
                        return payload
                except Exception as retry_exc:
                    exc = retry_exc
            _log_event(
                "farm_db_context_skipped",
                error_type=type(exc).__name__,
                elapsed_ms=round((time.perf_counter() - t0) * 1000, 2),
            )
            return None

    # =====================================================
    # PRODUCT SCENARIO MATCHING & CHIMERTECH CATALOG
    # =====================================================

    def _calculate_match_score(
        self,
        query: str,
        target_texts: List[str],
        keywords: List[str],
    ) -> float:
        normalized_query = query.lower()
        normalized_query = re.sub(
            r"\b(diasese|desease|diseas|deseas)\b",
            "disease",
            normalized_query,
        )

        query_words = set(re.findall(r"\w+", normalized_query))
        if not query_words:
            return 0.0

        score = 0.0
        keyword_set = {keyword.lower() for keyword in keywords}
        keyword_matches = query_words.intersection(keyword_set)
        score += len(keyword_matches) * 3.0

        for target in target_texts:
            target_lower = target.lower()
            if target_lower in normalized_query:
                score += 5.0
            target_words = set(re.findall(r"\w+", target_lower))
            overlap = query_words.intersection(target_words)
            score += len(overlap) * 1.5

        return score

    def _find_best_scenario(self, query: str) -> Optional[Dict[str, Any]]:
        self._ensure_kb_loaded()
        best_scenario = None
        best_score = 0.0

        for scenario in self.scenarios_data:
            targets = (
                scenario.get("farmer_questions", [])
                + scenario.get("trigger_keywords", [])
                + [scenario.get("intent", "")]
            )
            keywords = scenario.get("trigger_keywords", [])
            score = self._calculate_match_score(query, targets, keywords)

            if score > best_score:
                best_score = score
                best_scenario = scenario

        if best_score < 5.0:
            return None

        return best_scenario

    def _get_relevant_products(
        self,
        query: str,
        scenario: Optional[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        self._ensure_kb_loaded()
        if scenario:
            recommended_products = scenario.get("recommended_products", [])
            if recommended_products:
                return recommended_products

            recommended_product_ids = scenario.get("recommended_product_ids", [])
            if recommended_product_ids:
                product_ids = set(recommended_product_ids)
                matched = [
                    {
                        "name": product.get("name"),
                        "purpose": product.get("safe_answer", product.get("role", "")),
                        "store_url": product.get("url") or product.get("store_url") or CHIMERTECH_STORE_URL,
                    }
                    for product in self.products_data
                    if product.get("product_id") in product_ids
                ]
                if matched:
                    return matched

        q_lower = (query or "").lower()
        q_words = set(re.findall(r"\w+", q_lower))
        if not q_words or not self.products_data:
            return []

        scored_products: List[tuple[float, Dict[str, Any]]] = []
        for product in self.products_data:
            text_blob = " ".join(
                str(product.get(k) or "")
                for k in ("name", "category", "role", "safe_answer", "description", "indications")
            ).lower()
            p_words = set(re.findall(r"\w+", text_blob))
            overlap = len(q_words.intersection(p_words))
            if overlap > 0:
                scored_products.append(
                    (
                        float(overlap),
                        {
                            "name": product.get("name"),
                            "purpose": product.get("safe_answer", product.get("role", "")),
                            "store_url": product.get("url") or product.get("store_url") or CHIMERTECH_STORE_URL,
                        },
                    )
                )

        scored_products.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in scored_products[:3]]

    # =====================================================
    # FAST ROUTING + AI INTENT FALLBACK & RETRIEVAL
    # =====================================================

    @staticmethod
    def _split_subquestions(query: str) -> List[str]:
        parts = [p.strip() for p in re.split(r"[?\n]+", query or "") if p.strip()]
        return parts if parts else ([query.strip()] if (query or "").strip() else [])

    def _fast_route_query(self, query: str) -> Optional[Dict[str, Any]]:
        """Zero-LLM-call fast path for pure English queries and regional-script DB ID/tag lookups."""
        s = (query or "").strip()
        if not s:
            return None

        script_lang = self._detect_script_language(s)
        db_cues = re.search(
            r"\b(?:bcs|tag|camera|cctv|analytics|herd|milk|weight|record|records|status|id)\b"
            r"|(?:गाय|गौ|पशु|टैग|स्थिति|रिकॉर्ड|दूध)"
            r"|(?:மாடு|பசு|டேக்|நிலை|பால்|பதிவு)",
            s,
            re.IGNORECASE,
        )
        needs_db = bool(db_cues)
        has_number = bool(re.search(r"[\d०-९]", s))

        # Fast-route Tamil/Hindi only when querying a specific numeric ID/tag in DB;
        # otherwise let LLM translate regional veterinary questions into English for hybrid_search.
        if script_lang in ("Tamil (Tamil script)", "Hindi (Devanagari script)") and needs_db and has_number:
            norm_query = f"{s} cattle cow tag status bcs analytics record"
            return {
                "detected_language": script_lang,
                "needs_db": True,
                "english_query": norm_query,
                "fast_routed": True,
            }

        tokens = re.findall(r"[A-Za-z0-9_]+", s)
        if tokens and all(tok.isascii() for tok in tokens):
            non_ascii_chars = sum(1 for ch in s if not ch.isascii() and not ch.isspace())
            if non_ascii_chars == 0:
                # Route any Hinglish / Tanglish phrasing to LLM intent detection
                if re.search(
                    r"\b(?:meri|mera|mere|ka|ki|ke|hai|hain|kaisa|kaisi|kitna|batao|aur|gaay|gaiya|doodh|bimari"
                    r"|enna|epdi|eppadi|irukku|sollu|sollunga|oda|maadu|madu|pasu|paal|illa)\b",
                    s,
                    re.IGNORECASE,
                ):
                    return None
                return {
                    "detected_language": "English",
                    "needs_db": needs_db,
                    "english_query": s,
                    "fast_routed": True,
                }

        return None

    def _analyze_query_intent(self, query: str) -> Dict[str, Any]:
        """Fast regex/script router first; LLM fallback for Tanglish/Hinglish/regional KB queries."""
        fast = self._fast_route_query(query)
        if fast is not None:
            _log_event(
                "query_intent_fast_routed",
                detected_language=fast["detected_language"],
                needs_db=fast["needs_db"],
            )
            return fast

        fallback_lang = self._detect_script_language(query) or "English"
        client = self._get_llm_client()
        if client is None:
            return {
                "detected_language": fallback_lang,
                "needs_db": False,
                "english_query": query,
            }

        system_prompt = (
            "You are a multilingual query analyzer for PashuX Dairy Farms. Analyze the user's input "
            "(which may be in English, Tamil, Tanglish, Hindi, Hinglish, or any other language, even with typos) "
            "and return ONLY a valid JSON object with three keys:\n"
            '1. "detected_language": string — exact language and script of the user input '
            '(e.g., "Tamil (Tamil script)", "Tanglish (Romanized Tamil)", "Hindi (Devanagari script)", "Hinglish (Romanized Hindi)", "English"). '
            'If Hindi or Tamil words/grammar appear mixed with English words (e.g., "Meri cow ka milk yield aur health status kaisa hai?" '
            'or "Enna maadu oda recent BCS record eppadi irukku?"), '
            'classify as "Hinglish (Romanized Hindi)" or "Tanglish (Romanized Tamil)", NOT "English".\n'
            '2. "needs_db": boolean — true ONLY if the user is asking for live farm records, specific cattle/cow IDs or tags '
            '(e.g., "cow 1004", "गाय 1004", "மாடு 4"), their own herd\'s BCS/weight/health/milk analytics, camera status, or farmer/village logs. '
            "Set to false for general veterinary disease, symptom, prevention, BCS scale guidelines, medicines/supplements, or nutrition questions.\n"
            '3. "english_query": string — translate and normalize the question into clean, accurate English veterinary/farm terminology '
            "for search retrieval, preserving any animal ID or tag numbers (e.g., 'गाय 1004 की स्थिति बताओ' -> 'Tell me the status of cow ID or tag 1004', "
            "'மாடுகளில் மடிநோய் வராமல் தடுக்க என்ன செய்ய வேண்டும்?' -> 'How to prevent mastitis in cattle?')."
        )

        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query},
                ],
                temperature=0,
                max_tokens=300,
                extra_body={"reasoning_effort": "low", "clear_thinking": True},
            )
            raw = (resp.choices[0].message.content or "").strip()
            raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.IGNORECASE).strip()
            parsed = json.loads(raw)
            detected_language = str(parsed.get("detected_language") or fallback_lang).strip()
            needs_db = bool(parsed.get("needs_db", False))
            english_query = str(parsed.get("english_query") or query).strip()
            _log_event(
                "query_intent_routed",
                detected_language=detected_language,
                needs_db=needs_db,
                english_query=english_query,
            )
            return {
                "detected_language": detected_language,
                "needs_db": needs_db,
                "english_query": english_query,
            }
        except Exception as exc:
            _log_event("query_intent_fallback", error_type=type(exc).__name__)
            return {
                "detected_language": fallback_lang,
                "needs_db": False,
                "english_query": query,
            }

    def _retrieve_clinical_evidence(self, english_query: str) -> Dict[str, Any]:
        t0 = time.perf_counter()
        try:
            subqs = self._split_subquestions(english_query)
            raw_results: List[Dict[str, Any]] = []

            if len(subqs) <= 1:
                raw_results = hybrid_search(english_query, top_k=5, verbose=False) or []
            else:
                per_q_k = max(2, min(3, (5 + len(subqs) - 1) // len(subqs) + 1))
                seen_keys = set()
                for subq in subqs:
                    sub_hits = hybrid_search(subq, top_k=per_q_k, verbose=False) or []
                    for hit in sub_hits:
                        meta = hit.get("metadata", {}) or {}
                        key = (
                            meta.get("filename") or meta.get("source") or "",
                            meta.get("page") or meta.get("page_number") or "",
                            (hit.get("text") or hit.get("content") or "")[:120],
                        )
                        if key not in seen_keys:
                            seen_keys.add(key)
                            raw_results.append(hit)
                        if len(raw_results) >= max(5, len(subqs) * 2):
                            break

        except Exception as e:
            _log_event(
                "retrieval_error",
                error_type=type(e).__name__,
                elapsed_ms=round((time.perf_counter() - t0) * 1000, 2),
            )
            return {"results": [], "error": str(e)}

        if not raw_results:
            _log_event(
                "retrieval_complete",
                raw_count=0,
                filtered_count=0,
                elapsed_ms=round((time.perf_counter() - t0) * 1000, 2),
            )
            return {"results": [], "error": None}

        evidence: List[Dict[str, Any]] = []
        for result in raw_results:
            text = (result.get("text") or result.get("content") or "").strip()
            if not text:
                continue

            raw_score = result.get("rerank_score")
            if raw_score is None:
                raw_score = result.get("score")

            numeric_score: Optional[float] = None
            if raw_score is not None:
                try:
                    numeric_score = float(raw_score)
                    if numeric_score < MIN_RERANK_SCORE:
                        continue
                except (TypeError, ValueError):
                    numeric_score = None

            metadata = result.get("metadata", {}) or {}
            evidence.append(
                {
                    "text": text,
                    "source": metadata.get(
                        "filename",
                        metadata.get("source", "Veterinary knowledge base"),
                    ),
                    "page": metadata.get("page", metadata.get("page_number", None)),
                    "score": numeric_score if numeric_score is not None else 0.0,
                }
            )

        _log_event(
            "retrieval_complete",
            raw_count=len(raw_results),
            filtered_count=len(evidence),
            elapsed_ms=round((time.perf_counter() - t0) * 1000, 2),
        )
        return {"results": evidence, "error": None}

    # =====================================================
    # SINGLE-CALL EVIDENCE ASSESSMENT, GROUNDING & SYNTHESIS
    # =====================================================

    @staticmethod
    def _format_evidence_context(evidence: List[Dict[str, Any]]) -> str:
        blocks = []
        for idx, item in enumerate(evidence, start=1):
            page_str = f", Page: {item['page']}" if item.get("page") is not None else ""
            blocks.append(
                f"SOURCE {idx} (Document: {item['source']}{page_str})\n{item['text']}"
            )
        return "\n\n---\n\n".join(blocks)

    @staticmethod
    def _extract_field(text: str, field: str, following_fields: List[str]) -> str:
        if following_fields:
            next_headers = "|".join(re.escape(name) for name in following_fields)
            end_pattern = rf"(?=^[ \t]*(?:\*\*)?(?:{next_headers})(?:\*\*)?[ \t]*:|\Z)"
        else:
            end_pattern = r"(?=\Z)"

        pattern = (
            rf"^[ \t]*(?:\*\*)?{re.escape(field)}(?:\*\*)?[ \t]*:"
            rf"[ \t]*(?:\*\*)?(.*?)"
            rf"{end_pattern}"
        )
        match = re.search(
            pattern,
            text or "",
            re.IGNORECASE | re.MULTILINE | re.DOTALL,
        )
        return match.group(1).strip() if match else ""

    def _call_llm_with_retry(self, client: OpenAI, system_prompt: str, user_prompt: str) -> Any:
        last_exc: Optional[Exception] = None
        for attempt in range(LLM_MAX_RETRIES + 1):
            try:
                return client.chat.completions.create(
                    model=MODEL,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=SYNTHESIS_TEMPERATURE,
                    max_tokens=COMBINED_MAX_TOKENS,
                    extra_body={"reasoning_effort": "low", "clear_thinking": True},
                )
            except Exception as exc:
                last_exc = exc
                if attempt < LLM_MAX_RETRIES:
                    delay = RETRY_BASE_DELAY_SECONDS * (2 ** attempt)
                    _log_event(
                        "llm_retry",
                        attempt=attempt + 1,
                        max_retries=LLM_MAX_RETRIES,
                        delay_s=round(delay, 2),
                        error_type=type(exc).__name__,
                    )
                    time.sleep(delay)
        assert last_exc is not None
        raise last_exc

    def _synthesize_grounded_response(
        self,
        query: str,
        detected_language: str,
        evidence: List[Dict[str, Any]],
        nasem_context: Optional[Dict[str, Any]] = None,
        farm_context: Optional[Dict[str, Any]] = None,
        products_context: Optional[List[Dict[str, Any]]] = None,
        history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        t0 = time.perf_counter()
        unique_sources = list(
            dict.fromkeys(
                f"{item['source']}, page {item['page']}"
                if item.get("page") is not None
                else item["source"]
                for item in evidence
            )
        )
        top_score = max((item.get("score", 0.0) or 0.0 for item in evidence), default=0.0)
        localized_fallback = self._localized_fallback(detected_language)

        if not evidence and not nasem_context and not farm_context and not products_context:
            _log_event("synthesis_no_evidence", elapsed_ms=round((time.perf_counter() - t0) * 1000, 2))
            return self._make_response(
                topic="Veterinary Information",
                clinical_answer=localized_fallback,
                spoken_response=localized_fallback,
                score=0.0,
                sources=[],
                grounded=False,
            )

        client = self._get_llm_client()
        if client is None:
            _log_event("synthesis_client_unavailable", elapsed_ms=round((time.perf_counter() - t0) * 1000, 2))
            return self._make_response(
                topic="Veterinary Information",
                clinical_answer=localized_fallback,
                spoken_response=localized_fallback,
                score=top_score,
                sources=unique_sources,
                grounded=False,
            )

        context_str = self._format_evidence_context(evidence)
        chronology_block = self._build_ist_chronology_block()
        history_block = self._format_history_block(history)

        history_section = ""
        if history_block:
            history_section = f"\n\nRECENT CONVERSATION HISTORY:\n{history_block}"

        nasem_section = ""
        if nasem_context:
            nasem_section = (
                "\n\nSTRUCTURED NASEM 2021 RULES MATCH:\n"
                + json.dumps(nasem_context, default=str)
            )
            if "NASEM 2021 Dairy Nutrition" not in unique_sources:
                unique_sources.append("NASEM 2021 Dairy Nutrition")

        farm_db_section = ""
        if farm_context:
            farm_db_section = (
                "\n\nLIVE SUPABASE FARM DATABASE RECORDS:\n"
                + json.dumps(farm_context, default=str)
            )
            db_source_label = f"Supabase Farm DB ({farm_context.get('table', 'live')})"
            if db_source_label not in unique_sources:
                unique_sources.append(db_source_label)
            for rel_tbl in (farm_context.get("related_records") or {}).keys():
                rel_label = f"Supabase Farm DB ({rel_tbl})"
                if rel_label not in unique_sources:
                    unique_sources.append(rel_label)

        chimertech_section = ""
        if products_context:
            chimertech_section = (
                f"\n\nCHIMERTECH CATALOG MATCHES (Store URL: {CHIMERTECH_STORE_URL}):\n"
                + json.dumps(products_context, default=str)
            )
            chimertech_source_label = f"Chimertech Catalog ({CHIMERTECH_STORE_URL})"
            if chimertech_source_label not in unique_sources:
                unique_sources.append(chimertech_source_label)

        prompt = f"""
Evaluate the retrieved local evidence against the user's question and produce a strictly grounded, voice-friendly response that directly answers what the user asked.

DETECTED USER LANGUAGE: {detected_language}
(CRITICAL: Write TOPIC, CLINICAL_ANSWER, ACTION, PREVENTION, PREVENTION_TIPS, and SPOKEN_RESPONSE 100% in {detected_language}, even if all retrieved excerpts and database records below are in English.)

REAL-TIME CHRONOLOGY:
{chronology_block}{history_section}

USER QUESTION:
{query}

RETRIEVED LOCAL KNOWLEDGE-BASE EXCERPTS:
{context_str if context_str else "No PDF excerpts passed relevance filtering."}{nasem_section}{farm_db_section}{chimertech_section}

INSTRUCTIONS:
1. DIRECT ANSWER & LANGUAGE LOCK:
  - Always answer the user's exact question directly in {detected_language}. Never switch back to plain English unless {detected_language} is "English".
  - If {detected_language} is "Tanglish (Romanized Tamil)", write the entire answer naturally in Romanized Tamil (Tanglish) using the English alphabet (e.g., "Unga maadoda recent BCS score 3.34 ah irukku..."), NOT pure English and NOT Tamil script.
  - If {detected_language} is "Hinglish (Romanized Hindi)", write the entire answer naturally in Romanized Hindi (Hinglish) using the English alphabet (e.g., "Aapki gaay ka milk yield aur health status..."), NOT pure English and NOT Devanagari script.
  - Speak naturally and directly without adding "Sir" or honorifics.
  - If LIVE SUPABASE FARM DATABASE RECORDS shows `"found": false` for a queried cattle/cow ID or tag, set STATUS to SUFFICIENT (because the live database was checked) and state clearly in {detected_language} that no record was found for that ID or tag in the farm database, without inventing status details.
  - If LIVE SUPABASE FARM DATABASE RECORDS includes `related_records`, incorporate relevant details smoothly when answering about that animal.
2. EVIDENCE STATUS:
  - SUFFICIENT: The retrieved excerpts, structured NASEM rules, Chimertech catalog matches, or live farm database lookup directly answer the question (including confirming when a queried animal ID or tag does not exist in the DB).
  - PARTIAL: The retrieved context supports part of the question, while other requested parts are unsupported.
  - INSUFFICIENT: None of the retrieved context addresses the user's question.
3. SAFETY, MEDICINES & CHIMERTECH GROUNDING:
  - Use ONLY facts supported by the supplied excerpts, structured NASEM rules, Chimertech catalog matches, or live Supabase farm database records.
  - If the user asks for an individualized treatment plan, antibiotic selection, prescription medicine, or exact drug dosage for a specific animal, refuse the prescription in {detected_language} and instruct them to consult a qualified veterinarian immediately.
  - When mentioning Chimertech products/supplements/care items from CHIMERTECH CATALOG MATCHES, describe only their listed role/purpose and note following label instructions or a veterinarian's guidance, without inventing drug claims or dosages.
  - If STATUS is INSUFFICIENT, explain clearly in {detected_language} that verified information for this question is not available in the local knowledge base and advise consulting a qualified veterinarian; do NOT invent facts.
  - Make SPOKEN_RESPONSE natural, complete sentences suitable for text-to-speech (no raw JSON, no markdown tables, no asterisks, no bullet symbols, or citation codes).

Return EXACTLY these headings (keep the English heading labels, write all values in {detected_language}):

STATUS: SUFFICIENT, PARTIAL, or INSUFFICIENT
TOPIC: Short topic title in {detected_language}
CLINICAL_ANSWER: Direct factual answer in {detected_language}
ACTION: Immediate practical action in {detected_language}, or NONE
PREVENTION: Key preventive measure in {detected_language}, or NONE
PREVENTION_TIPS: Semicolon-separated short prevention tips in {detected_language}, or NONE
SPOKEN_RESPONSE: Direct, voice-ready answer to the user's question in {detected_language}
""".strip()

        try:
            response = self._call_llm_with_retry(client, RAGUL_SYNTHESIS_SYSTEM_PROMPT, prompt)

            finish_reason = ""
            if getattr(response, "choices", None):
                finish_reason = str(response.choices[0].finish_reason or "")
                raw = (getattr(response.choices[0].message, "content", None) or "").strip()
            else:
                raw = ""

            if finish_reason == "length" or not raw:
                _log_event(
                    "synthesis_incomplete_output",
                    finish_reason=finish_reason or "empty",
                    elapsed_ms=round((time.perf_counter() - t0) * 1000, 2),
                )
                return self._make_response(
                    topic="Veterinary Information",
                    clinical_answer=localized_fallback,
                    spoken_response=localized_fallback,
                    score=top_score,
                    sources=unique_sources,
                    grounded=False,
                )

            fields = [
                "STATUS",
                "TOPIC",
                "CLINICAL_ANSWER",
                "ACTION",
                "PREVENTION",
                "PREVENTION_TIPS",
                "SPOKEN_RESPONSE",
            ]

            status_raw = self._extract_field(raw, "STATUS", fields[1:]).upper()
            status_match = re.search(r"\b(SUFFICIENT|PARTIAL|INSUFFICIENT)\b", status_raw)
            status = status_match.group(1) if status_match else "INSUFFICIENT"

            topic = self._extract_field(raw, "TOPIC", fields[2:]) or "Veterinary Information"
            clinical_answer = self._extract_field(raw, "CLINICAL_ANSWER", fields[3:])
            action = self._extract_field(raw, "ACTION", fields[4:])
            prevention = self._extract_field(raw, "PREVENTION", fields[5:])
            tips_raw = self._extract_field(raw, "PREVENTION_TIPS", fields[6:])
            spoken_response = self._extract_field(raw, "SPOKEN_RESPONSE", [])

            if action.upper() == "NONE":
                action = ""
            if prevention.upper() == "NONE":
                prevention = ""

            prevention_tips: List[str] = []
            if tips_raw and tips_raw.upper() != "NONE":
                prevention_tips = [
                    tip.strip(" -•\t")
                    for tip in re.split(r"[;\n]+", tips_raw)
                    if tip.strip(" -•\t")
                ]

            grounded = status in ("SUFFICIENT", "PARTIAL") and bool(clinical_answer)

            if not grounded:
                if not clinical_answer:
                    clinical_answer = localized_fallback
                if not spoken_response:
                    spoken_response = clinical_answer

            _log_event(
                "synthesis_complete",
                detected_language=detected_language,
                status=status,
                grounded=grounded,
                sources_count=len(unique_sources) if grounded else 0,
                elapsed_ms=round((time.perf_counter() - t0) * 1000, 2),
            )

            return self._make_response(
                topic=topic,
                clinical_answer=clinical_answer,
                action=action,
                prevention=prevention,
                prevention_tips=prevention_tips,
                store_url=CHIMERTECH_STORE_URL,
                spoken_response=spoken_response or clinical_answer,
                score=top_score if grounded else 0.0,
                sources=unique_sources if grounded else [],
                grounded=grounded,
            )

        except Exception as e:
            _log_event(
                "synthesis_failed",
                error_type=type(e).__name__,
                elapsed_ms=round((time.perf_counter() - t0) * 1000, 2),
            )
            return self._make_response(
                topic="Veterinary Information",
                clinical_answer=localized_fallback,
                spoken_response=localized_fallback,
                score=0.0,
                sources=[],
                grounded=False,
            )

    # =====================================================
    # MAIN SEARCH INTERFACE (SYNC + ASYNC)
    # =====================================================

    def search(
        self,
        user_query: str,
        history: Optional[List[Dict[str, str]]] = None,
    ) -> Optional[Dict[str, Any]]:
        t0 = time.perf_counter()
        query = (user_query or "").strip()
        if not query:
            return None

        _log_event("search_start", query_len=len(query), has_history=bool(history))

        # -------------------------------------------------
        # 1. GUARDRAILS INPUT & DOMAIN GATE
        # -------------------------------------------------
        allowed, rejection_message = check_guardrails(query)
        if not allowed:
            _log_event(
                "guardrails_blocked",
                elapsed_ms=round((time.perf_counter() - t0) * 1000, 2),
            )
            msg = rejection_message or (
                "I can only assist with cattle health, dairy nutrition, and livestock management."
            )
            return self._make_response(
                topic="Guardrails",
                clinical_answer=msg,
                spoken_response=msg,
                score=0.0,
                sources=[],
                grounded=False,
            )

        # -------------------------------------------------
        # 2. FAST ROUTING / AI LANGUAGE DETECTION & LIVE DB
        # -------------------------------------------------
        intent = self._analyze_query_intent(query)
        detected_language = intent["detected_language"]
        english_query = intent["english_query"]
        needs_db = intent["needs_db"]

        nasem_rules_res: Optional[Dict[str, Any]] = None
        try:
            from app.knowledge.nasem_calculator import nasem_calculator

            candidate_rules = nasem_calculator.query_nasem_rules(english_query)
            if candidate_rules and candidate_rules.get("matches"):
                nasem_rules_res = candidate_rules
        except Exception as e:
            _log_event("nasem_lookup_skipped", error_type=type(e).__name__)

        farm_db_context = (
            self._retrieve_farm_db_context(english_query) if needs_db else None
        )

        # -------------------------------------------------
        # 3. HYBRID CLINICAL RETRIEVAL
        # -------------------------------------------------
        evidence_result = self._retrieve_clinical_evidence(english_query)
        evidence = evidence_result.get("results", [])

        if evidence_result.get("error") and not farm_db_context and not nasem_rules_res:
            fallback_msg = self._localized_fallback(detected_language)
            _log_event(
                "search_failed_retrieval",
                elapsed_ms=round((time.perf_counter() - t0) * 1000, 2),
            )
            return self._make_response(
                topic="Veterinary Information",
                clinical_answer=fallback_msg,
                spoken_response=fallback_msg,
                score=0.0,
                sources=[],
                grounded=False,
            )

        # -------------------------------------------------
        # 4. PRODUCT SCENARIO ROUTING (CHIMERTECH)
        # -------------------------------------------------
        scenario = self._find_best_scenario(english_query)
        products = self._get_relevant_products(english_query, scenario)

        # -------------------------------------------------
        # 5. SINGLE-CALL GROUNDED SYNTHESIS & SAFETY CHECK
        # -------------------------------------------------
        response = self._synthesize_grounded_response(
            query=query,
            detected_language=detected_language,
            evidence=evidence,
            nasem_context=nasem_rules_res,
            farm_context=farm_db_context,
            products_context=products,
            history=history,
        )

        response["detected_language"] = detected_language
        response["store_url"] = CHIMERTECH_STORE_URL

        if nasem_rules_res:
            response["rules_data"] = nasem_rules_res

        if farm_db_context:
            response["farm_db_data"] = farm_db_context

        if products:
            response["products"] = products

        if scenario and response.get("topic") == "Veterinary Information":
            response["topic"] = scenario.get("primary_disease", response["topic"])

        _log_event(
            "search_complete",
            detected_language=detected_language,
            grounded=bool(response.get("grounded")),
            products_count=len(response.get("products") or []),
            elapsed_ms=round((time.perf_counter() - t0) * 1000, 2),
        )
        return response

    async def asearch(
        self,
        user_query: str,
        history: Optional[List[Dict[str, str]]] = None,
    ) -> Optional[Dict[str, Any]]:
        return await asyncio.to_thread(self.search, user_query, history)

    # =====================================================
    # NASEM NUTRITION RETRIEVAL (COMPATIBILITY HELPER)
    # =====================================================

    def search_nasem_nutrition(self, query: str) -> Optional[Dict[str, Any]]:
        try:
            from app.knowledge.nasem_calculator import nasem_calculator

            rules_res = nasem_calculator.query_nasem_rules(query)
            if not rules_res or not rules_res.get("matches"):
                return None

            matches = rules_res.get("matches", [])
            matched_categories = [
                match.get("category", "")
                for match in matches
                if match.get("category")
            ]
            category_label = (
                ", ".join(matched_categories[:2])
                if matched_categories
                else "Dairy Feed & Nutrition"
            )

            overview = (
                "According to NASEM 2021 (Nutrient Requirements of Dairy Cattle, "
                "8th Revised Edition), dairy feeding, water intake, energy, and minerals "
                "must follow standardized scientific requirements and equations."
            )

            return self._make_response(
                topic=f"NASEM 2021 Dairy Nutrition ({category_label})",
                clinical_answer=overview,
                action="Apply the authoritative NASEM 2021 equations and calculated requirements.",
                prevention=(
                    "Prevent nutritional and metabolic disorders through balanced ration "
                    "formulation and appropriate inventory constraints."
                ),
                prevention_tips=[
                    "Use consistent calculated results across all farm nutrition modules.",
                    "Calculate water intake using the appropriate NASEM equation.",
                    "Calculate mineral supplementation based on nutritional deficits.",
                    "Evaluate the complete ration, not dry matter intake alone.",
                ],
                products=[],
                store_url=CHIMERTECH_STORE_URL,
                spoken_response=(
                    f"The query relates to NASEM 2021 dairy nutrition for {category_label}. "
                    "Requirements should be calculated using the appropriate standardized "
                    "equations and nutritional inputs."
                ),
                score=25.0,
                sources=["NASEM 2021 Dairy Nutrition"],
                grounded=True,
                extra={"rules_data": rules_res},
            )

        except Exception:
            _log_event("nasem_search_failed")
            return None


# =====================================================
# GLOBAL ENGINE INSTANCE
# =====================================================

rag_engine = VeterinaryRAGEngine(lazy_load=True)