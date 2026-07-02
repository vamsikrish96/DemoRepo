# Clean Code Review Checklist

Use this checklist when reviewing code or pull requests against Clean Code principles.

## Meaningful Names ✓

- [ ] Variable names clearly state their purpose (not `data`, `info`, `temp`)
- [ ] Class names are nouns/noun phrases (`UserAccount`, `PaymentProcessor`)
- [ ] Method names are verbs/verb phrases (`calculateTotal()`, `isValid()`)
- [ ] Boolean methods/variables prefixed with `is`, `has`, `can`, `should`
- [ ] Names are searchable (no single-letter variables except loop counters)
- [ ] No Hungarian notation or member prefixes (`m_`, `s_`)
- [ ] Constants in UPPER_CASE with underscores
- [ ] Names require no comments to understand intent

## Functions & Abstraction ✓

- [ ] Each function does ONE thing only
- [ ] Function length <20 lines (strict guideline)
- [ ] Argument count: 0-1 preferred, 2 acceptable, 3+ is a red flag
- [ ] No boolean flag arguments (split into two functions instead)
- [ ] Single level of abstraction (no mixing high-level with low-level)
- [ ] Command-Query Separation: functions either change state OR return info, not both
- [ ] Error handling extracted into separate functions
- [ ] No nested try-catch blocks deeper than one level

**Example Red Flags:**
```python
# ❌ Too many arguments
def process_user(user_id, active, admin, verified, email_confirmed):
    pass

# ✓ Encapsulate into object
def process_user(user_context):
    pass
```

## Comments & Documentation ✓

- [ ] No commented-out code anywhere
- [ ] Comments explain "why," not "what"
- [ ] No redundant comments that mirror code
- [ ] No TODO comments left in code
- [ ] Public APIs have clear docstrings
- [ ] Code is self-documenting (comments are minimal)

**Examples:**
```python
# ❌ Noise comment
x = x + 1  # increment x

# ✓ Clear code, no comment needed
count += 1

# ✓ Valid "why" comment
# We cache this result because it's called in hot loop
result = expensive_calculation()
```

## Objects & Data Structures ✓

- [ ] Classes hide internal data behind behavior (not getters/setters for everything)
- [ ] No "train wrecks": `obj.get().get().get()`
- [ ] Law of Demeter: methods access only immediate members
- [ ] No hybrid structures mixing data exposure with business logic
- [ ] Data Transfer Objects (DTOs) are pure data, no logic

## Defensive Design ✓

- [ ] No `null` returns (use Optional, empty collections, or exceptions)
- [ ] No `null` parameters passed (except at API boundaries)
- [ ] Special Case Pattern used for edge cases
- [ ] Error handling doesn't nest deeply
- [ ] Preconditions validated early (fail fast)

## Unit Testing (F.I.R.S.T.) ✓

- [ ] **Fast**: Tests run instantly (no I/O, DB, network)
- [ ] **Independent**: Tests don't depend on each other
- [ ] **Repeatable**: Tests pass in any environment
- [ ] **Self-Validating**: Clear pass/fail (no manual log inspection)
- [ ] **Timely**: Tests written before production code (TDD)

**Triple-A Pattern:**
```python
# ✓ Good test structure
def test_should_calculate_total_with_tax():
    # Arrange
    calculator = TaxCalculator()
    items = [Item(10), Item(20)]
    
    # Act
    total = calculator.calculate(items)
    
    # Assert
    assert total == 32.50  # 30 + 8.33% tax
```

- [ ] One assertion per test (or assertions testing same concept)
- [ ] Test names clearly describe what is being tested
- [ ] Test setup minimal and clear
- [ ] No magic numbers (use named constants)

## Class Design ✓

- [ ] Single Responsibility Principle: one reason to change
- [ ] High cohesion: methods use most instance variables
- [ ] Class length <200 lines (guideline)
- [ ] No "God classes" doing too much
- [ ] Related methods grouped together

## The Boy Scout Rule ✓

- [ ] File left cleaner than when opened
- [ ] At least one small refactoring done (rename, extract, remove duplication)
- [ ] No "temporary hacks" left behind

## Error Handling ✓

- [ ] Specific exception types (not generic `Exception`)
- [ ] Exception messages are clear and actionable
- [ ] Error handling code is separate from business logic
- [ ] No catching and ignoring exceptions
- [ ] Logging meaningful context with errors

## Anti-Patterns to Flag ❌

- ❌ Functions with 3+ arguments
- ❌ Boolean flag arguments
- ❌ Long parameter lists
- ❌ Nested conditionals >2 levels deep
- ❌ Classes >200 lines
- ❌ "God classes" with multiple responsibilities
- ❌ Train wreck method chains
- ❌ Null returns or null parameters
- ❌ Commented-out code
- ❌ Vague variable names
- ❌ Functions doing multiple things
- ❌ Comments explaining "what" instead of "why"
- ❌ Catching generic `Exception`
- ❌ Silent exception handlers
- ❌ Flag arguments instead of separate functions

## Rating Scale

**5/5 (Excellent):** All boxes checked, code exemplifies clean principles  
**4/5 (Good):** Minor issues, mostly clean  
**3/5 (Acceptable):** Several issues, needs refactoring  
**2/5 (Poor):** Many violations, request changes  
**1/5 (Unacceptable):** Pervasive violations, reject with guidance  

## Review Comment Template

```markdown
### Clean Code Issue: [Principle Name]

**What:** [Brief description of violation]

**Why:** [Explanation of why this matters]

**Suggestion:** [Concrete refactoring suggestion]

**Reference:** Section X.X of Clean Code principles
```

## Example: Refactoring Request

```markdown
### Clean Code Issue: Multiple Arguments

**What:** `validateUser(user_id, is_admin, check_email, verify_phone)` has 4 arguments

**Why:** Multiple arguments are harder to test and understand. This violates argument reduction.

**Suggestion:** Encapsulate into a context object:
```python
user_context = UserValidationContext(
    user_id=user_id,
    is_admin=is_admin,
    check_email=check_email,
    verify_phone=verify_phone
)
validate_user(user_context)
```

**Reference:** Section 2.5, Relentless Argument Reduction
```
