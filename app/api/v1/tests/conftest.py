# app/api/v1/tests/conftest.py
import pytest
import uuid

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from app.db.base import Base
from app.core.deps import get_db
from app.core.config import settings


from app.models.identity import User
from app.models.organization import Vendor
from app.core.security import create_access_token


# app/api/v1/tests/conftest.py


TEST_DATABASE_URL = settings.TEST_DATABASE_URL

engine = create_engine(TEST_DATABASE_URL)


TestingSessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,  # ✅ IMPORTANT
)



@pytest.fixture
def test_vendor(db):
    vendor = Vendor(
        id=uuid.uuid4(),
        name="Test Vendor",
        slug="test-vendor"
    )

    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    return vendor


@pytest.fixture
def test_user(db, test_vendor):
    user = User(
        id=uuid.uuid4(),
        email="admin@test.com",
        password_hash="fakehash",
        vendor_id=test_vendor.id,
        is_active=True
    )

    # permissions used by endpoint
    user.permissions = ["users:invite"]

    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user=user, db=db)

    headers = {"Authorization": f"Bearer {token}"}

    return {
        "user": user,
        "token": token,
        "headers": headers
    }

@pytest.fixture
def test_user_no_permission(db, test_vendor):

    user = User(
        id=uuid.uuid4(),
        email="staff@test.com",
        password_hash="fakehash",
        vendor_id=test_vendor.id,
        is_active=True
    )

    user.permissions = []  # 🚨 no permissions

    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user=user, db=db)

    headers = {"Authorization": f"Bearer {token}"}

    return {
        "user": user,
        "token": token,
        "headers": headers
    }

@pytest.fixture(scope="session", autouse=True)
def create_test_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db():

    connection = engine.connect()
    transaction = connection.begin()  # outer transaction

    session = TestingSessionLocal(bind=connection)

    # 👉 START nested transaction (SAVEPOINT)
    session.begin_nested()

    from sqlalchemy import event

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(sess, trans):
        if trans.nested and not trans._parent.nested:
            sess.begin_nested()

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()  # rollback EVERYTHING
        connection.close()


@pytest.fixture(scope="function")
def client(db):
    from fastapi.testclient import TestClient

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)

    app.dependency_overrides.clear()