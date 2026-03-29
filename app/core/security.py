# app/core/security
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta, timezone
from app.core.config import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 🔐 Password hashing
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

# ⏱️ Time helper
def utc_now():
    return datetime.now(timezone.utc)

def create_access_token(user):
    now = utc_now()

    payload = {
        "user_id": str(user.id),
        "vendor_id": str(user.vendor_id),
        "location_id": str(user.location_id) if user.location_id else None,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=8)).timestamp()),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# 🔄 Refresh Token
def create_refresh_token(user):
    now = utc_now()

    payload = {
        "user_id": str(user.id),
        "type": "refresh",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(days=7)).timestamp()),
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
