---
name: to-issues
description: Break a plan, spec, or PRD into feature slices. Invokes /publish-issues to create GitHub issues once user approves. Automatically invoked by /to-prd after plan/PRD is ready.
---

# To Issues

Break a plan into independently-grabbable issues using vertical slices (tracer bullets).

This skill is typically invoked by `/to-prd` after a plan or PRD document is created, but can also be used standalone to break down existing plans or specifications.

The issue tracker and triage label vocabulary should have been provided to you — run `/setup-matt-pocock-skills` if not.

## Process

### 1. Gather context

Work from whatever is already in the conversation context. If the user passes an issue reference (issue number, URL, or path) as an argument, fetch it from the issue tracker and read its full body and comments.

### 2. Explore the codebase (optional)

If you have not already explored the codebase, do so to understand the current state of the code. Issue titles and descriptions should use the project's domain glossary vocabulary, and respect ADRs in the area you're touching.

Look for opportunities to prefactor the code to make the implementation easier. "Make the change easy, then make the easy change."

### 3. Draft vertical slices

Break the plan into **tracer bullet** issues. Each issue is a thin vertical slice that cuts through ALL integration layers end-to-end, NOT a horizontal slice of one layer.

<vertical-slice-rules>

- Each slice delivers a narrow but COMPLETE path through every layer (schema, API, UI, tests)
- A completed slice is demoable or verifiable on its own
- Any prefactoring should be done first

</vertical-slice-rules>

### 4. Quiz the user

Present the proposed breakdown as a numbered list. For each slice, show:

- **Title**: short descriptive name
- **Blocked by**: which other slices (if any) must complete first
- **User stories covered**: which user stories this addresses (if the source material has them)

Ask the user:

- Does the granularity feel right? (too coarse / too fine)
- Are the dependency relationships correct?
- Should any slices be merged or split further?

Iterate until the user approves the breakdown.

### 5. Invoke /publish-issues

Once the user approves the slice breakdown, invoke `/publish-issues` to automatically create GitHub issues for each approved slice.

The skill will:
- Validate slice structure
- Order by dependencies (blockers first)
- Show preview for confirmation
- Create issues with acceptance criteria and blocking relationships
- Print issue URLs

Do NOT close or modify any parent issue.
