---
name: grill-me
description: Interview the user about requirements and architectural design decisions. Use when the user wants to stress-test a plan before building, or uses any 'Plan' trigger phrases. Invokes /to-prd to write PLAN.md when complete.
---

Interview the user relentlessly about every aspect of this plan until we reach a shared understanding, focusing on both **functional requirements** and **architectural design decisions**. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one. For each question, provide your recommended answer.

Ask the questions one at a time, waiting for feedback on each question before continuing. Asking multiple questions at once is bewildering.

If a question can be answered by exploring the codebase, explore the codebase instead.

## When Interview is Complete

Once the interview is complete and the plan has been thoroughly discussed and validated, invoke the `/to-prd` skill to synthesize the conversation into a PLAN.md document that captures:
- All requirements discovered through the interview
- All architectural decisions and their rationale
- Key assumptions and constraints
- Testing approach
- Out of scope items

This ensures the refined plan is documented before implementation begins.
