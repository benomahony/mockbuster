# Philosophy: Real Implementations vs Mocks

The testing philosophy behind mockbuster and why we favor real implementations over mocks.

## Core Philosophy

**Write tests that verify behavior, not implementation.**

This means:

- Tests should care about *what* the code does, not *how* it does it
- Implementation details should be free to change without breaking tests
- Tests should use real implementations, even if they're simplified

## The Testing Pyramid

Traditional testing wisdom says:

```
     /\
    /  \      Integration Tests (few)
   /----\
  /      \    Unit Tests (more)
 /--------\
/          \  End-to-End Tests (very few)
```

We say: **Focus on integration tests with real implementations.**

```
     /\
    /  \      E2E Tests (few)
   /----\
  /      \    Integration Tests (most)
 /--------\
/          \  Unit Tests (only for complex logic)
```

## Real Implementations

### What Are Real Implementations?

Real implementations are actual working code that implements an interface:

```python
class Database(Protocol):
    def save(self, data: dict) -> int:
        ...

# Real implementation (production)
class PostgresDatabase:
    def save(self, data: dict) -> int:
        # Actually saves to PostgreSQL
        pass

# Real implementation (test)
class FakeDatabase:
    def __init__(self):
        self.data = {}

    def save(self, data: dict) -> int:
        new_id = len(self.data) + 1
        self.data[new_id] = data
        return new_id
```

Both are *real implementations* - they actually implement the interface and have real behavior.

### Why Real Implementations?

1. **They test actual behavior**

```python
# With mock - tests implementation
mock_db.save.assert_called_once_with(data)  # Who cares HOW it's called?

# With fake - tests behavior
result = fake_db.save(data)
assert result > 0  # Tests WHAT happens
```

1. **They survive refactoring**

```python
# Original implementation
def save_user(user: dict) -> int:
    return self.db.save(user)

# Refactored with validation
def save_user(user: dict) -> int:
    if not user.get("email"):
        raise ValueError("Email required")
    return self.db.save(user)

# With mocks: Tests break (assert_called_once changes)
# With fakes: Tests still pass (behavior unchanged)
```

1. **They catch real bugs**

```python
# Mock can return anything
mock_db.get_user.return_value = "not a dict"  # Impossible in reality

# Fake enforces types
fake_db.get_user(1)  # Returns dict[str, str] - type checked!
```

1. **They're reusable**

```python
# Create once
class FakeDatabase:
    def __init__(self):
        self.users = {}

    def save_user(self, user: dict) -> int:
        new_id = len(self.users) + 1
        self.users[new_id] = user
        return new_id

    def get_user(self, user_id: int) -> dict:
        return self.users.get(user_id, {})

# Use in many tests
def test_save():
    fake_db = FakeDatabase()
    # ...

def test_get():
    fake_db = FakeDatabase()
    # ...

def test_update():
    fake_db = FakeDatabase()
    # ...
```

## Testing Strategies

### Integration Tests

Test multiple components together with real implementations:

```python
def test_user_registration():
    # Real implementations (all fakes)
    fake_db = FakeDatabase()
    fake_email = FakeEmailService()
    fake_hasher = FakePasswordHasher()

    # Real service using real dependencies
    service = UserService(fake_db, fake_email, fake_hasher)

    # Test the integration
    user_id = service.register("alice@example.com", "password123")

    # Verify behavior across components
    assert user_id > 0
    assert len(fake_db.users) == 1
    assert len(fake_email.sent) == 1
    assert fake_email.sent[0][0] == "alice@example.com"
```

**Benefits:**

- Tests real interactions between components
- Catches integration bugs
- More confidence than isolated unit tests

### Unit Tests (When Needed)

For complex logic, test in isolation:

```python
def calculate_discount(price: int, user_level: str) -> int:
    """Complex discount logic."""
    if user_level == "gold":
        return price * 0.8
    elif user_level == "silver":
        return price * 0.9
    else:
        return price

def test_discount_calculation():
    # No dependencies needed - just test the logic
    assert calculate_discount(100, "gold") == 80
    assert calculate_discount(100, "silver") == 90
    assert calculate_discount(100, "bronze") == 100
```

**When to use:**

- Pure functions with complex logic
- Algorithms that need detailed testing
- Edge cases in calculations

### End-to-End Tests (Sparingly)

Test the full system with real infrastructure:

```python
def test_full_user_journey():
    # Real PostgreSQL database (in Docker)
    # Real Redis cache
    # Real HTTP server

    # Test the full system
    response = requests.post("http://localhost:8000/register", json={
        "email": "alice@example.com",
        "password": "password123"
    })

    assert response.status_code == 201
```

**When to use:**

- Critical user flows
- Deployment verification
- Acceptance criteria

## Design Principles

### 1. Dependency Inversion

Depend on abstractions, not concretions:

```python
# Bad - depends on concrete PostgresDB
class UserService:
    def __init__(self):
        self.db = PostgresDB()

# Good - depends on abstract Database
class UserService:
    def __init__(self, db: Database):
        self.db = db
```

### 2. Explicit Dependencies

Make all dependencies visible:

```python
# Bad - hidden dependency
class UserService:
    def send_email(self, user: dict):
        smtp = SMTP("smtp.gmail.com")  # Hidden!
        smtp.send(user["email"], "Welcome")

# Good - explicit dependency
class UserService:
    def __init__(self, email_service: EmailService):
        self.email_service = email_service

    def send_email(self, user: dict):
        self.email_service.send(user["email"], "Welcome")
```

### 3. Interface Segregation

Small, focused interfaces:

```python
# Bad - large interface
class Repository(Protocol):
    def get(self, id: int): ...
    def save(self, data: dict): ...
    def delete(self, id: int): ...
    def query(self, sql: str): ...
    def bulk_insert(self, data: list): ...
    # 15 more methods...

# Good - focused interfaces
class UserReader(Protocol):
    def get_user(self, user_id: int): ...

class UserWriter(Protocol):
    def save_user(self, user: dict): ...
```

### 4. Composition Over Inheritance

Compose behavior from simple parts:

```python
# Bad - inheritance hierarchy
class BaseRepository:
    pass

class CachedRepository(BaseRepository):
    pass

class LoggedCachedRepository(CachedRepository):
    pass

# Good - composition
class UserRepository:
    def __init__(self, db: Database, cache: Cache, logger: Logger):
        self.db = db
        self.cache = cache
        self.logger = logger
```

## The mockbuster Way

1. **Design for testability** - Use dependency injection
2. **Write integration tests** - Test components together
3. **Use real implementations** - Create simple fakes
4. **Test behavior** - Not implementation details
5. **Keep fakes simple** - Just enough to make tests work
6. **Avoid mocks** - They couple tests to implementation

## Example: The Full Picture

### Bad (With Mocks)

```python
from unittest.mock import Mock, patch

@patch('stripe.Charge.create')
@patch('database.query')
@patch('email.send')
def test_process_payment(mock_email, mock_db, mock_stripe):
    # Setup mocks
    mock_db.return_value = {"id": 1, "amount": 100}
    mock_stripe.return_value = {"id": "ch_123", "status": "succeeded"}
    mock_email.return_value = True

    # Test
    result = process_payment(1)

    # Assert implementation details
    mock_db.assert_called_once_with("SELECT * FROM orders WHERE id = 1")
    mock_stripe.assert_called_once_with(amount=100, currency="usd")
    mock_email.assert_called_once()

    assert result is True
```

**Problems:**

- Tests HOW things are called
- Breaks if implementation changes
- Can't reuse setup
- Mocks can return impossible values

### Good (With Fakes)

```python
class FakeDatabase:
    def __init__(self):
        self.orders = {1: {"id": 1, "amount": 100, "email": "test@example.com"}}

    def get_order(self, order_id: int) -> dict:
        return self.orders.get(order_id, {})

class FakePaymentGateway:
    def __init__(self):
        self.charges = []

    def charge(self, amount: int) -> dict:
        charge_id = f"ch_{len(self.charges)}"
        self.charges.append({"id": charge_id, "amount": amount})
        return {"id": charge_id, "status": "succeeded"}

class FakeEmailService:
    def __init__(self):
        self.sent = []

    def send(self, to: str, subject: str) -> None:
        self.sent.append((to, subject))

def test_process_payment():
    # Setup with real implementations
    fake_db = FakeDatabase()
    fake_payment = FakePaymentGateway()
    fake_email = FakeEmailService()

    service = PaymentService(fake_db, fake_payment, fake_email)

    # Test behavior
    result = service.process_payment(1)

    # Assert behavior, not implementation
    assert result is True
    assert len(fake_payment.charges) == 1
    assert fake_payment.charges[0]["amount"] == 100
    assert len(fake_email.sent) == 1
    assert fake_email.sent[0][0] == "test@example.com"
```

**Benefits:**

- Tests WHAT happens
- Survives refactoring
- Reusable fakes
- Type-checked

## Summary

**Mockbuster enforces a testing philosophy based on:**

1. Real implementations over mocks
2. Integration tests over unit tests
3. Behavior verification over implementation verification
4. Dependency injection for testability
5. Simple fakes over complex mock setups

**The result:**

- Tests that survive refactoring
- Clearer, more maintainable test code
- Better designed production code
- More confidence in your test suite

## Further Reading

- [Why Avoid Mocks?](why-no-mocks.md) - Detailed problems with mocks
- [Dependency Injection](dependency-injection.md) - How it works
- [How-to Guides](../howto/index.md) - Practical examples
