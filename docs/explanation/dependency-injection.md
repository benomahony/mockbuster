# Dependency Injection Explained

Understanding dependency injection and why it makes code more testable.

## What Is Dependency Injection?

**Dependency injection** means passing dependencies into a component rather than having the component create them itself.

### Without Dependency Injection

```python
class UserService:
    def __init__(self):
        self.db = PostgresDatabase()  # Hard dependency created internally
        self.cache = RedisCache()      # Hard dependency created internally

    def get_user(self, user_id: int) -> dict:
        cached = self.cache.get(f"user:{user_id}")
        if cached:
            return cached

        user = self.db.query(f"SELECT * FROM users WHERE id = {user_id}")
        self.cache.set(f"user:{user_id}", user)
        return user
```

**Problems:**

- Can't test without a real PostgreSQL database
- Can't test without a real Redis instance
- Dependencies are hidden (not visible in the constructor)
- Can't swap implementations easily

### With Dependency Injection

```python
from typing import Protocol

class Database(Protocol):
    def query(self, sql: str) -> dict:
        ...

class Cache(Protocol):
    def get(self, key: str) -> dict | None:
        ...

    def set(self, key: str, value: dict) -> None:
        ...

class UserService:
    def __init__(self, db: Database, cache: Cache):
        self.db = db      # Injected dependency
        self.cache = cache # Injected dependency

    def get_user(self, user_id: int) -> dict:
        cached = self.cache.get(f"user:{user_id}")
        if cached:
            return cached

        user = self.db.query(f"SELECT * FROM users WHERE id = {user_id}")
        self.cache.set(f"user:{user_id}", user)
        return user
```

**Benefits:**

- Easy to test with fake implementations
- Dependencies are explicit and visible
- Can swap implementations easily
- Follows the Dependency Inversion Principle

## Types of Dependency Injection

### 1. Constructor Injection

Pass dependencies through the constructor (most common):

```python
class OrderService:
    def __init__(self, db: Database, payment: PaymentGateway):
        self.db = db
        self.payment = payment

# Production
service = OrderService(PostgresDB(), StripeGateway())

# Testing
service = OrderService(FakeDB(), FakePayment())
```

**When to use:** For dependencies that are used throughout the class lifetime.

### 2. Function/Method Injection

Pass dependencies as function parameters:

```python
def process_payment(
    order_id: int,
    payment_gateway: PaymentGateway,
    notification: NotificationService
) -> bool:
    # Process payment using injected dependencies
    pass

# Production
process_payment(123, StripeGateway(), EmailService())

# Testing
process_payment(123, FakePayment(), FakeEmail())
```

**When to use:** For dependencies that are only needed in specific methods.

### 3. Property Injection

Set dependencies via properties (less common):

```python
class ReportGenerator:
    def __init__(self):
        self.db: Database | None = None

    def generate(self) -> str:
        assert self.db is not None
        data = self.db.query("SELECT * FROM reports")
        return format_report(data)

# Production
generator = ReportGenerator()
generator.db = PostgresDB()
generator.generate()

# Testing
generator = ReportGenerator()
generator.db = FakeDB()
generator.generate()
```

**When to use:** Rarely - prefer constructor injection.

## Defining Interfaces

### Using Protocols (Recommended)

Python 3.8+ supports structural subtyping with protocols:

```python
from typing import Protocol

class EmailService(Protocol):
    """Interface for sending emails."""
    def send(self, to: str, subject: str, body: str) -> bool:
        ...

class SMTPEmailService:
    """Production implementation using SMTP."""
    def send(self, to: str, subject: str, body: str) -> bool:
        # Real SMTP implementation
        return True

class FakeEmailService:
    """Test implementation storing emails in memory."""
    def __init__(self):
        self.sent = []

    def send(self, to: str, subject: str, body: str) -> bool:
        self.sent.append((to, subject, body))
        return True

# Both work - no explicit inheritance needed!
def notify(email_service: EmailService, recipient: str) -> None:
    email_service.send(recipient, "Notification", "Hello")
```

**Benefits:**

- No explicit inheritance required
- Duck typing with type checking
- Simple and Pythonic

### Using Abstract Base Classes

For more complex interfaces:

```python
from abc import ABC, abstractmethod

class PaymentGateway(ABC):
    """Abstract interface for payment operations."""

    @abstractmethod
    def charge(self, amount: int, token: str) -> dict:
        """Charge a payment method."""
        pass

    @abstractmethod
    def refund(self, transaction_id: str) -> dict:
        """Refund a transaction."""
        pass

class StripeGateway(PaymentGateway):
    """Production Stripe implementation."""
    def charge(self, amount: int, token: str) -> dict:
        # Real Stripe API call
        return {"id": "ch_123", "status": "succeeded"}

    def refund(self, transaction_id: str) -> dict:
        # Real Stripe refund
        return {"id": "re_123", "status": "succeeded"}

class FakePaymentGateway(PaymentGateway):
    """Test implementation."""
    def __init__(self):
        self.charges = []
        self.refunds = []

    def charge(self, amount: int, token: str) -> dict:
        charge_id = f"ch_{len(self.charges)}"
        self.charges.append({"id": charge_id, "amount": amount})
        return {"id": charge_id, "status": "succeeded"}

    def refund(self, transaction_id: str) -> dict:
        refund_id = f"re_{len(self.refunds)}"
        self.refunds.append({"id": refund_id, "transaction": transaction_id})
        return {"id": refund_id, "status": "succeeded"}
```

**Benefits:**

- Enforces interface implementation
- Explicit contracts
- Can't instantiate abstract class

## Creating Test Doubles

### Fake Objects

Fake objects have working implementations, but are simplified:

```python
class FakeDatabase:
    """In-memory database for testing."""
    def __init__(self):
        self.data: dict[int, dict] = {
            1: {"id": 1, "name": "Alice"},
            2: {"id": 2, "name": "Bob"},
        }

    def query(self, sql: str) -> list[dict]:
        # Simplified query logic
        if "SELECT * FROM users" in sql:
            return list(self.data.values())
        return []

    def insert(self, table: str, values: dict) -> int:
        new_id = max(self.data.keys()) + 1
        self.data[new_id] = values
        return new_id
```

**Characteristics:**

- Working implementation
- Simplified logic
- Fast (in-memory)
- Reusable across tests

### Stub Objects

Stubs provide canned responses:

```python
class StubWeatherAPI:
    """Always returns the same weather."""
    def get_forecast(self, city: str) -> dict:
        return {"temp": 72, "condition": "sunny"}
```

**Characteristics:**

- Fixed responses
- No logic
- Very simple

### Spy Objects

Spies record how they're used:

```python
class SpyEmailService:
    """Records all email sends."""
    def __init__(self):
        self.calls: list[tuple[str, str, str]] = []

    def send(self, to: str, subject: str, body: str) -> bool:
        self.calls.append((to, subject, body))
        return True
```

**Characteristics:**

- Records interactions
- Used for verification
- Simple tracking

## Real-World Example

### The Problem

Hard-coded dependencies:

```python
import requests
import psycopg2

class OrderProcessor:
    def __init__(self):
        self.db = psycopg2.connect("postgresql://localhost/mydb")
        self.http = requests.Session()

    def process_order(self, order_id: int) -> bool:
        # Can't test without real database and network!
        order = self.db.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
        response = self.http.post("https://api.payment.com/charge", json=order)
        return response.status_code == 200
```

### The Solution

Dependency injection with protocols:

```python
from typing import Protocol

class Database(Protocol):
    def execute(self, sql: str, params: tuple) -> dict:
        ...

class HTTPClient(Protocol):
    def post(self, url: str, json: dict) -> dict:
        ...

class OrderProcessor:
    def __init__(self, db: Database, http: HTTPClient):
        self.db = db
        self.http = http

    def process_order(self, order_id: int) -> bool:
        order = self.db.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
        response = self.http.post("https://api.payment.com/charge", json=order)
        return response.get("status") == 200

# Production implementation
class PostgresDB:
    def __init__(self, connection_string: str):
        import psycopg2
        self.conn = psycopg2.connect(connection_string)

    def execute(self, sql: str, params: tuple) -> dict:
        # Real database query
        pass

class RealHTTPClient:
    def __init__(self):
        import requests
        self.session = requests.Session()

    def post(self, url: str, json: dict) -> dict:
        response = self.session.post(url, json=json)
        return {"status": response.status_code}

# Test implementation
class FakeDB:
    def __init__(self):
        self.orders = {1: {"id": 1, "amount": 100}}

    def execute(self, sql: str, params: tuple) -> dict:
        order_id = params[0]
        return self.orders.get(order_id, {})

class FakeHTTPClient:
    def __init__(self, should_succeed: bool = True):
        self.should_succeed = should_succeed
        self.requests = []

    def post(self, url: str, json: dict) -> dict:
        self.requests.append((url, json))
        return {"status": 200 if self.should_succeed else 500}

# Testing
def test_process_order():
    fake_db = FakeDB()
    fake_http = FakeHTTPClient(should_succeed=True)
    processor = OrderProcessor(fake_db, fake_http)

    result = processor.process_order(1)

    assert result is True
    assert len(fake_http.requests) == 1
```

## Key Principles

### 1. Depend on Abstractions

```python
# Bad - depends on concrete class
class Service:
    def __init__(self, db: PostgresDatabase):
        self.db = db

# Good - depends on protocol
class Service:
    def __init__(self, db: Database):
        self.db = db
```

### 2. Inject All Dependencies

```python
# Bad - creates dependency internally
class Service:
    def __init__(self):
        self.logger = Logger()

# Good - injects dependency
class Service:
    def __init__(self, logger: Logger):
        self.logger = logger
```

### 3. Keep Interfaces Small

```python
# Bad - large interface
class Database(Protocol):
    def query(self, sql: str) -> list: ...
    def insert(self, table: str, data: dict) -> int: ...
    def update(self, table: str, data: dict) -> int: ...
    def delete(self, table: str, id: int) -> int: ...
    # 20 more methods...

# Good - focused interface
class UserRepository(Protocol):
    def get_user(self, user_id: int) -> dict: ...
    def save_user(self, user: dict) -> int: ...
```

### 4. Make Dependencies Explicit

```python
# Bad - hidden dependency
class Service:
    def process(self):
        config = load_config()  # Hidden!

# Good - explicit dependency
class Service:
    def __init__(self, config: Config):
        self.config = config

    def process(self):
        # Use self.config
```

## Benefits Summary

1. **Testability** - Easy to test with fakes
2. **Flexibility** - Easy to swap implementations
3. **Clarity** - Dependencies are explicit
4. **Maintainability** - Changes are localized
5. **Reusability** - Components are decoupled

## Further Reading

- [Why Avoid Mocks?](why-no-mocks.md) - The problems with mocking
- [Philosophy](philosophy.md) - The bigger picture
- [How to Use Dependency Injection](../howto/dependency-injection.md) - Practical guide
