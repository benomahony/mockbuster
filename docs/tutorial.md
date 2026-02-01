# Tutorial: Getting Started with mockbuster

This tutorial will guide you through using mockbuster to detect mocking in your tests and refactor them to use dependency injection instead.

## Prerequisites

- Python 3.12 or higher
- A Python project with tests

## Installation

Install mockbuster using pip or uv:

```bash
pip install mockbuster
```

or

```bash
uv add --dev mockbuster
```

## Your First Scan

Let's scan a test file that uses mocks. Create a file called `test_example.py`:

```python
from unittest.mock import Mock

def test_user_service():
    mock_db = Mock()
    mock_db.get_user.return_value = {"name": "Alice"}

    # Test code here
    assert mock_db.get_user() == {"name": "Alice"}
```

Now scan it with mockbuster:

```bash
mockbuster test_example.py
```

You'll see output like:

```
test_example.py
  Line 1: Mock import detected: unittest.mock - Use dependency injection instead (pass dependencies as constructor/function parameters)

Found 1 violation in 1 file.
```

## Understanding the Results

The output tells you:

- **File**: `test_example.py` contains violations
- **Line 1**: The violation is on line 1
- **Message**: What was detected and the recommended fix

## Fixing Your First Violation

Let's refactor the test to use dependency injection. First, define a protocol for the database:

```python
from typing import Protocol

class Database(Protocol):
    def get_user(self, user_id: str) -> dict[str, str]:
        ...

class FakeDatabase:
    """Test implementation of Database."""
    def __init__(self):
        self.users = {"1": {"name": "Alice"}}

    def get_user(self, user_id: str) -> dict[str, str]:
        return self.users.get(user_id, {})

class UserService:
    def __init__(self, db: Database):
        self.db = db

    def get_user_name(self, user_id: str) -> str:
        user = self.db.get_user(user_id)
        return user.get("name", "Unknown")

def test_user_service():
    # No mocks needed!
    fake_db = FakeDatabase()
    service = UserService(fake_db)

    assert service.get_user_name("1") == "Alice"
```

Now scan again:

```bash
mockbuster test_example.py
```

Output:

```
No violations found.
```

Success! You've refactored your first test to use dependency injection instead of mocks.

## Using in CI/CD

To fail your CI build when mocks are detected, use `--strict` mode:

```bash
mockbuster tests/ --strict
```

This exits with code 1 if any violations are found.

## Next Steps

- Read the [How-to Guides](howto/index.md) for practical examples
- Understand [Why avoid mocks?](explanation/why-no-mocks.md)
- Learn more about [Dependency Injection](explanation/dependency-injection.md)
