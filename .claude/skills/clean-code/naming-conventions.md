# Clean Code Naming Conventions Guide

Reference for intention-revealing, searchable names across all scopes.

## Variables

### Scope-Based Length

**Wide Scope → Longer Names**
```python
# ✓ Module-level configuration: long, explicit
MAX_RETRY_ATTEMPTS = 3
DEFAULT_TIMEOUT_SECONDS = 30
CACHE_EXPIRATION_HOURS = 24

class UserService:
    def __init__(self):
        # ✓ Instance variables: descriptive
        self.active_session_count = 0
        self.user_cache = {}
```

**Narrow Scope → May Be Shorter**
```python
# ✓ Loop variable: acceptable in tight context
for user in users:
    user.activate()

# ✓ Simple iterator: i acceptable only in tight loops
for i in range(10):
    print(array[i])

# ✗ Single-letter at module scope: unacceptable
x = calculate_total()  # What is x?
```

### Avoid Vague Names

**❌ Never:**
- `data` — Data about what?
- `info` — Information about what?
- `temp` — Temporary holder of what?
- `obj` — Object of what type?
- `var` — Variable holding what?
- `result` — Result of what operation?

**✓ Instead:**
```python
# ❌ Bad
data = fetch_from_api()
temp = data.split(',')
info = process(temp)

# ✓ Good
user_records = fetch_users_from_api()
user_ids = [record.id for record in user_records]
active_users = filter_active_users(user_ids)
```

### Boolean Variables & Methods

**Prefix with: `is`, `has`, `can`, `should`, `will`**

```python
# ✓ Clear boolean names
is_active = True
has_permission = user.has_admin_role()
can_delete = user.can_delete_post(post_id)
should_retry = attempt_count < max_retries
will_expire_soon = days_until_expiration < 7

# ❌ Vague
active = True  # Active what?
admin = False  # Is admin? Admin what?
delete = user.delete_check(post)  # What does this return?
```

### Constants

**UPPER_CASE with underscores for clarity**

```python
# ✓ Clear constants
MAX_PASSWORD_LENGTH = 128
MIN_PASSWORD_LENGTH = 8
DEFAULT_RETRY_COUNT = 3
CACHE_EXPIRATION_HOURS = 24
API_TIMEOUT_SECONDS = 30

# ❌ Vague
MAX_LENGTH = 128  # Max length of what?
DEFAULT_RETRY = 3  # Retry what? For how long?
TIMEOUT = 30  # Timeout in what unit?
```

---

## Functions & Methods

### Naming Pattern

**Verb + Object + Modifier**

```python
# Format: verb_noun or verb_noun_when_condition

# ✓ Clear function names
def calculate_total_price(items):
    """Calculate price including tax and shipping."""

def validate_email_format(email):
    """Validate email format per RFC 5322."""

def find_active_users_by_department(department_id):
    """Find all active users in a department."""

def update_user_profile(user_id, profile_data):
    """Update user profile information."""

def delete_inactive_sessions():
    """Delete sessions expired >30 days ago."""
```

### Action Verbs

**Common meaningful verbs:**
- `get` / `fetch` — Retrieve data
- `set` / `update` — Modify data
- `create` / `make` — Create new entity
- `delete` / `remove` — Remove entity
- `is` / `has` / `can` — Boolean check
- `calculate` / `compute` — Perform calculation
- `validate` / `verify` — Check validity
- `transform` / `convert` — Change form
- `filter` / `search` — Select subset
- `build` / `construct` — Build object
- `parse` / `extract` — Extract from structure

### Avoid Vague Verbs

**❌ Avoid:**
- `handle()` — Handle what? How?
- `process()` — Process what? How?
- `do()` — Do what?
- `make()` — Make what?
- `check()` — Check what?

**✓ Instead:**
```python
# ❌ Vague
def handle(data):
    pass

def process(items):
    pass

# ✓ Specific
def validate_user_input(data):
    pass

def transform_items_to_dto(items):
    pass
```

### Boolean Methods

**Prefix with query verbs:**

```python
# ✓ Clear boolean methods
def is_valid_email(email):
    return '@' in email and '.' in email.split('@')[1]

def has_permission(user, action):
    return action in user.permissions

def can_delete_post(user, post_id):
    post = get_post(post_id)
    return post.owner_id == user.id or user.is_admin()

def should_retry(attempt_count, max_attempts):
    return attempt_count < max_attempts

def is_expired(created_date):
    return (datetime.now() - created_date).days > 30
```

---

## Classes

### Naming Pattern

**Noun / Noun Phrase**

```python
# ✓ Clear class names
class UserAccount:
    """Represents a user's account."""

class PaymentProcessor:
    """Processes payments for orders."""

class EmailValidator:
    """Validates email addresses."""

class InvoiceGenerator:
    """Generates invoices from orders."""

class DatabaseConnection:
    """Manages database connections."""

# ❌ Vague
class Handler:
    pass

class Process:
    pass

class Manager:
    pass  # Manage what?
```

### Repository / Data Access

```python
# ✓ Clear repository names
class UserRepository:
    def find_by_id(self, user_id):
        pass
    
    def find_active_users(self):
        pass
    
    def save(self, user):
        pass

class InvoiceRepository:
    def find_unpaid_invoices(self):
        pass
    
    def find_by_customer_id(self, customer_id):
        pass
```

### Service / Business Logic

```python
# ✓ Clear service names
class UserAuthenticationService:
    def authenticate(self, username, password):
        pass
    
    def generate_auth_token(self, user_id):
        pass

class PaymentProcessingService:
    def process_payment(self, order_id, payment_method):
        pass
    
    def validate_payment_method(self, payment_method):
        pass
```

### Exception Classes

```python
# ✓ Clear exception names (suffix with Exception)
class InvalidEmailException(Exception):
    pass

class PaymentFailedException(Exception):
    pass

class UserNotAuthenticatedException(Exception):
    pass

class InsufficientBalanceException(Exception):
    pass
```

---

## Modules & Packages

### Naming Pattern

**Lowercase with underscores (snake_case)**

```
project/
├── user_service/
│   ├── __init__.py
│   ├── models.py          # Data models
│   ├── repository.py      # Data access
│   ├── service.py         # Business logic
│   ├── validators.py      # Validation logic
│   └── exceptions.py      # Custom exceptions
├── payment_service/
├── email_service/
└── common/
    ├── utils.py           # Utility functions
    ├── constants.py       # Application constants
    └── decorators.py      # Reusable decorators
```

### Module Purpose in Filename

```python
# ✓ Clear module names (indicate purpose)
users/
  models.py           # User domain models
  repository.py       # Database access
  service.py          # Business logic
  validators.py       # Input validation
  exceptions.py       # Custom exceptions
  
payment/
  models.py           # Payment domain models
  processor.py        # Payment processing
  gateway.py          # Payment gateway integration
```

---

## Interfaces & Contracts

### Abstract Base Classes

```python
# ✓ Clear interface names
from abc import ABC, abstractmethod

class PaymentGateway(ABC):
    """Interface for payment gateway implementations."""
    
    @abstractmethod
    def process_payment(self, amount: float, currency: str) -> dict:
        pass
    
    @abstractmethod
    def refund_payment(self, transaction_id: str) -> dict:
        pass

class Validator(ABC):
    """Interface for validation implementations."""
    
    @abstractmethod
    def validate(self, data):
        pass
```

---

## Anti-Patterns: Names to Avoid

### Vague Suffixes
```python
# ❌ Avoid these suffixes (too vague)
class UserHandler:      # Handle what?
    pass

class DataProcessor:    # Process what?
    pass

class InputManager:     # Manage what?
    pass

class ConfigUtil:       # Too generic
    pass
```

### Misleading Names
```python
# ❌ Names that mislead about behavior
def get_user(user_id):  # ✗ "get" implies local cache, but queries DB
    return database.query_user(user_id)

def is_valid(email):    # ✗ Name doesn't indicate what's being validated
    return len(email) > 0

def process(items):     # ✗ What processing happens?
    return [item * 2 for item in items]
```

### Redundant Names
```python
# ❌ Redundant naming
class UserService:
    def getUserService():  # "Service" redundant
        pass
    
    def getUser(self):  # "get" implied by method
        pass

# ✓ Better
class UserService:
    def instance():
        pass
    
    def get(self, user_id):
        pass
```

---

## Naming Checklist

Before finalizing a name, verify:

- [ ] **Intention-revealing**: Name clearly states purpose
- [ ] **Searchable**: Can be easily found in IDE search
- [ ] **No Hungarian notation**: No type prefixes (`str_`, `num_`)
- [ ] **No member prefixes**: No `m_`, `s_` prefixes
- [ ] **Consistent**: Follows project conventions
- [ ] **Pronounceable**: Can be spoken aloud
- [ ] **Single purpose**: Doesn't describe multiple things
- [ ] **No abbreviations**: Full words except common `id`, `dto`
- [ ] **Matches scope**: Width of name matches scope width
- [ ] **No noise words**: No `data`, `info`, `temp` unless essential

---

## Examples: Before & After

### Variable Renaming

```python
# ❌ Bad
def process_transaction(txn):
    amt = txn.amount
    t = datetime.now()
    d = calculate_discount(amt)
    r = amt - d
    return r

# ✓ Good
def process_transaction(transaction):
    transaction_amount = transaction.amount
    current_timestamp = datetime.now()
    discount_amount = calculate_discount(transaction_amount)
    final_amount = transaction_amount - discount_amount
    return final_amount
```

### Function Renaming

```python
# ❌ Bad
def handle_user(u):
    if u.is_active():
        process(u)
    else:
        do_something_else(u)

# ✓ Good
def activate_user_workflow(user):
    if user.is_active():
        send_welcome_email(user)
    else:
        send_reactivation_request(user)
```

### Class Renaming

```python
# ❌ Bad
class Handler:
    def handle(self, data):
        pass

# ✓ Good
class EmailNotificationService:
    def send_notification(self, user_id, message):
        pass
```

---

## Summary

**Great names:**
- Reveal intention
- Avoid disinformation
- Make code self-documenting
- Reduce need for comments
- Enable future developers to understand quickly

**Invest in naming.** Renaming is cheap during refactoring; confusion is expensive during maintenance.
