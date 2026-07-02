# /implement-slices Skill

Automate feature slice implementation with testing, progress tracking, and git commits.

## Overview

This skill runs after `/publish-issues` to implement each feature slice:

1. **Runs tests** for each slice in order
2. **Tracks progress** in PROGRESS.md (real-time)
3. **Commits to GitHub** after successful tests
4. **Updates task list** automatically
5. **Respects dependencies** (blocked slices)

## How It Works

The skill invokes Claude Code to:

```
/implement-slices
  ↓
For each slice:
  1. Install requirements.txt
  2. Run tests
  3. Update PROGRESS.md
  4. Commit if tests pass
  5. Update task list
  ↓
Final summary in PROGRESS.md
```

## Quick Start

```
/implement-slices
```

That's it! The skill handles:
- Finding test files
- Running pytest
- Tracking progress
- Creating commits
- Updating tasks

## Process for Each Slice

```
1. Check if blocked by other slices
   ↓
2. Install requirements.txt
   ↓
3. Run corresponding unit tests
   ↓
4. If tests pass:
   - Create git commit
   - Update PROGRESS.md
   - Mark task as completed
5. If tests fail:
   - Log error to PROGRESS.md
   - Mark task as blocked
   - Continue to next slice
```

## Test Mapping

The skill automatically maps slices to test files:

**Expense Approval API:**

| Slice | Test File | Tests |
|-------|-----------|-------|
| 1: Auth | test_auth.py | 8 |
| 2: Models | test_models.py | 8 |
| 3: Database | test_workflows.py | 3 |
| 4: Error Handling | Various | Multiple |
| 5-12 | test_workflows.py | Per-slice |

**See test-mapping.json** for complete mapping with test patterns.

### How Test Mapping Works

- Look at slice title
- Find corresponding test file in test-mapping.json
- Run: `pytest tests/test_file.py -v`
- Parse output for pass/fail counts
- Update PROGRESS.md

## Example Execution

### Input: 12 Feature Slices

```bash
/implement-slices --repo vamsikrish96/expense-approval
```

### Output Progress

```
Implementing feature slices for vamsikrish96/expense-approval...

Installing requirements...
✓ requirements.txt installed

[1/12] [Slice 1] Foundation: Project Setup & Auth Middleware
  → Running tests: test_auth.py...
  ✓ 8 tests passed
  → Committing changes...
  ✓ Committed (a1b2c3d)
  → Marking as completed

[2/12] [Slice 2] Domain Models & Validation
  → Running tests: test_models.py...
  ✓ 8 tests passed
  → Committing changes...
  ✓ Committed (b2c3d4e)
  → Marking as completed

[3/12] [Slice 3] In-Memory Database Layer
  → Running tests: test_workflows.py...
  ✓ 3 tests passed
  → Committing changes...
  ✓ Committed (c3d4e5f)
  → Marking as completed

[4/12] [Slice 4] Error Handling & Configuration
  → Running tests: test_*.py...
  ✓ Tests passed
  → Committing changes...
  ✓ Committed (d4e5f6g)
  → Marking as completed

[5/12] [Slice 5] Employee: Submit Expense Claim
  → Running tests: test_submit_expense_workflow...
  ✓ 1 test passed
  → Committing changes...
  ✓ Committed (e5f6g7h)
  → Marking as completed

...

============================================================
Implementation Summary: 12/12 slices completed
============================================================

Progress saved to PROGRESS.md
```

### PROGRESS.md Generated

```markdown
# Implementation Progress

**Last Updated**: 2026-06-28T20:30:00Z

## Summary

- Total Slices: 12
- Completed: 12
- In Progress: 0
- Pending: 0
- Failed: 0

## Status by Slice

### ✅ [Slice 1] Foundation: Project Setup & Auth Middleware

- **Status**: completed
- **Tests**: Passed (8/8)
- **Committed**: 2026-06-28T20:05:00Z
- **Commit**: a1b2c3d

### ✅ [Slice 2] Domain Models & Validation

- **Status**: completed
- **Tests**: Passed (8/8)
- **Committed**: 2026-06-28T20:10:00Z
- **Commit**: b2c3d4e

...
```

### Git Commits Created

```
commit a1b2c3d
Author: Claude Haiku 4.5 <noreply@anthropic.com>

    Implement [Slice 1] Foundation: Project Setup & Auth Middleware

    Slice #1: Set up FastAPI with mocked Entra ID JWT auth

    Tests: 8/8 passed

    Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>

commit b2c3d4e
Author: Claude Haiku 4.5 <noreply@anthropic.com>

    Implement [Slice 2] Domain Models & Validation

    Slice #2: Create Pydantic models with validation

    Tests: 8/8 passed
```

## Options in Detail

### --repo (Required)
GitHub repository in format `owner/repo`

### --progress-file
Path to progress tracking file (default: PROGRESS.md)

### --skip-tests
Skip running tests for each slice (useful for demonstration)

### --no-commit
Don't create git commits after successful tests

### --parallel
Run multiple slices in parallel (default: sequential)

### --max-parallel
Maximum number of parallel slices (default: 3)

### --only-failed
Only implement slices that previously failed

## Task List Integration

The skill automatically:
- Creates a task for each slice
- Marks as `in_progress` when implementing
- Marks as `completed` when tests pass
- Marks as `blocked` if tests fail

Tasks can be viewed with `/help` or in the task list.

## Error Handling

### Test Failures

If a test fails:
1. Error logged to PROGRESS.md
2. Slice marked as "failed"
3. Implementation continues to next slice
4. User can review failures and retry

### Git Commit Failures

If git commit fails:
1. Tests still passed ✓
2. Changes are staged
3. Manual commit may be needed
4. Logged to PROGRESS.md

### Requirements Installation Failures

If requirements.txt installation fails:
1. Process stops
2. User must install manually
3. Re-run skill after manual fix

## Real-World Example

The Expense Approval API has 12 slices:

```
/implement-slices
  ↓
[1/12] Slice 1: Auth Middleware
  → pytest test_auth.py
  ✓ 8/8 passed → Commit #a1b2c3d
  ✓ Task marked completed
  ↓
[2/12] Slice 2: Models
  → pytest test_models.py
  ✓ 8/8 passed → Commit #b2c3d4e
  ✓ Task marked completed
  ↓
[3/12] Slice 3: Database
  → pytest test_workflows.py
  ✓ 3/3 passed → Commit #c3d4e5f
  ✓ Task marked completed
  ↓
... (9 more slices)
  ↓
============================================================
Summary: 12/12 slices completed
PROGRESS.md updated with all results
============================================================
```

## Best Practices

### Before Running

1. **Ensure clean git state**: `git status` should show no uncommitted changes
2. **Update requirements.txt** if dependencies changed
3. **Review PROGRESS.md** to understand current state
4. **Have tests ready** for each slice

### During Execution

1. **Monitor progress** in real-time
2. **Check PROGRESS.md** for failures
3. **Review commits** in GitHub

### After Execution

1. **Verify all tests passed**
2. **Check PROGRESS.md** for summary
3. **Review git log** for commits
4. **Push to GitHub** (if not auto-pushed)

## Troubleshooting

### "Tests failed for Slice X"

Check PROGRESS.md for error details:
```bash
cat PROGRESS.md | grep -A5 "Slice X"
```

Run tests manually:
```bash
pytest tests/ -v
```

### "Requirements not installed"

Install manually:
```bash
pip install -r requirements.txt
```

Then re-run skill.

### "Git commit failed"

Check git status:
```bash
git status
```

Resolve conflicts/issues, then re-run.

### "No tests found for Slice X"

Verify test file exists:
```bash
ls tests/test_*.py
```

Update test mapping or create tests.

## Files in This Skill

- **SKILL.md** - Complete documentation of how the skill works
- **test-mapping.json** - Slice-to-test file mappings
- **README.md** - This file, usage guide

## Implementation Details

The skill is implemented in Claude Code using:
- **Bash** - Run pytest, git commands
- **Read/Write** - Update PROGRESS.md
- **TaskCreate/TaskUpdate** - Manage task list
- **Bash** - Git commits with detailed messages

No external Python script needed - everything uses Claude Code's native tools.

## Requirements

- Python 3.9+ (for pytest)
- pytest installed
- git configured
- requirements.txt present
- Working directory: project root

## Safety

✓ Tests must pass before committing
✓ No changes without successful tests
✓ PROGRESS.md always shows current state
✓ Easy to review what happened
✓ Can resume/retry after interruption
