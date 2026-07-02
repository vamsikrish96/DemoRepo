# Expense Approval Workflow API - Implementation Plan

## Problem Statement

Organizations need a streamlined system for employees to submit expense claims, managers to approve them, and finance teams to process approved claims. Currently, there's no centralized API to manage this workflow, track approval status, and maintain audit trails.

## Solution

Build a FastAPI-based REST API that manages the complete expense approval workflow. The system will handle claim submission, manager approval/rejection, finance processing, and provide status visibility to employees at each stage. Authentication will use Bearer tokens, and data will be stored in-memory for this MVP.

## User Stories

1. As an **employee**, I want to create a new expense claim, so that I can request reimbursement for my work-related expenses
2. As an **employee**, I want to view the status of my submitted claims, so that I can track the approval progress
3. As an **employee**, I want to submit a claim with expense details (amount, description, receipt), so that the approval process has all required information
4. As an **employee**, I want to cancel my draft or submitted claims, so that I can withdraw incorrect submissions
5. As an **employee**, I want to see rejection reasons when my claim is denied, so that I can correct and resubmit if needed
6. As a **manager**, I want to view all claims from my assigned employees, so that I can process approvals efficiently
7. As a **manager**, I want to approve an expense claim, so that I can authorize reimbursement
8. As a **manager**, I want to reject an expense claim with a reason, so that employees understand why their claim was declined
9. As a **manager**, I want to see pending claims first, so that I can prioritize high-volume workflows
10. As **finance**, I want to view all approved claims, so that I can process them for reimbursement
11. As **finance**, I want to mark a claim as processed, so that employees and managers know the reimbursement is in progress
12. As **finance**, I want to see processing history, so that I can maintain records for audit purposes
13. As an **admin**, I want to view all claims in the system, so that I can troubleshoot and verify workflow correctness
14. As an **API consumer**, I want clear error messages with error codes, so that I can handle errors appropriately

## Implementation Decisions

### 1. Workflow States & Transitions

The expense claim lifecycle follows a linear, non-cyclical workflow:

- **DRAFT** → Created by employee, not yet submitted
- **SUBMITTED** → Sent to manager for review
- **APPROVED** → Manager approved, awaiting finance processing
- **REJECTED** → Manager rejected; employee can view reason
- **PROCESSED** → Finance has completed processing
- **CANCELLED** → Employee or system cancelled (end state)

Valid transitions:
- DRAFT → SUBMITTED (employee submits)
- DRAFT → CANCELLED (employee cancels)
- SUBMITTED → APPROVED (manager approves)
- SUBMITTED → REJECTED (manager rejects)
- APPROVED → PROCESSED (finance processes)
- SUBMITTED/APPROVED → CANCELLED (can be cancelled before processing)

### 2. Expense Claim Data Model

Each expense claim contains:
- `claim_id`: Unique identifier (UUID or auto-increment)
- `employee_id`: Submitting employee
- `amount`: Expense amount (positive decimal)
- `description`: What the expense was for (required, non-empty)
- `receipt_path`: Path/reference to receipt file (required, non-empty)
- `category`: Optional categorization (e.g., Travel, Meals, Office Supplies)
- `status`: Current state in workflow
- `manager_id`: Assigned manager for approval
- `submission_date`: Timestamp when SUBMITTED
- `approval_reason`: Reason for approval/rejection (populated only if APPROVED/REJECTED)
- `processed_date`: Timestamp when PROCESSED
- `created_at`: Creation timestamp
- `updated_at`: Last modification timestamp

### 3. User Roles & Permissions

Four distinct roles:
- **Employee**: Can create, submit, view own claims; can cancel DRAFT/SUBMITTED claims
- **Manager**: Can approve/reject SUBMITTED claims; can view assigned employee claims
- **Finance**: Can view APPROVED claims; can mark as PROCESSED
- **Admin**: Can view all claims and perform any action (for testing/debugging)

### 4. Authentication & Authorization

- Use Bearer token authentication (mocked for this implementation)
- Token payload should include: `user_id`, `role`, and optional `department`
- Middleware will extract and validate tokens
- Role-based access control (RBAC) enforced at endpoint level
- Manager must be assigned to employee to approve their claims

### 5. Approval Model

Simple two-stage approval:
- **Stage 1 (Manager)**: Manager approves or rejects (no amount thresholds)
- **Stage 2 (Finance)**: Finance processes all approved claims

No complex routing or multi-level approvals for this MVP.

### 6. Input Validation Rules

- `amount` must be > 0
- `receipt_path` must be non-empty string (max 500 chars)
- `description` must be 10-1000 characters
- `category` if provided, must be from predefined list (optional)
- State transitions must follow the state machine above
- Only manager assigned to employee can approve their claims

### 7. Error Response Format

Standardized error responses across all endpoints:
```json
{
  "error": "Human-readable error message",
  "code": "ERROR_CODE",
  "details": {}  // Optional additional context
}
```

HTTP status codes:
- 400: Bad Request (validation errors)
- 401: Unauthorized (missing/invalid token)
- 403: Forbidden (insufficient permissions)
- 404: Not Found
- 409: Conflict (invalid state transition)
- 500: Server Error

### 8. Data Persistence

In-memory storage using Python dictionaries/lists. Data is lost on server restart. For production, this would be replaced with a database.

### 9. API Endpoints Structure

**Expense Claims:**
- `POST /claims` - Create new claim (Employee)
- `GET /claims` - List claims (filtered by role)
- `GET /claims/{id}` - View specific claim
- `PATCH /claims/{id}` - Update claim (draft only, Employee)
- `PUT /claims/{id}/submit` - Submit claim for approval (Employee)
- `PUT /claims/{id}/cancel` - Cancel claim (Employee)

**Manager Actions:**
- `PUT /claims/{id}/approve` - Approve claim (Manager)
- `PUT /claims/{id}/reject` - Reject claim (Manager)

**Finance Actions:**
- `PUT /claims/{id}/process` - Mark as processed (Finance)

**User/Auth:**
- `POST /auth/login` - Get bearer token (mocked)
- `GET /users/me` - Get current user info

### 10. Testing Seam

Single high-level seam: Test all endpoints via HTTP requests through FastAPI test client. This tests the complete flow without mocking internal components. Unit tests for validators and business logic as needed.

## Testing Decisions

### Testing Philosophy

- Test **external behavior** (API responses, state changes) not implementation details
- Each test should verify one logical flow
- Use FastAPI's TestClient for integration testing
- Mock authentication by providing tokens directly in test fixtures

### Test Coverage Goals

- Aim for >80% code coverage
- Cover happy paths: submit → approve → process
- Cover error paths: validation errors, invalid transitions, permission denials
- Cover edge cases: concurrent submissions, state conflicts

### Test Categories

1. **Authentication & Authorization Tests**
   - Valid/invalid tokens
   - Role-based access control
   - Permission checks per endpoint

2. **Claim Submission Tests**
   - Create claim with valid data
   - Validation errors (invalid amount, missing receipt, etc.)
   - Submit claim state transition
   - Cancel claim

3. **Manager Approval Tests**
   - Approve valid claim
   - Reject with reason
   - Only assigned manager can approve
   - Cannot approve non-SUBMITTED claims

4. **Finance Processing Tests**
   - Process APPROVED claims
   - Cannot process non-APPROVED claims
   - View approved claims list

5. **Workflow Tests**
   - Complete happy path: DRAFT → SUBMITTED → APPROVED → PROCESSED
   - Rejection and cancellation flows
   - Invalid state transitions

6. **Data Validation Tests**
   - Amount boundaries
   - Description length
   - Receipt path requirement
   - Category validation

## Out of Scope

1. **Database persistence**: Using in-memory storage only
2. **Real authentication**: Using mocked bearer tokens
3. **File upload/storage**: Receipt path is a string reference only, no file handling
4. **Email notifications**: No user notifications for approvals/rejections
5. **Audit logging**: No detailed audit trail of all actions
6. **Advanced reporting**: No analytics or reporting dashboards
7. **Multi-company support**: Single organization only
8. **Concurrent conflict resolution**: No handling of race conditions
9. **Budget limits**: No enforcement of department/employee budgets
10. **Integration with payroll**: No connection to payroll systems

## Further Notes

### Architecture

The API will follow a layered architecture:
- **Routes/Handlers**: Define endpoints and request/response handling
- **Services**: Business logic for claim management and workflow
- **Models**: Pydantic models for data validation and serialization
- **Storage**: In-memory repository pattern
- **Middleware**: Authentication and error handling

### Dependencies

- FastAPI: Web framework
- Pydantic: Data validation
- pytest: Testing framework
- python-jose (or simple JWT): Token handling

### Next Steps

1. Break down into feature slices using `/to-issues`
2. Implement each slice using `/implement-slices`
3. Ensure >80% test coverage
4. Verify all workflows end-to-end
