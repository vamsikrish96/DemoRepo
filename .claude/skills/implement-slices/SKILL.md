---
name: implement-slices
description: Implement feature slices from /to-issues. Writes code with /clean-code, runs tests, invokes /feature-slice-reviewer, commits to GitHub, updates task list.
---

Implement feature slices one by one with testing, code review, and git commits.

## ⚠️ NON-NEGOTIABLE REQUIREMENTS

**1. Code review with /feature-slice-reviewer is MANDATORY before every commit.**
   - After writing code and running tests, MUST invoke /feature-slice-reviewer agent
   - Code review CANNOT be skipped, deferred, or bypassed
   - Review findings MUST be addressed before proceeding to commit
   - This ensures adherence to /clean-code principles for every slice

**2. GitHub commit to remote is MANDATORY after every feature slice.**
   - After each slice passes clean code review:
   - GitHub remote MUST be configured (`git remote -v`)
   - Code MUST be committed: `git commit -m "[Slice N] <slice-title>"`
   - Commit MUST be pushed to remote: `git push origin <branch-name>`

Both requirements are hard rules for EVERY feature slice, with no exceptions. If GitHub is not configured, configure it before proceeding.

## Workflow

For each feature slice (in order, respecting dependencies):

1. **Show task list** - Display all slices with current status
2. **Mark in-progress** - Update task as currently being worked on
3. **Write code** - Follow /clean-code principles for implementation
4. **Run tests** - Execute relevant test suite
5. **Review** - Invoke /feature-slice-reviewer agent for code review **(CANNOT BE SKIPPED)**
6. **If approved** → **COMMIT TO REMOTE GITHUB (NON-NEGOTIABLE)**, mark task completed
7. **If changes needed** → Apply feedback, re-test, and re-review (return to step 5)

⚠️ **Step 5 (Review) is mandatory and cannot be deferred or skipped for any reason.**

## Key Features

- **Sequential**: One slice at a time in dependency order
- **Clean code**: Applies /clean-code principles during implementation
- **Automated review**: /feature-slice-reviewer checks quality before commit
- **Task tracking**: Updates task list after each slice
- **Git integration**: Commits with slice info and test results
- **Dependency respect**: Skips blocked slices, resumes when blocker completes

## Requirements

- **GitHub repository MUST be configured** - Remote origin must be set and accessible (`git remote -v`)
- Test suite available
- requirements.txt with dependencies
- Working directory: project root

## GitHub Configuration Check

Before starting: `git remote -v` must show an origin URL. If missing, configure now:
```bash
git remote add origin https://github.com/user/repo.git
git remote -v  # verify
```
