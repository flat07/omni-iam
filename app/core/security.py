# app/core/security
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import jwt
from uuid import uuid4
from app.core.config import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

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
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    now = utc_now()

    payload = {
        "jti": str(uuid4()),
        "user_id": str(user.id),
        "vendor_id": str(user.vendor_id),
        "location_id": str(user.location_id) if user.location_id else None,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": expire,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# 🔄 Refresh Token
def create_refresh_token(user):
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    now = utc_now()

    payload = {
        "jti": str(uuid4()),
        "user_id": str(user.id),
        "type": "refresh",
        "iat": int(now.timestamp()),
        "exp": expire,
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
