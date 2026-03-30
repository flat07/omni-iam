# app/api/v1/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from sqlalchemy.orm import Session
from app.core.deps import get_db, require_permission
from app.models.identity import User, UserGroup
from app.core.security import hash_password, utc_now
from app.schemas.user import UserCreate
from typing import Dict, Any

# app/api/v1/users.py
router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=Dict[str, Any])
def list_users(db: Session = Depends(get_db), current_user = Depends(require_permission("users:read"))):
    users = db.query(User).all()
    return {
        "message": "User list", 
        "requested_by": current_user["user_id"], 
        "users": users # FastAPI/Pydantic will now handle the validation for you
    }

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    context = Depends(require_permission("users:create"))
):
    # ✅ Check duplicate email
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    try:
        user = User(
            email=user_in.email,
            password_hash=hash_password(user_in.password),
            is_active=user_in.is_active,
            vendor_id=context["vendor_id"],  # multi-tenant safety
            created_at=utc_now()
        )

        db.add(user)
        db.commit()
        db.refresh(user)

    except Exception as e:
        print("DB ERROR >>>", str(e))   # 👈 ADD THIS
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "message": "User created",
        "id": str(user.id),
        "email": user.email
    }

@router.post("/{user_id}/groups/{group_id}", status_code=status.HTTP_201_CREATED)
def assign_group(
    user_id: UUID,
    group_id: UUID,
    db: Session = Depends(get_db),
    _=Depends(require_permission("users:assign_group"))
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    existing = db.query(UserGroup).filter_by(
        user_id=user_id,
        group_id=group_id
    ).first()

    if existing:
        # Option A: Return 200 with a message
        # Option B: Raise 400/409 error (Recommended if the frontend shouldn't be doing this)
        return {"message": "Already assigned"}
    
    try:
        link = UserGroup(user_id=user_id, group_id=group_id)
        db.add(link)
        db.commit()
        db.refresh(link) # Refreshes the object with DB-generated defaults
    except Exception as _e:
        db.rollback() # Important: undo changes if something goes wrong
        raise HTTPException(status_code=500, detail="Database error")

    return {"message": "Group assigned"}
