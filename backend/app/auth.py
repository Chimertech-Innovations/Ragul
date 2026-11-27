import os
import json
import base64
import logging
from typing import Optional, Dict, Any
from fastapi import Request
from .database.supabase_client import supabase_db

logger = logging.getLogger("ragul_auth")

def _decode_jwt_payload_safe(token: str) -> Optional[Dict[str, Any]]:
    """Safely decodes JWT payload using standard Python base64 & json (zero third-party dependencies)."""
    try:
        parts = token.split(".")
        if len(parts) >= 2:
            payload_b64 = parts[1]
            rem = len(payload_b64) % 4
            if rem > 0:
                payload_b64 += "=" * (4 - rem)
            decoded = base64.urlsafe_b64decode(payload_b64.encode("ascii"))
            return json.loads(decoded.decode("utf-8"))
    except Exception as e:
        logger.debug(f"[Auth] Standard JWT payload decode notice: {e}")
    return None

def extract_uid_from_request(
    request: Request,
    explicit_uid: Optional[str] = None,
    explicit_user_id: Optional[str] = None
) -> Optional[str]:
    """
    Extracts User UID from multiple client sources in order of priority:
    1. Direct form or JSON parameter: 'uid' or 'user_id'
    2. Header: 'X-User-UID' or 'X-UID'
    3. Authorization Header: 'Bearer <token_or_uid>'
       - Decodes Supabase JWT token payload to extract 'sub' (User UID)
       - If not a JWT, treats the Bearer token as a raw UID string
    """
    if explicit_uid and str(explicit_uid).strip():
        return str(explicit_uid).strip()

    if explicit_user_id and str(explicit_user_id).strip():
        return str(explicit_user_id).strip()

    # Check custom headers
    header_uid = request.headers.get("X-User-UID") or request.headers.get("X-UID")
    if header_uid and header_uid.strip():
        return header_uid.strip()

    # Check Authorization header
    auth_header = request.headers.get("Authorization") or request.headers.get("authorization")
    if auth_header and auth_header.strip():
        token = auth_header.strip()
        if token.lower().startswith("bearer "):
            token = token[7:].strip()

        # Check if token is a 3-part JWT
        if token.count(".") == 2:
            payload = _decode_jwt_payload_safe(token)
            if payload:
                jwt_uid = payload.get("sub") or payload.get("user_id") or payload.get("uid")
                if jwt_uid:
                    logger.info(f"[Auth] Extracted UID from JWT token: {jwt_uid}")
                    return str(jwt_uid)

        # If not a valid JWT, token is passed as raw UID string
        if token:
            return token

    return None


async def resolve_user_farm(
    uid: Optional[str] = None,
    explicit_farm_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Resolves the authentic user and their assigned farm data from Supabase:
    1. If UID is provided:
       - Queries public.users for the matching user record
       - Queries public.farms for the farm owned by that user (user_id = users.id)
    2. If explicit farm_id is provided, checks public.farms directly
    3. Fallback: Resolves to the first available farm in the database
    """
    # 1. Resolve by UID
    if uid and str(uid).strip():
        clean_uid = str(uid).strip()
        try:
            user = await supabase_db.fetch_one(
                """
                SELECT id, uid, name, phone_number, village, district, state 
                FROM public.users 
                WHERE uid = $1 OR id::text = $1 
                LIMIT 1;
                """,
                clean_uid
            )
            if user:
                farm = await supabase_db.fetch_one(
                    """
                    SELECT id as farm_id, farm_name, address, district, state 
                    FROM public.farms 
                    WHERE user_id = $1 
                    LIMIT 1;
                    """,
                    user["id"]
                )
                if farm:
                    logger.info(f"[Auth] UID '{clean_uid}' authenticated -> User '{user.get('name')}', Farm '{farm.get('farm_name')}' (ID: {farm.get('farm_id')})")
                    return {
                        "authenticated": True,
                        "uid": user.get("uid") or clean_uid,
                        "user_id": user.get("id"),
                        "user_name": user.get("name"),
                        "farm_id": str(farm.get("farm_id")),
                        "farm_name": farm.get("farm_name"),
                        "location": f"{farm.get('district', '')}, {farm.get('state', '')}".strip(", ")
                    }
                else:
                    logger.warning(f"[Auth] UID '{clean_uid}' found in public.users, but no farm linked to user_id {user['id']}")
                    return {
                        "authenticated": True,
                        "uid": user.get("uid") or clean_uid,
                        "user_id": user.get("id"),
                        "user_name": user.get("name"),
                        "farm_id": "",
                        "farm_name": "Unassigned Farm",
                        "location": ""
                    }
        except Exception as e:
            logger.error(f"[Auth] Error querying user by UID '{clean_uid}': {e}")

    # 2. Resolve by explicit farm_id
    if explicit_farm_id and str(explicit_farm_id).strip():
        clean_fid = str(explicit_farm_id).strip()
        try:
            farm = await supabase_db.fetch_one(
                "SELECT id as farm_id, farm_name, district, state FROM public.farms WHERE id::text = $1 LIMIT 1",
                clean_fid
            )
            if farm:
                return {
                    "authenticated": False,
                    "uid": None,
                    "user_id": None,
                    "user_name": "Farmer",
                    "farm_id": str(farm.get("farm_id")),
                    "farm_name": farm.get("farm_name"),
                    "location": f"{farm.get('district', '')}, {farm.get('state', '')}".strip(", ")
                }
        except Exception as e:
            logger.error(f"[Auth] Error querying farm by ID '{clean_fid}': {e}")

    # 3. Default Fallback
    try:
        first_farm = await supabase_db.fetch_one("SELECT id as farm_id, farm_name, district, state FROM public.farms ORDER BY id ASC LIMIT 1")
        if first_farm:
            return {
                "authenticated": False,
                "uid": None,
                "user_id": None,
                "user_name": "Farmer",
                "farm_id": str(first_farm.get("farm_id")),
                "farm_name": first_farm.get("farm_name", "Dairy Farm"),
                "location": f"{first_farm.get('district', '')}, {first_farm.get('state', '')}".strip(", ")
            }
    except Exception:
        pass

    return {
        "authenticated": False,
        "uid": None,
        "user_id": None,
        "user_name": "Farmer",
        "farm_id": "",
        "farm_name": "Dairy Farm",
        "location": ""
    }
