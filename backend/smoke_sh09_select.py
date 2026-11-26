import asyncio
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env", override=True)


async def main():
    from app.database.supabase_client import supabase_db
    from app.tools.farm_tools import _resolve_farm_id, get_warehouse_inventory

    if hasattr(supabase_db, "connect"):
        await supabase_db.connect()

    try:
        f_id = await _resolve_farm_id()
        print("Resolved farm_id:", f_id)

        cows = await supabase_db.fetch_all(
            """
            SELECT id, farm_id, cattle_tag_no, name
            FROM public.cattles
            WHERE ($1 = '' OR farm_id::text = $1)
            ORDER BY id ASC
            LIMIT 10
            """,
            f_id,
        )
        print("\n--- Sample Cattle Rows ---")
        for c in cows:
            print(dict(c))

        moo_rows = await supabase_db.fetch_all(
            """
            SELECT id, farm_id, item_name, quantity, unit, low_stock_level, last_updated
            FROM public.inventory_items
            WHERE ($1 = '' OR farm_id::text = $1)
              AND item_name ILIKE '%MooPoshaq%'
            ORDER BY id ASC
            """,
            f_id,
        )
        print("\n--- MooPoshaq Inventory Rows (SELECT only) ---")
        for m in moo_rows:
            d = dict(m)
            qty = float(d.get("quantity") or 0.0)
            low = float(d.get("low_stock_level") or 0.0)
            sim_rem = qty - 2.0
            d["simulated_after_2kg_deduction"] = sim_rem
            d["simulated_restock_alert"] = sim_rem <= low
            print(d)

        inv_all = await get_warehouse_inventory(farm_id=f_id or None)
        print("\n--- Warehouse Inventory Summary ---")
        print("Total items:", inv_all.get("total_items"))
        for item in inv_all.get("items", []):
            print(
                f"  - {item.get('item_name')}: qty={item.get('quantity')} {item.get('unit')}, "
                f"low_stock_level={item.get('low_stock_level')}, alert={item.get('low_stock_alert')}"
            )
    finally:
        if hasattr(supabase_db, "disconnect"):
            await supabase_db.disconnect()
        elif hasattr(supabase_db, "close"):
            await supabase_db.close()


if __name__ == "__main__":
    asyncio.run(main())
