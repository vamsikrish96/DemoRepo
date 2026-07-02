# /clean-code

Enforce Robert C. Martin's Clean Code principles across all development phases.

## Trigger Conditions

This skill auto-loads when:
- Writing new code
- Refactoring existing structures
- Reviewing pull requests or feature implementations
- Optimizing functions and classes
- Designing architecture (/grill-me, /to-prd)
- Implementing test-driven development

## The Seven Pillars of Clean Code

### 1. Meaningful Names

**Intention-Revealing Names**
- Variable, class, and method names must clearly state **why** they exist, **what** they do, and **how** they are used
- Avoid vague names: `data`, `info`, `handler`, `temp`, `obj`
- Names should answer the "why" without requiring comments

**Searchable Names**
- Use longer, descriptive names for variables with broader scopes
- Avoid brief technical encodings, Hungarian notation (`m_var`, `s_str`), or member prefixes
- Single-letter names only acceptable in short loop contexts (but even `index` is better than `i`)

**Naming Conventions**
- **Classes**: Nouns or noun phrases (`UserAccount`, `PaymentProcessor`, `InvoiceValidator`)
- **Methods**: Verbs or verb phrases (`calculateTotal()`, `isValid()`, `fetchUser()`)
- **Boolean methods/variables**: Prefix with `is`, `has`, `can`, `should` (`isActive`, `hasPermission`, `canDelete`)
- **Constants**: UPPER_CASE with underscores (`MAX_RETRY_COUNT`, `DEFAULT_TIMEOUT`)

**Anti-Patterns**
- ❌ Names that require comments to explain
- ❌ Names that differ from their actual behavior
- ❌ Names that mislead about scope or lifetime
- ❌ Names copied from external domains without clarification

---

### 2. Functions & Abstraction Levels

**Do One Thing**
- Functions must be exceptionally small
- One reason to change = one thing the function does
- If a distinct block can be extracted into a named function, the parent is doing too much
- If a function has more than one level of nesting, it's probably doing too much

**The Stepdown Rule**
- Arrange code top-to-bottom like a narrative
- High-level operations flow to lower-level details
- Each function followed by functions it calls at the next abstraction level

**Single Level of Abstraction**
- Don't mix high-level business logic with low-level implementation details
- ❌ Bad: `if (user.email.contains('@'))` mixed with complex business validation
- ✓ Good: `isValidEmail(user.email)` abstracts the detail

**Argument Reduction**
- **0 arguments**: Ideal (query methods)
- **1 argument**: Acceptable (transformations, filters)
- **2 arguments**: Tolerable (compare operations, map operations)
- **3+ arguments**: Red flag—encapsulate into configuration/argument objects

**No Flag Arguments**
- Never pass boolean flags to alter execution path
- ❌ `process(data, true)` — what does true mean?
- ✓ `processAndCache(data)` and `process(data)` — separate, intention-clear functions

**Command Query Separation (CQS)**
- **Command**: Changes state, returns nothing (`save()`, `delete()`, `update()`)
- **Query**: Returns information, changes nothing (`get()`, `find()`, `calculateTotal()`)
- ❌ Bad: `if (deleteUser(id))` — is this querying or commanding?
- ✓ Good: `deleteUser(id); wasDeleted = exists(id)` — clear separation

**Error Handling**
- Prefer throwing structured exceptions over returning error codes
- Extract entire `try/catch` blocks into standalone functions
- Error handling is the singular responsibility of that function

---

### 3. Comments & Documentation

**Let Code Speak**
- Write clean, expressive code rather than writing comments to explain messy logic
- The best comment is a good function name or clear variable name
- If you need a comment to explain what code does, refactor the code instead

**Zero Commented-Out Code**
- Never leave commented-out source code in files
- Delete it entirely; version control preserves the history
- Commented code confuses future readers about intent

**Eliminate Noise**
- Remove redundant comments that mirror clear method signatures
- ❌ `// increment counter` above `counter++`
- ✓ No comment needed—the code is clear
- ✓ Only add comments for "why" decisions, not "what" the code does

**Valid Comments**
- ✓ Legal/copyright headers
- ✓ Explanations of intent (why this approach over alternatives)
- ✓ Warnings about hidden consequences (`// WARNING: This is slower than...`)
- ✓ Clarification of intent when code is unclear and can't be refactored
- ✓ Documentation of public APIs (docstrings)

---

### 4. Objects, Data Structures & Demeter

**Data-Object Anti-Symmetry**
- **Objects**: Hide internal data behind behavioral abstractions
  - Expose behavior (methods)
  - Hide implementation (private state)
  - Example: `userAccount.withdraw(amount)` — caller doesn't know *how*
- **Data Structures**: Expose raw data, contain zero business logic
  - Example: DTO/config objects with getters/setters only
  - No mixing of logic into data holders

**Law of Demeter**
- A module must not know the inner workings of objects it manipulates
- Access only the immediate members of your object
- Eliminate "train wrecks":
  - ❌ `entity.getProfile().getSettings().getTheme().getValue()`
  - ✓ `entity.getTheme()` — hide the path

**Hybrid Structures (Anti-Pattern)**
- Don't build confusing hybrid structures mixing data exposure with hidden behavior
- Either expose data (DTO) or hide it (Object), never both

---

### 5. Defensive Design & Stability

**Define the Normal Flow**
- Use Special Case Pattern or Null Object Pattern to handle edge cases cleanly
- Avoid deeply nested conditional exception-handling blocks
- Handle exceptions at boundaries; let the happy path flow

**Never Return or Pass Null**
- Don't return `null` to force callers into constant null-checking boilerplate
- Instead:
  - Use Optional types
  - Return empty collections instead of null
  - Use Null Object pattern
  - Raise exceptions for true error conditions
- Only pass `null` when crossing third-party API boundaries

**Assertions and Contracts**
- Use assertions to validate preconditions in private methods
- Make contracts explicit in public method documentation
- Fail fast with clear error messages

---

### 6. Clean Unit Testing Architecture & TDD

**The Three Laws of TDD** (Absolute)
1. **You are NOT allowed to write production code unless it is to make a failing unit test pass.**
2. **You are NOT allowed to write more of a unit test than is sufficient to fail** (not compiling is failing).
3. **You are NOT allowed to write more production code than is sufficient to pass the one failing test.**

**Build-Operate-Check Pattern**
Every unit test follows the Triple-A or Build-Operate-Check pattern:
```
1. Arrange (Build): Set up test fixtures, data, preconditions
2. Act (Operate): Execute the function/behavior under test
3. Assert (Check): Verify the outcome matches expectations
```

**F.I.R.S.T. Principles for Tests**
- **Fast**: Tests run instantly. No I/O, database, network. Use mocks/fakes.
- **Independent**: No test depends on another. Each test fully self-contained.
- **Repeatable**: Tests pass in any environment. No flaky timing dependencies.
- **Self-Validating**: Clear pass/fail. No manual inspection of logs or output.
- **Timely**: Tests written before production code (TDD). Not afterthoughts.

**Single Concept Per Test**
- Minimize assertions per test to validate exactly one conceptual outcome
- One test = one reason to fail
- Clear, intention-revealing test names: `shouldThrowExceptionWhenAmountIsNegative()`

**Testing Pyramid**
- Many unit tests (fast, isolated)
- Fewer integration tests (real dependencies)
- Few end-to-end tests (full system)

---

### 7. Class Design & Emergence

**Single Responsibility Principle (SRP)**
- A class has one, and only one, structural reason to change
- If you struggle to name a class, it likely has multiple responsibilities
- Ask: "What would cause this class to change?"—only one answer

**High Cohesion**
- Keep classes small
- Tightly couple instance variables to methods executing logic on them
- If methods don't use most instance variables, split the class

**Small Classes**
- Aim for 100-150 lines per class (strict guideline)
- If nearing 200 lines, look for extraction opportunities
- Small classes are easier to test, understand, maintain

**The Boy Scout Rule**
- Always leave code cleaner than you found it
- Whenever touching a file, refactor at least one small item before finalizing:
  - Rename a vague variable
  - Break up a long statement
  - Remove duplicated code
  - Extract a complex condition into a named method

---

## Application Across All Phases

### During Architecture Design (/grill-me)

**Apply Clean Code Principles to Design Decisions**
- Ensure classes have single responsibility
- Design function contracts with few arguments
- Plan for testability—avoid complex dependencies
- Use intention-revealing names for layers and components

### During Planning (/to-prd)

**Embed Clean Code into Architecture Documentation**
- Name design patterns explicitly
- Document the responsibility of each component
- Plan for testability at the design stage
- Define clear interfaces (high abstraction, low implementation detail)

### During Implementation

**Enforce Clean Code in Code Generation**
- Every function does one thing
- Names reveal intention
- Arguments minimized
- Tests written first (TDD)
- No null returns or flag arguments
- Comments explain "why," not "what"

### During Code Review (/code-review)

**Checklist Against These Principles**
- Are names intention-revealing?
- Is the function doing one thing?
- Are arguments minimized?
- Is error handling isolated?
- Are tests F.I.R.S.T. compliant?
- Does the code follow the Boy Scout Rule?

---

## Clean Code Checklist for Every Commit

- [ ] **Names**: All variables, methods, classes have intention-revealing names
- [ ] **Functions**: Each function does one thing; arguments minimized (0-1 preferred)
- [ ] **Abstraction**: No mixing of high-level logic with low-level details
- [ ] **Comments**: Only "why" comments; no commented-out code
- [ ] **Null Handling**: No null returns; null only at API boundaries
- [ ] **Error Handling**: Exceptions thrown; error logic isolated
- [ ] **Tests**: F.I.R.S.T. compliant; follow Triple-A pattern; one concept per test
- [ ] **Classes**: Single responsibility; high cohesion; <200 lines
- [ ] **Demeter**: No train wrecks; methods access only immediate members
- [ ] **Boy Scout Rule**: File left cleaner than when opened

---

## When Clean Code Conflicts with Pragmatism

Clean Code is not dogma—context matters:
- **Legacy systems**: Incrementally apply principles using the Boy Scout Rule
- **Third-party APIs**: Adapt Demeter and null-handling at boundaries
- **Performance-critical code**: Optimize after proving slowness via profiling; still apply clean principles first
- **Prototyping**: Speed matters; refactor to clean code before production

The goal is always **maximum readability and maintainability** within project constraints.
