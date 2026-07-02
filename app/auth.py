from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import HTTPException, status
from jose import JWTError, jwt
from app.models import User, UserRole

SECRET_KEY = "dev-secret-key-change-in-production"
ALGORITHM = "HS256"
TOKEN_EXPIRY_MINUTES = 60

MOCK_USERS = {
    "emp1": {"password": "pass", "role": UserRole.EMPLOYEE, "department": "Sales"},
    "emp2": {"password": "pass", "role": UserRole.EMPLOYEE, "department": "Engineering"},
    "emp3": {"password": "pass", "role": UserRole.EMPLOYEE, "department": "Marketing"},
    "mgr1": {"password": "pass", "role": UserRole.MANAGER, "department": "Sales"},
    "mgr2": {"password": "pass", "role": UserRole.MANAGER, "department": "Engineering"},
    "mgr3": {"password": "pass", "role": UserRole.MANAGER, "department": "Marketing"},
    "fin1": {"password": "pass", "role": UserRole.FINANCE, "department": "Finance"},
    "admin1": {"password": "pass", "role": UserRole.ADMIN, "department": "Admin"},
}

MANAGER_ASSIGNMENTS = {
    "emp1": "mgr1",
    "emp2": "mgr2",
    "emp3": "mgr3",
}


def create_bearer_token(user_id: str, role: UserRole, department: Optional[str] = None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRY_MINUTES)
    payload = {
        "user_id": user_id,
        "role": role.value,
        "department": department,
        "exp": expire,
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def decode_bearer_token(token: str) -> Optional[User]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return User(
            user_id=payload["user_id"],
            role=UserRole(payload["role"]),
            department=payload.get("department"),
        )
    except JWTError:
        return None


def authenticate_user(user_id: str, password: str) -> Optional[User]:
    if user_id not in MOCK_USERS:
        return None
    user_data = MOCK_USERS[user_id]
    if user_data["password"] != password:
        return None
    return User(
        user_id=user_id,
        role=user_data["role"],
        department=user_data["department"],
    )


def get_user_from_token(token: str) -> User:
    user = decode_bearer_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_manager_for_employee(employee_id: str) -> Optional[str]:
    return MANAGER_ASSIGNMENTS.get(employee_id)
