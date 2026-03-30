# app/api/v1/auth.py
from fastapi import APIRouter, Depends, Header, HTTPException, Request
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
from app.models.audit import AuditLog

from app.models.invite import Invite
from app.schemas.invite import InviteAcceptRequest
from app.core.security import hash_password, utc_now


SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM

# app/api/v1/auth.py
router = APIRouter(prefix="/auth", tags=["auth"])



@router.post("/accept-invite")
def accept_invite(payload: InviteAcceptRequest, db: Session = Depends(get_db)):

    invite = db.query(Invite).filter(Invite.token == payload.token).first()

    if not invite:
        raise HTTPException(status_code=404, detail="Invalid invite token")

    if invite.accepted:
        raise HTTPException(status_code=400, detail="Invite already used")
    
    if invite.expires_at < utc_now():
        raise HTTPException(status_code=400, detail="Invite expired")

    # check user already exists
    existing = db.query(User).filter(User.email == invite.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    user = User(
        email=invite.email,
        password_hash=hash_password(payload.password),
        is_active=True,
        vendor_id=invite.vendor_id
    )

    db.add(user)

    invite.accepted = True
    invite.updated_at = utc_now()

    db.commit()

    return {"message": "Account activated"}


# 🔑 LOGIN
@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, request: Request, db: Session = Depends(get_db), vendor: Vendor = Depends(get_vendor)):
    
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

    log = AuditLog(
        action="login",
        actor_user_id=user.id,
        vendor_id=user.vendor_id,
        meta={"ip": request.client.host}
    )

    db.add(log)
    db.commit()

    return TokenResponse(
        access_token=create_access_token(user, db),
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
        access_token=create_access_token(user, db),
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