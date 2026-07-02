# Test-Driven Development Workflow

Strict adherence to the Three Laws of TDD ensures clean, well-tested code from the start.

## The Three Laws of TDD (Absolute Rules)

### Law 1: No Production Code Without Failing Test
**Rule:** You are NOT allowed to write any production code unless it is to make a failing unit test pass.

- Write the test first
- Watch it fail (red)
- Write only the minimum code to make it pass (green)
- Refactor (blue)

### Law 2: Write Minimal Failing Test
**Rule:** You are NOT allowed to write more of a unit test than is sufficient to fail.

- One assertion (or closely related assertions)
- Just enough code to define the behavior
- Not compiling counts as failing

### Law 3: Write Minimal Production Code
**Rule:** You are NOT allowed to write more production code than is sufficient to pass the one failing test.

- Write the absolute minimum
- Even if it feels like cheating (e.g., `return true` for a boolean test)
- Refactor only after the test passes

---

## The TDD Cycle: Red-Green-Refactor

### 1. RED: Write Failing Test

Start with a test for behavior that doesn't exist yet.

```python
def test_should_add_two_positive_numbers():
    calculator = Calculator()
    result = calculator.add(2, 3)
    assert result == 5
```

The test fails because `Calculator` class doesn't exist yet. **This is expected.**

### 2. GREEN: Write Minimum Code to Pass

Write the absolute minimum code to make the test pass.

```python
class Calculator:
    def add(self, a, b):
        return a + b
```

The test passes. **Do not over-engineer.** Even if the implementation seems too simple, trust the process.

### 3. BLUE: Refactor Without Changing Behavior

Now improve the code while keeping tests passing.

```python
class Calculator:
    def add(self, a: int, b: int) -> int:
        """Add two numbers and return the result."""
        return a + b
```

- Add type hints
- Improve naming
- Extract duplication
- Ensure all tests still pass

---

## Test Structure: Build-Operate-Check (Triple-A)

Every test follows this explicit structure:

### Arrange (Build)
Set up all preconditions and test data.

```python
def test_should_deduct_transaction_fee():
    # Arrange
    account = BankAccount(initial_balance=100)
    transaction_fee = 5
```

### Act (Operate)
Execute the single behavior under test.

```python
    # Act
    account.withdraw(50, fee=transaction_fee)
```

### Assert (Check)
Verify the outcome matches expectations.

```python
    # Assert
    assert account.balance == 45  # 100 - 50 - 5
```

**Full Example:**
```python
def test_should_reject_negative_withdrawal_amount():
    # Arrange
    account = BankAccount(initial_balance=100)
    
    # Act & Assert
    with pytest.raises(ValueError):
        account.withdraw(-50)
```

---

## F.I.R.S.T. Principles

### Fast
Tests run instantly without I/O, database access, or network calls.

**Bad (slow):**
```python
def test_user_creation():
    user = create_user_in_database("john@example.com")  # Database call!
```

**Good (fast):**
```python
def test_user_creation():
    # Arrange
    user_repo = FakeUserRepository()
    user_service = UserService(user_repo)
    
    # Act
    user = user_service.create_user("john@example.com")
    
    # Assert
    assert user.email == "john@example.com"
```

### Independent
No test depends on another test's state or output.

**Bad (dependent):**
```python
def test_create_user():
    user = create_user("alice@example.com")
    assert user is not None

def test_update_user():
    # ❌ Depends on test_create_user() running first
    user = get_user(user_id_from_previous_test)
    assert user.email == "alice@example.com"
```

**Good (independent):**
```python
def test_create_user():
    repository = InMemoryUserRepository()
    user_service = UserService(repository)
    user = user_service.create_user("alice@example.com")
    assert user is not None

def test_update_user():
    # ✓ Self-contained; no external dependencies
    repository = InMemoryUserRepository()
    user_service = UserService(repository)
    user = user_service.create_user("bob@example.com")
    user_service.update_email(user.id, "bob.new@example.com")
    updated_user = user_service.get_user(user.id)
    assert updated_user.email == "bob.new@example.com"
```

### Repeatable
Tests pass in any environment (local, CI, production staging).

**Bad (not repeatable):**
```python
def test_process_payment():
    # ❌ Calls real API
    response = payment_api.charge_card(card="4111-1111-1111-1111", amount=100)
    assert response.success is True
```

**Good (repeatable):**
```python
def test_process_payment():
    # Arrange
    fake_payment_api = FakePaymentAPI()
    payment_service = PaymentService(fake_payment_api)
    
    # Act
    result = payment_service.charge_customer(customer_id=123, amount=100)
    
    # Assert
    assert result.success is True
```

### Self-Validating
Tests have a clear pass/fail with no manual inspection required.

**Bad (not self-validating):**
```python
def test_calculate_tax():
    tax = calculate_tax(100, 0.08)
    print(tax)  # ❌ Human must inspect output
    # No assertion!
```

**Good (self-validating):**
```python
def test_calculate_tax():
    tax = calculate_tax(100, 0.08)
    assert tax == 8.0  # ✓ Clear pass/fail
```

### Timely
Tests written before production code (TDD discipline).

**Process:**
1. Write test (RED)
2. Write code to pass test (GREEN)
3. Refactor (BLUE)
4. Repeat

---

## Single Concept Per Test

Each test validates exactly one behavior.

**Bad (multiple concepts):**
```python
def test_user_validation():
    # ❌ Three concepts in one test
    user = create_user("john@example.com", "password123")
    assert user.email_is_valid()
    assert user.password_meets_requirements()
    assert user.is_active()
```

**Good (one concept per test):**
```python
def test_should_validate_valid_email():
    user = create_user("john@example.com")
    assert user.email_is_valid()

def test_should_reject_invalid_email():
    user = create_user("invalid-email")
    assert not user.email_is_valid()

def test_should_enforce_password_requirements():
    user = create_user("john@example.com", "password123")
    assert user.password_meets_requirements()

def test_should_require_strong_password():
    user = create_user("john@example.com", "123")
    assert not user.password_meets_requirements()
```

**Benefit:** Each test fails for one reason only. Easier to diagnose bugs.

---

## Naming Tests: Intention-Revealing

Test names should clearly describe what is being tested and the expected outcome.

**Format:** `test_should_<expected_behavior>_when_<condition>`

**Bad:**
```python
def test_user():
    pass

def test_validation():
    pass

def test_1():
    pass
```

**Good:**
```python
def test_should_create_user_with_valid_email():
    pass

def test_should_reject_user_with_invalid_email():
    pass

def test_should_throw_exception_when_password_too_short():
    pass

def test_should_deactivate_user_after_30_days_inactivity():
    pass
```

---

## Test Pyramid

Optimize test coverage by type:

```
         /\
        /  \     End-to-End Tests (Few)
       /    \    Integration tests,
      /______\   UI tests, slow

     /\      /\
    /  \    /  \  Integration Tests (Some)
   /    \  /    \ Test real deps,
  /______\/______\ database calls

 /\              /\
/  \            /  \  Unit Tests (Many)
    \          /     Fast, isolated,
 ____\________/____  mocked deps
```

**Guideline:**
- **Unit tests**: 70% (fast, isolated, mocked)
- **Integration tests**: 20% (real dependencies, slower)
- **End-to-end tests**: 10% (full system, slowest)

---

## Example: Full TDD Cycle

### Iteration 1: Basic Addition

**RED:** Write test
```python
def test_should_add_two_positive_numbers():
    calculator = Calculator()
    result = calculator.add(2, 3)
    assert result == 5
```

**GREEN:** Minimal code
```python
class Calculator:
    def add(self, a, b):
        return a + b
```

**BLUE:** Refactor
```python
class Calculator:
    def add(self, a: int, b: int) -> int:
        """Add two integers."""
        return a + b
```

### Iteration 2: Negative Numbers

**RED:** Write test
```python
def test_should_add_negative_number():
    calculator = Calculator()
    result = calculator.add(-5, 3)
    assert result == -2
```

**GREEN:** Code already works (no change needed!)

**BLUE:** No refactoring needed

### Iteration 3: Floating Point

**RED:** Write test
```python
def test_should_add_floating_point_numbers():
    calculator = Calculator()
    result = calculator.add(2.5, 3.7)
    assert abs(result - 6.2) < 0.0001  # Account for floating-point precision
```

**GREEN:** Code already works!

**BLUE:** Update type hints
```python
class Calculator:
    def add(self, a: float, b: float) -> float:
        """Add two numbers (integers or floats)."""
        return a + b
```

---

## Common TDD Pitfalls

### Pitfall 1: Testing Implementation, Not Behavior

**Bad (testing implementation):**
```python
def test_user_dict():
    user = User("john", "john@example.com")
    assert user.__dict__["name"] == "john"  # ❌ Tied to internal structure
```

**Good (testing behavior):**
```python
def test_should_create_user_with_name():
    user = User("john", "john@example.com")
    assert user.name == "john"  # ✓ Tests the public interface
```

### Pitfall 2: Over-Testing

**Bad (over-testing):**
```python
def test_getter():
    assert get_name("john") == "john"  # ❌ Trivial test

def test_setter():
    set_name("john")
    assert get_name() == "john"  # ❌ Tests only getters/setters
```

**Good (test behavior, not trivial accessors):**
```python
def test_should_validate_user_with_valid_name():
    user = User("john", "john@example.com")
    assert user.is_valid()
```

### Pitfall 3: Test Interdependence

**Bad:**
```python
def test_setup():
    global test_user
    test_user = create_user()  # ❌ Modifying global state

def test_update():
    test_user.update(...)  # ❌ Depends on test_setup
```

**Good:**
```python
def test_create_and_update_user():
    # Each test self-contained
    user = create_user()
    user.update(...)
    assert user.name == "updated"
```

---

## TDD Workflow Summary

```
1. Write failing test (RED)
   └─ Defines expected behavior
2. Write minimal code (GREEN)
   └─ Make the test pass
3. Refactor (BLUE)
   └─ Improve code quality
4. Repeat for next behavior
```

**Discipline:**
- Always start with a failing test
- Never write more code than the test requires
- Refactor only after tests pass
- One test drives one small feature
