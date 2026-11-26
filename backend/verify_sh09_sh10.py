import asyncio
import json
import os
import warnings
from pathlib import Path
import asyncpg
from dotenv import load_dotenv

os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
warnings.filterwarnings("ignore")

load_dotenv(Path(".env"), override=True)

from app.database.supabase_client import supabase_db
from app.llm.router import tool_router


async def main() -> None:
    farm_id = "45"
    db_url = os.environ["DATABASE_URL"]

    conn = await asyncpg.connect(db_url, statement_cache_size=0)
    try:
        initial_row = await conn.fetchrow(
            """
            SELECT id, farm_id, item_name, quantity, unit, low_stock_level
            FROM public.inventory_items
            WHERE id = 23 AND farm_id = $1
            """,
            int(farm_id),
        )
        initial_qty = float(initial_row["quantity"])

        print("=" * 72)
        print("SH-09 & SH-10 END-TO-END VERIFICATION REPORT (FARM_ID = 45)")
        print("=" * 72)
        print(
            f"[BASELINE] {initial_row['item_name']}: "
            f"{initial_qty:.2f} {initial_row['unit']} "
            f"(Low-stock threshold: {float(initial_row['low_stock_level']):.2f} {initial_row['unit']})\n"
        )

        # 1. SH-09 Trigger Case (Cow 1004, BCS 2.40 < 3.0)
        q_sh09_trigger = (
            "Cow 1004 has a low BCS score. Deduct 2 kg of MooPoshaq from inventory and log a recommendation."
        )
        reply_1, meta_1 = await tool_router.process_user_message(
            user_text=q_sh09_trigger, history=[], farm_id=farm_id
        )
        res_1 = meta_1.get("result", {})
        print("--- [TEST 1] SH-09 Auto-Inventory Deduction (Low BCS < 3.0) ---")
        print(f"Prompt   : {q_sh09_trigger}")
        print(f"Tool     : {meta_1.get('tool')} (executed={meta_1.get('executed')})")
        print(
            f"DB Result: status={res_1.get('status')} | cow={res_1.get('cow_name')} (#{res_1.get('cattle_id')}) | "
            f"BCS={res_1.get('bcs_score')} | stock={res_1.get('previous_qty')} -> {res_1.get('remaining_qty')} {res_1.get('unit')} | "
            f"rec_id={res_1.get('recommendation_id')} | restock_alert={res_1.get('restock_alert')}"
        )
        print(f"Response : {reply_1}\n")

        # 2. SH-09 Skip Guard Case (Cow 1005, BCS 3.20 >= 3.0)
        q_sh09_guard = "Check Cow 1005's BCS and deduct MooPoshaq if her BCS is below 3.0."
        reply_2, meta_2 = await tool_router.process_user_message(
            user_text=q_sh09_guard, history=[], farm_id=farm_id
        )
        res_2 = meta_2.get("result", {})
        print("--- [TEST 2] SH-09 Normal-BCS Guard (BCS >= 3.0) ---")
        print(f"Prompt   : {q_sh09_guard}")
        print(f"Tool     : {meta_2.get('tool')} (executed={meta_2.get('executed')})")
        print(
            f"DB Result: triggered={res_2.get('triggered')} | cow={res_2.get('cow_name')} | "
            f"BCS={res_2.get('bcs_score')}"
        )
        print(f"Response : {reply_2}\n")

        # 3. SH-10 NZ / DairyNZ Compliance Audit
        q_sh10_nz = (
            "Run a DairyNZ BCS compliance audit for our herd and list any cows breaching welfare thresholds."
        )
        reply_3, meta_3 = await tool_router.process_user_message(
            user_text=q_sh10_nz, history=[], farm_id=farm_id
        )
        res_3 = meta_3.get("result", {})
        print("--- [TEST 3] SH-10 Compliance Audit (New Zealand / DairyNZ) ---")
        print(f"Prompt   : {q_sh10_nz}")
        print(f"Tool     : {meta_3.get('tool')} (executed={meta_3.get('executed')})")
        print(
            f"Summary  : audited={res_3.get('total_cows_audited')} | compliant={res_3.get('compliant_count')} | "
            f"statutory_breaches={res_3.get('statutory_breach_count')} | warnings={res_3.get('management_warning_count')}"
        )
        for b in res_3.get("breaches_and_alerts", []):
            print(
                f"  - Tag #{b['cattle_id']} ({b['name']}, {b['breed']}): "
                f"BCS={b['latest_bcs']} | rule={b['rule_id']} | severity={b['severity']}"
            )
        print()

        # 4. SH-10 AUS Welfare Audit
        q_sh10_aus = "Run an Australian welfare BCS compliance audit for our herd."
        reply_4, meta_4 = await tool_router.process_user_message(
            user_text=q_sh10_aus, history=[], farm_id=farm_id
        )
        res_4 = meta_4.get("result", {})
        print("--- [TEST 4] SH-10 Compliance Audit (Australia Welfare Rules) ---")
        print(f"Prompt   : {q_sh10_aus}")
        print(f"Tool     : {meta_4.get('tool')} (executed={meta_4.get('executed')})")
        print(
            f"Summary  : audited={res_4.get('total_cows_audited')} | compliant={res_4.get('compliant_count')} | "
            f"statutory_breaches={res_4.get('statutory_breach_count')} | warnings={res_4.get('management_warning_count')}"
        )
        for b in res_4.get("breaches_and_alerts", []):
            print(
                f"  - Tag #{b['cattle_id']} ({b['name']}, {b['breed']}): "
                f"BCS={b['latest_bcs']} | rule={b['rule_id']} | severity={b['severity']}"
            )

        # Restore baseline quantity cleanly
        restored = await conn.fetchrow(
            """
            UPDATE public.inventory_items
            SET quantity = $1, last_updated = NOW()
            WHERE id = 23 AND farm_id = $2
            RETURNING item_name, quantity, unit
            """,
            initial_qty,
            int(farm_id),
        )
        print("\n" + "=" * 72)
        print(
            f"[CLEANUP] Restored {restored['item_name']} to "
            f"{float(restored['quantity']):.2f} {restored['unit']}"
        )
        print("=" * 72)
    finally:
        await conn.close()
        if getattr(supabase_db, "_pool", None):
            await supabase_db._pool.close()


if __name__ == "__main__":
    asyncio.run(main())
