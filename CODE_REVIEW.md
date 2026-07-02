# Code Review: Expense Approval Workflow API

**Status**: ISSUES FOUND - Multiple security and code quality concerns must be addressed before production deployment.

---

## CRITICAL SECURITY ISSUES

### 1. Insecure Token Implementation (MUST FIX)
**File**: `app/auth.py:22-30`
**Severity**: CRITICAL

The token implementation uses base64 encoding, which is NOT encryption or signing:
```python
def create_bearer_token(user_id: str, role: UserRole, department: Optional[str] = None) -> str:
    payload = {...}
    payload_json = json.dumps(payload)
    token = base64.b64encode(payload_json.encode()).decode()  # NOT SECURE
    return token
```

**Problems**:
- Base64 is trivially reversible - anyone with a token can decode it to read user_id, role, department
- No cryptographic signature or HMAC - tokens can be forged
- No expiration time - tokens are valid forever
- No way to revoke tokens

**Fix**:
Replace with proper JWT using `python-jose` (already in requirements.txt):
```python
from jose import jwt
from datetime import datetime, timedelta, timezone

SECRET_KEY = "your-secret-key-here"  # Should be from environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_bearer_token(user_id: str, role: UserRole, department: Optional[str] = None) -> str:
    payload = {
        "user_id": user_id,
        "role": role.value,
        "department": department,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
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
    except jwt.ExpiredSignatureError:
        return None
    except jwt.JWTError:
        return None
```

---

### 2. Hardcoded Mock Credentials in Source Code
**File**: `app/auth.py:7-14`
**Severity**: HIGH

```python
MOCK_USERS = {
    "emp1": {"password": "pass", "role": UserRole.EMPLOYEE, "department": "Sales"},
    # All users have password: "pass"
}
```

**Problems**:
- Even for mock/demo, credentials shouldn't be in source code
- Passwords stored in plaintext (no hashing)
- Single password for all users makes testing unclear

**Fix**:
```python
# Only in test files via conftest, not in production code
# Or move to environment variable for demo
import os

DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"

if DEMO_MODE:
    # Load from env or fixture
    pass
else:
    # Real authentication backend
    pass
```

---

### 3. Incomplete Manager Assignment Logic
**File**: `app/auth.py:16-19`
**Severity**: HIGH

```python
MANAGER_ASSIGNMENTS = {
    "emp1": "mgr1",
    "emp2": "mgr2",
}
```

**Problem**: Only 2 employees have manager assignments. When an employee not in this dict creates a claim:
- `get_manager_for_employee()` returns `None`
- Claim created with `manager_id=None`
- No manager can approve the claim (workflow breaks)

**Fix**:
Define all manager assignments or implement a function to determine manager by department:
```python
def get_manager_for_employee(employee_id: str) -> Optional[str]:
    manager = MANAGER_ASSIGNMENTS.get(employee_id)
    if not manager:
        raise ValueError(f"No manager assigned for employee {employee_id}")
    return manager
```

---

### 4. Missing Request Rate Limiting
**File**: `app/main.py`
**Severity**: HIGH

**Problem**: 
- No rate limiting on `/auth/login` - vulnerable to brute force attacks
- No rate limiting on any endpoints - vulnerable to DOS attacks

**Fix**:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/auth/login", response_model=LoginResponse)
@limiter.limit("5/minute")  # Max 5 login attempts per minute
def login(request: LoginRequest, request_limit: Request):
    ...
```

---

### 5. Missing CORS Configuration
**File**: `app/main.py`
**Severity**: MEDIUM

If this API is consumed by a frontend, CORS is not configured. This could cause security issues if not handled properly.

**Fix**:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific origins, never use "*"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## HIGH PRIORITY ISSUES

### 6. Thread-Safety Issues with In-Memory Storage
**File**: `app/storage.py:8-10`
**Severity**: HIGH

```python
class ExpenseClaimStore:
    def __init__(self):
        self.claims: Dict[str, dict] = {}
        self.claim_counter = 0  # NOT THREAD-SAFE
```

**Problem**:
- `claim_counter` is not thread-safe for concurrent requests
- Two concurrent create operations could generate the same claim_id
- Dictionary access not synchronized

**Fix**:
```python
from threading import Lock
from uuid import uuid4

class ExpenseClaimStore:
    def __init__(self):
        self.claims: Dict[str, dict] = {}
        self._lock = Lock()
    
    def create_claim(self, ...) -> ExpenseClaimResponse:
        with self._lock:
            # Use UUID instead of counter
            claim_id = str(uuid4())[:8].upper()  # or f"CLM{uuid4().hex[:8]}"
            # ... rest of creation
```

**Or switch to UUID**:
```python
claim_id = f"CLM{uuid4().hex[:8].upper()}"  # CLM12A4B5C6
```

---

### 7. Missing Authorization Scheme in OpenAPI Docs
**File**: `app/main.py:23-27`
**Severity**: MEDIUM

The API uses Bearer token authentication but doesn't declare it in OpenAPI schema.

**Fix**:
```python
from fastapi.openapi.utils import get_openapi

app = FastAPI(
    title="Expense Approval Workflow API",
    description="API for managing expense claims with approval workflow",
    version="1.0.0",
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Expense Approval Workflow API",
        version="1.0.0",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "Bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    openapi_schema["security"] = [{"Bearer": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

---

## CODE QUALITY ISSUES

### 8. Excessive Code Duplication - Authorization Checks
**File**: `app/main.py:74-177`
**Severity**: MEDIUM

Authorization logic is repeated in multiple endpoints:

```python
# Pattern repeated 7+ times:
if current_user.role != UserRole.EMPLOYEE or claim.employee_id != current_user.user_id:
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="...")
```

**Fix**: Extract to helper functions:
```python
def require_claim_owner(current_user: User, claim: ExpenseClaimResponse) -> None:
    if current_user.role != UserRole.EMPLOYEE or claim.employee_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owner can access this claim"
        )

def require_assigned_manager(current_user: User, claim: ExpenseClaimResponse) -> None:
    if claim.manager_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager not assigned to this claim"
        )

def require_role(current_user: User, role: UserRole) -> None:
    if current_user.role != role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Only {role.value}s can perform this action"
        )
```

Then use FastAPI dependencies:
```python
from fastapi import Depends

def get_current_user(authorization: Optional[str] = Header(None)) -> User:
    # ... existing code
    return user

@app.put("/claims/{claim_id}/submit")
def submit_claim(
    claim_id: str,
    current_user: User = Depends(get_current_user),
) -> ExpenseClaimResponse:
    claim = store.get_claim(claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    require_claim_owner(current_user, claim)
    require_status(claim, ClaimStatus.DRAFT)
    
    return store.submit_claim(claim_id)
```

---

### 9. Overly Broad Exception Handling
**File**: `app/auth.py:42-43`
**Severity**: MEDIUM

```python
except Exception:  # Catches EVERYTHING silently
    return None
```

**Fix**: Catch specific exceptions:
```python
except (json.JSONDecodeError, KeyError, TypeError, ValueError):
    return None
```

---

### 10. Misleading Field Name: approval_reason
**File**: `app/models.py:103`, `app/storage.py:95-109`
**Severity**: MEDIUM

`approval_reason` field is used for both approvals AND rejections. When a claim is rejected, this field is overwritten with rejection reason, losing the approval reason (if any).

```python
# In rejection, this overwrites the approval_reason field:
claim["approval_reason"] = rejection_reason
```

**Fix**:
```python
class ExpenseClaimResponse(BaseModel):
    ...
    approval_reason: Optional[str] = None
    rejection_reason: Optional[str] = None  # Separate field
    # OR
    # review_notes: Optional[str] = None  # Generic field for both
```

---

### 11. Validation Logic Issues
**File**: `app/models.py:78-80`
**Severity**: MEDIUM

```python
@field_validator("description")
@classmethod
def validate_description(cls, v):
    if v is not None and (len(v) < 10 or len(v) > 1000):  # v could be empty string
        raise ValueError("description must be 10-1000 characters")
    return v
```

**Problem**: Empty string `""` passes because `len("")` is 0, and the condition is `len(v) < 10`. An empty string should be rejected.

**Fix**:
```python
if v is not None and (not v.strip() or len(v) < 10 or len(v) > 1000):
    raise ValueError("description must be 10-1000 characters and non-empty")
return v
```

---

### 12. Magic Strings and Numbers
**File**: `app/storage.py:22`, `app/models.py:51`
**Severity**: LOW

```python
claim_id = f"CLM{self.claim_counter:05d}"  # Magic format string
if len(v) < 10 or len(v) > 1000:  # Magic numbers
```

**Fix**: Use constants:
```python
# In a constants file or at module level
CLAIM_ID_PREFIX = "CLM"
CLAIM_ID_FORMAT = 5  # Zero-padded width
MIN_DESCRIPTION_LENGTH = 10
MAX_DESCRIPTION_LENGTH = 1000

# Then:
claim_id = f"{CLAIM_ID_PREFIX}{self.claim_counter:0{CLAIM_ID_FORMAT}d}"
if len(v) < MIN_DESCRIPTION_LENGTH or len(v) > MAX_DESCRIPTION_LENGTH:
```

---

## TEST COVERAGE GAPS

### 13. Missing Test Cases
**File**: `tests/`
**Severity**: MEDIUM

Significant gaps in test coverage despite 90% line coverage:

**Missing Tests**:
1. Employee with no manager assignment (workflow breaks)
2. Manager approval with unassigned claims
3. Invalid status filter value: `GET /claims?status=invalid`
4. Concurrent claim creation (claim_counter race condition)
5. Float precision in amount calculations
6. Very long strings (edge cases for validation)
7. Timestamp verification (not just presence, verify accuracy)
8. GET with invalid/non-existent claim_id for manager
9. Admin token usage (admin_token fixture exists but tests don't use it)
10. Health check endpoint behavior
11. Claim state transitions that should fail (e.g., can't approve rejected claim)
12. Manager cannot update claims (only employee)
13. Finance cannot cancel claims
14. Unauthorized access to other manager's claims

**Example of missing test**:
```python
def test_employee_without_manager_assignment(client, clear_store):
    """Test that employee without manager can still create claims"""
    # emp3 has no manager assignment
    token = get_token("emp3", UserRole.EMPLOYEE, "Sales")
    response = client.post(
        "/claims",
        json={"amount": 100.0, "description": "This is a test" * 2, ...},
        headers={"Authorization": f"Bearer {token}"}
    )
    # What should happen? Currently returns 201 with manager_id=None
    # but then workflow breaks because manager can't approve
```

---

## DESIGN & ARCHITECTURE ISSUES

### 14. Claim State Machine Not Validated
**File**: `app/main.py`
**Severity**: MEDIUM

The claim workflow states and transitions are not centrally defined. State machine is implicit in endpoint checks.

**Current flow**:
```
DRAFT -> SUBMITTED -> APPROVED -> PROCESSED
  |         |
  +-CANCELLED
        |
        v
      REJECTED
```

**Problem**: Logic scattered across endpoints; no single source of truth for valid transitions.

**Fix**: Define a state machine:
```python
from enum import Enum

class ClaimStateMachine:
    VALID_TRANSITIONS = {
        ClaimStatus.DRAFT: {ClaimStatus.SUBMITTED, ClaimStatus.CANCELLED},
        ClaimStatus.SUBMITTED: {ClaimStatus.APPROVED, ClaimStatus.REJECTED, ClaimStatus.CANCELLED},
        ClaimStatus.APPROVED: {ClaimStatus.PROCESSED},
        ClaimStatus.REJECTED: set(),  # Terminal state
        ClaimStatus.PROCESSED: set(),  # Terminal state
        ClaimStatus.CANCELLED: set(),  # Terminal state
    }
    
    @staticmethod
    def can_transition(from_status: ClaimStatus, to_status: ClaimStatus) -> bool:
        return to_status in ClaimStateMachine.VALID_TRANSITIONS.get(from_status, set())
```

---

### 15. Missing Audit Logging
**File**: `app/`
**Severity**: MEDIUM

No tracking of who approved/rejected claims or when state changes occurred.

**Current data**: `approval_reason` only, no approver_id, no audit trail.

**Fix**: Add audit logging:
```python
class ClaimAuditLog(BaseModel):
    claim_id: str
    action: str  # "created", "submitted", "approved", "rejected", "processed"
    performed_by: str
    timestamp: datetime
    reason: Optional[str] = None
    previous_status: Optional[ClaimStatus] = None
    new_status: Optional[ClaimStatus] = None

# Track all state changes
def log_action(claim_id: str, action: str, user_id: str, ...):
    store.add_audit_log(...)
```

---

### 16. No Request/Response Logging
**File**: `app/main.py`
**Severity**: LOW

No logging of requests or responses for debugging and monitoring.

**Fix**:
```python
import logging
from fastapi.middleware.trustedhost import TrustedHostMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1"])

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"{request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response
```

---

## MINOR ISSUES

### 17. Unused Import: python-jose not used
**File**: `requirements.txt` vs `app/auth.py`
**Severity**: LOW

`python-jose==3.3.0` in requirements but not used (base64 is used instead).

**Fix**: Either use it (recommended for JWT) or remove it.

---

### 18. Missing Input Sanitization
**File**: `app/models.py`
**Severity**: LOW

Receipt path and other string inputs not sanitized. Potential for path traversal if used directly.

```python
receipt_path: str  # Could be "../../../../etc/passwd"
```

**Fix**:
```python
from pathlib import Path

@field_validator("receipt_path")
@classmethod
def validate_receipt_path(cls, v):
    # Prevent path traversal
    if ".." in v or v.startswith("/"):
        raise ValueError("Invalid receipt path")
    # Validate as valid filename
    try:
        Path(v).name  # Extract just the filename
    except (ValueError, OSError):
        raise ValueError("Invalid receipt path format")
    return v
```

---

### 19. No Pagination for List Endpoint
**File**: `app/main.py:99-124`
**Severity**: LOW

`GET /claims` returns all claims without pagination. Could be problematic with large datasets.

**Fix**:
```python
@app.get("/claims", response_model=Page[ExpenseClaimResponse])
def list_claims(
    status_filter: Optional[str] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    authorization: Optional[str] = Header(None),
) -> Page[ExpenseClaimResponse]:
    # ... filter logic
    total = len(filtered_claims)
    paginated = filtered_claims[skip:skip + limit]
    return Page(items=paginated, total=total, skip=skip, limit=limit)
```

---

### 20. No Database Persistence
**File**: `app/storage.py`
**Severity**: MEDIUM (for production)

In-memory storage means all data is lost on restart. Fine for demo/testing, but must be documented.

**Fix for production**:
- Use SQLAlchemy with PostgreSQL/MySQL
- Add database migration system (Alembic)
- Implement connection pooling

---

## SUMMARY OF FIXES BY PRIORITY

### MUST FIX (Before any production use):
1. Replace base64 tokens with JWT (python-jose)
2. Add token expiration
3. Fix manager assignment logic
4. Add rate limiting to auth endpoint
5. Fix thread-safety issues

### SHOULD FIX (Before production):
6. CORS configuration
7. OpenAPI security scheme
8. Code duplication in auth checks
9. Audit logging
10. Better test coverage (especially edge cases)

### NICE TO HAVE (Best practices):
11. Request/response logging
12. Pagination for list endpoints
13. Input sanitization
14. Constants for magic numbers
15. Centralized state machine

---

## Test Coverage Analysis

**Positive Aspects**:
- Good happy path testing (test_happy_path_workflow)
- Status filtering tests
- Role-based access control tests
- State transition tests (submit, approve, reject, process)

**Negative Aspects**:
- No tests for missing manager assignment scenario
- No concurrent request tests
- No edge case testing (empty descriptions, very long strings)
- No timestamp validation
- Admin token not used in tests
- No negative tests for invalid transitions
- No tests for claims outside assigned manager scope

---

## Recommendations

1. **Immediate** (Security): Implement proper JWT tokens with expiration
2. **Immediate** (Security): Implement rate limiting on auth endpoint
3. **Week 1**: Extract duplicated authorization logic to dependencies
4. **Week 1**: Fix thread-safety issues
5. **Week 2**: Add audit logging
6. **Week 2**: Improve test coverage
7. **Week 3**: Add API documentation
8. **Before Production**: Replace in-memory storage with database

