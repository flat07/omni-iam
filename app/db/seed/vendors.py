from sqlalchemy.orm import Session
from app.models.organization import Vendor


def seed_vendors(db: Session):

    vendor = db.query(Vendor).filter(Vendor.slug == "demo").first()

    if vendor:
        return vendor

    vendor = Vendor(
        name="Demo Hotel",
        slug="demo",
    )

    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    print("✅ Vendor seeded")

    return vendor