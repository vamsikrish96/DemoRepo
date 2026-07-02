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


def extract_token(authorization: Optional[str]) -> str:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
        )
    try:
        scheme, token = authorization.split(" ", 1)
        if scheme.lower() != "bearer":
            raise ValueError()
        return token
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
        )


def get_current_user(authorization: Optional[str] = Header(None)) -> User:
    token = extract_token(authorization)
    return get_user_from_token(token)


def require_role(user: User, required_role: UserRole) -> User:
    if user.role != required_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"This action requires {required_role.value} role",
        )
    return user


def require_any_role(user: User, *required_roles: UserRole) -> User:
    if user.role not in required_roles:
        roles = ", ".join(r.value for r in required_roles)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"This action requires one of: {roles}",
        )
    return user


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
    require_role(current_user, UserRole.EMPLOYEE)

    manager_id = get_manager_for_employee(current_user.user_id)
    if not manager_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee must have assigned manager",
        )

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
    require_role(current_user, UserRole.MANAGER)

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

    return store.approve_claim(claim_id, request.approval_reason)


@app.put("/claims/{claim_id}/reject", response_model=ExpenseClaimResponse)
def reject_claim(
    claim_id: str,
    request: ApprovalRequest,
    authorization: Optional[str] = Header(None),
) -> ExpenseClaimResponse:
    current_user = get_current_user(authorization)
    require_role(current_user, UserRole.MANAGER)

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

    return store.reject_claim(claim_id, request.approval_reason)


# ===== Finance Processing Endpoints =====


@app.put("/claims/{claim_id}/process", response_model=ExpenseClaimResponse)
def process_claim(
    claim_id: str,
    authorization: Optional[str] = Header(None),
) -> ExpenseClaimResponse:
    current_user = get_current_user(authorization)
    require_role(current_user, UserRole.FINANCE)

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

    return store.process_claim(claim_id)


@app.get("/health")
def health_check():
    return {"status": "healthy"}
