import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.storage import store
from app.auth import create_bearer_token
from app.models import UserRole


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def clear_store():
    store.claims.clear()
    store.claim_counter = 0
    yield
    store.claims.clear()
    store.claim_counter = 0


def get_token(user_id: str, role: UserRole, department: str = None) -> str:
    return create_bearer_token(user_id, role, department)


@pytest.fixture
def employee_token():
    return get_token("emp1", UserRole.EMPLOYEE, "Sales")


@pytest.fixture
def manager_token():
    return get_token("mgr1", UserRole.MANAGER, "Sales")


@pytest.fixture
def finance_token():
    return get_token("fin1", UserRole.FINANCE, "Finance")


@pytest.fixture
def admin_token():
    return get_token("admin1", UserRole.ADMIN, "Admin")


@pytest.fixture
def other_employee_token():
    return get_token("emp2", UserRole.EMPLOYEE, "Engineering")
