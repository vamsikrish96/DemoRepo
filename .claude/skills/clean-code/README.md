# Clean Code Skill: Complete Guide

This skill enforces Robert C. Martin's Clean Code principles across all development phases.

## Auto-Load Conditions

This skill automatically activates when:
- ✓ Writing new code
- ✓ Refactoring existing code
- ✓ Reviewing pull requests
- ✓ Designing architecture (/grill-me)
- ✓ Planning implementation (/to-prd)
- ✓ Implementing features
- ✓ Writing unit tests

## The Seven Pillars

### 1. Meaningful Names
- Intention-revealing names (no `data`, `info`, `temp`)
- Searchable names (no Hungarian notation)
- Nouns for classes, verbs for methods
- Boolean methods prefixed: `is`, `has`, `can`, `should`

**Quick Check:** Can someone understand what a variable does without reading its usage?

### 2. Functions & Abstraction
- Do one thing (one reason to change)
- Small (usually <20 lines)
- Few arguments (0-1 ideal, 2 ok, 3+ red flag)
- No boolean flags (split into separate functions)
- Command-Query Separation

**Quick Check:** Can you explain the function in one sentence?

### 3. Comments & Documentation
- Code speaks for itself (minimal comments)
- NO commented-out code ever
- Comments explain "why," not "what"
- Valid: legal headers, intent, warnings

**Quick Check:** Would the code be unclear without the comments?

### 4. Objects & Data Structures
- Objects hide data, expose behavior
- Data structures expose data, no logic
- No "train wrecks" (method chaining)
- Law of Demeter: access only immediate members

**Quick Check:** Can you tell if this is an object or data structure?

### 5. Defensive Design
- No null returns (use Optional, exceptions, Null Object)
- No null parameters (except at API boundaries)
- Fail fast with clear errors
- Edge cases handled cleanly

**Quick Check:** Are callers forced to null-check?

### 6. Clean Testing & TDD
- Three Laws of TDD (absolute rules)
- F.I.R.S.T. principles (Fast, Independent, Repeatable, Self-Validating, Timely)
- Triple-A pattern (Arrange, Act, Assert)
- One concept per test

**Quick Check:** Can each test run independently? Do tests tell you exactly what failed?

### 7. Class Design
- Single Responsibility Principle
- High cohesion (methods use most instance variables)
- Small (<200 lines)
- Boy Scout Rule (leave code cleaner)

**Quick Check:** Would this class have only one reason to change?

---

## During Architecture Design (/grill-me)

When designing the system architecture:

1. **Name Components Intentionally**
   - Service names should be verbs: `UserAuthenticator`, `InvoiceProcessor`
   - Layer names should be nouns: `Repository`, `Service`, `Controller`

2. **Design Single Responsibilities**
   - Each component has one reason to change
   - Ask: "Why would we need to modify this?"—should have only one answer

3. **Plan for Testability**
   - Design dependencies to be injectable
   - Minimize hidden dependencies
   - Design for unit testability from the start

4. **Define Clear Abstractions**
   - High-level business logic separate from low-level details
   - Interfaces should be minimal and focused
   - Plan for the Law of Demeter

5. **Example Questions:**
   - "Does this component have a single responsibility?"
   - "Can we test this in isolation?"
   - "Would a future developer understand this component's purpose from its name?"

---

## During Planning (/to-prd)

When creating architecture documentation:

1. **Embed Clean Principles into Design**
   - Document responsibility boundaries (SRP)
   - Define argument contracts (minimal arguments)
   - Plan error handling strategy

2. **Specify Test Strategy**
   - How will components be tested?
   - What are unit test boundaries?
   - What dependencies need mocking?

3. **Define Naming Conventions**
   - Class naming (nouns)
   - Method naming (verbs)
   - Constant naming (UPPER_CASE)

4. **Plan for Boy Scout Rule**
   - How will refactoring be tracked?
   - Code review process to enforce clean code?

---

## During Implementation

### Follow TDD Strictly

```
Red → Green → Refactor → Repeat
```

1. Write failing test
2. Write minimal code to pass
3. Refactor for clarity
4. Move to next feature

### Apply Clean Code to Every File

**Before committing, verify:**

- [ ] All names are intention-revealing
- [ ] All functions do one thing
- [ ] All arguments minimized (0-1)
- [ ] All comments explain "why"
- [ ] No commented-out code
- [ ] No null returns
- [ ] Error handling isolated
- [ ] Tests follow F.I.R.S.T.
- [ ] Classes have single responsibility
- [ ] File left cleaner than opened (Boy Scout Rule)

### Example: Clean Function

**Before (Violates Clean Code):**
```python
def proc(d, f):
    """Process data."""
    r = []
    for item in d:
        if f and len(item) > 0:
            r.append(item.upper())
        elif not f and len(item) < 50:
            r.append(item)
    return r
```

**After (Follows Clean Code):**
```python
def process_items(items: list[str], should_uppercase: bool) -> list[str]:
    if should_uppercase:
        return uppercase_nonempty_items(items)
    else:
        return filter_short_items(items)

def uppercase_nonempty_items(items: list[str]) -> list[str]:
    """Return non-empty items converted to uppercase."""
    return [item.upper() for item in items if item]

def filter_short_items(items: list[str]) -> list[str]:
    """Return items shorter than 50 characters."""
    return [item for item in items if len(item) < 50]
```

---

## During Code Review

Use the code review checklist in `code-review-checklist.md`.

**Focus Areas:**

1. **Names**: Are they intention-revealing?
2. **Function size**: Is it doing one thing?
3. **Arguments**: Are there too many?
4. **Comments**: Are they explaining "why"?
5. **Tests**: Do they follow F.I.R.S.T.?
6. **Error handling**: Is it isolated?
7. **Classes**: Do they have single responsibility?
8. **Demeter**: Are there train wrecks?

---

## When to Apply Clean Code Pragmatically

Clean Code is not dogma. Context matters:

### Legacy Systems
- Apply Boy Scout Rule incrementally
- Don't refactor everything at once
- Improve one small area with each change

### Performance-Critical Code
- Optimize only after proving slowness (profile first)
- Apply clean code principles first, optimize second
- Document performance reasoning in comments

### Third-Party APIs
- Wrap external APIs in adapters
- Handle null/error returns at boundaries
- Don't force clean code on external contracts

### Prototyping
- Speed matters initially
- Refactor to clean code before production
- Don't carry prototype patterns forward

---

## TDD Discipline

See `tdd-workflow.md` for comprehensive TDD guide.

### The Three Laws (Absolute)

1. **You are NOT allowed to write production code unless it is to make a failing test pass.**
2. **You are NOT allowed to write more test than is sufficient to fail.**
3. **You are NOT allowed to write more production code than is sufficient to pass the test.**

### F.I.R.S.T. Test Principles

- **F**ast: Runs instantly (no I/O, DB, network)
- **I**ndependent: No test depends on another
- **R**epeatable: Passes in any environment
- **S**elf-Validating: Clear pass/fail
- **T**imely: Written before production code

### Test Structure (Triple-A)

```python
def test_should_<expected_behavior>_when_<condition>():
    # Arrange: Set up preconditions
    calculator = Calculator()
    
    # Act: Execute behavior
    result = calculator.add(2, 3)
    
    # Assert: Verify outcome
    assert result == 5
```

---

## Key Resources

- **SKILL.md**: Complete reference of all 7 pillars
- **code-review-checklist.md**: Quick checklist for reviews
- **tdd-workflow.md**: Step-by-step TDD guide
- **naming-conventions.md**: Naming reference

---

## Summary: The Clean Code Covenant

```
I will:
✓ Write intention-revealing names
✓ Keep functions small and focused
✓ Minimize arguments and avoid flags
✓ Write tests before code (TDD)
✓ Make tests F.I.R.S.T. compliant
✓ Never return or pass null
✓ Keep classes focused (SRP)
✓ Follow the Boy Scout Rule
✓ Write comments that explain "why"
✓ Never leave commented-out code

I will not:
✗ Write vague variable names
✗ Create multi-purpose functions
✗ Use boolean flags
✗ Skip unit tests
✗ Write flaky or interdependent tests
✗ Return null without good reason
✗ Create "God classes"
✗ Leave code dirtier than I found it
✗ Use comments to explain bad code
✗ Leave commented-out code
```

**Every commit should make the codebase cleaner and more readable.**
