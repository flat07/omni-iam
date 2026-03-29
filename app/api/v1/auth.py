# app/api/v1/auth.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from datetime import datetime, timezone

from app.schemas.auth import LoginRequest, TokenResponse
from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
)
from app.crud.user import get_user_by_email
from app.core.config import settings
from app.core.deps import get_current_user, get_vendor, get_db
from app.models.identity import User
from app.models.organization import Vendor
from app.schemas.user import UserMeResponse

from app.core.token_blacklist import blacklist_jti


SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM

router = APIRouter(prefix="/auth", tags=["Auth"])

# app/api/v1/auth.py

# 🔑 LOGIN
@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db), vendor: Vendor = Depends(get_vendor)):
    print("DEBUG ### vendor.slug:", vendor.slug)
    all_vendors = db.query(Vendor).all()
    print(f"DEBUG ### All vendors in DB: {[v.slug for v in all_vendors]}")
    
    user = get_user_by_email(db, data.email, vendor.id)

    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="User inactive")

    return TokenResponse(
        access_token=create_access_token(user),
        refresh_token=create_refresh_token(user),
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")

    user_id = payload.get("user_id")

    user = db.get(User, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return TokenResponse(
        access_token=create_access_token(user),
        refresh_token=create_refresh_token(user),
    )

@router.post("/logout")
def logout(token: str):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    jti = payload.get("jti")

    if not jti:
        raise HTTPException(status_code=401, detail="Invalid token")

    exp = payload.get("exp")

    expire_time = datetime.fromtimestamp(exp, tz=timezone.utc)
    ttl = int((expire_time - datetime.now(timezone.utc)).total_seconds())

    blacklist_jti(jti, ttl)

    return {"message": "Logged out"}


@router.get("/me", response_model=UserMeResponse)
def get_me(user=Depends(get_current_user)):
    return user
