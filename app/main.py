from fastapi import FastAPI, HTTPException, status, Header, Query
from typing import Optional, List
from app.models import (
    LoginRequest,
    LoginResponse,
    User,
    UserRole,
    ExpenseClaimCreate,
    ExpenseClaimUpdate,
    ExpenseClaimResponse,
    ApprovalRequest,
    ErrorResponse,
    ClaimStatus,
)
from app.auth import (
    authenticate_user,
    create_bearer_token,
    get_user_from_token,
    get_manager_for_employee,
)
from app.storage import store

app = FastAPI(
    title="Expense Approval Workflow API",
    description="API for managing expense claims with approval workflow",
    version="1.0.0",
)


def get_current_user(authorization: Optional[str] = Header(None)) -> User:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
        )

    try:
        scheme, token = authorization.split(" ", 1)
        if scheme.lower() != "bearer":
            raise ValueError()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
        )

    return get_user_from_token(token)


# ===== Auth Endpoints =====


@app.post("/auth/login", response_model=LoginResponse)
def login(request: LoginRequest) -> LoginResponse:
    user = authenticate_user(request.user_id, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    token = create_bearer_token(user.user_id, user.role, user.department)
    return LoginResponse(access_token=token, user=user)


@app.get("/users/me", response_model=User)
def get_current_user_info(authorization: Optional[str] = Header(None)) -> User:
    return get_current_user(authorization)


# ===== Expense Claims CRUD Endpoints =====


@app.post("/claims", response_model=ExpenseClaimResponse, status_code=status.HTTP_201_CREATED)
def create_claim(
    request: ExpenseClaimCreate,
    authorization: Optional[str] = Header(None),
) -> ExpenseClaimResponse:
    current_user = get_current_user(authorization)

    if current_user.role != UserRole.EMPLOYEE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only employees can create claims",
        )

    manager_id = get_manager_for_employee(current_user.user_id)
    claim = store.create_claim(
        employee_id=current_user.user_id,
        amount=request.amount,
        description=request.description,
        receipt_path=request.receipt_path,
        category=request.category,
        manager_id=manager_id,
    )
    return claim


@app.get("/claims", response_model=List[ExpenseClaimResponse])
def list_claims(
    status_filter: Optional[str] = Query(None, alias="status"),
    authorization: Optional[str] = Header(None),
) -> List[ExpenseClaimResponse]:
    current_user = get_current_user(authorization)

    all_claims = store.list_claims()

    if current_user.role == UserRole.EMPLOYEE:
        filtered_claims = [c for c in all_claims if c.employee_id == current_user.user_id]
    elif current_user.role == UserRole.MANAGER:
        filtered_claims = [
            c for c in all_claims if c.manager_id == current_user.user_id
        ]
    elif current_user.role in [UserRole.FINANCE, UserRole.ADMIN]:
        filtered_claims = all_claims
    else:
        filtered_claims = []

    if status_filter:
        filtered_claims = [
            c for c in filtered_claims if c.status.value == status_filter
        ]

    return filtered_claims


@app.get("/claims/{claim_id}", response_model=ExpenseClaimResponse)
def get_claim(
    claim_id: str,
    authorization: Optional[str] = Header(None),
) -> ExpenseClaimResponse:
    current_user = get_current_user(authorization)

    claim = store.get_claim(claim_id)
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found",
        )

    if current_user.role == UserRole.EMPLOYEE and claim.employee_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other employee's claims",
        )

    if current_user.role == UserRole.MANAGER and claim.manager_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access unassigned claims",
        )

    return claim


@app.patch("/claims/{claim_id}", response_model=ExpenseClaimResponse)
def update_claim(
    claim_id: str,
    request: ExpenseClaimUpdate,
    authorization: Optional[str] = Header(None),
) -> ExpenseClaimResponse:
    current_user = get_current_user(authorization)

    claim = store.get_claim(claim_id)
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found",
        )

    if current_user.role != UserRole.EMPLOYEE or claim.employee_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owner can update claim",
        )

    if claim.status != ClaimStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Can only update draft claims",
        )

    updated_claim = store.update_claim(
        claim_id,
        amount=request.amount,
        description=request.description,
        receipt_path=request.receipt_path,
        category=request.category,
    )
    return updated_claim


# ===== Claim State Transition Endpoints =====


@app.put("/claims/{claim_id}/submit", response_model=ExpenseClaimResponse)
def submit_claim(
    claim_id: str,
    authorization: Optional[str] = Header(None),
) -> ExpenseClaimResponse:
    current_user = get_current_user(authorization)

    claim = store.get_claim(claim_id)
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found",
        )

    if current_user.role != UserRole.EMPLOYEE or claim.employee_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owner can submit claim",
        )

    if claim.status != ClaimStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Can only submit draft claims",
        )

    submitted_claim = store.submit_claim(claim_id)
    return submitted_claim


@app.put("/claims/{claim_id}/cancel", response_model=ExpenseClaimResponse)
def cancel_claim(
    claim_id: str,
    authorization: Optional[str] = Header(None),
) -> ExpenseClaimResponse:
    current_user = get_current_user(authorization)

    claim = store.get_claim(claim_id)
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found",
        )

    if current_user.role == UserRole.EMPLOYEE:
        if claim.employee_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only owner can cancel claim",
            )
    elif current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only employee or admin can cancel claim",
        )

    if claim.status in [ClaimStatus.PROCESSED, ClaimStatus.CANCELLED, ClaimStatus.REJECTED]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot cancel claims in this state",
        )

    cancelled_claim = store.cancel_claim(claim_id)
    return cancelled_claim


# ===== Manager Approval Endpoints =====


@app.put("/claims/{claim_id}/approve", response_model=ExpenseClaimResponse)
def approve_claim(
    claim_id: str,
    request: ApprovalRequest,
    authorization: Optional[str] = Header(None),
) -> ExpenseClaimResponse:
    current_user = get_current_user(authorization)

    if current_user.role != UserRole.MANAGER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can approve claims",
        )

    claim = store.get_claim(claim_id)
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found",
        )

    if claim.manager_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager not assigned to this claim",
        )

    if claim.status != ClaimStatus.SUBMITTED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Can only approve submitted claims",
        )

    approved_claim = store.approve_claim(claim_id, request.approval_reason)
    return approved_claim


@app.put("/claims/{claim_id}/reject", response_model=ExpenseClaimResponse)
def reject_claim(
    claim_id: str,
    request: ApprovalRequest,
    authorization: Optional[str] = Header(None),
) -> ExpenseClaimResponse:
    current_user = get_current_user(authorization)

    if current_user.role != UserRole.MANAGER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can reject claims",
        )

    claim = store.get_claim(claim_id)
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found",
        )

    if claim.manager_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager not assigned to this claim",
        )

    if claim.status != ClaimStatus.SUBMITTED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Can only reject submitted claims",
        )

    rejected_claim = store.reject_claim(claim_id, request.approval_reason)
    return rejected_claim


# ===== Finance Processing Endpoints =====


@app.put("/claims/{claim_id}/process", response_model=ExpenseClaimResponse)
def process_claim(
    claim_id: str,
    authorization: Optional[str] = Header(None),
) -> ExpenseClaimResponse:
    current_user = get_current_user(authorization)

    if current_user.role != UserRole.FINANCE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only finance can process claims",
        )

    claim = store.get_claim(claim_id)
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found",
        )

    if claim.status != ClaimStatus.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Can only process approved claims",
        )

    processed_claim = store.process_claim(claim_id)
    return processed_claim


@app.get("/health")
def health_check():
    return {"status": "healthy"}
