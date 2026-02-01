# Why Avoid Mocks?

Understanding the problems with mocking and why we should avoid it.

## The Problems with Mocking

### 1. Mocks Couple Tests to Implementation

Mocks force you to specify exactly how your code should work internally:

```python
from unittest.mock import Mock

def test_user_service():
    mock_db = Mock()
    mock_db.get_user.return_value = {"name": "Alice"}

    service = UserService(mock_db)
    result = service.get_user_name(1)

    # Test is coupled to implementation details
    mock_db.get_user.assert_called_once_with(1)
    assert result == "Alice"
```

**Problem:** If you refactor `UserService` to cache the user or batch requests, your tests break even though the behavior is correct.

### 2. Mocks Make Refactoring Difficult

When you change implementation details, all your mocks need updating:

```python
# Before: Single call
def get_user_name(self, user_id: int) -> str:
    user = self.db.get_user(user_id)
    return user["name"]

# After: With caching
def get_user_name(self, user_id: int) -> str:
    if user_id not in self.cache:
        self.cache[user_id] = self.db.get_user(user_id)
    return self.cache[user_id]["name"]
```

**Result:** All tests with `assert_called_once_with` break, even though the external behavior is identical.

### 3. Mocks Don't Test Real Behavior

Mocks can return anything - even impossible values:

```python
mock_db = Mock()
mock_db.get_user.return_value = "not a dict"  # Would never happen!

service = UserService(mock_db)
# Tests pass but code would fail in production
```

**Problem:** Tests pass but don't reflect real-world behavior.

### 4. Mocks Are Complex and Verbose

Setting up mocks is tedious:

```python
from unittest.mock import Mock, patch

@patch('module.api_client')
@patch('module.database')
@patch('module.email_service')
def test_process_order(mock_email, mock_db, mock_api):
    # Configure mock_db
    mock_db.get_order.return_value = {"id": 1, "amount": 100}
    mock_db.update_order.return_value = True

    # Configure mock_api
    mock_api.charge.return_value = {"success": True}

    # Configure mock_email
    mock_email.send.return_value = True

    # 15 lines just to set up mocks!
    # Actual test logic...
```

Compare with dependency injection:

```python
def test_process_order():
    fake_db = FakeDatabase()
    fake_api = FakePaymentAPI()
    fake_email = FakeEmailService()

    # Test logic...
    # Fakes are reusable and simpler
```

### 5. Mocks Hide Design Problems

If your code is hard to test without mocks, it's a sign of poor design:

```python
class OrderProcessor:
    def __init__(self):
        self.db = Database()  # Hard dependency
        self.api = PaymentAPI()  # Hard dependency
        self.email = EmailService()  # Hard dependency

    def process(self, order_id: int):
        # Hard to test - dependencies are hidden
        pass
```

**Better design with dependency injection:**

```python
class OrderProcessor:
    def __init__(self, db: Database, api: PaymentAPI, email: EmailService):
        self.db = db
        self.api = api
        self.email = email

    def process(self, order_id: int):
        # Easy to test - dependencies are explicit
        pass
```

## The Alternative: Real Implementations

Instead of mocks, use simple real implementations (fakes):

```python
class FakeDatabase:
    """Test implementation of Database."""
    def __init__(self):
        self.users = {
            1: {"name": "Alice"},
            2: {"name": "Bob"},
        }

    def get_user(self, user_id: int) -> dict:
        return self.users.get(user_id, {})

def test_user_service():
    # No mocks - real implementation
    fake_db = FakeDatabase()
    service = UserService(fake_db)

    result = service.get_user_name(1)
    assert result == "Alice"
```

### Benefits of Fakes

1. **Test real behavior** - Fakes implement the actual interface
2. **Easy to refactor** - Tests only break if behavior changes
3. **Reusable** - One fake can be used across many tests
4. **Clear** - Simple code that's easy to understand
5. **Catch bugs** - Type checking works with real implementations

## Common Objections

### "But I need to test error handling!"

You can still test errors with fakes:

```python
class FakeDatabase:
    def __init__(self, should_fail: bool = False):
        self.should_fail = should_fail

    def get_user(self, user_id: int) -> dict:
        if self.should_fail:
            raise DatabaseError("Connection failed")
        return {"name": "Alice"}

def test_error_handling():
    fake_db = FakeDatabase(should_fail=True)
    service = UserService(fake_db)

    with pytest.raises(DatabaseError):
        service.get_user_name(1)
```

### "But setting up real implementations is slow!"

Not if you design them well:

- In-memory databases instead of real databases
- Fake HTTP clients instead of real network calls
- Simple data structures instead of complex external services

```python
class FakeHTTPClient:
    """Instant responses - no network calls."""
    def __init__(self):
        self.responses = {}

    def get(self, url: str) -> dict:
        return self.responses.get(url, {})
```

### "But I need to verify calls were made!"

You can track calls in your fakes:

```python
class FakeEmailService:
    def __init__(self):
        self.sent_emails = []

    def send(self, to: str, subject: str, body: str) -> None:
        self.sent_emails.append((to, subject, body))

def test_email_sent():
    fake_email = FakeEmailService()
    service = NotificationService(fake_email)

    service.notify_user("test@example.com", "Hello")

    # Verify the call
    assert len(fake_email.sent_emails) == 1
    assert fake_email.sent_emails[0][0] == "test@example.com"
```

### "But mocks are easier for simple cases!"

Only initially. The maintenance cost is high:

**With mocks:**

- Quick to write
- Breaks when refactoring
- Tied to implementation
- Can't be reused
- Complex for multiple tests

**With fakes:**

- Slightly more upfront work
- Survives refactoring
- Tests behavior, not implementation
- Reusable across tests
- Simple once created

## When Are Mocks Acceptable?

Very rarely. Consider mocks only when:

1. **Legacy integration** - You're working with legacy code that can't be changed yet
2. **Temporary solution** - While refactoring to dependency injection
3. **Framework limitations** - The framework forces you (rare)

Even then, aim to remove mocks as soon as possible.

## The Goal

Write tests that:

- Test behavior, not implementation
- Use real implementations (even if simple)
- Survive refactoring
- Are clear and maintainable
- Catch real bugs

This is easier with dependency injection and fakes than with mocks.

## Further Reading

- [Dependency Injection Explained](dependency-injection.md) - How to implement it
- [Philosophy](philosophy.md) - The bigger picture
- [How to Refactor Tests](../howto/refactor-tests.md) - Practical guide
