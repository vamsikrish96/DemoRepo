# Slice Review Agent - Quick Start

## TL;DR

After implementing each feature slice with `/implement-slices`, invoke the review agent:

```bash
Agent({
  subagent_type: "slice-review",
  description: "Review Slice N code quality",
  prompt: "Review git diff against C:\workspace\WithPlanCleanCode\.claude\skills\clean-code\code-review-checklist.md",
  model: "claude-sonnet-4-6"
})
```

The agent reviews your code, provides findings, and hands control back to you.

## Standard Workflow

```
1. Run /implement-slices
   ↓
2. Slice implemented, tests pass
   ↓
3. Run /slice-review (Agent call above)
   ↓
4. Review findings
   ↓
5. Apply suggested fixes (if any)
   ↓
6. Run /implement-slices (continue)
   ↓
7. Next slice...
```

## What You'll Get Back

The agent returns structured findings:

```markdown
# Code Review: Slice N

**Score**: X/5
**Status**: ✅ Ready | ⚠️ Changes Recommended

## ✅ Strengths
- [What passed]

## ⚠️ Issues (if any)
- Issue 1: [Principle] at file.py:line
  Suggestion: [Refactoring code]
  
- Issue 2: [Principle] at file.py:line
  Suggestion: [Refactoring code]

## Next Steps
[What to do with findings]
```

## Review Principles Checked

1. ✅ **Meaningful Names** - Clear intent in variable/method/class names
2. ✅ **Functions & Abstraction** - <20 lines, 0-1 args, single purpose
3. ✅ **Comments** - "Why" comments only, no commented code
4. ✅ **Objects & Data Structures** - Proper encapsulation, Law of Demeter
5. ✅ **Defensive Design** - No null returns/params, clean error handling
6. ✅ **Unit Testing** - F.I.R.S.T. principles, Triple-A pattern
7. ✅ **Class Design** - Single responsibility, high cohesion, <200 lines

## Scores Explained

| Score | Meaning | Action |
|-------|---------|--------|
| 5/5 | Perfect | Commit and move on |
| 4/5 | Good | Apply 1-2 fixes, then commit |
| 3/5 | Okay | Address issues, continue |
| 2/5 | Needs Work | Refactor before commit |
| 1/5 | Poor | Major rewrite needed |

## Example Usage

### Implementation Complete
```bash
/implement-slices
# → Slice 5: Submit Expense implemented and tested ✓
```

### Invoke Review
```bash
Agent({
  subagent_type: "slice-review",
  description: "Review Slice 5 implementation",
  prompt: "Review the current git diff for the Submit Expense slice against the clean code checklist at C:\workspace\WithPlanCleanCode\.claude\skills\clean-code\code-review-checklist.md. Provide findings with line numbers and concrete suggestions.",
  model: "claude-sonnet-4-6"
})
```

### Review Results
```markdown
# Code Review: Slice 5 - Submit Expense

**Score**: 4/5
**Status**: ⚠️ Changes Recommended

## ✅ Strengths
- Excellent function naming
- All functions <20 lines
- Tests follow F.I.R.S.T.

## ⚠️ Issue Found

### Issue: Multiple Arguments
**Location**: expense.py:45-52
**What**: submitExpense(user_id, expense_data, requires_approval, auto_notify) has 4 args
**Why**: Hard to test; violates argument reduction
**Suggestion**: 
class ExpenseRequest:
    user_id: str
    expense_data: ExpenseData
    requires_approval: bool
    auto_notify: bool

def submitExpense(request):
    # implementation

## Next: Apply fix and proceed to Slice 6
```

### Apply Suggested Changes
```bash
# Main agent edits expense.py, applies refactoring
# Tests pass ✓
# Commit: "Refactor: encapsulate expense submission arguments"
```

### Continue
```bash
/implement-slices  # Resume to Slice 6
```

## Files Created

| File | Purpose |
|------|---------|
| `.claude/agents/slice-review-prompt.md` | Agent system prompt & instructions |
| `.claude/agents/QUICKSTART.md` | This file - quick reference |

## Tips

✅ **Do This:**
- Run review after EVERY slice
- Read findings carefully
- Apply high-impact suggestions (function length, arguments, tests)
- Use findings as learning opportunity
- Commit "code reviewed" when passing

❌ **Don't Do This:**
- Skip review to go faster
- Ignore 4/5 or lower scores
- Refactor unrelated code
- Bypass major issues
- Commit without addressing critical findings

## Questions?

See:
- **Agent Instructions**: `.claude/agents/slice-review-prompt.md`
- **Clean Code Checklist**: `.claude/skills/clean-code/code-review-checklist.md`

## Ready?

1. Implement a feature slice with `/implement-slices`
2. Copy the agent call above and paste it when prompted
3. Review the findings
4. Apply suggestions
5. Continue to next slice

**That's it!** The agent handles the heavy lifting of reviewing your code against clean principles.
