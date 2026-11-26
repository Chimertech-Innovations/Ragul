import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env", override=True)


async def main():
    from app.database.supabase_client import supabase_db
    from app.tools.farm_tools import deduct_mooposhaq_for_low_bcs, _resolve_farm_id
    from app.llm.router import tool_router

    if hasattr(supabase_db, "connect"):
        await supabase_db.connect()

    try:
        role_row = await supabase_db.fetch_one("SELECT current_user, session_user")
        print("DB User:", dict(role_row) if role_row else "unknown")

        for tbl in ("inventory_items", "bcs_tests", "bcs_recommendations", "cattles"):
            priv = await supabase_db.fetch_one(
                """
                SELECT
                    has_table_privilege(current_user, $1, 'SELECT') AS can_select,
                    has_table_privilege(current_user, $1, 'INSERT') AS can_insert,
                    has_table_privilege(current_user, $1, 'UPDATE') AS can_update
                """,
                f"public.{tbl}",
            )
            print(f"Privileges public.{tbl}:", dict(priv) if priv else {})

        f_id = await _resolve_farm_id()
        print("Resolved farm_id:", f_id)

        cow = await supabase_db.fetch_one(
            "SELECT cattle_tag_no, id FROM public.cattles WHERE ($1 = '' OR farm_id::text = $1) LIMIT 1",
            f_id,
        )
        cow_id = str(cow["cattle_tag_no"] or cow["id"]) if cow else "1004"

        r_high = await deduct_mooposhaq_for_low_bcs(cattle_id=cow_id, bcs_score=3.2, deduction_kg=2.0, farm_id=f_id or None)
        print("1. Normal BCS (>= 3.0):", r_high.get("triggered"), "|", r_high.get("message"))

        r_low = await deduct_mooposhaq_for_low_bcs(cattle_id=cow_id, bcs_score=2.4, deduction_kg=2.0, farm_id=f_id or None)
        print("2. Low BCS (< 3.0):", r_low.get("status"), "| restock_alert:", r_low.get("restock_alert"), "|", r_low.get("message"))

        reply, meta = await tool_router.process_user_message(
            f"Cow {cow_id} has low BCS, deduct 2 kg MooPoshaq from inventory",
            history=[],
            farm_id=f_id or None,
        )
        print("3. Router tool:", meta.get("tool"), "| executed:", meta.get("executed"))
        print("   Reply:", reply)
    finally:
        if hasattr(supabase_db, "disconnect"):
            await supabase_db.disconnect()
        elif hasattr(supabase_db, "close"):
            await supabase_db.close()


if __name__ == "__main__":
    asyncio.run(main())
