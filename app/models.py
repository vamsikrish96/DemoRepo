from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List
from enum import Enum
from datetime import datetime


class UserRole(str, Enum):
    EMPLOYEE = "employee"
    MANAGER = "manager"
    FINANCE = "finance"
    ADMIN = "admin"


class ClaimStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    PROCESSED = "processed"
    CANCELLED = "cancelled"


class User(BaseModel):
    user_id: str
    role: UserRole
    department: Optional[str] = None


class ErrorResponse(BaseModel):
    error: str
    code: str
    details: Optional[dict] = None


class ExpenseClaimCreate(BaseModel):
    amount: float
    description: str
    receipt_path: str
    category: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("amount must be greater than 0")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v):
        if not v or len(v) < 10 or len(v) > 1000:
            raise ValueError("description must be 10-1000 characters")
        return v

    @field_validator("receipt_path")
    @classmethod
    def validate_receipt_path(cls, v):
        if not v or len(v) > 500:
            raise ValueError("receipt_path is required and must be < 500 chars")
        return v


class ExpenseClaimUpdate(BaseModel):
    amount: Optional[float] = None
    description: Optional[str] = None
    receipt_path: Optional[str] = None
    category: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v):
        if v is not None and v <= 0:
            raise ValueError("amount must be greater than 0")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v):
        if v is not None and (len(v) < 10 or len(v) > 1000):
            raise ValueError("description must be 10-1000 characters")
        return v

    @field_validator("receipt_path")
    @classmethod
    def validate_receipt_path(cls, v):
        if v is not None and (not v or len(v) > 500):
            raise ValueError("receipt_path must be < 500 chars")
        return v


class ExpenseClaimResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    claim_id: str
    employee_id: str
    amount: float
    description: str
    receipt_path: str
    category: Optional[str] = None
    status: ClaimStatus
    manager_id: Optional[str] = None
    submission_date: Optional[datetime] = None
    approval_reason: Optional[str] = None
    rejection_reason: Optional[str] = None
    processed_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class ApprovalRequest(BaseModel):
    approval_reason: str

    @field_validator("approval_reason")
    @classmethod
    def validate_reason(cls, v):
        if not v or len(v) < 5:
            raise ValueError("reason must be at least 5 characters")
        return v


class LoginRequest(BaseModel):
    user_id: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User
