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

def _is_valid_id(val: Any) -> bool:
    """Filters out empty values and Swagger UI's auto-generated 'string' dummy placeholders."""
    if not val:
        return False
    s = str(val).strip()
    return bool(s and s.lower() not in ("string", "null", "undefined", "none", "optional", "empty"))

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
    if _is_valid_id(explicit_uid):
        return str(explicit_uid).strip()

    if _is_valid_id(explicit_user_id):
        return str(explicit_user_id).strip()

    # Check custom headers
    header_uid = request.headers.get("X-User-UID") or request.headers.get("X-UID")
    if _is_valid_id(header_uid):
        return str(header_uid).strip()

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
                if _is_valid_id(jwt_uid):
                    logger.info(f"[Auth] Extracted UID from JWT token: {jwt_uid}")
                    return str(jwt_uid)

        # If not a valid JWT, token is passed as raw UID string
        if _is_valid_id(token):
            return token

    return None


async def resolve_user_farm(
    uid: Optional[str] = None,
    explicit_farm_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Resolves the authentic user and their assigned farm data from Supabase:
    1. If UID is provided (via JWT token, custom header, or param):
       - Queries public.users for the matching user record (by uid or integer id)
       - Queries public.farms for the farm owned by that user (user_id = users.id)
       - If user not found, returns clear unauthenticated error (no silent fallback).
    2. If explicit farm_id is provided, checks public.farms directly (for guest/demo access).
    3. If neither is provided, returns clear authentication required error.
    """
    # 1. Resolve by authentic UID
    if _is_valid_id(uid):
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
            if not user:
                logger.warning(f"[Auth] UID '{clean_uid}' was provided but does not exist in public.users")
                return {
                    "authenticated": False,
                    "uid": clean_uid,
                    "user_id": None,
                    "user_name": None,
                    "farm_id": None,
                    "farm_name": None,
                    "error": f"Invalid User UID: No account found with UID '{clean_uid}' in Supabase."
                }

            # User found, now fetch their registered farm
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
                    "user_name": user.get("name") or "Farmer",
                    "farm_id": str(farm.get("farm_id")),
                    "farm_name": farm.get("farm_name", "Registered Farm"),
                    "location": f"{farm.get('district', '')}, {farm.get('state', '')}".strip(", ")
                }
            else:
                logger.warning(f"[Auth] User '{user.get('name')}' (ID: {user['id']}) has no farm linked in public.farms")
                return {
                    "authenticated": True,
                    "uid": user.get("uid") or clean_uid,
                    "user_id": user.get("id"),
                    "user_name": user.get("name") or "Farmer",
                    "farm_id": None,
                    "farm_name": "No Farm Registered",
                    "location": "",
                    "error": f"User '{user.get('name')}' is authenticated, but no farm is registered under this account yet."
                }
        except Exception as e:
            logger.error(f"[Auth] Database error querying user by UID '{clean_uid}': {e}")
            return {
                "authenticated": False,
                "error": f"Database error resolving user UID: {str(e)}"
            }

    # 2. Resolve by explicit farm_id (Direct testing or guest farm access)
    if _is_valid_id(explicit_farm_id):
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
                    "user_name": "Guest Farmer",
                    "farm_id": str(farm.get("farm_id")),
                    "farm_name": farm.get("farm_name", f"Farm {clean_fid}"),
                    "location": f"{farm.get('district', '')}, {farm.get('state', '')}".strip(", ")
                }
            else:
                return {
                    "authenticated": False,
                    "error": f"Farm ID '{clean_fid}' not found in database."
                }
        except Exception as e:
            logger.error(f"[Auth] Error querying farm by ID '{clean_fid}': {e}")
            return {
                "authenticated": False,
                "error": f"Database error resolving farm_id: {str(e)}"
            }

    # 3. Clean Authentication Required (No silent fallback to arbitrary users)
    return {
        "authenticated": False,
        "uid": None,
        "user_id": None,
        "user_name": None,
        "farm_id": None,
        "farm_name": None,
        "error": "Authentication required: Please provide a valid Supabase Auth Bearer token, 'uid', or 'farm_id' to access farm data."
    }
