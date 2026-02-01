# How to Use Dependency Injection

This guide shows you how to use dependency injection to make your code testable without mocks.

## The Problem

Hard-coded dependencies make testing difficult:

```python
from external_api import APIClient

class UserService:
    def __init__(self):
        self.client = APIClient()  # Hard dependency!

    def get_user(self, user_id: str) -> dict:
        return self.client.fetch(f"/users/{user_id}")
```

To test this, you'd need to mock `APIClient`. But there's a better way.

## Solution: Constructor Injection

Inject dependencies through the constructor:

```python
from typing import Protocol

class APIClientProtocol(Protocol):
    """Interface for API clients."""
    def fetch(self, path: str) -> dict:
        ...

class UserService:
    def __init__(self, client: APIClientProtocol):
        self.client = client  # Injected dependency

    def get_user(self, user_id: str) -> dict:
        return self.client.fetch(f"/users/{user_id}")
```

## Create a Test Double

Now create a simple fake for testing:

```python
class FakeAPIClient:
    """Test implementation of APIClientProtocol."""
    def __init__(self):
        self.responses = {
            "/users/1": {"id": "1", "name": "Alice"},
            "/users/2": {"id": "2", "name": "Bob"},
        }

    def fetch(self, path: str) -> dict:
        return self.responses.get(path, {})

def test_user_service():
    # No mocks needed!
    fake_client = FakeAPIClient()
    service = UserService(fake_client)

    user = service.get_user("1")
    assert user["name"] == "Alice"
```

## Function-Level Injection

For simpler cases, inject dependencies as function parameters:

```python
from typing import Protocol
from pathlib import Path

class FileSystem(Protocol):
    def read_text(self, path: Path) -> str:
        ...

def process_config(fs: FileSystem, config_path: Path) -> dict:
    content = fs.read_text(config_path)
    # Process config...
    return {"config": content}

class FakeFileSystem:
    def __init__(self, files: dict[Path, str]):
        self.files = files

    def read_text(self, path: Path) -> str:
        return self.files.get(path, "")

def test_process_config():
    fake_fs = FakeFileSystem({
        Path("config.txt"): "setting=value"
    })

    result = process_config(fake_fs, Path("config.txt"))
    assert "setting=value" in result["config"]
```

## Benefits

- **No mocks needed** - Use real test implementations
- **Explicit dependencies** - Clear from function signatures
- **Flexible** - Easy to swap implementations
- **Testable** - Simple to test with fakes
- **Maintainable** - Tests don't break when implementation details change

## Common Patterns

### Protocol-Based Interfaces

Use Python protocols to define interfaces:

```python
from typing import Protocol

class Database(Protocol):
    def query(self, sql: str) -> list[dict]:
        ...

    def execute(self, sql: str) -> None:
        ...
```

### Abstract Base Classes

For more complex interfaces, use ABCs:

```python
from abc import ABC, abstractmethod

class PaymentGateway(ABC):
    @abstractmethod
    def charge(self, amount: int, token: str) -> bool:
        pass

    @abstractmethod
    def refund(self, transaction_id: str) -> bool:
        pass

class FakePaymentGateway(PaymentGateway):
    def __init__(self):
        self.charges = []
        self.refunds = []

    def charge(self, amount: int, token: str) -> bool:
        self.charges.append((amount, token))
        return True

    def refund(self, transaction_id: str) -> bool:
        self.refunds.append(transaction_id)
        return True
```

### Factory Functions

For complex object creation:

```python
def create_service(config: dict) -> UserService:
    if config.get("env") == "test":
        client = FakeAPIClient()
    else:
        client = RealAPIClient(api_key=config["api_key"])

    return UserService(client)
```

## Next Steps

- See [Refactor Tests](refactor-tests.md) for step-by-step refactoring
- Read [Why avoid mocks?](../explanation/why-no-mocks.md) for the philosophy
- Check [Third-Party APIs](third-party-apis.md) for handling external dependencies
