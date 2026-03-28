from sqlalchemy.orm import Session
from app.models.organization import Location


def seed_locations(db: Session, vendor):

    location = db.query(Location).filter(
        Location.name == "demo-location1",
        Location.vendor_id == vendor.id
    ).first()

    if location:
        return location

    location = Location(
        name="demo-location1",
        vendor_id=vendor.id
    )

    db.add(location)
    db.commit()
    db.refresh(location)

    print("✅ Location seeded")

    return location