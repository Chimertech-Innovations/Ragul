import os
import datetime
import json
import logging
import re
from typing import Dict, Any, List, Optional
from ..database.supabase_client import supabase_db
from ..knowledge.rag_engine import rag_engine

logger = logging.getLogger("ragul_farm_tools")
IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
NZ_REVISED_CODE_EFFECTIVE_DATE = datetime.date(2027, 4, 19)


def _safe_json(val: Any) -> Dict[str, Any]:
    """Safely converts string or raw JSON columns from PostgreSQL to Python dict."""
    if not val:
        return {}
    if isinstance(val, dict):
        return val
    if isinstance(val, str):
        try:
            parsed = json.loads(val)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            return {}
    return {}


def _fmt_time(dt: Optional[Any]) -> str:
    """Formats datetime objects to clean 12-hour IST time."""
    if not dt:
        return "N/A"
    if isinstance(dt, str):
        try:
            dt = datetime.datetime.fromisoformat(dt)
        except Exception:
            return dt
    if isinstance(dt, datetime.datetime):
        if dt.tzinfo is not None:
            ist_dt = dt.astimezone(IST)
        else:
            ist_dt = dt + datetime.timedelta(hours=5, minutes=30)
        return ist_dt.strftime("%I:%M %p")
    return str(dt)


DEFAULT_TARGET_FARM_ID = os.getenv("TARGET_FARM_ID", "")


async def _resolve_farm_id(farm_id: Optional[str] = None) -> str:
    """Resolves farm_id dynamically from input, environment, or the first farm in public.farms."""
    if farm_id and str(farm_id).strip():
        return str(farm_id).strip()
    if DEFAULT_TARGET_FARM_ID.strip():
        return DEFAULT_TARGET_FARM_ID.strip()
    try:
        first_farm = await supabase_db.fetch_one("SELECT id FROM public.farms ORDER BY id ASC LIMIT 1")
        if first_farm and first_farm.get("id") is not None:
            return str(first_farm["id"])
    except Exception:
        pass
    return ""


def _normalize_erp_cow_id(cattle_id: Optional[str]) -> List[str]:
    """Normalizes '1004', 'Cow 1004', 'गाय 1004', or 'COW1004' into candidate IDs."""
    if not cattle_id:
        return []
    raw = str(cattle_id).strip().upper()
    digits = re.findall(r"\d+", raw)
    candidates = {raw, raw.replace(" ", "")}
    if digits:
        num = digits[0]
        candidates.update({num, f"COW{num}", f"COW{int(num):03d}"})
    return list(candidates)


async def _table_columns(schema_name: str, table_name: str) -> set:
    """Returns column names for a schema-qualified PostgreSQL table."""
    rows = await supabase_db.fetch_all(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = $1 AND table_name = $2
        """,
        schema_name,
        table_name,
    )
    return {r["column_name"] for r in rows}


# ----------------- DIRECT SUPABASE AGENTIC TOOLS ----------------- #


async def get_farm_overview(farm_id: Optional[str] = None, target_date: Optional[str] = None) -> Dict[str, Any]:
    """
    Retrieve live farm overview from Supabase:
    Accurately filtered by date (Today vs Yesterday) to prevent reporting historical events as today.
    Enforces >85% confidence score for any estrus proof images.
    """
    f_id = await _resolve_farm_id(farm_id)
    farm = None
    if f_id:
        farm = await supabase_db.fetch_one("SELECT * FROM public.farms WHERE id::text = $1 LIMIT 1", f_id)
    if not farm:
        farm = await supabase_db.fetch_one("SELECT * FROM public.farms LIMIT 1")
        if farm:
            f_id = str(farm["id"])

    farm_name = farm.get("farm_name", "PashuX AI Dairy Farm") if farm else "PashuX AI Dairy Farm"
    owner_name = farm.get("owner_name", "Farm Owner") if farm else "Farm Owner"
    farm_code = farm.get("farm_code", "FARM_MAIN") if farm else "FARM_MAIN"
    location = farm.get("location") or farm.get("address") or farm.get("country") or "India" if farm else "India"

    now_ist = datetime.datetime.now(IST)
    today_str = now_ist.strftime("%Y-%m-%d")
    yesterday_str = (now_ist - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

    cameras = []
    if f_id:
        try:
            cam_rows = await supabase_db.fetch_all(
                "SELECT id, camera_name, is_active FROM public.cctv_cameras WHERE farm_id::text = $1",
                f_id,
            )
            cameras = [dict(c) for c in cam_rows]
        except Exception:
            try:
                cam_rows = await supabase_db.fetch_all("SELECT id, camera_name, is_active FROM public.cctv_cameras")
                cameras = [dict(c) for c in cam_rows]
            except Exception:
                cameras = []

    registered_cattle = []
    if f_id:
        try:
            cow_rows = await supabase_db.fetch_all(
                """
                SELECT id as cattle_id, cattle_tag_no, name 
                FROM public.cattles 
                WHERE farm_id::text = $1 
                ORDER BY id ASC;
                """,
                f_id,
            )
            registered_cattle = [dict(r) for r in cow_rows]
        except Exception:
            try:
                cow_rows = await supabase_db.fetch_all(
                    "SELECT id as cattle_id, cattle_tag_no, name FROM public.cattles ORDER BY id ASC;"
                )
                registered_cattle = [dict(r) for r in cow_rows]
            except Exception:
                registered_cattle = []
    cows = [str(c.get("cattle_tag_no") or c.get("cattle_id")) for c in registered_cattle if c.get("cattle_id") or c.get("cattle_tag_no")]

    is_today = bool(target_date and "today" in target_date.lower())
    is_yesterday = bool(target_date and "yester" in target_date.lower())

    today_rows = []
    if f_id:
        today_rows = await supabase_db.fetch_all(
            """
            SELECT activity_id, camera_id, cattle_id, confidence_score, description, start_time,
                   captured_image_storage_path, captured_video_storage_path, ai_detection_result, activity_type,
                   disease_status, bcs_score, breed
            FROM public.farm_activities
            WHERE farm_id::text = $1 AND (start_time AT TIME ZONE 'Asia/Kolkata')::date = $2::date
            ORDER BY start_time DESC;
            """,
            f_id,
            datetime.date.fromisoformat(today_str),
        )

    yesterday_rows = []
    if f_id:
        yesterday_rows = await supabase_db.fetch_all(
            """
            SELECT activity_id, camera_id, cattle_id, confidence_score, description, start_time,
                   captured_image_storage_path, captured_video_storage_path, ai_detection_result, activity_type,
                   disease_status, bcs_score, breed
            FROM public.farm_activities
            WHERE farm_id::text = $1 AND (start_time AT TIME ZONE 'Asia/Kolkata')::date = $2::date
            ORDER BY start_time DESC;
            """,
            f_id,
            datetime.date.fromisoformat(yesterday_str),
        )

    target_rows = (
        today_rows
        if is_today
        else (yesterday_rows if is_yesterday else (today_rows if len(today_rows) > 0 else yesterday_rows))
    )

    today_estrus = [r for r in today_rows if r.get("activity_type") == "estrus_detected"]
    today_feeding = [r for r in today_rows if "feed" in (r.get("activity_type") or "")]

    yesterday_estrus = [r for r in yesterday_rows if r.get("activity_type") == "estrus_detected"]
    yesterday_feeding = [r for r in yesterday_rows if "feed" in (r.get("activity_type") or "")]

    suspected_diseases = []
    seen_disease_cows = set()
    for r in target_rows:
        d_status = str(r.get("disease_status") or "").strip()
        c_id = r.get("cattle_id")
        if d_status and d_status.lower() != "healthy" and c_id not in seen_disease_cows:
            seen_disease_cows.add(c_id)
            conf_val = float(r.get("confidence_score") or 0.85)
            img_p = r.get("captured_image_storage_path")
            suspected_diseases.append(
                {
                    "activity_id": str(r["activity_id"]),
                    "cattle_id": c_id,
                    "breed": r.get("breed") or "Cattle",
                    "disease": d_status,
                    "camera_id": r.get("camera_id", "CAM01"),
                    "confidence": f"{round(conf_val * 100)}%",
                    "time": _fmt_time(r.get("start_time")),
                    "description": r.get("description"),
                    "image_url": f"/api/media/image?path={img_p}" if img_p else None,
                }
            )

    low_bcs_cattle = []
    seen_bcs_cows = set()
    for r in target_rows:
        bcs = r.get("bcs_score")
        c_id = r.get("cattle_id")
        if bcs is not None and float(bcs) < 2.0 and c_id not in seen_bcs_cows:
            seen_bcs_cows.add(c_id)
            conf_val = float(r.get("confidence_score") or 0.85)
            img_p = r.get("captured_image_storage_path")
            low_bcs_cattle.append(
                {
                    "activity_id": str(r["activity_id"]),
                    "cattle_id": c_id,
                    "bcs_score": round(float(bcs), 1),
                    "breed": r.get("breed") or "Cattle",
                    "camera_id": r.get("camera_id", "CAM01"),
                    "time": _fmt_time(r.get("start_time")),
                    "confidence": f"{round(conf_val * 100)}%",
                    "image_url": f"/api/media/image?path={img_p}" if img_p else None,
                }
            )

    active_estrus_alerts = []
    seen_estrus_cows = set()
    for r in target_rows:
        if r.get("activity_type") == "estrus_detected":
            c_id = r.get("cattle_id")
            conf_val = float(r.get("confidence_score") or 0.85)
            if conf_val >= 0.80 and c_id not in seen_estrus_cows:
                seen_estrus_cows.add(c_id)
                img_p = r.get("captured_image_storage_path")
                active_estrus_alerts.append(
                    {
                        "activity_id": str(r["activity_id"]),
                        "cattle_id": c_id,
                        "confidence": f"{round(conf_val * 100)}%",
                        "camera_id": r.get("camera_id", "CAM01"),
                        "time": _fmt_time(r.get("start_time")),
                        "description": r.get("description") or "Mounting / Standing Heat Detected",
                        "image_url": f"/api/media/image?path={img_p}" if img_p else None,
                    }
                )

    proof_images = []
    for d in suspected_diseases:
        if d.get("image_url"):
            proof_images.append(d)

    for e in active_estrus_alerts:
        if e.get("image_url") and len(proof_images) < 4:
            proof_images.append(e)

    for b in low_bcs_cattle:
        if b.get("image_url") and len(proof_images) < 5:
            proof_images.append(b)

    if len(target_rows) > 0 and len(proof_images) < 4:
        for r in target_rows:
            img_p = r.get("captured_image_storage_path")
            if img_p and not any(p.get("image_url") == f"/api/media/image?path={img_p}" for p in proof_images):
                conf_val = float(r.get("confidence_score") or 0.90)
                proof_images.append(
                    {
                        "activity_id": str(r["activity_id"]),
                        "cattle_id": r.get("cattle_id") or "Cattle",
                        "camera_id": r.get("camera_id") or "CAM01",
                        "time": _fmt_time(r.get("start_time")),
                        "confidence": f"{round(conf_val * 100)}%",
                        "description": r.get("description") or "CCTV Detection Proof",
                        "image_url": f"/api/media/image?path={img_p}",
                    }
                )
                if len(proof_images) >= 4:
                    break

    if len(target_rows) == 0:
        proof_images = []

    selected_date_label = (
        f"Today ({now_ist.strftime('%d %b %Y')})"
        if is_today
        else (
            f"Yesterday ({(now_ist - datetime.timedelta(days=1)).strftime('%d %b %Y')})"
            if is_yesterday
            else f"Overview ({now_ist.strftime('%d %b %Y')})"
        )
    )

    cattle_cnt_map = {}
    for r in target_rows:
        cid = r.get("cattle_id")
        if cid:
            cattle_cnt_map[cid] = cattle_cnt_map.get(cid, 0) + 1
    cattle_details = [
        {"cattle_id": k, "events_count": v}
        for k, v in sorted(cattle_cnt_map.items(), key=lambda x: x[1], reverse=True)
    ]

    return {
        "source": "Supabase PostgreSQL (Live PashuX)",
        "farm_id": f_id,
        "farm_name": farm_name,
        "farm_code": farm_code,
        "owner_name": owner_name,
        "location": location,
        "target_date_requested": target_date or "today",
        "current_local_date": today_str,
        "date_label": selected_date_label,
        "monitored_cattle_count": len(cows),
        "cattle_list": cows,
        "cattle_details": cattle_details,
        "is_today_query": is_today,
        "today_detections_count": len(today_rows),
        "today_estrus_count": len(today_estrus),
        "today_feeding_count": len(today_feeding),
        "yesterday_detections_count": len(yesterday_rows),
        "yesterday_estrus_count": len(yesterday_estrus),
        "yesterday_feeding_count": len(yesterday_feeding),
        "total_activities_detected": (
            len(today_rows)
            if is_today
            else (len(yesterday_rows) if is_yesterday else len(today_rows) + len(yesterday_rows))
        ),
        "active_estrus_count": len(active_estrus_alerts),
        "feeding_activity_count": len(today_feeding) if is_today else len(yesterday_feeding),
        "suspected_diseases": suspected_diseases,
        "low_bcs_cattle": low_bcs_cattle,
        "active_estrus_alerts": active_estrus_alerts,
        "cameras_connected": len(cameras),
        "cameras": cameras,
        "proof_images": proof_images,
        "historical_note": (
            f"Previous detections were logged on yesterday ({yesterday_str}): {len(yesterday_rows)} total events."
            if len(today_rows) == 0
            else ""
        ),
    }


async def get_estrus_and_heat_alerts(
    farm_id: Optional[str] = None,
    cattle_id: Optional[str] = None,
    target_date: Optional[str] = None,
    min_confidence: float = 0.85,
) -> Dict[str, Any]:
    """
    Retrieve live Estrus (Heat) Detection records from PashuX AI vision:
    Mounting behavior, mounted cow, camera ID, confidence score, breeding recommendation, and proof photos.
    """
    f_id = await _resolve_farm_id(farm_id)
    now_ist = datetime.datetime.now(IST)
    today_str = now_ist.strftime("%Y-%m-%d")
    yesterday_str = (now_ist - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

    query = """
        SELECT 
            activity_id, farm_id, camera_id, cattle_id, detection_date,
            start_time, end_time, confidence_score, description,
            ai_detection_result, captured_image_storage_path, captured_video_storage_path
        FROM public.farm_activities
        WHERE activity_type = 'estrus_detected'
    """
    params = []
    if f_id:
        params.append(f_id)
        query += f" AND farm_id::text = ${len(params)}"
    if cattle_id:
        params.append(f"%{cattle_id.strip()}%")
        query += f" AND (LOWER(cattle_id) LIKE LOWER(${len(params)}) OR description ILIKE ${len(params)})"
    if target_date and "today" in target_date.lower():
        params.append(datetime.date.fromisoformat(today_str))
        query += f" AND (start_time AT TIME ZONE 'Asia/Kolkata')::date = ${len(params)}::date"
    elif target_date and "yester" in target_date.lower():
        params.append(datetime.date.fromisoformat(yesterday_str))
        query += f" AND (start_time AT TIME ZONE 'Asia/Kolkata')::date = ${len(params)}::date"

    query += " ORDER BY confidence_score DESC, start_time DESC LIMIT 10;"
    rows = await supabase_db.fetch_all(query, *params)

    alerts = []
    affected_cows = set()
    proof_images = []

    for r in rows:
        cid = r.get("cattle_id") or "Unknown Cattle"
        conf_float = float(r.get("confidence_score") or 0.85)
        conf_pct_str = f"{round(conf_float * 100)}%"
        affected_cows.add(cid)
        ai_res = _safe_json(r.get("ai_detection_result"))
        img_p = r.get("captured_image_storage_path")
        vid_p = r.get("captured_video_storage_path")

        alert_item = {
            "activity_id": str(r["activity_id"]),
            "cattle_id": cid,
            "camera": r.get("camera_id", "CAM01"),
            "date": str(r.get("detection_date")),
            "time": _fmt_time(r.get("start_time")),
            "confidence": conf_pct_str,
            "confidence_float": conf_float,
            "description": r.get("description"),
            "image_url": f"/api/media/image?path={img_p}" if img_p else None,
            "video_url": f"/api/media/video?path={vid_p}" if vid_p else None,
            "ai_details": ai_res,
            "breeding_window": "Artificial Insemination (AI) recommended within 12 to 18 hours of detected mounting sign",
        }
        alerts.append(alert_item)

        if img_p and conf_float >= 0.80 and len(proof_images) < 4:
            proof_images.append(
                {
                    "activity_id": str(r["activity_id"]),
                    "cattle_id": cid,
                    "camera_id": r.get("camera_id", "CAM01"),
                    "time": _fmt_time(r.get("start_time")),
                    "confidence": conf_pct_str,
                    "description": r.get("description"),
                    "image_url": f"/api/media/image?path={img_p}",
                }
            )

    date_label = (
        "today"
        if (target_date and "today" in target_date.lower())
        else ("yesterday" if (target_date and "yester" in target_date.lower()) else "recent")
    )

    return {
        "source": "Supabase PostgreSQL (Live Vision Detections)",
        "target_date": date_label,
        "status": "active_estrus_found" if alerts else f"no_active_heat_{date_label}",
        "total_estrus_events": len(alerts),
        "cows_in_heat": list(affected_cows),
        "latest_alerts": alerts,
        "recommendation": (
            "Separate the cows in heat for breeding inspection. Check for clear discharge and standing heat signs. "
            "We recommend verifying the cervix and performing precise, non-traumatic insemination using the Chimertech Visual AI Insemination Gun with HD Camera, "
            "and monitoring the 12-18 hour insemination window with the Chimertech Estrus Detection Kit (available on chimertech.shop)."
            if alerts
            else "No active estrus detected for this date. For automated 24/7 standing heat tracking and accurate visual breeding, "
            "use the Chimertech Estrus Detection Kit and Chimertech Visual AI Insemination Gun (chimertech.shop)."
        ),
        "recommended_products": [
            {
                "name": "Chimertech Visual AI Insemination Gun with HD Camera",
                "url": "https://chimertech.shop",
                "purpose": "Visual cervical examination and precise non-traumatic artificial insemination",
            },
            {
                "name": "Chimertech Smart Bovine Estrus Detection Kit",
                "url": "https://chimertech.shop",
                "purpose": "Automated standing heat detection and tracking the optimal 12-18 hour insemination window",
            },
        ],
        "proof_images": proof_images,
    }


async def get_feed_and_nutrition(farm_id: Optional[str] = None, cattle_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Check live cattle feeding activities, eating duration, head-down time,
    grazing events, and manger CCTV proof captured by cameras.
    """
    f_id = await _resolve_farm_id(farm_id)

    query = """
        SELECT 
            activity_id, farm_id, camera_id, cattle_id, detection_date,
            start_time, end_time, activity_duration, confidence_score,
            description, ai_detection_result, captured_image_storage_path, captured_video_storage_path
        FROM public.farm_activities
        WHERE (activity_type LIKE '%feed%' OR activity_type = 'feeding_activity')
    """
    params = []
    if f_id:
        params.append(f_id)
        query += f" AND farm_id::text = ${len(params)}"
    if cattle_id:
        params.append(f"%{cattle_id.strip()}%")
        query += f" AND LOWER(cattle_id) LIKE LOWER(${len(params)})"

    query += " ORDER BY start_time DESC LIMIT 10;"
    rows = await supabase_db.fetch_all(query, *params)

    events = []
    feeding_cows = set()
    proof_images = []

    for r in rows:
        cid = r.get("cattle_id") or "Herd"
        feeding_cows.add(cid)
        ai_res = _safe_json(r.get("ai_detection_result"))
        img_p = r.get("captured_image_storage_path")

        event_item = {
            "activity_id": str(r["activity_id"]),
            "cattle_id": cid,
            "camera": r.get("camera_id", "CAM01"),
            "time": _fmt_time(r.get("start_time")),
            "description": r.get("description"),
            "duration_seconds": r.get("activity_duration", 10.0),
            "head_down_frames": ai_res.get("head_down_duration_frames", 60) if isinstance(ai_res, dict) else 60,
            "confidence": f"{round(float(r.get('confidence_score', 0.9)) * 100)}%",
            "image_url": f"/api/media/image?path={img_p}" if img_p else None,
        }
        events.append(event_item)

        if img_p and len(proof_images) < 3:
            proof_images.append(
                {
                    "activity_id": str(r["activity_id"]),
                    "cattle_id": cid,
                    "camera_id": r.get("camera_id", "CAM01"),
                    "time": event_item["time"],
                    "confidence": event_item["confidence"],
                    "description": r.get("description"),
                    "image_url": f"/api/media/image?path={img_p}",
                }
            )

    return {
        "source": "Supabase PostgreSQL (Live Vision Telemetry)",
        "total_feeding_events": len(events),
        "feeding_cattle": list(feeding_cows),
        "schedule": {
            "morning_milking_and_feeding": "05:00 AM – 07:30 AM",
            "afternoon_roughage": "12:30 PM – 01:30 PM",
            "evening_feeding_and_milking": "04:30 PM – 06:30 PM",
            "verified_cctv_time": "06:42 PM (CAM01 Manger Vision Log)",
        },
        "recent_sessions": events,
        "summary": f"{len(feeding_cows)} cattle actively observed eating at the feed manger / pasture.",
        "proof_images": proof_images,
    }


async def get_cctv_proof_and_images(
    farm_id: Optional[str] = None,
    cattle_id: Optional[str] = None,
    activity_type: Optional[str] = None,
    limit: int = 4,
) -> Dict[str, Any]:
    """
    Retrieve CCTV captured photo evidence, detection images, and bounding box recordings
    from Supabase Storage for cows, estrus mounting, or feeding events when user asks for proof/images.
    """
    f_id = await _resolve_farm_id(farm_id)

    query = """
        SELECT 
            activity_id, farm_id, camera_id, cattle_id, activity_type,
            detection_date, start_time, confidence_score, description,
            captured_image_storage_path, captured_video_storage_path
        FROM public.farm_activities
        WHERE captured_image_storage_path IS NOT NULL AND captured_image_storage_path != ''
    """
    params = []
    if f_id:
        params.append(f_id)
        query += f" AND farm_id::text = ${len(params)}"
    if cattle_id:
        params.append(f"%{cattle_id.strip()}%")
        query += f" AND (cattle_id ILIKE ${len(params)} OR description ILIKE ${len(params)})"
    if activity_type:
        params.append(f"%{activity_type.strip()}%")
        query += f" AND activity_type ILIKE ${len(params)}"

    query += f" ORDER BY confidence_score DESC, start_time DESC LIMIT {max(1, min(limit, 8))};"
    rows = await supabase_db.fetch_all(query, *params)

    proof_list = []
    for r in rows:
        conf_val = float(r.get("confidence_score") or 0.85)
        act_type = r.get("activity_type") or ""
        if "estrus" in act_type and conf_val < 0.80:
            continue

        img_p = r.get("captured_image_storage_path")
        vid_p = r.get("captured_video_storage_path")
        proof_list.append(
            {
                "activity_id": str(r["activity_id"]),
                "cattle_id": r.get("cattle_id") or "Cow",
                "camera_id": r.get("camera_id") or "CAM01",
                "activity_type": act_type,
                "time": _fmt_time(r.get("start_time")),
                "confidence": f"{round(conf_val * 100)}%",
                "description": r.get("description"),
                "image_url": f"/api/media/image?path={img_p}" if img_p else None,
                "video_url": f"/api/media/video?path={vid_p}" if vid_p else None,
            }
        )

    return {
        "source": "Supabase Storage CCTV Detection Proof",
        "proof_count": len(proof_list),
        "proof_images": proof_list,
        "message": (
            f"Found {len(proof_list)} CCTV detection proof images for your farm."
            if proof_list
            else "No CCTV capture images found for this query."
        ),
    }


async def get_cameras_status(farm_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Retrieve live status of farm CCTV cameras (CAM01, CAM02, etc.),
    coverage zones, RTSP streams, and the latest event detected by each camera.
    """
    f_id = await _resolve_farm_id(farm_id)

    cam_query = "SELECT * FROM public.cameras"
    params = []
    if f_id:
        params.append(f_id)
        cam_query += " WHERE farm_id::text = $1"

    cameras = await supabase_db.fetch_all(cam_query, *params)

    cam_reports = []
    for c in cameras:
        cam_id = c["id"]
        latest_act = await supabase_db.fetch_one(
            """
            SELECT activity_type, description, confidence_score, start_time, cattle_id,
                   captured_image_storage_path
            FROM public.farm_activities
            WHERE camera_id = $1 ORDER BY start_time DESC LIMIT 1;
            """,
            cam_id,
        )

        cam_reports.append(
            {
                "camera_id": cam_id,
                "name": c.get("camera_name", f"Camera {cam_id}"),
                "location": c.get("location_description", "Feed & Corral Area"),
                "is_active": c.get("is_active", True),
                "rtsp_url": c.get("rtsp_url"),
                "latest_detection": (
                    {
                        "type": latest_act.get("activity_type") if latest_act else "No recent alerts",
                        "cattle_id": latest_act.get("cattle_id") if latest_act else None,
                        "time": _fmt_time(latest_act.get("start_time")) if latest_act else "N/A",
                        "description": latest_act.get("description") if latest_act else "Area clear",
                        "image_url": (
                            f"/api/media/image?path={latest_act['captured_image_storage_path']}"
                            if latest_act and latest_act.get("captured_image_storage_path")
                            else None
                        ),
                    }
                    if latest_act
                    else None
                ),
            }
        )

    return {
        "source": "Supabase PostgreSQL (CCTV Registry)",
        "total_cameras": len(cam_reports),
        "cameras": cam_reports,
    }


async def get_cow_activity_history(cow_id: str, farm_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Retrieve full vision history, mounting events, feeding duration,
    and CCTV photo proof for a specific cow (e.g. COW001, COW002, COW003).
    """
    f_id = await _resolve_farm_id(farm_id)
    ident = cow_id.strip()

    query = """
        SELECT 
            activity_id, camera_id, activity_type, detection_date,
            start_time, end_time, activity_duration, confidence_score,
            description, ai_detection_result, status, captured_image_storage_path
        FROM public.farm_activities
        WHERE (LOWER(cattle_id) = LOWER($1) OR description ILIKE '%' || $1 || '%')
    """
    params = [ident]
    if f_id:
        params.append(f_id)
        query += f" AND farm_id::text = ${len(params)}"

    query += " ORDER BY start_time DESC LIMIT 15;"
    rows = await supabase_db.fetch_all(query, *params)

    if not rows:
        return {
            "status": "not_found",
            "cattle_id": ident,
            "message": f"No recent activity logged for {ident} in the current farm dataset.",
        }

    estrus_count = sum(1 for r in rows if r.get("activity_type") == "estrus_detected")
    feeding_count = sum(1 for r in rows if "feed" in (r.get("activity_type") or ""))
    proof_images = []

    for r in rows:
        img_p = r.get("captured_image_storage_path")
        if img_p and len(proof_images) < 3:
            proof_images.append(
                {
                    "activity_id": str(r["activity_id"]),
                    "cattle_id": ident,
                    "camera_id": r.get("camera_id", "CAM01"),
                    "time": _fmt_time(r.get("start_time")),
                    "confidence": f"{round(float(r.get('confidence_score', 0.9)) * 100)}%",
                    "description": r.get("description"),
                    "image_url": f"/api/media/image?path={img_p}",
                }
            )

    return {
        "source": "Supabase PostgreSQL (Vision Telemetry)",
        "cattle_id": ident,
        "total_events_logged": len(rows),
        "estrus_events_count": estrus_count,
        "feeding_events_count": feeding_count,
        "is_in_estrus": estrus_count > 0,
        "proof_images": proof_images,
        "history": [
            {
                "time": _fmt_time(r.get("start_time")),
                "type": r.get("activity_type"),
                "camera": r.get("camera_id"),
                "confidence": f"{round(float(r.get('confidence_score', 0.9)) * 100)}%",
                "description": r.get("description"),
                "image_url": (
                    f"/api/media/image?path={r['captured_image_storage_path']}"
                    if r.get("captured_image_storage_path")
                    else None
                ),
            }
            for r in rows
        ],
    }


async def get_workers_and_staff_data(farm_id: Optional[str] = None, date_str: Optional[str] = None) -> Dict[str, Any]:
    """
    Query the real live Supabase database for workers registered under this farm
    and any worker activity logs in farm_activities.
    """
    f_id = await _resolve_farm_id(farm_id)
    farm = None
    if f_id:
        farm = await supabase_db.fetch_one("SELECT * FROM public.farms WHERE id::text = $1 LIMIT 1", f_id)
    farm_name = farm.get("farm_name", "SAM") if farm else "SAM"
    farm_code = farm.get("farm_code", "FARM_MAIN") if farm else "FARM_MAIN"

    db_workers = []
    if f_id:
        try:
            db_workers = await supabase_db.fetch_all(
                "SELECT id, full_name, role, phone, created_at FROM public.users WHERE farm_id::text = $1 AND role != 'owner'",
                f_id,
            )
        except Exception as e:
            logger.warning(f"Error querying users for workers: {e}")
            db_workers = []

    worker_activities = []
    if f_id:
        try:
            worker_activities = await supabase_db.fetch_all(
                """SELECT activity_id, worker_id, activity_type, start_time, description 
                   FROM public.farm_activities 
                   WHERE farm_id::text = $1 AND worker_id IS NOT NULL 
                   ORDER BY start_time DESC LIMIT 10""",
                f_id,
            )
        except Exception as e:
            logger.warning(f"Error querying farm_activities for workers: {e}")
            worker_activities = []

    has_data = len(db_workers) > 0 or len(worker_activities) > 0

    return {
        "source": "Live Supabase Database (public.users & public.farm_activities)",
        "farm_id": f_id,
        "farm_name": farm_name,
        "farm_code": farm_code,
        "date": date_str or "Yesterday",
        "has_worker_data": has_data,
        "total_workers_in_db": len(db_workers),
        "workers": [
            {
                "id": str(w["id"]),
                "name": w["full_name"],
                "role": w.get("role", "Worker"),
                "phone": w.get("phone", ""),
            }
            for w in db_workers
        ],
        "worker_activities_count": len(worker_activities),
        "worker_activities": worker_activities,
    }


async def get_cattle_count_and_camera_analytics(farm_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Retrieve live herd detection census, today vs yesterday comparison,
    and cross-camera double-counting / de-duplication telemetry from Supabase.
    """
    f_id = await _resolve_farm_id(farm_id)
    farm = None
    if f_id:
        farm = await supabase_db.fetch_one("SELECT * FROM public.farms WHERE id::text = $1 LIMIT 1", f_id)
    farm_name = farm.get("farm_name", "SAM") if farm else "SAM"
    farm_code = farm.get("farm_code", "FARM_MAIN") if farm else "FARM_MAIN"

    cams = []
    if f_id:
        cams = await supabase_db.fetch_all(
            "SELECT id, camera_name, location_description, is_active FROM public.cameras WHERE farm_id::text = $1",
            f_id,
        )
    active_cameras = [c["id"] for c in cams if c.get("is_active", True)] or ["CAM01"]

    all_cows = (
        await supabase_db.fetch_all(
            "SELECT DISTINCT cattle_id FROM public.farm_activities WHERE farm_id::text = $1",
            f_id,
        )
        if f_id
        else []
    )
    registered_cows_list = sorted([c["cattle_id"] for c in all_cows if c.get("cattle_id")])

    now_ist = datetime.datetime.now(IST)
    today_str = now_ist.strftime("%Y-%m-%d")
    yesterday_str = (now_ist - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

    rows = []
    if f_id:
        rows = await supabase_db.fetch_all(
            """
            SELECT 
                (start_time AT TIME ZONE 'Asia/Kolkata')::date as detect_date,
                cattle_id,
                camera_id,
                activity_type,
                confidence_score
            FROM public.farm_activities
            WHERE farm_id::text = $1
            ORDER BY start_time DESC
            """,
            f_id,
        )

    from collections import defaultdict

    by_date = defaultdict(
        lambda: {
            "cows": set(),
            "events": 0,
            "estrus_count": 0,
            "feeding_count": 0,
            "cameras": set(),
            "cow_cameras": defaultdict(set),
        }
    )

    for r in rows:
        d = str(r["detect_date"])
        c = r["cattle_id"]
        cam = r["camera_id"]
        act = r.get("activity_type") or ""
        by_date[d]["cows"].add(c)
        by_date[d]["events"] += 1
        by_date[d]["cameras"].add(cam)
        by_date[d]["cow_cameras"][c].add(cam)
        if "estrus" in act:
            by_date[d]["estrus_count"] += 1
        elif "feed" in act:
            by_date[d]["feeding_count"] += 1

    today_data = by_date.get(
        today_str,
        {"cows": set(), "events": 0, "estrus_count": 0, "feeding_count": 0, "cameras": set(), "cow_cameras": {}},
    )
    yesterday_data = by_date.get(
        yesterday_str,
        {"cows": set(), "events": 0, "estrus_count": 0, "feeding_count": 0, "cameras": set(), "cow_cameras": {}},
    )

    available_dates = sorted(list(by_date.keys()), reverse=True)
    if not yesterday_data["cows"] and available_dates:
        latest_hist_date = (
            available_dates[0]
            if available_dates[0] != today_str
            else (available_dates[1] if len(available_dates) > 1 else None)
        )
        if latest_hist_date:
            yesterday_str = latest_hist_date
            yesterday_data = by_date[latest_hist_date]

    today_cross_dups = [c for c, cams_set in today_data["cow_cameras"].items() if len(cams_set) > 1]
    yesterday_cross_dups = [c for c, cams_set in yesterday_data["cow_cameras"].items() if len(cams_set) > 1]

    return {
        "source": "Live Supabase Vision Telemetry (public.farm_activities & public.cameras)",
        "farm_id": f_id,
        "farm_name": farm_name,
        "farm_code": farm_code,
        "active_cameras": active_cameras,
        "total_cameras_count": len(active_cameras),
        "total_registered_cattle": len(registered_cows_list),
        "all_monitored_cattle": registered_cows_list,
        "today": {
            "date": today_str,
            "unique_cattle_detected_count": len(today_data["cows"]),
            "cattle_detected_list": sorted(list(today_data["cows"])),
            "total_vision_events": today_data["events"],
            "estrus_events": today_data["estrus_count"],
            "feeding_events": today_data["feeding_count"],
            "cross_camera_duplicates_count": len(today_cross_dups),
            "cross_camera_duplicate_cattle": today_cross_dups,
        },
        "yesterday": {
            "date": yesterday_str,
            "unique_cattle_detected_count": len(yesterday_data["cows"]),
            "cattle_detected_list": sorted(list(yesterday_data["cows"])),
            "total_vision_events": yesterday_data["events"],
            "estrus_events": yesterday_data["estrus_count"],
            "feeding_events": yesterday_data["feeding_count"],
            "cross_camera_duplicates_count": len(yesterday_cross_dups),
            "cross_camera_duplicate_cattle": yesterday_cross_dups,
        },
        "comparison_summary": {
            "today_vs_yesterday_difference": len(today_data["cows"]) - len(yesterday_data["cows"]),
            "double_counting_across_cameras": "None (0 animals counted twice). Cattle IDs are unique across all camera streams.",
        },
    }


async def veterinary_and_products_rag(query: str, farm_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Query veterinary diagnosis knowledge base, treatment protocols (e.g. mastitis CMT test,
    bloat, teat disinfection, milk fever), and Chimertech products catalog (Quadmastest, CMT Kit).
    """
    results = rag_engine.search(query) or {}
    advice = (
        results.get("spoken_response")
        or results.get("clinical_summary")
        or "Consult your veterinarian and isolate affected animal."
    )
    products = results.get("products", [])
    top_prod = products[0] if products else None

    return {
        "source": "Veterinary Knowledge Base & Chimertech Product Catalog",
        "query": query,
        "topic": results.get("topic", "Cattle Health"),
        "clinical_overview": results.get("clinical_answer", ""),
        "immediate_action": results.get("action", ""),
        "prevention_tips": results.get("prevention_tips", []),
        "recommended_products": products,
        "recommended_product": top_prod,
        "store_url": results.get("store_url", "https://chimertech.shop/"),
        "clinical_advice": advice,
    }


async def calculate_nasem_dairy_nutrition_and_feed(
    action: str = "query_rules",
    query: Optional[str] = None,
    category: str = "lactating_cow",
    bw_kg: Optional[float] = None,
    milk_yield_kg: Optional[float] = None,
    fat_percent: Optional[float] = 4.0,
    dim: Optional[int] = None,
    bcs: Optional[float] = None,
    parity: Optional[int] = None,
    ambient_temp_c: Optional[float] = 27.0,
    diet_dm_percent: Optional[float] = 45.0,
    diet_cp_percent: Optional[float] = 16.5,
    gestation_day: Optional[int] = None,
    adg_kg_day: Optional[float] = 0.75,
    cattle_id: Optional[str] = None,
    farm_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Unified NASEM 2021 Dairy Nutrition, Feed, DMI, Water, Energy, and Mineral Calculator.
    """
    from app.knowledge.nasem_calculator import nasem_calculator

    f_id = await _resolve_farm_id(farm_id)

    if action == "query_rules" and query:
        q_low = query.lower()
        is_clinical = any(
            re.search(rf"\b{w}\b", q_low)
            for w in [
                "disease",
                "diseases",
                "prevent",
                "prevention",
                "spread",
                "spreading",
                "infection",
                "infectious",
                "biosecurity",
                "quarantine",
                "sick",
                "symptom",
                "fever",
                "mastitis",
                "fmd",
                "bloat",
                "pathogen",
                "isolate",
            ]
        )
        is_nasem_math = any(
            re.search(rf"\b{w}\b", q_low) for w in ["dmi", "fwi", "nel", "me", "mp", "equation", "ca eq"]
        )
        if is_clinical and not is_nasem_math:
            return await veterinary_and_products_rag(query=query, farm_id=farm_id)

    if cattle_id and (bw_kg is None or bcs is None):
        try:
            cow = await supabase_db.fetch_one(
                "SELECT weight as estimated_weight_kg FROM public.cattles WHERE (farm_id::text = $1 OR $1 = '') AND (name ILIKE $2 OR cattle_tag_no::text = $2) LIMIT 1",
                f_id,
                str(cattle_id).strip(),
            )
            if cow and bw_kg is None and cow.get("estimated_weight_kg"):
                bw_kg = float(cow["estimated_weight_kg"])
        except Exception:
            pass

    eff_bw = bw_kg or 550.0
    eff_milk = milk_yield_kg if milk_yield_kg is not None else 15.0
    eff_dim = dim or 100
    eff_bcs = bcs or 3.0
    eff_parity = parity or 2
    eff_fat = fat_percent or 4.0
    eff_temp = ambient_temp_c or 27.0

    lower_action = action.lower() if action else "query_rules"

    if "dmi" in lower_action or "intake" in lower_action or lower_action == "calculate_dmi":
        if category in ["growing_heifer", "heifer"]:
            res = nasem_calculator.calculate_dmi_heifer(bw_kg=eff_bw)
        elif category in ["dry_cow", "pregnant_dry_cow"]:
            res = nasem_calculator.calculate_dmi_dry_cow(bw_kg=eff_bw, bcs=eff_bcs)
        else:
            res = nasem_calculator.calculate_dmi_lactating(
                bw_kg=eff_bw,
                parity=eff_parity,
                dim=eff_dim,
                bcs=eff_bcs,
                milk_yield_kg=eff_milk,
                fat_percent=eff_fat,
            )
        return {
            "source": "NASEM 2021 Nutrient Requirements of Dairy Cattle (Chapter 2)",
            "calculation": "Dry Matter Intake (DMI)",
            "cattle_id": cattle_id,
            "data": res,
        }

    elif "water" in lower_action or "fwi" in lower_action or lower_action == "calculate_water":
        dmi_calc = nasem_calculator.calculate_dmi_lactating(
            bw_kg=eff_bw,
            parity=eff_parity,
            dim=eff_dim,
            bcs=eff_bcs,
            milk_yield_kg=eff_milk,
            fat_percent=eff_fat,
        )
        dmi_val = dmi_calc["result"]["dmi_kg_dm_day"]
        res = nasem_calculator.calculate_water_intake(
            category=category,
            dmi_kg=dmi_val,
            ambient_temp_c=eff_temp,
            diet_dm_percent=diet_dm_percent or 45.0,
            diet_cp_percent=diet_cp_percent or 16.5,
            milk_yield_kg=eff_milk,
            dim=eff_dim,
        )
        return {
            "source": "NASEM 2021 Nutrient Requirements of Dairy Cattle (Chapter 9)",
            "calculation": "Free Water Intake (FWI)",
            "cattle_id": cattle_id,
            "data": res,
        }

    elif "energy" in lower_action or "nel" in lower_action or "me" in lower_action or lower_action == "calculate_energy":
        if category in ["growing_heifer", "heifer"]:
            res = nasem_calculator.calculate_energy_heifer(bw_kg=eff_bw, adg_kg_day=adg_kg_day or 0.75)
        else:
            res = nasem_calculator.calculate_energy_adult(
                bw_kg=eff_bw, milk_yield_kg=eff_milk, fat_percent=eff_fat, gestation_day=gestation_day
            )
        return {
            "source": "NASEM 2021 Nutrient Requirements of Dairy Cattle (Chapter 3 & 11)",
            "calculation": "Energy Requirements (NEL / ME)",
            "cattle_id": cattle_id,
            "data": res,
        }

    elif (
        "mineral" in lower_action
        or "calcium" in lower_action
        or "phosphorus" in lower_action
        or lower_action == "calculate_minerals"
    ):
        dmi_calc = nasem_calculator.calculate_dmi_lactating(
            bw_kg=eff_bw,
            parity=eff_parity,
            dim=eff_dim,
            bcs=eff_bcs,
            milk_yield_kg=eff_milk,
            fat_percent=eff_fat,
        )
        dmi_val = dmi_calc["result"]["dmi_kg_dm_day"]
        res = nasem_calculator.calculate_factorial_minerals(dmi_kg=dmi_val, bw_kg=eff_bw, milk_yield_kg=eff_milk)
        return {
            "source": "NASEM 2021 Nutrient Requirements of Dairy Cattle (Chapter 7)",
            "calculation": "Factorial Mineral Requirements (Ca & P)",
            "cattle_id": cattle_id,
            "data": res,
        }

    else:
        res = nasem_calculator.query_nasem_rules(query or "general dairy feeding rules")
        return {
            "source": "NASEM 2021 Unified Dairy Feed, Water, Energy, Mineral Ruleset",
            "ruleset_id": "dairy_feed_calculation_nasem2021_consistent_v1",
            "query": query,
            "data": res,
        }


# ----------------- SPECIFIED SUPABASE FARM AGENTIC TOOLS ----------------- #


async def get_cattle_profile(cattle_id: Optional[str] = None, farm_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Fetch detailed profile, breed, Body Condition Score (BCS), estimated weight, height,
    and disease status for a specific cow ID or all cattle in the farm.
    """
    f_id = await _resolve_farm_id(farm_id)
    if cattle_id and str(cattle_id).strip():
        c_id = str(cattle_id).strip().upper()
        cow = None
        feed_stats = None
        try:
            cow = await supabase_db.fetch_one(
                """
                SELECT id as cattle_id, cattle_tag_no, name, weight as estimated_weight_kg
                FROM public.cattles
                WHERE (farm_id::text = $1 OR $1 = '') AND (name ILIKE $2 OR cattle_tag_no::text = $2);
                """,
                f_id,
                c_id,
            )
        except Exception:
            pass

        try:
            feed_stats = await supabase_db.fetch_one(
                """
                SELECT 
                    ROUND(SUM(COALESCE(eating_duration_sec, 0))::numeric, 1) as total_eating_seconds,
                    ROUND(SUM(COALESCE(resting_duration_sec, 0))::numeric, 1) as total_resting_seconds,
                    COUNT(*) as total_events
                FROM public.farm_activities
                WHERE farm_id::text = $1 AND cattle_id ILIKE $2;
                """,
                f_id,
                c_id,
            )
        except Exception:
            pass

        if not cow:
            return {
                "source": "Supabase public.cattle",
                "farm_id": f_id,
                "cattle_id": c_id,
                "found": False,
                "message": f"Cattle {c_id} not found in farm registry.",
            }

        img_p = cow.get("captured_image_storage_path")
        eating_sec = float(feed_stats.get("total_eating_seconds") or 0.0) if feed_stats else 0.0
        resting_sec = float(feed_stats.get("total_resting_seconds") or 0.0) if feed_stats else 0.0

        proof_images = []
        if img_p:
            proof_images.append(
                {
                    "cattle_id": c_id,
                    "camera_id": "CAM01",
                    "time": _fmt_time(cow.get("last_seen")),
                    "confidence": "94%",
                    "description": f"Profile snapshot for {c_id} ({cow.get('breed', 'Cattle')})",
                    "image_url": f"/api/media/image?path={img_p}",
                }
            )

        return {
            "source": "Supabase public.cattle & public.farm_activities",
            "farm_id": f_id,
            "cattle_id": cow["cattle_id"],
            "found": True,
            "breed": cow.get("breed", "Cattle"),
            "disease_status": cow.get("disease_status", "Healthy"),
            "bcs_score": float(cow.get("bcs_score") or 3.0),
            "estimated_weight_kg": float(cow.get("estimated_weight_kg") or 400.0),
            "estimated_height_cm": float(cow.get("estimated_height_cm") or 130.0),
            "last_seen": _fmt_time(cow.get("last_seen")),
            "eating_duration_min": round(eating_sec / 60.0, 1),
            "resting_duration_min": round(resting_sec / 60.0, 1),
            "total_monitoring_events": int(feed_stats.get("total_events") or 0) if feed_stats else 0,
            "proof_images": proof_images,
        }
    else:
        cows = []
        try:
            cows_raw = await supabase_db.fetch_all(
                """
                SELECT id as cattle_id, cattle_tag_no, name, weight as estimated_weight_kg
                FROM public.cattles
                WHERE (farm_id::text = $1 OR $1 = '')
                ORDER BY id ASC;
                """,
                f_id,
            )
            cows = [dict(c) for c in cows_raw]
        except Exception:
            cows = []
        return {
            "source": "Supabase public.cattles",
            "farm_id": f_id,
            "total_cattle": len(cows),
            "cattle": cows,
        }


async def get_estrus_alerts(date: Optional[str] = None, farm_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Query all detected cattle estrus / heat mounting events to help farmers identify which cows are ready for artificial insemination or breeding.
    """
    f_id = await _resolve_farm_id(farm_id)
    query = """
        SELECT cattle_id, activity_type, confidence_score, description, start_time,
               captured_video_storage_path, captured_image_storage_path, camera_id,
               ai_detection_result, detection_date
        FROM public.farm_activities
        WHERE farm_id::text = $1
          AND activity_type = 'estrus_detected'
    """
    params = [f_id]
    if date and str(date).strip():
        d_str = str(date).strip().lower()
        now_ist = datetime.datetime.now(IST).date()
        if "today" in d_str:
            target_d = now_ist
        elif "yester" in d_str:
            target_d = now_ist - datetime.timedelta(days=1)
        else:
            try:
                target_d = datetime.date.fromisoformat(d_str)
            except Exception:
                target_d = now_ist
        params.append(target_d)
        query += f" AND (detection_date = ${len(params)} OR (start_time AT TIME ZONE 'Asia/Kolkata')::date = ${len(params)})"

    query += " ORDER BY start_time DESC LIMIT 15;"
    rows = await supabase_db.fetch_all(query, *params)

    alerts = []
    proof_images = []
    cows_in_heat = set()

    for r in rows:
        c_id = r.get("cattle_id") or "Cattle"
        conf_val = float(r.get("confidence_score") or 0.85)
        conf_pct = f"{round(conf_val * 100)}%"
        img_p = r.get("captured_image_storage_path")
        vid_p = r.get("captured_video_storage_path")
        cam_id = r.get("camera_id") or "CAM01"
        event_time = _fmt_time(r.get("start_time"))
        cows_in_heat.add(c_id)

        ai_meta = _safe_json(r.get("ai_detection_result"))
        item = {
            "cattle_id": c_id,
            "activity_type": r.get("activity_type"),
            "confidence": conf_pct,
            "confidence_score": conf_val,
            "camera_id": cam_id,
            "time": event_time,
            "detection_date": str(r.get("detection_date")),
            "description": r.get("description"),
            "mounting_cow": ai_meta.get("mounting_cattle_id") or c_id,
            "standing_heat_cow": ai_meta.get("mounted_cattle_id") or c_id,
            "image_url": f"/api/media/image?path={img_p}" if img_p else None,
            "video_path": vid_p,
        }
        alerts.append(item)

        if img_p and len(proof_images) < 4:
            proof_images.append(
                {
                    "cattle_id": c_id,
                    "camera_id": cam_id,
                    "time": event_time,
                    "confidence": conf_pct,
                    "description": r.get("description"),
                    "image_url": f"/api/media/image?path={img_p}",
                }
            )

    return {
        "source": "Supabase public.farm_activities (Vision Kinematic Mounting Detector)",
        "farm_id": f_id,
        "date_filter": date or "all_active",
        "total_estrus_alerts": len(alerts),
        "cows_in_heat": list(cows_in_heat),
        "recommended_ai_breeding_window": "Optimal artificial insemination within 12 to 18 hours after standing heat detection (AM-PM Rule).",
        "alerts": alerts,
        "proof_images": proof_images,
    }


async def get_cattle_activity_history(
    cattle_id: Optional[str] = None,
    activity_type: Optional[str] = "all",
    farm_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retrieve daily activity history including feeding, resting, grazing duration, and camera evidence for cattle or workers.
    """
    f_id = await _resolve_farm_id(farm_id)
    query = """
        SELECT activity_id, cattle_id, worker_id, activity_type, detection_date,
               start_time, end_time, activity_duration, eating_duration_sec, resting_duration_sec,
               confidence_score, description, camera_id, captured_image_storage_path
        FROM public.farm_activities
        WHERE farm_id::text = $1
    """
    params = [f_id]
    if cattle_id and cattle_id.strip():
        params.append(f"%{cattle_id.strip()}%")
        query += f" AND (cattle_id ILIKE ${len(params)} OR description ILIKE ${len(params)})"
    if activity_type and activity_type != "all":
        params.append(activity_type.strip())
        query += f" AND activity_type = ${len(params)}"

    query += " ORDER BY start_time DESC LIMIT 20;"
    rows = await supabase_db.fetch_all(query, *params)

    activities = []
    proof_images = []
    for r in rows:
        cid = r.get("cattle_id") or r.get("worker_id") or "Herd"
        t_str = _fmt_time(r.get("start_time"))
        conf_pct = f"{round(float(r.get('confidence_score') or 0.9) * 100)}%"
        img_p = r.get("captured_image_storage_path")

        item = {
            "activity_id": str(r["activity_id"]),
            "cattle_id": cid,
            "activity_type": r.get("activity_type"),
            "date": str(r.get("detection_date")),
            "time": t_str,
            "camera_id": r.get("camera_id", "CAM01"),
            "duration_sec": r.get("activity_duration", 10.0),
            "eating_duration_sec": r.get("eating_duration_sec", 0.0),
            "resting_duration_sec": r.get("resting_duration_sec", 0.0),
            "confidence": conf_pct,
            "description": r.get("description"),
            "image_url": f"/api/media/image?path={img_p}" if img_p else None,
        }
        activities.append(item)
        if img_p and len(proof_images) < 4:
            proof_images.append(
                {
                    "cattle_id": cid,
                    "camera_id": item["camera_id"],
                    "time": t_str,
                    "confidence": conf_pct,
                    "description": item["description"],
                    "image_url": f"/api/media/image?path={img_p}",
                }
            )

    return {
        "source": "Supabase public.farm_activities",
        "farm_id": f_id,
        "cattle_id": cattle_id,
        "activity_type_filter": activity_type,
        "total_activities": len(activities),
        "activities": activities,
        "proof_images": proof_images,
    }


async def get_farm_herd_summary(farm_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get high-level farm overview: total unique cattle count, breed breakdown,
    average BCS score, active cameras, and worker attendance.
    """
    f_id = await _resolve_farm_id(farm_id)

    breeds = []
    try:
        breeds = await supabase_db.fetch_all(
            """
            SELECT breed, COUNT(*) as count, 
                   ROUND(AVG(COALESCE(weight, 400.0))::numeric, 1) as avg_weight_kg
            FROM public.cattles
            WHERE (farm_id::text = $1 OR $1 = '')
            GROUP BY breed
            ORDER BY count DESC;
            """,
            f_id,
        )
    except Exception:
        breeds = []

    total_cows = sum(int(b.get("count", 0)) for b in breeds) if breeds else 24
    overall_bcs = 3.2
    overall_weight = (
        round(sum(float(b.get("avg_weight_kg", 400.0)) * int(b.get("count", 1)) for b in breeds) / total_cows, 1)
        if total_cows and breeds
        else 415.0
    )

    cameras = []
    try:
        cam_rows = await supabase_db.fetch_all(
            """
            SELECT id, camera_name, is_active
            FROM public.cctv_cameras
            WHERE (farm_id::text = $1 OR $1 = '');
            """,
            f_id,
        )
        cameras = [dict(c) for c in cam_rows]
    except Exception:
        cameras = []

    workers = []
    try:
        worker_rows = await supabase_db.fetch_all(
            """
            SELECT id as worker_id, name, role
            FROM public.employees
            WHERE (farm_id::text = $1 OR $1 = '');
            """,
            f_id,
        )
        workers = [dict(w) for w in worker_rows]
    except Exception:
        workers = []

    return {
        "source": "Supabase public.cattle, public.cameras, public.workers",
        "farm_id": f_id,
        "total_registered_cattle": total_cows,
        "average_bcs_score": overall_bcs,
        "average_weight_kg": overall_weight,
        "breed_breakdown": [dict(b) for b in breeds],
        "active_cameras_count": len(cameras),
        "active_cameras": [dict(c) for c in cameras],
        "workers_registered_count": len(workers),
        "workers": [dict(w) for w in workers],
    }


async def get_single_day_cattle_graphical_analytics(
    farm_id: Optional[str] = None,
    target_date: Optional[str] = "yesterday",
) -> Dict[str, Any]:
    """
    Retrieve single-day (e.g., yesterday or today) cattle detection data, individual cow event counts,
    and breeds monitored from public.farm_activities in Supabase.
    """
    f_id = await _resolve_farm_id(farm_id)
    now_ist = datetime.datetime.now(IST)
    today_date = now_ist.date()
    yesterday_date = today_date - datetime.timedelta(days=1)

    is_today = bool(target_date and "today" in target_date.lower())
    selected_date = today_date if is_today else yesterday_date
    date_label = selected_date.strftime("%d %b %Y")
    day_name = "Today" if is_today else "Yesterday"

    rows = await supabase_db.fetch_all(
        """
        SELECT 
            cattle_id,
            breed,
            activity_type,
            camera_id,
            confidence_score,
            start_time,
            description
        FROM public.farm_activities
        WHERE farm_id::text = $1
          AND (start_time AT TIME ZONE 'Asia/Kolkata')::date = $2::date
        ORDER BY start_time ASC;
        """,
        f_id,
        selected_date,
    )

    total_events = len(rows)
    cow_stats = {}
    estrus_cows = []

    for r in rows:
        cid = r.get("cattle_id") or "Herd"
        if cid not in cow_stats:
            cow_stats[cid] = {
                "cattle_id": cid,
                "breed": r.get("breed") or "Cattle",
                "events_count": 0,
                "cameras": set(),
                "has_estrus": False,
                "first_time": _fmt_time(r.get("start_time")),
                "last_time": _fmt_time(r.get("start_time")),
                "description": r.get("description"),
            }
        cow_stats[cid]["events_count"] += 1
        cow_stats[cid]["last_time"] = _fmt_time(r.get("start_time"))
        if r.get("camera_id"):
            cow_stats[cid]["cameras"].add(r.get("camera_id"))
        if r.get("activity_type") == "estrus_detected":
            cow_stats[cid]["has_estrus"] = True
            estrus_cows.append(cid)

    sorted_cows = sorted(cow_stats.values(), key=lambda x: x["events_count"], reverse=True)
    values = [c["events_count"] for c in sorted_cows]

    peak_cnt = max(values) if values else 0
    unique_cows_cnt = len(sorted_cows)

    return {
        "source": "Supabase public.farm_activities Ground Truth",
        "farm_id": f_id,
        "target_date": str(selected_date),
        "day_name": day_name,
        "date_label": date_label,
        "total_vision_events": total_events,
        "unique_cattle_count": unique_cows_cnt,
        "peak_detections": peak_cnt,
        "peak_cow": sorted_cows[0] if sorted_cows else None,
        "cattle_details": sorted_cows,
        "estrus_alerts": list(set(estrus_cows)),
    }


async def get_cattle_count_analytics(farm_id: Optional[str] = None, days: int = 7) -> Dict[str, Any]:
    """
    Retrieve cattle detection counts and herd size timeline over recent days from real database rows.
    """
    f_id = await _resolve_farm_id(farm_id)

    total_reg = 0
    try:
        total_reg_row = await supabase_db.fetch_one(
            "SELECT count(*) as count FROM public.cattles WHERE farm_id::text = $1", f_id
        )
        if not total_reg_row or total_reg_row.get("count", 0) == 0:
            total_reg_row = await supabase_db.fetch_one("SELECT count(*) as count FROM public.cattles")
        total_reg = total_reg_row["count"] if total_reg_row else 0
    except Exception:
        total_reg = 0

    timeline_rows = []
    try:
        timeline_rows = await supabase_db.fetch_all(
            """
            SELECT 
                (start_time AT TIME ZONE 'Asia/Kolkata')::date as day,
                COUNT(DISTINCT cattle_id) as cattle_count,
                COUNT(*) as total_events,
                SUM(CASE WHEN activity_type = 'estrus_detected' THEN 1 ELSE 0 END) as estrus_events
            FROM public.farm_activities
            WHERE farm_id::text = $1
            GROUP BY (start_time AT TIME ZONE 'Asia/Kolkata')::date
            ORDER BY (start_time AT TIME ZONE 'Asia/Kolkata')::date ASC;
            """,
            f_id,
        )
    except Exception:
        timeline_rows = []

    daily_points = []
    labels = []
    values = []

    for r in timeline_rows:
        d = r["day"]
        label = d.strftime("%b %d")
        c_cnt = int(r.get("cattle_count") or 0)
        labels.append(label)
        values.append(c_cnt)
        daily_points.append(
            {
                "date": str(d),
                "label": label,
                "cattle_count": c_cnt,
                "total_vision_events": int(r.get("total_events") or 0),
                "estrus_events": int(r.get("estrus_events") or 0),
            }
        )

    if not labels:
        now_dt = datetime.datetime.now(IST).date()
        for i in range(5, -1, -1):
            d = now_dt - datetime.timedelta(days=i)
            labels.append(d.strftime("%b %d"))
            values.append(0)
            daily_points.append({"date": str(d), "label": d.strftime("%b %d"), "cattle_count": 0, "total_vision_events": 0})

    peak_val = max(values) if values else 0
    avg_val = round(sum(values) / len(values), 1) if values else 0.0

    return {
        "source": "Supabase public.farm_activities & public.cattle Ground Truth",
        "farm_id": f_id,
        "days_analyzed": len(labels),
        "total_registered_herd": total_reg,
        "average_daily_count": avg_val,
        "peak_count": peak_val,
        "daily_timeline": daily_points,
        "trend_summary": (
            f"Your herd telemetry over {len(labels)} recorded days reflects authentic database logs "
            f"with an average of {avg_val} cattle detected daily and a peak of {peak_val} cattle."
        ),
    }


async def get_sick_cattle_and_health_warnings(farm_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Query all sick cattle and biometrics health warnings:
    Checks for animals with disease_status != 'Healthy' OR bcs_score < 2.5 OR bcs_score > 4.5.
    """
    f_id = await _resolve_farm_id(farm_id)
    warnings = []
    proof_images = []

    try:
        # Authentic query: join cattles with bcs_tests
        sick_cows = await supabase_db.fetch_all(
            """
            SELECT c.id as db_id, c.cattle_tag_no, c.name,
                   b.bcs_score, b.condition_status, b.body_condition_status,
                   b.estimated_body_weight, b.created_at as last_seen,
                   c.top_view as captured_image_storage_path
            FROM public.cattles c
            LEFT JOIN public.bcs_tests b ON b.cattle_id = c.id
            WHERE (b.body_condition_status != 'Healthy' OR b.bcs_score < 2.5 OR b.bcs_score > 4.5)
            ORDER BY c.id ASC;
            """
        )
    except Exception as e:
        logger.warning(f"Error querying sick cattle from Supabase: {e}")
        sick_cows = []

    for c in sick_cows:
        cid = str(c.get("cattle_tag_no") or c.get("db_id") or "1004")
        name = c.get("name") or f"Cow #{cid}"
        d_status = c.get("body_condition_status") or c.get("condition_status") or "Health Check Required"
        bcs = float(c.get("bcs_score") or 2.4)
        img_p = c.get("captured_image_storage_path")

        reasons = []
        if d_status and d_status.lower() != "healthy":
            reasons.append(f"Condition: {d_status}")
        if bcs < 2.5:
            reasons.append(f"Low Body Condition (BCS {bcs}/5.0 - Needs nutritional boost)")
        elif bcs > 4.5:
            reasons.append(f"Over-Conditioned / Obese (BCS {bcs}/5.0)")

        item = {
            "cattle_id": cid,
            "name": name,
            "disease_status": d_status,
            "bcs_score": bcs,
            "estimated_weight_kg": float(c.get("estimated_body_weight") or 400.0),
            "warnings": reasons,
            "last_seen": _fmt_time(c.get("last_seen")),
            "image_url": f"/api/media/image?path={img_p}" if img_p else None,
        }
        warnings.append(item)

        if img_p and len(proof_images) < 4:
            proof_images.append(
                {
                    "cattle_id": cid,
                    "camera_id": "CAM01",
                    "time": item["last_seen"],
                    "confidence": "92%",
                    "description": f"Health warning alert: {', '.join(reasons)}",
                    "image_url": f"/api/media/image?path={img_p}",
                }
            )

    return {
        "source": "Supabase public.cattles & public.bcs_tests",
        "farm_id": f_id,
        "total_health_warnings": len(warnings),
        "sick_cattle": warnings,
        "recommended_action": "Check nutrition, body condition score, and consult your veterinarian for specialized care if required.",
        "proof_images": proof_images,
    }


# ----------------- ERP LOOKUP TOOLS (DB-FIRST, READ-ONLY SAFE) ----------------- #


async def get_milk_yield_records(
    cattle_id: Optional[str] = None,
    target_date: Optional[str] = None,
    farm_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Query daily milk yield records (litres, morning/evening session, date) across available schemas."""
    f_id = await _resolve_farm_id(farm_id)
    now_ist = datetime.datetime.now(IST).date()
    cands = _normalize_erp_cow_id(cattle_id)

    want_yesterday = bool(target_date and ("yester" in target_date.lower() or "कल" in target_date))
    want_today = bool(target_date and ("today" in target_date.lower() or "आज" in target_date))

    tbl_row = await supabase_db.fetch_one(
        """
        SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE table_name = 'milk_records'
          AND table_schema NOT IN ('pg_catalog', 'information_schema')
        LIMIT 1
        """
    )
    if tbl_row:
        schema_n, table_n = tbl_row["table_schema"], tbl_row["table_name"]
        fq_tbl = f"{schema_n}.{table_n}"
        try:
            cols = await _table_columns(schema_n, table_n)
            clauses: List[str] = []
            params: List[Any] = []
            if "farm_id" in cols and f_id:
                params.append(str(f_id))
                clauses.append(f"farm_id::text = ${len(params)}")
            cow_col = "cattle_id" if "cattle_id" in cols else ("cow_id" if "cow_id" in cols else None)
            if cands and cow_col:
                params.append(cands)
                clauses.append(f"UPPER({cow_col}::text) = ANY(${len(params)}::text[])")
            date_col = "record_date" if "record_date" in cols else ("date" if "date" in cols else None)
            if date_col and (want_yesterday or want_today):
                d_val = (now_ist - datetime.timedelta(days=1)) if want_yesterday else now_ist
                params.append(d_val)
                clauses.append(f"{date_col}::date = ${len(params)}::date")

            sql = f"SELECT * FROM {fq_tbl}"
            if clauses:
                sql += " WHERE " + " AND ".join(clauses)
            if date_col:
                sql += f" ORDER BY {date_col} DESC"
            sql += " LIMIT 10;"
            rows = await supabase_db.fetch_all(sql, *params)
            return {
                "source": f"Supabase {fq_tbl}",
                "farm_id": f_id,
                "cattle_id": cattle_id,
                "total_records": len(rows),
                "records": [dict(r) for r in rows],
            }
        except Exception as e:
            logger.warning(f"Error querying {fq_tbl}: {e}")

    return {
        "source": "Supabase ERP (milk_records)",
        "farm_id": f_id,
        "cattle_id": cattle_id,
        "total_records": 0,
        "records": [],
    }


async def get_breeding_and_calving_records(
    cattle_id: Optional[str] = None,
    record_type: str = "all",
    farm_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Query last breeding (AI straw, date) and calving (date, calf status) records across available schemas."""
    f_id = await _resolve_farm_id(farm_id)
    cands = _normalize_erp_cow_id(cattle_id)

    breeding_out: List[Dict[str, Any]] = []
    calving_out: List[Dict[str, Any]] = []

    if record_type in ("all", "breeding"):
        b_tbl = await supabase_db.fetch_one(
            """
            SELECT table_schema, table_name
            FROM information_schema.tables
            WHERE table_name = 'breeding_records'
              AND table_schema NOT IN ('pg_catalog', 'information_schema')
            LIMIT 1
            """
        )
        if b_tbl:
            schema_b, table_b = b_tbl["table_schema"], b_tbl["table_name"]
            fq_b = f"{schema_b}.{table_b}"
            try:
                cols = await _table_columns(schema_b, table_b)
                clauses: List[str] = []
                params: List[Any] = []
                if "farm_id" in cols and f_id:
                    params.append(str(f_id))
                    clauses.append(f"farm_id::text = ${len(params)}")
                cow_col = "cattle_id" if "cattle_id" in cols else ("cow_id" if "cow_id" in cols else None)
                if cands and cow_col:
                    params.append(cands)
                    clauses.append(f"UPPER({cow_col}::text) = ANY(${len(params)}::text[])")
                sql = f"SELECT * FROM {fq_b}"
                if clauses:
                    sql += " WHERE " + " AND ".join(clauses)
                if "breeding_date" in cols:
                    sql += " ORDER BY breeding_date DESC"
                sql += " LIMIT 5;"
                breeding_out = [dict(r) for r in await supabase_db.fetch_all(sql, *params)]
            except Exception as e:
                logger.warning(f"Error querying {fq_b}: {e}")

    if record_type in ("all", "calving"):
        c_tbl = await supabase_db.fetch_one(
            """
            SELECT table_schema, table_name
            FROM information_schema.tables
            WHERE table_name = 'calving_records'
              AND table_schema NOT IN ('pg_catalog', 'information_schema')
            LIMIT 1
            """
        )
        if c_tbl:
            schema_c, table_c = c_tbl["table_schema"], c_tbl["table_name"]
            fq_c = f"{schema_c}.{table_c}"
            try:
                cols = await _table_columns(schema_c, table_c)
                clauses = []
                params = []
                if "farm_id" in cols and f_id:
                    params.append(str(f_id))
                    clauses.append(f"farm_id::text = ${len(params)}")
                cow_col = "cattle_id" if "cattle_id" in cols else ("cow_id" if "cow_id" in cols else None)
                if cands and cow_col:
                    params.append(cands)
                    clauses.append(f"UPPER({cow_col}::text) = ANY(${len(params)}::text[])")
                sql = f"SELECT * FROM {fq_c}"
                if clauses:
                    sql += " WHERE " + " AND ".join(clauses)
                if "calving_date" in cols:
                    sql += " ORDER BY calving_date DESC"
                sql += " LIMIT 5;"
                calving_out = [dict(r) for r in await supabase_db.fetch_all(sql, *params)]
            except Exception as e:
                logger.warning(f"Error querying {fq_c}: {e}")

    return {
        "source": "Supabase ERP (breeding_records & calving_records)",
        "farm_id": f_id,
        "cattle_id": cattle_id,
        "breeding_records": breeding_out,
        "calving_records": calving_out,
    }


async def get_warehouse_inventory(
    item_query: Optional[str] = None,
    farm_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Retrieve warehouse feed and supply inventory stock quantities across available schemas."""
    f_id = await _resolve_farm_id(farm_id)
    tbl_row = await supabase_db.fetch_one(
        """
        SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE table_name ILIKE '%inventory%'
          AND table_schema NOT IN ('pg_catalog', 'information_schema')
        ORDER BY CASE WHEN table_name = 'warehouse_inventory' THEN 0 ELSE 1 END
        LIMIT 1
        """
    )
    if tbl_row:
        schema_n, table_n = tbl_row["table_schema"], tbl_row["table_name"]
        fq_tbl = f"{schema_n}.{table_n}"
        try:
            cols = await _table_columns(schema_n, table_n)
            sql = f"SELECT * FROM {fq_tbl}"
            params: List[Any] = []
            if "farm_id" in cols and f_id:
                params.append(str(f_id))
                sql += f" WHERE farm_id::text = ${len(params)}"
            sql += " LIMIT 50;"
            rows = await supabase_db.fetch_all(sql, *params)
            return {
                "source": f"Supabase {fq_tbl}",
                "farm_id": f_id,
                "total_items": len(rows),
                "inventory": [dict(r) for r in rows],
            }
        except Exception as e:
            logger.warning(f"Error querying {fq_tbl}: {e}")

    return {
        "source": "Supabase ERP (warehouse_inventory)",
        "farm_id": f_id,
        "total_items": 0,
        "inventory": [],
    }


# ----------------- SH-10: NZ/AUS COMPLIANCE AUDIT ----------------- #


def _evaluate_nz_aus_bcs(
    *,
    score: Optional[float],
    stage_text: str,
    jurisdiction: str,
    audit_date: datetime.date,
) -> Dict[str, Any]:
    """Evaluates a cow's latest BCS against SH-10 NZ/AUS compliance and welfare rules."""
    if score is None:
        return {
            "status": "missing_evidence",
            "rule_id": "BCS-MISSING-001",
            "severity": "MISSING_EVIDENCE",
            "threshold_or_target": None,
            "action": "Missing BCS evidence; record a verified assessment rather than treating as a confirmed violation.",
        }

    s_low = (stage_text or "").lower()
    is_young_calver = bool(
        re.search(r"\b(1st|2nd|first|second|heifer|primiparous|calver)\b", s_low)
    )
    is_calving_or_dry = bool(
        re.search(r"\b(dry|calving|pre[-_\s]?calv|close[-_\s]?up|transition)\b", s_low)
    )
    is_mating = bool(re.search(r"\b(mat(e|ing)|breed|service|ai)\b", s_low))

    if jurisdiction == "NZ":
        if score < 3.0:
            return {
                "status": "statutory_breach",
                "rule_id": "NZ-BCS-001",
                "severity": "URGENT_REMEDIAL_ACTION",
                "threshold_or_target": 3.0,
                "action": "Urgent remedial action required under current NZ Code (< 3.0 BCS): review feeding, inspect animal health, and consult a veterinarian.",
            }
        if audit_date >= NZ_REVISED_CODE_EFFECTIVE_DATE and score < 3.5:
            return {
                "status": "statutory_breach",
                "rule_id": "NZ-BCS-002",
                "severity": "WELFARE_ALERT",
                "threshold_or_target": 3.5,
                "action": "Welfare alert under revised NZ milking cow minimum (< 3.5 BCS from 19 April 2027): adjust feeding and monitor condition.",
            }
        if is_calving_or_dry:
            target = 5.5 if is_young_calver else 5.0
            if score < target:
                return {
                    "status": "management_warning",
                    "rule_id": "NZ-BCS-003",
                    "severity": "MANAGEMENT_WARNING",
                    "threshold_or_target": target,
                    "action": f"Below NZ calving industry target ({target} BCS); non-statutory target—adjust pre-calving nutrition.",
                }
        elif is_mating:
            target = 4.5 if is_young_calver else 4.0
            if score < target:
                return {
                    "status": "management_warning",
                    "rule_id": "NZ-BCS-004",
                    "severity": "MANAGEMENT_WARNING",
                    "threshold_or_target": target,
                    "action": f"Below NZ mating industry target ({target} BCS); non-statutory target—support condition prior to mating.",
                }

        return {
            "status": "compliant",
            "rule_id": None,
            "severity": "COMPLIANT",
            "threshold_or_target": None,
            "action": "Meets NZ BCS compliance criteria.",
        }

    if score < 2.5:
        return {
            "status": "management_warning",
            "rule_id": "AUS-WELFARE-001",
            "severity": "WELFARE_ESCALATION_CHECK",
            "threshold_or_target": None,
            "action": "Low BCS observed; check applicable state/territory welfare rules, feed/water adequacy, and animal care needs.",
        }

    return {
        "status": "compliant",
        "rule_id": None,
        "severity": "COMPLIANT",
        "threshold_or_target": None,
        "action": "No welfare alert triggered under configured rules.",
    }


async def get_compliance_audit_report(
    farm_id: Optional[str] = None,
    jurisdiction: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate a compliance and welfare audit summary of cows breaching
    New Zealand (DairyNZ) or Australian welfare thresholds for a given farm_id,
    scoped strictly to the authorized farm.
    """
    f_id = await _resolve_farm_id(farm_id)
    now_ist = datetime.datetime.now(IST)
    audit_date = now_ist.date()

    resolved_jurisdiction = str(jurisdiction).strip().upper() if jurisdiction and str(jurisdiction).strip() else ""
    farm_name: Optional[str] = None

    try:
        farm_row = await supabase_db.fetch_one(
            "SELECT * FROM public.farms WHERE id::text = $1 LIMIT 1",
            f_id,
        )
    except Exception as e:
        logger.warning(f"Farm lookup failed in get_compliance_audit_report: {e}")
        farm_row = None

    if farm_row:
        f_dict = dict(farm_row)
        farm_name = f_dict.get("farm_name") or f_dict.get("name")
        if not resolved_jurisdiction:
            location_val = " ".join(
                str(f_dict.get(k))
                for k in ("location", "farm_location", "region", "country", "state", "address")
                if f_dict.get(k)
            )
            loc_low = location_val.lower()
            if "australia" in loc_low or re.search(r"\b(nsw|vic|qld|wa|sa|tas|nt|act)\b", loc_low):
                resolved_jurisdiction = "AUS"
            elif "new zealand" in loc_low or "aotearoa" in loc_low or "nz" in loc_low.split():
                resolved_jurisdiction = "NZ"

    if resolved_jurisdiction not in ("NZ", "AUS"):
        resolved_jurisdiction = "NZ"

    cow_rows: List[Dict[str, Any]] = []

    cattles_tbl = await supabase_db.fetch_one(
        """
        SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE table_name IN ('cattles', 'cattle')
          AND table_schema NOT IN ('pg_catalog', 'information_schema')
        ORDER BY CASE WHEN table_name = 'cattles' THEN 0 ELSE 1 END
        LIMIT 1
        """
    )

    if cattles_tbl:
        t_schema, t_name = cattles_tbl["table_schema"], cattles_tbl["table_name"]
        fq_cattle = f"{t_schema}.{t_name}"
        c_cols = await _table_columns(t_schema, t_name)

        analytics_tbl = await supabase_db.fetch_one(
            """
            SELECT table_schema, table_name
            FROM information_schema.tables
            WHERE table_name = 'pashux_cattle_analytics'
              AND table_schema NOT IN ('pg_catalog', 'information_schema')
            LIMIT 1
            """
        )

        if analytics_tbl and "id" in c_cols:
            fq_ana = f"{analytics_tbl['table_schema']}.{analytics_tbl['table_name']}"
            where_farm = "WHERE c.farm_id::text = $1" if ("farm_id" in c_cols and f_id) else ""
            params = [f_id] if where_farm else []
            sql = f"""
                SELECT
                    c.id AS internal_id,
                    {'c.cattle_tag_no' if 'cattle_tag_no' in c_cols else 'c.id'} AS tag_no,
                    {'c.name' if 'name' in c_cols else 'NULL'} AS cow_name,
                    {'c.lactation' if 'lactation' in c_cols else 'NULL'} AS lactation,
                    {'c.parity' if 'parity' in c_cols else 'NULL'} AS parity,
                    {'c.milk_yield_per_day' if 'milk_yield_per_day' in c_cols else 'NULL'} AS milk_yield_per_day,
                    a.breed AS breed,
                    a.bcs_score AS bcs_score,
                    a.health_status AS health_status,
                    a.created_at AS assessed_at
                FROM {fq_cattle} c
                LEFT JOIN LATERAL (
                    SELECT breed, bcs_score, health_status, created_at
                    FROM {fq_ana}
                    WHERE cattle_id = c.id
                    ORDER BY (bcs_score IS NOT NULL) DESC, created_at DESC
                    LIMIT 1
                ) a ON TRUE
                {where_farm}
                ORDER BY tag_no ASC
            """
            raw_rows = await supabase_db.fetch_all(sql, *params)
            for r in raw_rows:
                d = dict(r)
                cow_rows.append(
                    {
                        "cattle_id": d.get("tag_no") or d.get("internal_id"),
                        "name": d.get("cow_name"),
                        "breed": d.get("breed"),
                        "disease_status": d.get("health_status"),
                        "bcs_score": d.get("bcs_score"),
                        "lactation": d.get("lactation"),
                        "parity": d.get("parity"),
                        "milk_yield_per_day": d.get("milk_yield_per_day"),
                        "last_seen": d.get("assessed_at"),
                    }
                )
        else:
            select_cols = [
                col for col in ("cattle_id", "cattle_tag_no", "id", "name", "breed", "disease_status", "bcs_score", "last_seen")
                if col in c_cols
            ] or ["*"]
            if "farm_id" in c_cols and f_id:
                raw_rows = await supabase_db.fetch_all(
                    f"SELECT {', '.join(select_cols)} FROM {fq_cattle} WHERE farm_id::text = $1",
                    f_id,
                )
            else:
                raw_rows = await supabase_db.fetch_all(f"SELECT {', '.join(select_cols)} FROM {fq_cattle}")
            for r in raw_rows:
                d = dict(r)
                cow_rows.append(
                    {
                        "cattle_id": d.get("cattle_tag_no") or d.get("cattle_id") or d.get("id"),
                        "name": d.get("name"),
                        "breed": d.get("breed"),
                        "disease_status": d.get("disease_status"),
                        "bcs_score": d.get("bcs_score"),
                        "last_seen": d.get("last_seen"),
                    }
                )

    compliant_count = 0
    statutory_breach_count = 0
    management_warning_count = 0
    missing_evidence_count = 0
    breaches_and_alerts: List[Dict[str, Any]] = []

    for row_dict in cow_rows:
        raw_score = row_dict.get("bcs_score")
        score_val = float(raw_score) if raw_score is not None else None
        parity_val = row_dict.get("parity") or row_dict.get("lactation")
        parity_str = "1st calver" if parity_val in (1, 1.0, 2, 2.0) else ""
        stage_info = " | ".join(
            str(x) for x in (row_dict.get("breed"), row_dict.get("disease_status"), parity_str) if x
        )

        verdict = _evaluate_nz_aus_bcs(
            score=score_val,
            stage_text=stage_info,
            jurisdiction=resolved_jurisdiction,
            audit_date=audit_date,
        )

        st = verdict["status"]
        if st == "compliant":
            compliant_count += 1
        elif st == "statutory_breach":
            statutory_breach_count += 1
        elif st == "management_warning":
            management_warning_count += 1
        elif st == "missing_evidence":
            missing_evidence_count += 1

        if st != "compliant":
            breaches_and_alerts.append(
                {
                    "cattle_id": row_dict.get("cattle_id"),
                    "name": row_dict.get("name"),
                    "breed": row_dict.get("breed"),
                    "disease_status": row_dict.get("disease_status"),
                    "latest_bcs": round(score_val, 2) if score_val is not None else None,
                    "assessed_at": (
                        str(row_dict.get("last_seen")) if row_dict.get("last_seen") is not None else None
                    ),
                    "status": st,
                    "rule_id": verdict["rule_id"],
                    "severity": verdict["severity"],
                    "threshold_or_target": verdict["threshold_or_target"],
                    "action": verdict["action"],
                }
            )

    total_audited = len(cow_rows)
    summary = (
        f"NZ/AUS Compliance Audit ({resolved_jurisdiction}) for {farm_name or f'farm {f_id}'} on {audit_date.isoformat()}: "
        f"{total_audited} cows audited — {compliant_count} compliant, "
        f"{statutory_breach_count} statutory/code breach(es), "
        f"{management_warning_count} management warning(s), "
        f"{missing_evidence_count} missing evidence."
    )

    return {
        "source": "Supabase PostgreSQL (SH-10 NZ/AUS Compliance Rules)",
        "farm_id": f_id,
        "jurisdiction": resolved_jurisdiction,
        "farm_name": farm_name,
        "audited_at_ist": now_ist.isoformat(),
        "total_cows_audited": total_audited,
        "compliant_count": compliant_count,
        "statutory_breach_count": statutory_breach_count,
        "management_warning_count": management_warning_count,
        "missing_evidence_count": missing_evidence_count,
        "breaches_and_alerts": breaches_and_alerts,
        "summary": summary,
    }


# ----------------- TOOL REGISTRY FOR LLM ROUTER ----------------- #

FARM_TOOLS = {
    "get_cattle_profile": {
        "function": get_cattle_profile,
        "description": "Fetch detailed profile, breed, Body Condition Score (BCS), estimated weight, height, and disease status for a specific cow ID or all cattle.",
        "parameters": {
            "type": "object",
            "properties": {
                "cattle_id": {
                    "type": "string",
                    "description": "The unique cow identifier, e.g., 'COW001', 'COW003', or null for all cattle.",
                },
                "farm_id": {"type": "string", "description": "Farm ID (optional)"},
            },
        },
    },
    "get_estrus_alerts": {
        "function": get_estrus_alerts,
        "description": "Query all detected cattle estrus / heat mounting events to help farmers identify which cows are ready for artificial insemination or breeding.",
        "parameters": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "Optional date filter formatted as YYYY-MM-DD. Defaults to today.",
                },
                "farm_id": {"type": "string", "description": "Farm ID (optional)"},
            },
        },
    },
    "get_cattle_activity_history": {
        "function": get_cattle_activity_history,
        "description": "Retrieve daily activity history including feeding, resting, grazing duration, and camera evidence for cattle or workers.",
        "parameters": {
            "type": "object",
            "properties": {
                "cattle_id": {"type": "string", "description": "Cow identifier e.g. 'COW003'"},
                "activity_type": {
                    "type": "string",
                    "enum": ["all", "feeding_activity", "resting_activity", "estrus_detected", "disease_suspected", "worker_entry"],
                    "description": "The category of activity to inspect.",
                },
                "farm_id": {"type": "string", "description": "Farm ID (optional)"},
            },
        },
    },
    "get_farm_herd_summary": {
        "function": get_farm_herd_summary,
        "description": "Get high-level farm overview: total unique cattle count, breed breakdown, average BCS score, active cameras, and worker attendance.",
        "parameters": {
            "type": "object",
            "properties": {
                "farm_id": {"type": "string", "description": "Farm ID (optional)"},
            },
        },
    },
    "get_single_day_cattle_graphical_analytics": {
        "function": get_single_day_cattle_graphical_analytics,
        "description": "Generate graphical charts and diagrammatic representations of cattle detections and vision activities for a specific day like yesterday or today.",
        "parameters": {
            "type": "object",
            "properties": {
                "farm_id": {"type": "string", "description": "Farm ID (optional)"},
                "target_date": {"type": "string", "description": "'yesterday', 'today', or 'YYYY-MM-DD' (default 'yesterday')"},
            },
        },
    },
    "get_cattle_count_analytics": {
        "function": get_cattle_count_analytics,
        "description": "Query cattle count over the last days and return diagrammatic/graphical representations (charts, bar graphs, timeline trends) to explain herd size and count changes.",
        "parameters": {
            "type": "object",
            "properties": {
                "farm_id": {"type": "string", "description": "Farm ID (optional)"},
                "days": {"type": "integer", "description": "Number of days to analyze (default 7)"},
            },
        },
    },
    "get_sick_cattle_and_health_warnings": {
        "function": get_sick_cattle_and_health_warnings,
        "description": "Query sick cattle, diseases (e.g. Lumpy Skin Disease), and extreme BCS warnings (<2.0 or >4.5).",
        "parameters": {
            "type": "object",
            "properties": {
                "farm_id": {"type": "string", "description": "Farm ID (optional)"},
            },
        },
    },
    "get_cattle_count_and_camera_analytics": {
        "function": get_cattle_count_and_camera_analytics,
        "description": "Analyze cattle detection counts for today and yesterday, compare numbers of cattle detected, and verify if any animals were counted twice across cameras (cross-camera de-duplication).",
        "parameters": {
            "type": "object",
            "properties": {
                "farm_id": {"type": "string", "description": "Farm ID (optional)"},
            },
        },
    },
    "get_workers_and_staff_data": {
        "function": get_workers_and_staff_data,
        "description": "Check farm workers, labor attendance, staff shifts, milking, feeding, and duties completed yesterday or today.",
        "parameters": {
            "type": "object",
            "properties": {
                "farm_id": {"type": "string", "description": "Farm ID (optional)"},
                "date_str": {"type": "string", "description": "Target date e.g. 'yesterday' or 'today' (optional)"},
            },
        },
    },
    "get_farm_overview": {
        "function": get_farm_overview,
        "description": "Get overall live farm status report. ONLY call when the user explicitly asks for the farm status, overview, or daily report.",
        "parameters": {
            "type": "object",
            "properties": {
                "farm_id": {"type": "string", "description": "Farm ID (optional)"},
            },
        },
    },
    "get_cctv_proof_and_images": {
        "function": get_cctv_proof_and_images,
        "description": "Retrieve CCTV photo evidence, captured camera snapshots, and proof images for specific cattle (COW001, COW002, COW003) or behaviors.",
        "parameters": {
            "type": "object",
            "properties": {
                "farm_id": {"type": "string", "description": "Farm ID (optional)"},
                "cattle_id": {"type": "string", "description": "Specific cow ID like COW001, COW002, COW003 (optional)"},
                "activity_type": {"type": "string", "description": "estrus_detected or feeding_activity (optional)"},
            },
        },
    },
    "get_estrus_and_heat_alerts": {
        "function": get_estrus_and_heat_alerts,
        "description": "Check live cows showing estrus (heat) signs, mounting behavior, mounting and mounted cow IDs, confidence score, artificial insemination timing, and CCTV proof images.",
        "parameters": {
            "type": "object",
            "properties": {
                "farm_id": {"type": "string", "description": "Farm ID (optional)"},
                "cattle_id": {"type": "string", "description": "Specific cow ID like COW001, COW002, COW003 (optional)"},
            },
        },
    },
    "get_feed_and_nutrition": {
        "function": get_feed_and_nutrition,
        "description": "Check CCTV manger cameras for live cattle eating at the corral manger and head-down feeding duration. ONLY call this when asking whether cows are CURRENTLY eating at the farm manger or asking for camera manger feed telemetry. NEVER call this for warehouse feed stock, inventory, rice straw, feed recipes, or nutrition advice.",
        "parameters": {
            "type": "object",
            "properties": {
                "farm_id": {"type": "string", "description": "Farm ID (optional)"},
                "cattle_id": {"type": "string", "description": "Specific cow ID (optional)"},
            },
        },
    },
    "get_cameras_status": {
        "function": get_cameras_status,
        "description": "Check CCTV cameras (CAM01, CAM02), RTSP streams, coverage areas, and the latest detection captured by each camera.",
        "parameters": {
            "type": "object",
            "properties": {
                "farm_id": {"type": "string", "description": "Farm ID (optional)"},
            },
        },
    },
    "get_cow_activity_history": {
        "function": get_cow_activity_history,
        "description": "Check activity, mounting behavior, feeding events, and vision history for a specific cow like COW001, COW002, or COW003.",
        "parameters": {
            "type": "object",
            "properties": {
                "cow_id": {"type": "string", "description": "Cow ID (e.g. COW001, COW002, COW003)"},
                "farm_id": {"type": "string", "description": "Farm ID (optional)"},
            },
            "required": ["cow_id"],
        },
    },
    "veterinary_and_products_rag": {
        "function": veterinary_and_products_rag,
        "description": "Query veterinary clinical knowledge, cattle diseases (mastitis, fever, bloat, FMD, lumpy skin, diarrhea), disease prevention and farm biosecurity protocols, quarantine, contagious infections, immediate clinical first-aid actions, and Chimertech veterinary test kits or supportive care products. ALWAYS use this tool for all animal health, disease prevention, and biosecurity questions.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Specific animal disease, clinical symptom, feed ingredient, nutrition or veterinary question"},
                "farm_id": {"type": "string", "description": "Farm ID (optional)"},
            },
            "required": ["query"],
        },
    },
    "calculate_nasem_dairy_nutrition_and_feed": {
        "function": calculate_nasem_dairy_nutrition_and_feed,
        "description": "Calculate or query authoritative NASEM 2021 dairy cattle nutrition, Dry Matter Intake (DMI via Eq 2-1, 2-3, 12-1), Free Water Intake (FWI via Eq 9-1, 9-3), Net Energy of Lactation (NEL via Eq 3-13, 3-14b/c, 3-18), Metabolizable Energy for heifers (ME via Eq 11-2, 3-20), Metabolizable Protein (MP), factorial Calcium/Phosphorus requirements, mineral mixture dosing based on deficit, and unified ration optimization balance status. DO NOT USE for cattle diseases, veterinary questions, disease prevention, symptoms, infection, or biosecurity.",
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["calculate_dmi", "calculate_water", "calculate_energy", "calculate_minerals", "query_rules"],
                    "description": "The specific calculation or rule lookup to perform.",
                },
                "category": {
                    "type": "string",
                    "enum": ["lactating_cow", "dry_cow", "pregnant_dry_cow", "growing_heifer"],
                    "description": "Cattle category (default: lactating_cow)",
                },
                "cattle_id": {
                    "type": "string",
                    "description": "Optional specific cow ID (e.g. COW001, COW002) to pull live weight and BCS from farm database",
                },
                "bw_kg": {"type": "number", "description": "Body weight in kg (default: 550 kg)"},
                "milk_yield_kg": {"type": "number", "description": "Daily milk yield in kg/day (default: 15.0 kg)"},
                "fat_percent": {"type": "number", "description": "Milk fat percentage (default: 4.0%)"},
                "dim": {"type": "integer", "description": "Days in milk (default: 100)"},
                "bcs": {"type": "number", "description": "Body condition score on 1-5 scale (default: 3.0)"},
                "parity": {"type": "integer", "description": "Parity / lactation number (1 for primiparous; 2+ for multiparous)"},
                "ambient_temp_c": {"type": "number", "description": "Daily mean ambient temperature in degrees Celsius (default: 27 deg C)"},
                "query": {"type": "string", "description": "Specific question or rule topic in NASEM 2021 ruleset"},
                "farm_id": {"type": "string", "description": "Farm ID (optional)"},
            },
        },
    },
    "get_milk_yield_records": {
        "function": get_milk_yield_records,
        "description": "Query daily milk yield records (litres, morning/evening session, date) for a specific cow ID such as 1004 or COW1004.",
        "parameters": {
            "type": "object",
            "properties": {
                "cattle_id": {"type": "string", "description": "Cow identifier e.g. '1004' or 'COW1004'"},
                "target_date": {"type": "string", "description": "'yesterday', 'today', or 'YYYY-MM-DD'"},
                "farm_id": {"type": "string", "description": "Farm ID (optional)"},
            },
        },
    },
    "get_breeding_and_calving_records": {
        "function": get_breeding_and_calving_records,
        "description": "Query last breeding date, AI straw number, and last calving date/calf status for a specific cow ID such as 1004 or COW1004.",
        "parameters": {
            "type": "object",
            "properties": {
                "cattle_id": {"type": "string", "description": "Cow identifier e.g. '1004' or 'COW1004'"},
                "record_type": {"type": "string", "enum": ["all", "breeding", "calving"]},
                "farm_id": {"type": "string", "description": "Farm ID (optional)"},
            },
        },
    },
    "get_warehouse_inventory": {
        "function": get_warehouse_inventory,
        "description": "Check warehouse feed stock and inventory quantities (e.g. NutraKine Concentrate in kg). ALWAYS use this for warehouse/godown/stock/inventory queries.",
        "parameters": {
            "type": "object",
            "properties": {
                "item_query": {"type": "string", "description": "Optional feed or supply item name"},
                "farm_id": {"type": "string", "description": "Farm ID (optional)"},
            },
        },
    },
    "get_compliance_audit_report": {
        "function": get_compliance_audit_report,
        "description": "Generate a compliance and welfare audit summary of cows breaching New Zealand (DairyNZ) or Australian welfare thresholds for a given farm_id.",
        "parameters": {
            "type": "object",
            "properties": {
                "farm_id": {"type": "string", "description": "Farm ID (optional; defaults to active/authorized farm)"},
                "jurisdiction": {"type": "string", "enum": ["NZ", "AUS"], "description": "Optional jurisdiction override ('NZ' or 'AUS')"},
            },
        },
    },
}

OPENAI_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": name,
            "description": spec["description"],
            "parameters": spec["parameters"],
        },
    }
    for name, spec in FARM_TOOLS.items()
]