from sqlalchemy.orm import Session
from app.models.organization import Department


DEPARTMENTS = [
    "Front Office",
    "Reservations",
    "Housekeeping",
    "Laundry",
    "Engineering",
    "IT",
    "Security",
    "Food & Beverage",
    "Restaurant",
    "Kitchen",
    "Room Service",
    "Banquets",
    "Sales",
    "Marketing",
    "Finance",
    "Accounting",
    "Human Resources",
    "Purchasing",
    "Spa",
    "Gym",
]


def seed_departments(db: Session, vendor, location):

    for name in DEPARTMENTS:

        exists = db.query(Department).filter(
            Department.name == name,
            Department.vendor_id == vendor.id
        ).first()

        if exists:
            continue

        department = Department(
            name=name,
            vendor_id=vendor.id,
            location_id=location.id
        )

        db.add(department)

    db.commit()

    print("✅ Departments seeded")