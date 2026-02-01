# How to Refactor Tests to Remove Mocks

This guide shows you how to systematically refactor tests that use mocks to use dependency injection instead.

## Step 1: Identify the Mock

Run mockbuster to find mocks in your tests:

```bash
mockbuster tests/test_service.py
```

Example output:

```
tests/test_service.py
  Line 3: Mock import detected: unittest.mock - Use dependency injection instead
```

## Step 2: Understand What's Being Mocked

Look at your test to see what's being mocked:

```python
from unittest.mock import Mock
from myapp.service import UserService

def test_get_user():
    mock_db = Mock()
    mock_db.get_user.return_value = {"name": "Alice"}

    service = UserService(mock_db)
    result = service.get_user_name(1)

    assert result == "Alice"
```

Here, we're mocking a database dependency.

## Step 3: Define an Interface

Create a protocol that defines the interface:

```python
from typing import Protocol

class Database(Protocol):
    """Interface for database operations."""
    def get_user(self, user_id: int) -> dict[str, str]:
        ...
```

## Step 4: Update the Production Code

Make sure your production code accepts the protocol:

```python
class UserService:
    def __init__(self, db: Database):
        self.db = db

    def get_user_name(self, user_id: int) -> str:
        user = self.db.get_user(user_id)
        return user.get("name", "Unknown")
```

## Step 5: Create a Test Double

Create a simple fake implementation:

```python
class FakeDatabase:
    """Test implementation of Database."""
    def __init__(self):
        self.users = {
            1: {"name": "Alice"},
            2: {"name": "Bob"},
        }

    def get_user(self, user_id: int) -> dict[str, str]:
        return self.users.get(user_id, {})
```

## Step 6: Refactor the Test

Replace the mock with your fake:

```python
from myapp.service import UserService

def test_get_user():
    # No mocks!
    fake_db = FakeDatabase()
    service = UserService(fake_db)

    result = service.get_user_name(1)
    assert result == "Alice"
```

## Step 7: Verify

Run mockbuster again:

```bash
mockbuster tests/test_service.py
```

Output:

```
No violations found.
```

## Real-World Example: HTTP Client

### Before (with mocks)

```python
from unittest.mock import Mock, patch
import requests

def test_fetch_weather():
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = {
            "temp": 72,
            "condition": "sunny"
        }

        result = fetch_weather("London")
        assert result["temp"] == 72
```

### After (with dependency injection)

```python
from typing import Protocol

class HTTPClient(Protocol):
    def get(self, url: str) -> dict:
        ...

class FakeHTTPClient:
    def __init__(self):
        self.responses = {
            "http://api.weather.com/London": {
                "temp": 72,
                "condition": "sunny"
            }
        }

    def get(self, url: str) -> dict:
        return self.responses.get(url, {})

def fetch_weather(city: str, client: HTTPClient) -> dict:
    url = f"http://api.weather.com/{city}"
    return client.get(url)

def test_fetch_weather():
    fake_client = FakeHTTPClient()
    result = fetch_weather("London", fake_client)

    assert result["temp"] == 72
    assert result["condition"] == "sunny"
```

## Complex Example: Multiple Dependencies

### Before (with mocks)

```python
from unittest.mock import Mock

def test_process_order():
    mock_db = Mock()
    mock_payment = Mock()
    mock_email = Mock()

    mock_db.get_order.return_value = {"id": 1, "total": 100}
    mock_payment.charge.return_value = True
    mock_email.send.return_value = True

    result = process_order(1, mock_db, mock_payment, mock_email)
    assert result is True
```

### After (with dependency injection)

```python
from typing import Protocol

class Database(Protocol):
    def get_order(self, order_id: int) -> dict:
        ...

class PaymentGateway(Protocol):
    def charge(self, amount: int) -> bool:
        ...

class EmailService(Protocol):
    def send(self, to: str, subject: str, body: str) -> bool:
        ...

class FakeDatabase:
    def __init__(self):
        self.orders = {1: {"id": 1, "total": 100, "email": "test@example.com"}}

    def get_order(self, order_id: int) -> dict:
        return self.orders.get(order_id, {})

class FakePaymentGateway:
    def __init__(self):
        self.charges = []

    def charge(self, amount: int) -> bool:
        self.charges.append(amount)
        return True

class FakeEmailService:
    def __init__(self):
        self.sent_emails = []

    def send(self, to: str, subject: str, body: str) -> bool:
        self.sent_emails.append((to, subject, body))
        return True

def process_order(
    order_id: int,
    db: Database,
    payment: PaymentGateway,
    email: EmailService
) -> bool:
    order = db.get_order(order_id)
    if not order:
        return False

    if not payment.charge(order["total"]):
        return False

    email.send(
        order["email"],
        "Order Confirmation",
        f"Your order #{order_id} has been processed"
    )
    return True

def test_process_order():
    fake_db = FakeDatabase()
    fake_payment = FakePaymentGateway()
    fake_email = FakeEmailService()

    result = process_order(1, fake_db, fake_payment, fake_email)

    assert result is True
    assert len(fake_payment.charges) == 1
    assert fake_payment.charges[0] == 100
    assert len(fake_email.sent_emails) == 1
    assert fake_email.sent_emails[0][0] == "test@example.com"
```

## Tips

- **Start small** - Refactor one test at a time
- **Keep fakes simple** - Just enough to make tests pass
- **Reuse fakes** - Create a `test_doubles.py` module for common fakes
- **Test behavior, not implementation** - Focus on what the code does, not how
- **Make it fail first** - Ensure your test can actually fail before considering it done

## Next Steps

- Read [Dependency Injection](dependency-injection.md) for more patterns
- See [Third-Party APIs](third-party-apis.md) for external dependencies
- Understand [Why avoid mocks?](../explanation/why-no-mocks.md)
