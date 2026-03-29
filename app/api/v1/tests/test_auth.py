# app/api/v1/tests/test_auth.py
import uuid

def test_login_success(client, db):

    # 👉 Create test data
    from app.models.organization import Vendor
    from app.models.identity import User
    from app.core.security import hash_password

    vendor = Vendor(name="Test", slug="test")
    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    user = User(
        email="test@test.com",
        password_hash=hash_password("password"),
        vendor_id=vendor.id,
        is_active=True,
    )
    db.add(user)
    db.commit()
    # 👉 simulate subdomain via headers
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@test.com",
            "password": "password"
        },
        headers={
            "host": "test.localhost"
        }
    )

    # Add this to see WHY it failed:
    if response.status_code != 200:
        print(f"\nError Detail: {response.json()}")

    assert response.status_code == 200
    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data

def test_login_invalid_password(client, db):

    from app.models.organization import Vendor
    from app.models.identity import User
    from app.core.security import hash_password

    vendor = Vendor(name="Test", slug="test")
    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    user = User(
        email="test@test.com",
        password_hash=hash_password("password"),
        vendor_id=vendor.id,
        is_active=True,
    )
    db.add(user)
    db.commit()

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@test.com",
            "password": "wrong"
        },
        headers={"host": "test.localhost"}
    )
    if response.status_code != 400:
        print(f"\nError Detail: {response.json()}")

    assert response.status_code == 400

def test_refresh_token(client, db):

    from app.models.organization import Vendor
    from app.models.identity import User
    from app.core.security import create_refresh_token
    from jose import jwt
    from app.models.session import UserSession
    from app.core.config import settings

    vendor = Vendor(name="Test", slug="test")
    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    user = User(
        email="test@test.com",
        password_hash="hashed",
        vendor_id=vendor.id,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    refresh_token = create_refresh_token(user)

    payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    jti = payload.get("jti")

    user_session = UserSession(
        user_id=user.id,
        refresh_jti=jti,
        is_revoked=False
    )
    db.add(user_session)
    db.commit()

    response = client.post(
        "/api/v1/auth/refresh",
        params={"refresh_token": refresh_token},
        headers={"host": "test.localhost"}
    )
    if response.status_code != 200:
        print(f"\nError Detail: {response.json()}")

    assert response.status_code == 200

def test_get_me(client, db):

    from app.models.organization import Vendor
    from app.models.identity import User
    from app.core.security import hash_password, create_access_token
    print("BEFORE:", db.query(User).count())
    

    # 👉 Create vendor
    vendor = Vendor(name="Test", slug="test")
    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    email = f"test-{uuid.uuid4()}@test.com"

    # 👉 Create user
    user = User(
        email=email,
        password_hash=hash_password("password"),
        vendor_id=vendor.id,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # 👉 Create token
    access_token = create_access_token(user)

    # 👉 Call /me
    response = client.get(
        "/api/v1/auth/me",
        headers={
            "Authorization": f"Bearer {access_token}",
            "host": "test.localhost"
        }
    )
    if response.status_code != 200:
        print(f"\nError Detail: {response.json()}")

    assert response.status_code == 200

    data = response.json()
    print("DEBUG ### data", data)

    assert data["email"] == email
    assert data["vendor_id"] == str(vendor.id)

def test_get_me_unauthorized(client):

    response = client.get(
        "/api/v1/auth/me",
        headers={"host": "test.localhost"}
    )

    assert response.status_code == 401