# app.core.deps.py
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.core.config import settings
from uuid import UUID

from app.core.token_blacklist import is_jti_blacklisted
from app.core.policy_engine import evaluate_policy
from app.models.organization import Vendor
from app.db.session import SessionLocal
from app.models.identity import User
# 1. This tells FastAPI to look for a 'Bearer' token in the Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login") 

DATABASE_URL = settings.DATABASE_URL
# HTTP Bearer token scheme
security = HTTPBearer()
engine = create_engine(DATABASE_URL)

# app.core.deps.py
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 🔥 NEW: get_vendor (recommended approach)
def get_vendor(
    request: Request,
    db: Session = Depends(get_db),
) -> Vendor:
    host = request.headers.get("host")

    if not host:
        raise HTTPException(status_code=400, detail="Missing host header")

    # remove port if exists
    host = host.split(":")[0]

    parts = host.split(".")
    print("DEBUG ### parts", parts)

    # Example:
    # test.localhost → ["test", "localhost"]
    # test.myapp.com → ["test", "myapp", "com"]

    if len(parts) < 2:
        raise HTTPException(status_code=400, detail="Invalid host")

    subdomain = parts[0]
    print("DEBUG ### subdomain", subdomain)

    # Optional: skip root domain (e.g. localhost or main domain)
    if subdomain in ["www", "localhost"]:
        raise HTTPException(status_code=404, detail="Organization not found")

    vendor = db.query(Vendor).filter(Vendor.slug == subdomain).first()

    print("DEBUG ### Found vendor:", vendor.slug if vendor else None)

    if not vendor:
        raise HTTPException(status_code=404, detail="Organization not found")

    return vendor

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db), vendor: Vendor = Depends(get_vendor)):
    
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    print("PAYLOAD:", payload)

    jti = payload.get("jti")

    if is_jti_blacklisted(jti):
        raise HTTPException(status_code=401, detail="Token revoked")
    
    user_id = payload.get("user_id")

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == UUID(user_id)).first()
    print("TOKEN SUB:", user_id, type(user_id))
    print("DB QUERY RESULT:", db.query(User).all())

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 🔥 CRITICAL: tenant isolation
    if user.vendor_id != vendor.id:
        raise HTTPException(status_code=403, detail="Cross-tenant access denied")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")
    print("DB expects:", type(user.id))
    print("USER ID IN DB:", user.id, type(user.id))
    print("TOKEN ID:", user_id, type(user_id))
    

    return user

def get_current_context(token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

    if not payload.get("user_id"):
        raise HTTPException(status_code=401, detail="Invalid token")

    return {
        "user_id": payload.get("user_id"),
        "vendor_id": payload.get("vendor_id"),
        "location_id": payload.get("location_id"),
    }

def SecurityChecker(required_permission: str):
    def checker(
        context=Depends(get_current_context),
        db=Depends(get_db),
    ):
        user_id = context["user_id"]
        vendor_id = context["vendor_id"]

        has_permission = db.execute(
            """
            SELECT 1
            FROM user_groups ug
            JOIN groups g ON ug.group_id = g.id
            JOIN group_permissions gp ON g.id = gp.group_id
            JOIN permissions p ON gp.permission_id = p.id
            WHERE ug.user_id = :user_id
            AND p.code = :perm
            AND g.vendor_id = :vendor_id
            AND p.vendor_id = :vendor_id
            """,
            {
                "user_id": user_id,
                "perm": required_permission,
                "vendor_id": vendor_id,
            },
        ).first()

        if not has_permission:
            raise HTTPException(status_code=403, detail="Forbidden")

        return context

    return checker

def require_permission(permission: str):

    def checker(context=Depends(get_current_context)):

        if permission not in context["permissions"]:
            raise HTTPException(status_code=403, detail="Forbidden")

        return context

    return checker

def authorize(user, permission, resource, policies):

    if permission not in user.permissions:
        return False

    for policy in policies:
        if not evaluate_policy(policy, user, resource):
            return False

    return True

def has_permission(user_permissions, required):

    if required in user_permissions:
        return True

    resource = required.split(":")[0]

    wildcard = f"{resource}:*"

    if wildcard in user_permissions:
        return True

    return False