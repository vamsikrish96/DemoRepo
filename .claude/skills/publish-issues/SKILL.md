---
name: publish-issues
description: Create GitHub issues for finalized feature slices. Automatically invoked by /to-issues after user approval.
---

Publish feature slices as GitHub issues once user approves them in /to-issues.

## ⚠️ NON-NEGOTIABLE REQUIREMENT

**GitHub remote MUST be configured before publishing issues.** If not already configured, work with the user to:
1. Create or authenticate with a GitHub repository
2. Add remote to local git: `git remote add origin <github-repo-url>`
3. Verify connection: `git remote -v`

Only after GitHub remote is confirmed should issue publishing proceed.

## Process

1. **Verify GitHub remote** - Check if origin is configured; if not, configure with user
2. Validate slice structure (required: title, description, acceptance_criteria)
3. Order by dependencies (blockers first)
4. Show preview to user for confirmation
5. Create GitHub issues in order, establishing "Blocked by" links
6. Print issue URLs

## Slice Format

```json
{
  "title": "[Slice 1] Feature name",
  "description": "What to build",
  "acceptance_criteria": ["Criterion 1", "Criterion 2"],
  "blocked_by": null,
  "labels": ["slice"]
}
```

**Required:** title, description, acceptance_criteria  
**Optional:** blocked_by (issue number), labels (array)
