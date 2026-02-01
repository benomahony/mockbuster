# How to Handle Third-Party APIs Without Mocks

This guide shows you how to test code that calls external services without using mocks.

## The Challenge

Testing code that calls external APIs is tricky because:

- API calls are slow
- APIs may have rate limits
- Tests should be reliable and repeatable
- External services might be unavailable during testing

But you don't need mocks! Use dependency injection instead.

## Pattern 1: HTTP Client Wrapper

### Define a Protocol

```python
from typing import Protocol

class HTTPClient(Protocol):
    """Interface for HTTP operations."""
    def get(self, url: str, headers: dict | None = None) -> dict:
        ...

    def post(self, url: str, data: dict, headers: dict | None = None) -> dict:
        ...
```

### Create Production Implementation

```python
import requests

class RealHTTPClient:
    """Production HTTP client using requests."""
    def __init__(self, timeout: int = 30):
        self.timeout = timeout

    def get(self, url: str, headers: dict | None = None) -> dict:
        response = requests.get(url, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def post(self, url: str, data: dict, headers: dict | None = None) -> dict:
        response = requests.post(url, json=data, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
```

### Create Test Implementation

```python
class FakeHTTPClient:
    """Test HTTP client with predefined responses."""
    def __init__(self):
        self.responses: dict[tuple[str, str], dict] = {}
        self.requests: list[tuple[str, str, dict | None]] = []

    def add_response(self, method: str, url: str, response: dict) -> None:
        self.responses[(method, url)] = response

    def get(self, url: str, headers: dict | None = None) -> dict:
        self.requests.append(("GET", url, headers))
        return self.responses.get(("GET", url), {})

    def post(self, url: str, data: dict, headers: dict | None = None) -> dict:
        self.requests.append(("POST", url, data))
        return self.responses.get(("POST", url), {})
```

### Use in Your Code

```python
class WeatherService:
    def __init__(self, client: HTTPClient, api_key: str):
        self.client = client
        self.api_key = api_key
        self.base_url = "https://api.weather.com"

    def get_forecast(self, city: str) -> dict:
        url = f"{self.base_url}/forecast/{city}"
        headers = {"X-API-Key": self.api_key}
        return self.client.get(url, headers=headers)
```

### Test It

```python
def test_get_forecast():
    fake_client = FakeHTTPClient()
    fake_client.add_response(
        "GET",
        "https://api.weather.com/forecast/London",
        {"temp": 72, "condition": "sunny"}
    )

    service = WeatherService(fake_client, "test-api-key")
    result = service.get_forecast("London")

    assert result["temp"] == 72
    assert result["condition"] == "sunny"
    assert len(fake_client.requests) == 1
    assert fake_client.requests[0][0] == "GET"
```

## Pattern 2: Service-Specific Wrapper

For complex APIs, create a service-specific wrapper:

```python
from typing import Protocol

class StripeGateway(Protocol):
    """Interface for Stripe payment operations."""
    def create_charge(self, amount: int, token: str) -> dict:
        ...

    def refund_charge(self, charge_id: str) -> dict:
        ...

class RealStripeGateway:
    """Production Stripe implementation."""
    def __init__(self, api_key: str):
        import stripe
        stripe.api_key = api_key
        self.stripe = stripe

    def create_charge(self, amount: int, token: str) -> dict:
        charge = self.stripe.Charge.create(
            amount=amount,
            currency="usd",
            source=token
        )
        return {"id": charge.id, "status": charge.status}

    def refund_charge(self, charge_id: str) -> dict:
        refund = self.stripe.Refund.create(charge=charge_id)
        return {"id": refund.id, "status": refund.status}

class FakeStripeGateway:
    """Test Stripe implementation."""
    def __init__(self):
        self.charges = []
        self.refunds = []
        self.next_charge_id = 1

    def create_charge(self, amount: int, token: str) -> dict:
        charge_id = f"ch_{self.next_charge_id}"
        self.next_charge_id += 1
        self.charges.append({"id": charge_id, "amount": amount, "token": token})
        return {"id": charge_id, "status": "succeeded"}

    def refund_charge(self, charge_id: str) -> dict:
        refund_id = f"re_{len(self.refunds) + 1}"
        self.refunds.append({"id": refund_id, "charge_id": charge_id})
        return {"id": refund_id, "status": "succeeded"}

def test_payment_flow():
    fake_stripe = FakeStripeGateway()

    # Create charge
    charge = fake_stripe.create_charge(1000, "tok_visa")
    assert charge["status"] == "succeeded"
    assert len(fake_stripe.charges) == 1

    # Refund
    refund = fake_stripe.refund_charge(charge["id"])
    assert refund["status"] == "succeeded"
    assert len(fake_stripe.refunds) == 1
```

## Pattern 3: Database as a Dependency

```python
from typing import Protocol

class Database(Protocol):
    """Interface for database operations."""
    def query(self, sql: str, params: tuple = ()) -> list[dict]:
        ...

    def execute(self, sql: str, params: tuple = ()) -> int:
        ...

class RealDatabase:
    """Production database using psycopg."""
    def __init__(self, connection_string: str):
        import psycopg
        self.conn = psycopg.connect(connection_string)

    def query(self, sql: str, params: tuple = ()) -> list[dict]:
        with self.conn.cursor() as cur:
            cur.execute(sql, params)
            columns = [desc[0] for desc in cur.description]
            return [dict(zip(columns, row)) for row in cur.fetchall()]

    def execute(self, sql: str, params: tuple = ()) -> int:
        with self.conn.cursor() as cur:
            cur.execute(sql, params)
            self.conn.commit()
            return cur.rowcount

class FakeDatabase:
    """Test database with in-memory storage."""
    def __init__(self):
        self.users = {
            1: {"id": 1, "name": "Alice", "email": "alice@example.com"},
            2: {"id": 2, "name": "Bob", "email": "bob@example.com"},
        }
        self.queries: list[tuple[str, tuple]] = []

    def query(self, sql: str, params: tuple = ()) -> list[dict]:
        self.queries.append((sql, params))

        if "SELECT * FROM users" in sql:
            return list(self.users.values())
        elif "WHERE id = " in sql and params:
            user_id = params[0]
            return [self.users[user_id]] if user_id in self.users else []

        return []

    def execute(self, sql: str, params: tuple = ()) -> int:
        self.queries.append((sql, params))

        if "INSERT INTO users" in sql:
            new_id = max(self.users.keys()) + 1
            self.users[new_id] = {"id": new_id, "name": params[0], "email": params[1]}
            return 1

        return 0

def test_user_repository():
    fake_db = FakeDatabase()

    # Query users
    users = fake_db.query("SELECT * FROM users")
    assert len(users) == 2

    # Insert user
    rows = fake_db.execute(
        "INSERT INTO users (name, email) VALUES (?, ?)",
        ("Charlie", "charlie@example.com")
    )
    assert rows == 1
    assert len(fake_db.users) == 3
```

## Pattern 4: File System Operations

```python
from typing import Protocol
from pathlib import Path

class FileSystem(Protocol):
    """Interface for file system operations."""
    def read_text(self, path: Path) -> str:
        ...

    def write_text(self, path: Path, content: str) -> None:
        ...

    def exists(self, path: Path) -> bool:
        ...

class RealFileSystem:
    """Production file system using pathlib."""
    def read_text(self, path: Path) -> str:
        return path.read_text()

    def write_text(self, path: Path, content: str) -> None:
        path.write_text(content)

    def exists(self, path: Path) -> bool:
        return path.exists()

class FakeFileSystem:
    """Test file system with in-memory storage."""
    def __init__(self):
        self.files: dict[Path, str] = {}

    def read_text(self, path: Path) -> str:
        if path not in self.files:
            raise FileNotFoundError(f"{path} not found")
        return self.files[path]

    def write_text(self, path: Path, content: str) -> None:
        self.files[path] = content

    def exists(self, path: Path) -> bool:
        return path in self.files

def test_config_manager():
    fake_fs = FakeFileSystem()
    config_path = Path("config.json")

    # Write config
    fake_fs.write_text(config_path, '{"debug": true}')
    assert fake_fs.exists(config_path)

    # Read config
    content = fake_fs.read_text(config_path)
    assert "debug" in content
```

## Benefits

- **Fast tests** - No network calls
- **Reliable** - No dependency on external services
- **Repeatable** - Same results every time
- **Clear** - Easy to see what's being tested
- **No mocks** - Use real implementations that follow protocols

## Next Steps

- Read [Dependency Injection](dependency-injection.md) for more patterns
- See [Refactor Tests](refactor-tests.md) for step-by-step guide
- Understand [Why avoid mocks?](../explanation/why-no-mocks.md)
