import os
import asyncio
import logging
import asyncpg
from typing import Optional, List, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

# Search for .env in current directory, backend/.env, or parent directory
for env_candidate in [Path.cwd() / ".env", Path.cwd() / "backend" / ".env", Path(__file__).resolve().parent.parent.parent / ".env"]:
    if env_candidate.exists():
        load_dotenv(env_candidate)
        break
else:
    load_dotenv()

logger = logging.getLogger("ragul_supabase_client")

def get_clean_database_url() -> str:
    """
    Returns an IPv4-compatible PostgreSQL connection string.
    Supabase's direct endpoint ('db.<project_ref>.supabase.co:5432') resolves strictly to IPv6.
    Render and standard cloud containers are IPv4-only, causing '[Errno 101] Network is unreachable'.
    This automatically transforms the URL to Supabase's IPv4 connection pooler.
    """
    dsn = os.getenv("DATABASE_URL", "").strip()
    if "db.gzklovtyqonpmwwdhrpx.supabase.co" in dsn:
        logger.info("[SupabaseClient] Translating direct IPv6 host to IPv4 Supabase pooler for cloud host compatibility...")
        dsn = dsn.replace("db.gzklovtyqonpmwwdhrpx.supabase.co", "aws-0-ap-northeast-1.pooler.supabase.com")
        if "shanjith_intern2026:" in dsn:
            dsn = dsn.replace("shanjith_intern2026:", "shanjith_intern2026.gzklovtyqonpmwwdhrpx:")
    return dsn

class SupabasePoolManager:
    _pool: Optional[asyncpg.Pool] = None
    _loop: Optional[asyncio.AbstractEventLoop] = None

    @classmethod
    async def get_pool(cls) -> asyncpg.Pool:
        current_loop = asyncio.get_running_loop()
        if cls._pool is None or cls._loop != current_loop:
            dsn = get_clean_database_url()
            if not dsn:
                raise ValueError("DATABASE_URL is not set in environment or .env")
            try:
                cls._pool = await asyncpg.create_pool(
                    dsn=dsn,
                    min_size=2,
                    max_size=10,
                    timeout=10,
                    command_timeout=10
                )
                cls._loop = current_loop
                logger.info("[SupabaseClient] Connected successfully to Supabase PostgreSQL pool.")
            except Exception as e:
                logger.error(f"[SupabaseClient] Error connecting to Supabase pool: {e}")
                raise e
        return cls._pool

    @classmethod
    async def fetch_all(cls, query: str, *args) -> List[Dict[str, Any]]:
        """Executes a SELECT query and returns rows as dictionaries with auto-reconnect."""
        for attempt in range(2):
            try:
                pool = await cls.get_pool()
                async with pool.acquire() as conn:
                    records = await conn.fetch(query, *args)
                    return [dict(r) for r in records]
            except Exception as e:
                if attempt == 0:
                    cls._pool = None
                    await asyncio.sleep(0.5)
                else:
                    raise e
        return []

    @classmethod
    async def fetch_one(cls, query: str, *args) -> Optional[Dict[str, Any]]:
        """Executes a query and returns single row as dictionary with auto-reconnect."""
        for attempt in range(2):
            try:
                pool = await cls.get_pool()
                async with pool.acquire() as conn:
                    record = await conn.fetchrow(query, *args)
                    return dict(record) if record else None
            except Exception as e:
                if attempt == 0:
                    cls._pool = None
                    await asyncio.sleep(0.5)
                else:
                    raise e
        return None

    @classmethod
    async def fetch_val(cls, query: str, *args) -> Any:
        """Executes a query and returns a single value with auto-reconnect."""
        for attempt in range(2):
            try:
                pool = await cls.get_pool()
                async with pool.acquire() as conn:
                    return await conn.fetchval(query, *args)
            except Exception as e:
                if attempt == 0:
                    cls._pool = None
                    await asyncio.sleep(0.5)
                else:
                    raise e
        return None

    @classmethod
    async def execute(cls, query: str, *args) -> str:
        """Executes an INSERT, UPDATE or DELETE query."""
        pool = await cls.get_pool()
        async with pool.acquire() as conn:
            return await conn.execute(query, *args)

    @classmethod
    async def close(cls):
        if cls._pool:
            try:
                await cls._pool.close()
            except Exception:
                pass
            cls._pool = None
            cls._loop = None
            logger.info("[SupabaseClient] Supabase pool closed.")

supabase_db = SupabasePoolManager
