# app/api/v1/tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from app.core.deps import get_db
from app.core.config import settings

# app/api/v1/tests/conftest.py


TEST_DATABASE_URL = settings.TEST_DATABASE_URL

engine = create_engine(TEST_DATABASE_URL)


TestingSessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,  # ✅ IMPORTANT
)


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