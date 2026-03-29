# app/crud/user.py
from app.models.identity import User

def get_user_by_email(db, email: str, vendor_id):
    print("DEBUG ### USERS:", db.query(User).all())
    return (
        db.query(User)
        .filter(
            User.email == email,
            User.vendor_id == vendor_id,
            User.is_active.is_(True),
        )
        .first()
    )