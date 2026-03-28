from app.db.session import SessionLocal

from app.db.seed.vendors import seed_vendors
from app.db.seed.locations import seed_locations
from app.db.seed.departments import seed_departments
from app.db.seed.identity import seed_identity


def run_seed():

    db = SessionLocal()

    try:

        vendor = seed_vendors(db)

        location = seed_locations(db, vendor)

        seed_departments(db, vendor, location)
        seed_identity(db, vendor)

        print("🌱 Database seeding complete!")

    finally:
        db.close()


if __name__ == "__main__":
    run_seed()