# Detected Patterns

Complete list of mock patterns detected by mockbuster.

mockbuster detects **actual mock usage**, not just imports. This means it only flags code that's actually using mocks, avoiding false positives from unused imports.

## Pattern Categories

mockbuster detects mocking usage in five categories:

1. [Mock instantiation](#mock-instantiation)
2. [@patch decorators](#patch-decorators)
3. [patch() context managers](#patch-context-managers)
4. [mocker fixture usage](#mocker-fixture-usage)
5. [monkeypatch fixture usage](#monkeypatch-fixture-usage)

## Mock Instantiation

Detects when Mock classes are instantiated.

### Mock()

**Detected:**

```python
from unittest.mock import Mock

def test_example():
    mock_obj = Mock()  # ← Detected here
```

**Line Reported:** The line where Mock() is called

**Message:**

```
Mock() instantiation detected - Use real objects, dependency injection, or integration tests
```

### MagicMock()

**Detected:**

```python
from unittest.mock import MagicMock

def test_example():
    magic = MagicMock()  # ← Detected here
```

### AsyncMock()

**Detected:**

```python
from unittest.mock import AsyncMock

async def test_example():
    mock = AsyncMock()  # ← Detected here
```

### PropertyMock()

**Detected:**

```python
from unittest.mock import PropertyMock

def test_example():
    prop = PropertyMock()  # ← Detected here
```

### With Module Prefix

Also detects usage with module prefixes:

```python
import unittest.mock
import mock

def test_example():
    m1 = unittest.mock.Mock()  # ← Detected
    m2 = mock.MagicMock()  # ← Detected
```

**Message Format:**

```
Mock() instantiation detected - Use real objects, dependency injection, or integration tests
MagicMock() instantiation detected - Use real objects, dependency injection, or integration tests
AsyncMock() instantiation detected - Use real objects, dependency injection, or integration tests
PropertyMock() instantiation detected - Use real objects, dependency injection, or integration tests
```

## @patch Decorators

Detects `@patch` decorators on test functions.

### @patch Decorator

**Detected:**

```python
from unittest.mock import patch

@patch('module.function')  # ← Detected here
def test_example(mock_func):
    pass
```

**Line Reported:** The decorator line

**Message:**

```
@patch decorator detected - Use real objects, dependency injection, or integration tests
```

### @patch.object Decorator

**Detected:**

```python
from unittest.mock import patch

@patch.object(MyClass, 'method')  # ← Detected here
def test_example(mock_method):
    pass
```

**Message:**

```
@patch.object decorator detected - Use real objects, dependency injection, or integration tests
```

### Multiple @patch Decorators

Each decorator is detected separately:

```python
@patch('module.func1')  # ← Detected (violation 1)
@patch('module.func2')  # ← Detected (violation 2)
def test_example(mock2, mock1):
    pass
```

## patch() Context Managers

Detects `patch()` used as a context manager.

### patch() Context Manager

**Detected:**

```python
from unittest.mock import patch

def test_example():
    with patch('module.function'):  # ← Detected here
        do_something()
```

**Message:**

```
patch() context manager detected - Use real objects, dependency injection, or integration tests
```

### patch.object() Context Manager

**Detected:**

```python
from unittest.mock import patch

def test_example():
    with patch.object(obj, 'attr') as mock_attr:  # ← Detected here
        do_something()
```

**Message:**

```
patch.object() context manager detected - Use real objects, dependency injection, or integration tests
```

### patch.multiple() and patch.dict()

Also detects other patch variants:

```python
with patch.multiple('module', attr1=DEFAULT, attr2=DEFAULT):  # ← Detected
    pass

with patch.dict('os.environ', {'KEY': 'value'}):  # ← Detected
    pass
```

## mocker Fixture Usage

The most common pattern with pytest-mock.

### Function Parameter

**Detected:**

```python
def test_example(mocker):
    mocker.patch('some.module')
```

**Line Reported:** The line with the function definition (`def test_example(mocker):`)

**Message:**

```
pytest-mock 'mocker' fixture detected - Use dependency injection instead (pass dependencies as test function parameters)
```

### Multiple Parameters

**Detected:**

```python
def test_example(mocker, tmp_path):
    mocker.patch('some.module')
```

**Line Reported:** The function definition line

**Message:**

```
pytest-mock 'mocker' fixture detected - Use real objects, dependency injection, or integration tests
```

## monkeypatch Fixture Usage

pytest's built-in `monkeypatch` fixture for runtime patching.

### Function Parameter

**Detected:**

```python
def test_example(monkeypatch):
    monkeypatch.setattr(module, 'function', fake_function)
    monkeypatch.setenv('API_KEY', 'test-key')
```

**Line Reported:** The line with the function definition (`def test_example(monkeypatch):`)

**Message:**

```
pytest 'monkeypatch' fixture detected - Use real objects, dependency injection, or integration tests
```

### Multiple Parameters

**Detected:**

```python
def test_example(monkeypatch, tmp_path):
    monkeypatch.setattr('os.path.exists', lambda x: True)
```

**Line Reported:** The function definition line

**Message:**

```
pytest 'monkeypatch' fixture detected - Use real objects, dependency injection, or integration tests
```

### Why Detect monkeypatch?

While `monkeypatch` is pytest's built-in fixture (not a third-party mock library), it still represents runtime patching that can be replaced with:

- **Real objects**: Use actual implementations or test doubles
- **Dependency injection**: Pass dependencies as parameters
- **Integration tests**: Test with real external services

## Ignoring Violations

Suppress violations on specific lines using ignore comments.

### Same-line Syntax

Place the ignore comment on the same line as the violation:

```python
from unittest.mock import Mock  # mockbuster: ignore
```

### Previous-line Syntax

Place the ignore comment on the line before the violation:

```python
# mockbuster: ignore
from unittest.mock import (
    Mock,
    MagicMock,
    patch,
)
```

The ignore applies to both the comment line and the next line with code.

### Multiple Ignores

You can use multiple ignore comments in the same file:

```python
# mockbuster: ignore
from unittest.mock import Mock

from unittest.mock import patch  # mockbuster: ignore

def test_with_mocker(mocker):  # mockbuster: ignore
    pass
```

### Case Insensitive

The comment is case-insensitive and flexible with whitespace:

```python
from unittest.mock import Mock  # MOCKBUSTER: IGNORE
from unittest.mock import patch  #mockbuster:ignore
from unittest.mock import MagicMock  # mockbuster : ignore
```

### When to Use Ignores

Use ignore comments sparingly for:

- ✅ Legacy code during incremental refactoring
- ✅ Third-party test fixtures requiring mocks
- ✅ Temporary exceptions with TODO comments

Avoid using ignores for:

- ❌ New code (fix the design instead)
- ❌ Hiding technical debt without a plan to fix it

### Example: Gradual Migration

```python
# Legacy test - refactor in JIRA-123
# mockbuster: ignore
from unittest.mock import Mock

def test_legacy():
    mock_obj = Mock()

# New test - using dependency injection
def test_new():
    fake_obj = FakeService()
    assert fake_obj.do_something() == "result"
```

### Programmatic Control

You can also control ignore behavior via the API:

```python
from mockbuster import detect_mocks

code = "from unittest.mock import Mock  # mockbuster: ignore"

# Default: respects ignore comments
violations = detect_mocks(code)
assert len(violations) == 0

# Disabled: reports all violations
violations = detect_mocks(code, respect_ignores=False)
assert len(violations) == 1
```

## Not Detected

mockbuster does **not** detect:

### Unused Imports

Imports without actual usage are not flagged:

```python
# Not detected - imported but never used
from unittest.mock import Mock, patch

def test_example():
    # No mock usage here
    assert 1 + 1 == 2
```

**Why:** Unused imports are caught by linters (ruff, flake8). mockbuster focuses on actual mock usage.

### Mock in Variable Names

Variables named "mock" are not detected:

```python
# Not detected - just a variable name
my_mock = SomeClass()
mock_data = {"key": "value"}
```

### User-Defined Functions Named "patch"

To avoid false positives, bare calls to `patch()` without a module prefix are not detected:

```python
# Not detected - could be a user-defined function
def patch(value):
    return value + 1

result = patch(5)
```

**Note:** Calls like `unittest.mock.patch()` or `mock.patch()` ARE detected because the module prefix confirms it's the mock library.

### String Literals

String references to mocks are not detected:

```python
# Not detected - just a string
patch_path = "unittest.mock.patch"
```

### Comments

Commented-out code is not detected:

```python
# Not detected - just a comment
# mock = Mock()
```

### Dynamic Imports

Dynamic imports require runtime analysis:

```python
# Not detected - dynamic import
mock_module = __import__("unittest.mock")
```

## Detection Method

mockbuster uses Python's `ast` (Abstract Syntax Tree) module to analyze code statically. This means:

- ✅ Safe - no code execution
- ✅ Fast - parses files quickly
- ✅ Accurate - detects imports and parameters
- ❌ Limited to static patterns
- ❌ Won't detect dynamic imports

## Complete Examples

### Example 1: Multiple Violations

```python
from unittest.mock import Mock, patch

@patch('module.func')  # Line 3 - Violation 1
def test_with_mocker(mock_func, mocker):  # Line 4 - Violation 2
    mock_obj = Mock()  # Line 5 - Violation 3
```

**Violations:**

- Line 3: `@patch` decorator
- Line 4: `mocker` fixture
- Line 5: `Mock()` instantiation

**Total:** 3 violations

### Example 2: Clean Code

```python
from typing import Protocol

class Database(Protocol):
    def query(self, sql: str) -> list[dict]:
        ...

class FakeDatabase:
    def query(self, sql: str) -> list[dict]:
        return [{"id": 1, "name": "Alice"}]

def test_query():
    fake_db = FakeDatabase()
    results = fake_db.query("SELECT * FROM users")
    assert len(results) == 1
```

**Violations:** None (no mocking!)

### Example 3: Imports Without Usage

```python
import pytest
from unittest.mock import Mock  # Imported but not used

def test_clean():
    assert 1 + 1 == 2
```

**Violations:** None (import is unused - let linters handle this)

### Example 4: Actual Usage Detected

```python
import pytest
from unittest.mock import Mock

def test_clean():
    assert 1 + 1 == 2

def test_with_mock():
    mock_obj = Mock()  # Line 8 - Violation
```

**Violations:**

- Line 8: `Mock()` instantiation

**Total:** 1 violation

## Rationale

These patterns are detected because they indicate code that could be refactored to use dependency injection instead of mocking. See the [Explanation](../explanation/index.md) section for more on why mocks should be avoided.

## See Also

- [CLI Reference](cli.md) - Command-line usage
- [API Reference](api.md) - Python API
- [Why avoid mocks?](../explanation/why-no-mocks.md) - Philosophy
- [Dependency Injection](../howto/dependency-injection.md) - Alternative approach
