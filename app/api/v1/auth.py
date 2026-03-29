# app/api/v1/auth.py
from fastapi import APIRouter, Depends, Header, HTTPException
from jose import jwt, JWTError
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.session import UserSession
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
    
    refresh_token = create_refresh_token(user)

    payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
    refresh_jti = payload["jti"]

    session = UserSession(
        user_id=user.id,
        refresh_jti=refresh_jti,
    )

    db.add(session)
    db.commit()

    return TokenResponse(
        access_token=create_access_token(user),
        refresh_token=refresh_token,
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")

    jti = payload.get("jti")
    user_id = payload.get("user_id")
    print("DEBUG ### jti", jti)

    session = db.query(UserSession).filter(UserSession.refresh_jti == jti).first()

    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")

    if session.is_revoked:
        raise HTTPException(status_code=401, detail="Session revoked")

    user = db.get(User, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 🔄 ROTATE TOKEN
    new_refresh = create_refresh_token(user)
    new_payload = jwt.decode(new_refresh, SECRET_KEY, algorithms=[ALGORITHM])
    new_jti = new_payload["jti"]

    session.refresh_jti = new_jti
    session.last_used_at = datetime.now(timezone.utc)

    db.commit()

    return TokenResponse(
        access_token=create_access_token(user),
        refresh_token=new_refresh,
    )



@router.post("/logout")
def logout(
    Authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    try:
        token = Authorization.split(" ")[1]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token format")

    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    jti = payload["jti"]

    session = db.query(UserSession).filter(
        UserSession.refresh_jti == jti
    ).first()

    if session:
        session.is_revoked = True
        db.commit()

    return {"message": "Logged out"}


@router.get("/me", response_model=UserMeResponse)
def get_me(user=Depends(get_current_user)):
    return user

@router.post("/logout-all")
def logout_all(user=Depends(get_current_user), db: Session = Depends(get_db)):

    db.query(UserSession).filter(UserSession.user_id == user.id).update(
        {"is_revoked": True}
    )

    db.commit()

    return {"message": "All sessions revoked"}