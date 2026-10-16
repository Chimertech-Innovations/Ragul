import logging
import re
from typing import Optional, Dict, Any
import bcrypt
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from .database.supabase_client import supabase_db

logger = logging.getLogger("ragul_auth")
router = APIRouter(prefix="/api/auth", tags=["auth"])

class LoginRequest(BaseModel):
    phone: str
    password: str

class RegisterRequest(BaseModel):
    phone: str
    password: str
    full_name: str
    farm_name: Optional[str] = None
    location: Optional[str] = "Tamil Nadu, India"

class ResetPasswordRequest(BaseModel):
    phone: str
    new_password: str

def normalize_phone_variants(raw_phone: str) -> list[str]:
    """Generates standard phone format variations to match database records."""
    cleaned = re.sub(r'[\s\-\(\)]', '', raw_phone.strip())
    variants = [cleaned]
    if cleaned.startswith("+91"):
        variants.append(cleaned[3:])
    elif cleaned.startswith("91") and len(cleaned) == 12:
        variants.append(cleaned[2:])
        variants.append("+" + cleaned)
    elif len(cleaned) == 10:
        variants.append("+91" + cleaned)
        variants.append("91" + cleaned)
    return list(dict.fromkeys(variants))

def verify_password(plain_password: str, stored_hash: str) -> bool:
    """Securely verifies password using standard bcrypt with support for $2b$, $2a$, $2y$."""
    if not stored_hash or not plain_password:
        return False

    # 1. Direct match (in case any dev account was plaintext)
    if plain_password == stored_hash:
        return True

    plain_bytes = plain_password.encode("utf-8")

    # 2. Standard bcrypt verification
    try:
        hash_bytes = stored_hash.encode("utf-8")
        if bcrypt.checkpw(plain_bytes, hash_bytes):
            return True
    except Exception as e:
        logger.warning(f"[Auth] Standard bcrypt check error: {e}")

    # 3. Compatibility fallback: convert $2b$ to $2a$ or vice versa
    try:
        if stored_hash.startswith("$2b$"):
            compat_hash = ("$2a$" + stored_hash[4:]).encode("utf-8")
            if bcrypt.checkpw(plain_bytes, compat_hash):
                return True
        elif stored_hash.startswith("$2a$"):
            compat_hash = ("$2b$" + stored_hash[4:]).encode("utf-8")
            if bcrypt.checkpw(plain_bytes, compat_hash):
                return True
    except Exception as e:
        logger.warning(f"[Auth] Compat bcrypt check error: {e}")

    return False

@router.post("/login")
async def login(req: LoginRequest):
    phone_variants = normalize_phone_variants(req.phone)
    password = req.password.strip()

    logger.info(f"[Auth] Attempting login for phone: {req.phone} (variants: {phone_variants})")

    placeholders = ", ".join(f"${i+1}" for i in range(len(phone_variants)))

    query = f"""
        SELECT 
            u.id as user_id,
            u.farm_id,
            u.phone,
            u.password_hash,
            u.full_name,
            u.role,
            u.is_verified,
            f.farm_code,
            f.farm_name,
            f.owner_name,
            f.owner_phone,
            f.location
        FROM public.users u
        LEFT JOIN public.farms f ON u.farm_id = f.id
        WHERE u.phone IN ({placeholders})
        ORDER BY u.created_at DESC
        LIMIT 1;
    """

    user_record = await supabase_db.fetch_one(query, *phone_variants)

    if not user_record:
        logger.warning(f"[Auth] No user found for phone variants: {phone_variants}")
        raise HTTPException(status_code=404, detail="No registered account found with this phone number.")

    stored_hash = user_record.get("password_hash") or ""
    is_valid = verify_password(password, stored_hash)

    if not is_valid:
        logger.warning(f"[Auth] Invalid password for user {user_record.get('phone')}")
        raise HTTPException(status_code=401, detail="Invalid password for this phone number. Please re-enter your PashuX password.")

    logger.info(f"[Auth] Login successful for user: {user_record.get('full_name')} ({user_record.get('phone')})")

    # Fetch farm cameras and quick counts
    farm_id = user_record.get("farm_id")
    cameras = []
    activity_count = 0
    if farm_id:
        cam_rows = await supabase_db.fetch_all(
            "SELECT id, camera_name, location_description, is_active FROM public.cameras WHERE farm_id = $1",
            farm_id
        )
        cameras = [dict(c) for c in cam_rows]
        activity_count = await supabase_db.fetch_val(
            "SELECT count(*) FROM public.farm_activities WHERE farm_id = $1",
            farm_id
        ) or 0

    return {
        "success": True,
        "message": f"Welcome back, {user_record.get('full_name', 'Farmer')}!",
        "user": {
            "id": str(user_record["user_id"]),
            "phone": user_record["phone"],
            "full_name": user_record["full_name"],
            "role": user_record["role"],
            "farm_id": str(user_record["farm_id"]) if user_record["farm_id"] else None,
            "farm_code": user_record.get("farm_code") or "FARM_MAIN",
            "farm_name": user_record.get("farm_name") or f"{user_record.get('full_name')}'s Dairy Farm",
            "owner_name": user_record.get("owner_name") or user_record.get("full_name"),
            "location": user_record.get("location") or "India",
            "cameras": cameras,
            "activity_count": activity_count
        }
    }

@router.post("/reset-password")
async def reset_password(req: ResetPasswordRequest):
    """Allows user to update/reset their password with a standard bcrypt hash."""
    phone_variants = normalize_phone_variants(req.phone)
    new_password = req.new_password.strip()

    if len(new_password) < 4:
        raise HTTPException(status_code=400, detail="Password must be at least 4 characters long.")

    placeholders = ", ".join(f"${i+1}" for i in range(len(phone_variants)))
    user = await supabase_db.fetch_one(
        f"SELECT id, phone, full_name FROM public.users WHERE phone IN ({placeholders}) LIMIT 1",
        *phone_variants
    )
    if not user:
        raise HTTPException(status_code=404, detail="No registered account found with this phone number.")

    # Generate standard bcrypt hash
    salt = bcrypt.gensalt(rounds=12)
    new_hash = bcrypt.hashpw(new_password.encode("utf-8"), salt).decode("utf-8")

    await supabase_db.execute(
        "UPDATE public.users SET password_hash = $1 WHERE id = $2",
        new_hash, user["id"]
    )

    logger.info(f"[Auth] Password reset successfully for {user['phone']}")
    return {
        "success": True,
        "message": f"Password updated successfully for {user.get('full_name')} ({user['phone']})!"
    }

@router.post("/register")
async def register(req: RegisterRequest):
    phone_clean = re.sub(r'[\s\-\(\)]', '', req.phone.strip())
    password = req.password.strip()
    full_name = req.full_name.strip()
    farm_name = (req.farm_name or f"{full_name}'s Farm").strip()
    
    existing = await supabase_db.fetch_one("SELECT id FROM public.users WHERE phone = $1", phone_clean)
    if existing:
        raise HTTPException(status_code=400, detail="Account with this phone number already exists. Please log in.")

    # 1. Create farm
    farm_code = f"FARM_{phone_clean[-4:]}"
    farm_id = await supabase_db.fetch_val(
        """
        INSERT INTO public.farms (farm_code, farm_name, owner_name, owner_phone, location)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING id;
        """,
        farm_code, farm_name, full_name, phone_clean, req.location
    )

    # 2. Create user with hashed password via standard bcrypt
    salt = bcrypt.gensalt(rounds=12)
    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    user_id = await supabase_db.fetch_val(
        """
        INSERT INTO public.users (farm_id, phone, password_hash, full_name, role, is_verified)
        VALUES ($1, $2, $3, $4, 'owner', TRUE)
        RETURNING id;
        """,
        farm_id, phone_clean, hashed_pw, full_name
    )

    return {
        "success": True,
        "message": "Account created successfully!",
        "user": {
            "id": str(user_id),
            "phone": phone_clean,
            "full_name": full_name,
            "role": "owner",
            "farm_id": str(farm_id),
            "farm_code": farm_code,
            "farm_name": farm_name
        }
    }

@router.get("/demo-accounts")
async def get_demo_accounts():
    """Lists registered accounts so the user can easily select or verify."""
    rows = await supabase_db.fetch_all("""
        SELECT u.phone, u.full_name, u.role, f.farm_code, f.farm_name, f.id as farm_id
        FROM public.users u
        LEFT JOIN public.farms f ON u.farm_id = f.id
        ORDER BY u.created_at ASC
        LIMIT 5;
    """)
    return [
        {
            "phone": r["phone"],
            "full_name": r["full_name"],
            "role": r["role"],
            "farm_code": r["farm_code"],
            "farm_name": r["farm_name"],
            "farm_id": str(r["farm_id"]) if r["farm_id"] else None
        }
        for r in rows
    ]
