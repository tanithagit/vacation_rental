import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load .env file
load_dotenv()

from database import Base, get_db
from main import app

# Get password from .env file automatically
DB_URL = os.getenv("DATABASE_URL", "")

# Replace main database name with test database name
TEST_DATABASE_URL = DB_URL.replace(
    "/vacation_rental",
    "/vacation_rental_test"
)

print(f"Using test database: {TEST_DATABASE_URL}")

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create test database tables"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db():
    """Get test database session"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db):
    """Get test client with overridden database"""
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def host_token(client):
    """Create a host user and return token"""
    client.post("/auth/register", json={
        "email": "testhost@test.com",
        "password": "password123",
        "full_name": "Test Host",
        "role": "host"
    })
    response = client.post("/auth/login", json={
        "email": "testhost@test.com",
        "password": "password123"
    })
    return response.json()["access_token"]


@pytest.fixture
def guest_token(client):
    """Create a guest user and return token"""
    client.post("/auth/register", json={
        "email": "testguest@test.com",
        "password": "password123",
        "full_name": "Test Guest",
        "role": "guest"
    })
    response = client.post("/auth/login", json={
        "email": "testguest@test.com",
        "password": "password123"
    })
    return response.json()["access_token"]


@pytest.fixture
def sample_property(client, host_token):
    """Create a sample property and return it"""
    response = client.post(
        "/properties/",
        json={
            "title": "Test Beach House",
            "description": "A test property",
            "location": "Chennai",
            "price_per_night": 2500.0,
            "max_guests": 4
        },
        headers={"Authorization": f"Bearer {host_token}"}
    )
    return response.json()