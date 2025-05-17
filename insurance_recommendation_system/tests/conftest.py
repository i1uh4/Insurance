import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import os
from dotenv import load_dotenv
import json
from app.main import app
from app.utils.auth import create_access_token
from app.database import Base

load_dotenv()

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/insurance_test")

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def db_engine():
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


@pytest.fixture
def test_user():
    return {
        "user_name": "testuser",
        "email": "test@example.com",
        "password": "Test123!",
        "first_name": "Test",
        "last_name": "User",
        "age": 30,
        "gender": "male",
        "occupation": "Software Engineer",
        "income": 75000,
        "marital_status": "single",
        "has_children": False,
        "has_vehicle": True,
        "has_home": False,
        "has_medical_conditions": False,
        "travel_frequency": "occasional"
    }


@pytest.fixture
def token_headers(test_user):
    access_token = create_access_token(
        data={"user_id": 1, "email": test_user["email"]}
    )
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def recommendation_request():
    return {
        "age": 30,
        "gender": "male",
        "occupation": "Software Engineer",
        "income": 75000,
        "marital_status": "single",
        "has_children": False,
        "has_vehicle": True,
        "has_home": False,
        "has_medical_conditions": False,
        "travel_frequency": "occasional"
    }


@pytest.fixture
def mock_insurance_data():
    return [
        {
            "product_id": 1,
            "product_name": "Term Life Insurance",
            "provider": "InsureCo",
            "category_name": "Life Insurance",
            "description": "Provides coverage at a fixed rate of payments for a limited period of time.",
            "premium": 5000,
            "coverage": 1000000,
            "duration": 120,
            "estimated_price": 5000,
            "match_score": 0.85,
            "recommendation_reason": "Based on your age and occupation, this would provide good protection.",
            "features": ["Fixed premium", "Tax-free death benefit", "Convertible to permanent insurance"],
            "suitable_for": ["Young professionals", "Families with children", "Mortgage holders"],
            "risks_covered": ["Death", "Terminal illness"]
        }
    ]