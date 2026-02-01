# Detected Patterns

Complete list of mock patterns detected by mockbuster.

## Pattern Categories

mockbuster detects mocking usage in four categories:

1. [unittest.mock imports](#unittestmock-imports)
2. [Legacy mock library](#legacy-mock-library)
3. [pytest-mock imports](#pytest-mock-imports)
4. [mocker fixture usage](#mocker-fixture-usage)

## unittest.mock Imports

### from unittest.mock import

**Detected:**

```python
from unittest.mock import Mock
from unittest.mock import MagicMock
from unittest.mock import AsyncMock
from unittest.mock import patch
from unittest.mock import call
from unittest.mock import ANY
from unittest.mock import Mock, MagicMock
```

**Line Reported:** The line with the `import` statement

**Message:**

```
Mock import detected: unittest.mock - Use dependency injection instead (pass dependencies as constructor/function parameters)
```

**Example:**

```python
# Line 1
from unittest.mock import Mock

def test_example():
    mock_obj = Mock()
```

**Detected on:** Line 1

### import unittest.mock

**Detected:**

```python
import unittest.mock

def test_example():
    mock_obj = unittest.mock.Mock()
```

**Line Reported:** The line with the `import` statement

**Message:**

```
Mock import detected: unittest.mock - Use dependency injection instead (pass dependencies as constructor/function parameters)
```

## Legacy mock Library

The standalone `mock` library (pre-Python 3.3) is also detected.

### from mock import

**Detected:**

```python
from mock import Mock
from mock import MagicMock
from mock import patch
```

**Line Reported:** The line with the `import` statement

**Message:**

```
Mock import detected: mock - Use dependency injection instead (pass dependencies as constructor/function parameters)
```

### import mock

**Detected:**

```python
import mock

def test_example():
    mock_obj = mock.Mock()
```

**Line Reported:** The line with the `import` statement

**Message:**

```
Mock import detected: mock - Use dependency injection instead (pass dependencies as constructor/function parameters)
```

## pytest-mock Imports

### from pytest_mock import

**Detected:**

```python
from pytest_mock import mocker
import pytest_mock
```

**Line Reported:** The line with the `import` statement

**Message:**

```
Mock import detected: pytest_mock - Use dependency injection instead (pass dependencies as constructor/function parameters)
```

**Note:** This is rare - most pytest-mock usage is through the fixture, not direct imports.

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
pytest-mock 'mocker' fixture detected - Use dependency injection instead (pass dependencies as test function parameters)
```

## Not Detected

mockbuster does **not** detect:

### Mock in Variable Names

These are not detected (they're just names):

```python
# Not detected - just a variable name
my_mock = SomeClass()
mock_data = {"key": "value"}
```

### String Literals

These are not detected:

```python
# Not detected - just a string
patch_path = "unittest.mock.patch"
```

### Comments

These are not detected:

```python
# Not detected - just a comment
# from unittest.mock import Mock
```

### Dynamic Imports

These are not detected (requires runtime analysis):

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
# Line 1
from unittest.mock import Mock, MagicMock
# Line 2
from unittest.mock import patch

# Line 4
def test_with_mocker(mocker):
    mock_obj = Mock()
```

**Violations:**

- Line 1: `unittest.mock` import
- Line 2: `unittest.mock` import
- Line 4: `mocker` fixture

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

### Example 3: Mixed Code

```python
# Line 1
import pytest
# Line 2
from unittest.mock import Mock

# Line 4
def test_clean():
    assert 1 + 1 == 2

# Line 7
def test_with_mock():
    mock_obj = Mock()
```

**Violations:**

- Line 2: `unittest.mock` import

**Total:** 1 violation

## Rationale

These patterns are detected because they indicate code that could be refactored to use dependency injection instead of mocking. See the [Explanation](../explanation/index.md) section for more on why mocks should be avoided.

## See Also

- [CLI Reference](cli.md) - Command-line usage
- [API Reference](api.md) - Python API
- [Why avoid mocks?](../explanation/why-no-mocks.md) - Philosophy
- [Dependency Injection](../howto/dependency-injection.md) - Alternative approach
