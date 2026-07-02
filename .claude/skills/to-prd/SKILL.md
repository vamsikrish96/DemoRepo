---
name: to-prd
description: Synthesize interview conversation into a plan document. When called after /grill-me, creates PLAN.md; otherwise publishes PRD to the project issue tracker.
---

This skill takes the current conversation context and codebase understanding to produce documentation. It is typically invoked by /grill-me after the interview phase is complete. Synthesis mode (no interview) — just synthesize what you already know from the conversation.

The issue tracker and triage label vocabulary should have been provided to you — run `/setup-matt-pocock-skills` if not.

## Process

1. Determine output mode:
   - **If called after /grill-me**: Write PLAN.md in the project root documenting the plan
   - **If called standalone**: Publish PRD to the project issue tracker

2. Explore the repo to understand the current state of the codebase, if you haven't already. Use the project's domain glossary vocabulary throughout the document, and respect any ADRs in the area you're touching.

3. Sketch out the seams at which you're going to test the feature. Existing seams should be preferred to new ones. Use the highest seam possible. If new seams are needed, propose them at the highest point you can. The fewer seams across the codebase, the better - the ideal number is one.

Check with the user that these seams match their expectations.

4. Write the document using the template below:
   - For PLAN.md: Document the refined plan with all requirements and architectural decisions
   - For PRD: Publish to the project issue tracker with the `ready-for-agent` triage label - no need for additional triage

5. Once the plan/PRD document is ready, invoke `/to-issues` to break it down into independently-grabbable feature slices or issues using vertical slice methodology

<prd-template>

## Problem Statement

The problem that the user is facing, from the user's perspective.

## Solution

The solution to the problem, from the user's perspective.

## User Stories

A LONG, numbered list of user stories. Each user story should be in the format of:

1. As an <actor>, I want a <feature>, so that <benefit>

<user-story-example>
1. As a mobile bank customer, I want to see balance on my accounts, so that I can make better informed decisions about my spending
</user-story-example>

This list of user stories should be extremely extensive and cover all aspects of the feature.

## Implementation Decisions

A list of implementation decisions that were made. This can include:

- The modules that will be built/modified
- The interfaces of those modules that will be modified
- Technical clarifications from the developer
- Architectural decisions
- Schema changes
- API contracts
- Specific interactions

Do NOT include specific file paths or code snippets. They may end up being outdated very quickly.

Exception: if a prototype produced a snippet that encodes a decision more precisely than prose can (state machine, reducer, schema, type shape), inline it within the relevant decision and note briefly that it came from a prototype. Trim to the decision-rich parts — not a working demo, just the important bits.

## Testing Decisions

A list of testing decisions that were made. Include:

- A description of what makes a good test (only test external behavior, not implementation details)
- Which modules will be tested
- Prior art for the tests (i.e. similar types of tests in the codebase)

## Out of Scope

A description of the things that are out of scope for this PRD.

## Further Notes

Any further notes about the feature.

</prd-template>
