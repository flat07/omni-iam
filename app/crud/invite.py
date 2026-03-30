import uuid
import secrets

from sqlalchemy.orm import Session

from app.models.invite import Invite


def create_invite(db: Session, email: str, vendor_id: uuid.UUID):

    token = secrets.token_urlsafe(32)

    invite = Invite(
        email=email,
        token=token,
        vendor_id=vendor_id,
        accepted=False
    )

    db.add(invite)
    db.commit()
    db.refresh(invite)

    return invite