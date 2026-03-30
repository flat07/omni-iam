# app/api/v1/tests/test_org.py
from datetime import timedelta

from app.models.organization import Vendor
from app.models.invite import Invite
from app.models.identity import User
from app.core.security import utc_now

def test_create_org(client, db):

    response = client.post(
        "/api/v1/org/create",
        params={
            "name": "Test Org",
            "slug": "test-org"
        }
    )

    if response.status_code != 200:
        print(f"\nError response Detail: {response.json()}")
    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Organization created"
    assert data["slug"] == "test-org"

    org = db.query(Vendor).filter(Vendor.slug == "test-org").first()

    assert org is not None
    assert org.name == "Test Org"

def test_invite_user_success(client, db, test_user, test_vendor):

    payload = {"email": "staff@test.com", "group": "staff"}

    headers = test_user["headers"].copy()
    headers["Host"] = f"{test_vendor.slug}.testserver"

    response = client.post(
        "/api/v1/org/invite-user",
        json=payload,
        headers=headers
    )

    if response.status_code != 200:
        print(f"\nError response Detail: {response.json()}")

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Invite created"
    assert data["email"] == "staff@test.com"
    assert "invite_url" in data

    invite = db.query(Invite).filter(Invite.email == "staff@test.com").first()

    assert invite is not None

def test_invite_user_permission_denied(client, db, test_user_no_permission, test_vendor):

    payload = {"email": "staff@test.com", "group": "staff"}

    headers = test_user_no_permission["headers"].copy()
    headers["Host"] = f"{test_vendor.slug}.testserver"

    response = client.post(
        "/api/v1/org/invite-user",
        json=payload,
        headers=headers
    )

    assert response.status_code == 403

def test_accept_invite_success(client, db, test_vendor):

    token = "test-token"

    invite = Invite(
        email="newuser@test.com",
        token=token,
        vendor_id=test_vendor.id,
        accepted=False,
        expires_at=utc_now() + timedelta(days=1)
    )

    db.add(invite)
    db.commit()

    payload = {
        "token": token,
        "password": "StrongPassword123"
    }

    response = client.post(
        "/api/v1/auth/accept-invite",
        json=payload
    )

    if response.status_code != 200:
        print(f"\nError response Detail: {response.json()}")

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Account activated"

    user = db.query(User).filter(User.email == "newuser@test.com").first()

    assert user is not None
    assert user.is_active is True

def test_accept_invite_invalid_token(client):

    payload = {
        "token": "invalid",
        "password": "StrongPassword123"
    }

    response = client.post(
        "/api/v1/auth/accept-invite",
        json=payload
    )

    if response.status_code != 404:
        print(f"\nError response Detail: {response.json()}")

    assert response.status_code == 404

def test_accept_invite_already_used(client, db, test_vendor):

    token = "used-token"

    invite = Invite(
        email="user@test.com",
        token=token,
        vendor_id=test_vendor.id,
        accepted=True,
        expires_at=utc_now() + timedelta(days=1)
    )

    db.add(invite)
    db.commit()

    payload = {
        "token": token,
        "password": "Password123"
    }

    response = client.post(
        "/api/v1/auth/accept-invite",
        json=payload
    )
    if response.status_code != 400:
        print(f"\nError response Detail: {response.json()}")

    assert response.status_code == 400

def test_accept_invite_expired(client, db, test_vendor):

    token = "expired-token"

    invite = Invite(
        email="user@test.com",
        token=token,
        vendor_id=test_vendor.id,
        accepted=False,
        expires_at=utc_now() - timedelta(days=1)
    )

    db.add(invite)
    db.commit()

    payload = {
        "token": token,
        "password": "Password123"
    }

    response = client.post(
        "/api/v1/auth/accept-invite",
        json=payload
    )
    if response.status_code != 400:
        print(f"\nError response Detail: {response.json()}")

    assert response.status_code == 400
