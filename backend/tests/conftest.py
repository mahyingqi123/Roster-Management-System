import os
import sys
from pathlib import Path
import tempfile
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure 'app' package is importable when running tests
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import importlib
from app.database import Base, get_db


@pytest.fixture(scope="session")
def test_db_url():
    # Use a temporary sqlite database file for persistence across tests in session
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    tmp.close()
    url = f"sqlite:///{tmp.name}"
    yield url
    try:
        os.remove(tmp.name)
    except OSError:
        pass


@pytest.fixture(scope="session")
def engine(test_db_url):
    connect_args = {"check_same_thread": False} if test_db_url.startswith("sqlite") else {}
    engine = create_engine(test_db_url, connect_args=connect_args)
    # Ensure models are registered on Base before creating tables
    importlib.import_module('app.models')
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session(engine):
    # Ensure a clean DB for every test
    importlib.import_module('app.models')
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_session):
    # Import app lazily after path injection
    main = importlib.import_module('app.main')

    # Override dependency
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    main.app.dependency_overrides[get_db] = override_get_db
    return TestClient(main.app)


