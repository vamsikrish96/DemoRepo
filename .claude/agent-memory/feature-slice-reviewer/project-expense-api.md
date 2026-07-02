---
name: project-expense-api
description: Expense Approval Workflow API — FastAPI project at C:\workspace\WithPlanCleanCode, reviewed through Slice 1 (foundation)
metadata:
  type: project
---

Python FastAPI project for an Expense Approval Workflow. Root at `C:\workspace\WithPlanCleanCode`.

Tech stack: FastAPI, Pydantic v2 (BaseModel with field_validator), pytest, Python dataclasses for domain models.

Architecture layers (Slice 1 current state):
- `app/models.py` — Python dataclasses (Expense, ExpenseHistory, User) + Enums
- `app/schemas.py` — Pydantic BaseModel schemas for request/response
- `app/auth.py` — Mock auth; token format is `user_id:role` (not base64 JSON)
- `app/repositories.py` — Three separate in-memory dicts (ExpenseRepository, ExpenseHistoryRepository, UserRepository) exposed as module-level singletons
- `app/services.py` — ExpenseService and ApprovalService; also exposed as module-level singletons; grab repos from module globals, not via constructor DI
- `app/api/expenses.py`, `app/api/approvals.py` — stub routers (populated in later slices)
- `app/main.py` — FastAPI app, calls `init_test_data()` on startup (SRP issue)

**Why:** Learning/demo project built slice-by-slice with a clean-code review gate before each slice proceeds. Mock auth is intentional.

**How to apply:** Focus suggestions on clean code principles (DRY, SRP, type safety, FIRST tests, null handling). Do not flag mock auth as a security concern — it's by design.

Key issues identified in Slice 1 review:
- Module-level singleton repos/services break test independence (FIRST)
- `Expense.expense_date: str` vs schema `date` type mismatch
- Approval guard pattern repeated 5× in ApprovalService (DRY)
- `get_expense_with_history` returns `Optional[dict]` with magic string keys
- `init_test_data()` called at production startup (SRP)
- `ApprovalSchema` is dead code in schemas.py
- Two `datetime.utcnow()` calls per approval method (timestamp drift bug)
- Repository `storage` attribute is public (encapsulation)
