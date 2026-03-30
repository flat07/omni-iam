# app/api/v1/tests/test_users.py
from app.models.identity import User, Group, UserGroup
from app.core.security import hash_password

def override_permission(permission: str):
    def _override():
        return {
            "user_id": "test-user",
            "vendor_id": None,
            "permissions": [
                "users:read",
                "users:create",
                "users:assign_group"
            ]
        }
    return _override



def test_create_user(client, db):
    from app.models.organization import Vendor
    from app.core.deps import get_current_context

    vendor = Vendor(name="Test", slug="test")
    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    client.app.dependency_overrides[get_current_context] = lambda: {
        "user_id": "test",
        "vendor_id": vendor.id,
        "permissions": ["users:create"]
    }


    payload = {
        "email": "test@test.com",
        "password": "password123"
    }

    response = client.post("/api/v1/users/", json=payload)

    if response.status_code != 201:
        print(f"\nError response Detail: {response.json()}")

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == payload["email"]

    user = db.query(User).filter_by(email=payload["email"]).first()
    assert user is not None
    assert user.password_hash != payload["password"]  # hashed


def test_create_user_duplicate_email(client, db):
    from app.models.organization import Vendor
    from app.models.identity import User
    from app.core.deps import get_current_context

    vendor = Vendor(name="Test", slug="test")
    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    client.app.dependency_overrides[get_current_context] = lambda: {
        "user_id": "test",
        "vendor_id": vendor.id,
        "permissions": ["users:create"]
    }

    user = User(
        email="dup@test.com",
        password_hash=hash_password("password"),
        vendor_id=vendor.id
    )
    db.add(user)
    db.commit()

    response = client.post("/api/v1/users", json={
        "email": "dup@test.com",
        "password": "password"
    })

    if response.status_code != 400:
        print(f"\nError response Detail: {response.json()}")

    assert response.status_code == 400


def test_list_users(client, db):
    from app.models.organization import Vendor
    from app.core.deps import get_current_context

    vendor = Vendor(name="Test", slug="test")
    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    client.app.dependency_overrides[get_current_context] = lambda: {
        "user_id": "admin",
        "vendor_id": vendor.id,
        "permissions": ["users:read"]
    }

    response = client.get("/api/v1/users/")

    if response.status_code != 200:
        print(f"\nError response Detail: {response.json()}")


    assert response.status_code == 200
    assert "users" in response.json()


def test_assign_group(client, db):
    from app.models.organization import Vendor
    from app.core.deps import get_current_context

    vendor = Vendor(name="Test", slug="test")
    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    client.app.dependency_overrides[get_current_context] = lambda: {
        "user_id": "admin",
        "vendor_id": vendor.id,
        "permissions": ["users:assign_group"]
    }

    user = User(email="g@test.com", password_hash="x", vendor_id=vendor.id)
    group = Group(name="Admin", vendor_id=vendor.id)

    db.add_all([user, group])
    db.commit()
    db.refresh(user)
    db.refresh(group)

    response = client.post(f"/api/v1/users/{user.id}/groups/{group.id}")

    if response.status_code != 201:
        print(f"\nError response Detail: {response.json()}")

    assert response.status_code == 201

    link = db.query(UserGroup).filter_by(
        user_id=user.id,
        group_id=group.id
    ).first()

    assert link is not None


def test_assign_group_duplicate(client, db):
    from app.models.organization import Vendor
    from app.core.deps import get_current_context

    vendor = Vendor(name="Test", slug="test")
    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    client.app.dependency_overrides[get_current_context] = lambda: {
        "user_id": "admin",
        "vendor_id": vendor.id,
        "permissions": ["users:assign_group"]
    }

    user = User(email="dupgroup@test.com", password_hash="x", vendor_id=vendor.id)
    group = Group(name="Admin", vendor_id=vendor.id)

    db.add_all([user, group])
    db.commit()
    db.refresh(user)
    db.refresh(group)

    db.add(UserGroup(user_id=user.id, group_id=group.id))
    db.commit()

    response = client.post(f"/api/v1/users/{user.id}/groups/{group.id}")

    if response.status_code != 201:
        print(f"\nError response Detail: {response.json()}")

    assert response.status_code == 201
    assert response.json()["message"] == "Already assigned"