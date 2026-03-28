from sqlalchemy.orm import Session
from app.models.identity import User


def get_user_by_email(db: Session, email: str, vendorid: str):
    
    return db.query(User).filter(
        User.email == email,
        User.vendor_id == vendorid
        ).first()