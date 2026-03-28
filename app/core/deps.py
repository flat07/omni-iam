from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import DATABASE_URL


# 1. This tells FastAPI to look for a 'Bearer' token in the Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login") 

# 2. These should ideally come from your environment variables
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-hard-to-guess-###")
ALGORITHM = "HS256"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token")

    return payload

def get_current_context(token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

    return {
        "user_id": payload.get("sub"),
        "vendor_id": payload.get("vendor_id"),
        "location_id": payload.get("location_id"),
    }

def SecurityChecker(required_permission: str):
    def checker(context=Depends(get_current_context), db=Depends(get_db)):
        user_id = context["user_id"]

        # join: user → group → permission
        has_permission = db.execute("""
            SELECT 1
            FROM user_groups ug
            JOIN group_permissions gp ON ug.group_id = gp.group_id
            JOIN permissions p ON gp.permission_id = p.id
            WHERE ug.user_id = :user_id
              AND p.code = :perm
        """, {"user_id": user_id, "perm": required_permission}).first()

        if not has_permission:
            raise HTTPException(status_code=403, detail="Forbidden")

        return context

    return checker