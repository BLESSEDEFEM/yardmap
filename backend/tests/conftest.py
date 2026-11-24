import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from app.main import app
from app.config import settings
from app.db import engine, SessionLocal
from app.models import User

if "yardmap_test" not in settings.database_url:
    raise RuntimeError("set $env:DATABASE_URL to yardmap_test")

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture(autouse=True)
def wipe() -> None:
    with engine.begin() as conn:
        conn.execute(text(
            "TRUNCATE movements, appointments, report_jobs, vehicles_containers, users RESTART IDENTITY"
        ))
        
def _add_user(email: str, role: str, full_name: str) -> int:
    with SessionLocal() as session:
        user = User(
            email=email,
            password_hash="not-a-real-hash",
            full_name=full_name,
            role=role,
        )
        session.add(user)
        session.commit()
        return user.id
    

@pytest.fixture()
def haulier() -> int:
    return _add_user("haulier1@example.com", "haulier", "Test Haulier")

@pytest.fixture()
def operator() -> int:
    return _add_user("operator1@example.com", "operator", "Test Operator")