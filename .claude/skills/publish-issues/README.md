# /publish-issues Skill

Publish finalized feature slices as GitHub issues with automatic dependency management.

## Overview

This skill invokes Claude Code to:

1. Parse finalized slices (from JSON file)
2. Validate structure and blocking relationships
3. Order by dependencies (blockers first)
4. Create GitHub issues automatically
5. Establish "Blocked by" links

## Workflow

```
/to-issues (Design slices)
     ↓
Review & refine
     ↓
/publish-issues (Create GitHub issues)
     ↓
GitHub issues #1, #2, #3... created with dependencies
     ↓
/implement-slices (Implement each issue)
```

## Usage

```
/publish-issues --repo owner/repo --file slices.json
```

That's it! The skill handles everything else:
- Parsing JSON
- Validating structure
- Ordering by dependencies
- Creating issues via GitHub API
- Linking dependencies

## Quick Start Example

### Step 1: Create slices.json

```json
[
  {
    "title": "[Slice 1] Foundation Setup",
    "description": "Initialize FastAPI project",
    "acceptance_criteria": ["App runs", "Auth works"],
    "blocked_by": null
  },
  {
    "title": "[Slice 2] Models",
    "description": "Create domain models",
    "acceptance_criteria": ["Models defined"],
    "blocked_by": 1
  }
]
```

### Step 2: Invoke skill

```
/publish-issues --repo owner/repo --file slices.json
```

### Step 3: Result

```
✓ Issue #1: [Slice 1] Foundation Setup
✓ Issue #2: [Slice 2] Models (blocked by #1)

2 issues created successfully!
```

## Input Format

### JSON Slice Structure

```json
{
  "title": "[Slice N] Feature Name",
  "description": "What to build - end-to-end description of this slice",
  "acceptance_criteria": [
    "Criterion 1",
    "Criterion 2",
    "Criterion 3"
  ],
  "blocked_by": null,
  "labels": ["slice", "priority:high"]
}
```

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Issue title (should follow "[Slice N]" pattern) |
| `description` | string | What to build (complete end-to-end behavior) |
| `acceptance_criteria` | array | Checklist of done conditions |

### Optional Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `blocked_by` | number | null | Issue number this slice depends on |
| `labels` | array | [] | Labels to add to GitHub issue |

## Real-World Example

### Input File: slices.json

```json
[
  {
    "title": "[Slice 1] Foundation: Project Setup & Auth",
    "description": "Set up FastAPI project with mocked Entra ID JWT authentication",
    "acceptance_criteria": [
      "FastAPI app running on port 8000",
      "JWT token parser works",
      "Auth middleware extracts claims",
      "Unit tests for auth"
    ],
    "blocked_by": null,
    "labels": ["slice", "foundation", "priority:high"]
  },
  {
    "title": "[Slice 2] Domain Models & Validation",
    "description": "Create Pydantic models with validation",
    "acceptance_criteria": [
      "Expense model with validators",
      "AuditLog model defined",
      "Tests for validation rules"
    ],
    "blocked_by": 1,
    "labels": ["slice", "models", "priority:high"]
  },
  {
    "title": "[Slice 3] Submit Expense Endpoint",
    "description": "Employee can submit expense claims",
    "acceptance_criteria": [
      "POST /expenses works",
      "Validation enforced",
      "Audit log created",
      "Integration tests pass"
    ],
    "blocked_by": 2,
    "labels": ["slice", "feature"]
  }
]
```

### Command

```bash
/publish-issues myorg/myapp --from-file slices.json
```

### Output

```
Creating GitHub issues for myorg/myapp...

Slices to be created (in order):

1. [Slice 1] Foundation: Project Setup & Auth
2. [Slice 2] Domain Models & Validation (blocked by #1)
3. [Slice 3] Submit Expense Endpoint (blocked by #2)

============================================================
Note: In actual implementation, this would call GitHub API
to create issues using: mcp__claude_ai_Github__github-create-issue
============================================================

✓ Issue #1: [Slice 1] Foundation: Project Setup & Auth
  https://github.com/myorg/myapp/issues/1

✓ Issue #2: [Slice 2] Domain Models & Validation (blocked by #1)
  https://github.com/myorg/myapp/issues/2

✓ Issue #3: [Slice 3] Submit Expense Endpoint (blocked by #2)
  https://github.com/myorg/myapp/issues/3

3 issues created successfully!
```

## Advanced Usage

### Using with /to-issues Output

1. Run `/to-issues` to design slices
2. Review and refine the output
3. Save as JSON file
4. Run `/publish-issues repo slices.json`

### Dependency Validation

The skill automatically validates that:
- All `blocked_by` references point to valid slices
- There are no circular dependencies
- Blockers are created before dependent issues

### Labels and Organization

```bash
/publish-issues org/repo \
  --labels "status:ready,priority:high" \
  --milestone "v1.0" \
  slices.json
```

## Integration Points

### With /to-issues

```
/to-issues plan
  → Review and discuss slices
  → Save finalized slices
/publish-issues org/repo --from-file finalized-slices.json
```

### With GitHub Project Boards

Once issues are created, link them to a project board:
- Create GitHub Project Board
- Add created issues
- Use board view to track progress

### With CI/CD

Reference issues in commit messages:
```
git commit -m "Implement Slice 1: Foundation setup

Closes #1 (GitHub issue created by /publish-issues)"
```

## Tips & Best Practices

### Design Phase
- Use `/to-issues` to break down work
- Keep slices vertical (thin but complete)
- Each slice should be deployable independently

### Refinement Phase
- Review acceptance criteria with team
- Verify blocking relationships
- Adjust slice size if too large/small

### Publication Phase
- Publish all slices at once for consistency
- Add to single milestone/project
- Assign immediately or use assignment rules

### Execution Phase
- Issues should be claimed in order (blockers first)
- Complete checklist items as work progresses
- Close issue when all criteria met

## Troubleshooting

### "Blocked by issue not found"
**Problem**: Referenced issue number doesn't exist
**Solution**: Check `blocked_by` values match actual slice indices

### "Repository not found"
**Problem**: GitHub authentication or wrong repo name
**Solution**: Verify repo exists and user has access

### Issues already exist
**Problem**: Want to update existing issues
**Solution**: Modify issues manually in GitHub or re-run with new slices

## Example Files

See `.claude/skills/publish-issues/example-slices.json` for a complete example of the Expense Approval Workflow API slices.

## Implementation Notes

The skill currently provides:
- ✅ Slice parsing (JSON, inline, file)
- ✅ Validation (blockers, references, structure)
- ✅ Dependency ordering (creates blockers first)
- ✅ Issue body formatting (with acceptance criteria)
- ✅ Preview before creation

When integrated with GitHub MCP tools, it will also:
- 📋 Call `github-create-issue` API
- 🔗 Establish "Blocked by" links
- 📍 Add labels and milestone
- 📊 Return issue URLs for tracking
