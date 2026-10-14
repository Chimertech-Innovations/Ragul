import datetime
import json
import os
from sqlalchemy import select, delete
from .db import async_session, init_db
from .models import Farm, Cattle, MilkReading, HealthEvent, FeedRecord, FarmTask, FarmWorker, MonthlyMetric

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "knowledge_base", "green_valley_farm.json")

async def seed_initial_farm_data():
    await init_db()
    
    if not os.path.exists(DATA_PATH):
        return

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        gv_data = json.load(f)

    async with async_session() as session:
        # Wipe old demo entities to ensure clean sync with Green Valley Dairy Farm
        await session.execute(delete(FarmTask))
        await session.execute(delete(FeedRecord))
        await session.execute(delete(HealthEvent))
        await session.execute(delete(MilkReading))
        await session.execute(delete(Cattle))
        await session.execute(delete(FarmWorker))
        await session.execute(delete(MonthlyMetric))
        await session.execute(delete(Farm))
        await session.flush()

        # 1. Farm
        farm_info = gv_data.get("farm", {})
        farm = Farm(
            id=1,
            name=farm_info.get("farm_name", "Green Valley Dairy Farm"),
            owner_name="Ragul Farmer",
            location=farm_info.get("location", "Tamil Nadu, India"),
            total_cows=len(gv_data.get("cattle", []))
        )
        session.add(farm)

        # 2. Workers (W001 - W005)
        worker_map = {
            "W001": {"shift": "05:42 AM - 05:48 PM", "duties": "Farm gate entry & overall supervisor"},
            "W002": {"shift": "05:49 AM - 05:20 PM", "duties": "Morning & evening TMR and green fodder distribution"},
            "W003": {"shift": "05:36 AM - 04:45 PM", "duties": "Milking parlour machine operation & teat hygiene"},
            "W004": {"shift": "05:55 AM - 05:10 PM", "duties": "Pen 1 & Pen 2 dung scraping and bed sanitizing"},
            "W005": {"shift": "06:02 AM - 05:30 PM", "duties": "General farm maintenance & cleaning relief"}
        }
        
        workers = []
        for idx, w in enumerate(gv_data.get("workers", []), start=1):
            w_id = w.get("worker_id", f"W00{idx}")
            meta = worker_map.get(w_id, {})
            workers.append(
                FarmWorker(
                    id=idx,
                    name=w.get("name"),
                    role=w.get("role"),
                    phone=f"+91 98421 {idx}000{idx}",
                    shift=meta.get("shift", "06:00 AM - 05:00 PM"),
                    status="Active",
                    duties=meta.get("duties", "Farm operations")
                )
            )
        session.add_all(workers)

        # 3. Cattle (COW001 - COW010)
        cattle_objs = []
        for idx, c in enumerate(gv_data.get("cattle", []), start=1):
            c_id_str = c.get("cattle_id", f"COW{idx:03d}")
            lact_status = c.get("lactation_status", "Lactating")
            is_lactating = lact_status == "Lactating"
            
            cattle_objs.append(
                Cattle(
                    id=idx,
                    tag_number=c.get("rfid", f"RFID-{c_id_str}"),
                    name=f"{c.get('name')} ({c_id_str})",
                    breed="Jersey / HF Cross",
                    age_years=3.5 + (idx % 3),
                    lactation_stage=lact_status,
                    parity=1 if idx == 8 else (2 if idx <= 5 else 3),
                    daily_average_milk=18.5 if is_lactating else 0.0,
                    health_status="Under Observation" if c_id_str in ["COW003", "COW005", "COW002"] else "Healthy",
                    mastitis_risk="High" if c_id_str == "COW003" else "Low",
                    affected_quarter="Left Rear Quarter" if c_id_str == "COW003" else None,
                    in_estrus=True if c_id_str in ["COW002", "COW005"] else False,
                    days_in_milk=120 if is_lactating else 0
                )
            )
        session.add_all(cattle_objs)
        await session.flush()

        # 4. Monthly Metrics (September 2026)
        ms = gv_data.get("monthly_summary", {})
        session.add(
            MonthlyMetric(
                id=1,
                month_year="September 2026",
                total_milk_produced_litres=ms.get("total_milk_litres", 3900.5),
                avg_daily_yield_litres=ms.get("average_daily_milk_litres", 130.0),
                total_feed_consumed_kg=7350.0,
                total_revenue_inr=156000.0,
                veterinary_expenses_inr=4500.0,
                lactating_cows_count=7,
                ai_inseminations_performed=2,
                calves_born=1
            )
        )

        await session.commit()

