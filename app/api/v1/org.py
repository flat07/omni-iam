import uuid
from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from app.models.organization import Vendor
from app.models.identity import User
from app.schemas.invite import InviteCreate
from app.crud.invite import create_invite
from app.core.deps import get_db, get_current_user, get_current_vendor
# from app.core.policy_engine import check_policy


router = APIRouter(prefix="/org", tags=["Organization"])

# check_policy sample
# @router.put("/rooms/{room_id}")
# def update_room(
#     room_id: str,
#     current_user = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):

#     allowed = check_policy(
#         db=db,
#         vendor_id=current_user.vendor_id,
#         action="room:update",
#         resource="room",
#         context={
#             "department": current_user.department,
#             "location": current_user.location
#         }
#     )

#     if not allowed:
#         raise HTTPException(status_code=403, detail="Access denied")

#     return {"message": "room updated"}

@router.post("/create")
def create_org(name: str, slug: str, db: Session = Depends(get_db)):

    org = Vendor(
        id=uuid.uuid4(),
        name=name,
        slug=slug
    )

    db.add(org)
    db.commit()

    return {
        "message": "Organization created",
        "slug": slug
    }

@router.post("/invite-user")
def invite_user(
    payload: InviteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    vendor = Depends(get_current_vendor)
):

    # Optional: check admin permission
    if "users:invite" not in current_user.permissions:
        raise HTTPException(status_code=403, detail="Not allowed")

    invite = create_invite(
        db=db,
        email=payload.email,
        vendor_id=vendor.id
    )

    invite_url = f"https://{vendor.slug}.omni-iam.me/accept-invite?token={invite.token}"

    return {
        "message": "Invite created",
        "email": invite.email,
        "invite_url": invite_url
    }


