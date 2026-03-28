# app/api/v1/auth.py
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.schemas.auth import LoginRequest, TokenResponse
from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
)
from app.crud.user import get_user_by_email
from app.db.session import SessionLocal
from app.core.security import SECRET_KEY, ALGORITHM
from app.core.deps import get_current_user
from app.models.identity import User
from app.models.organization import Vendor

router = APIRouter(prefix="/auth", tags=["Auth"])

# app/api/v1/auth.py

# DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_vendor_slug_from_subdomain(request: Request):
    host = request.headers.get("host", "")
    # Example host: "apple.omni-iam.me:8000" or "apple.yourdomain.com"
    parts = host.split(".")
    
    # If you expect 'apple.domain.com', the slug is the first part
    if len(parts) > 2:
        return parts[0]  # returns "apple"
    
    raise HTTPException(status_code=400, detail="Vendor subdomain missing")

# 🔑 LOGIN
@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db), vendor_slug: str = Depends(get_vendor_slug_from_subdomain)):

    vendor = db.query(Vendor).filter(Vendor.slug == vendor_slug).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Organization not found")
    
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
        raise HTTPException(status_code=401, detail="Invalid token")

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")

    user_id = payload.get("sub")

    user = db.query(User).get(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return TokenResponse(
        access_token=create_access_token(user),
        refresh_token=create_refresh_token(user),
    )

@router.post("/logout")
def logout(token: str):
    # store token in blacklist
    return {"message": "Logged out"}



@router.get("/me")
def get_me(user=Depends(get_current_user)):
    return user