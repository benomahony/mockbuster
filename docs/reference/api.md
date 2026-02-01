# API Reference

Python API documentation for mockbuster.

## Module: `mockbuster`

### `detect_mocks(code: str) -> list[dict[str, str | int]]`

Detect mocking usage in Python source code.

**Parameters:**

- `code` (str): Python source code to analyze

**Returns:**

List of violation dictionaries with the following structure:

```python
[
    {
        "line": int,      # Line number where violation was detected
        "message": str,   # Description of the violation
    },
    ...
]
```

**Raises:**

- `AssertionError`: If code is None or not a string

**Example:**

```python
from mockbuster import detect_mocks

code = """
from unittest.mock import Mock

def test_example():
    mock_obj = Mock()
    assert mock_obj is not None
"""

violations = detect_mocks(code)
print(violations)
# [{'line': 2, 'message': 'Mock import detected: unittest.mock - Use dependency injection instead'}]
```

## Detected Patterns

The `detect_mocks` function detects the following patterns:

### 1. unittest.mock Imports

Detects imports from `unittest.mock`:

```python
from unittest.mock import Mock
from unittest.mock import MagicMock, AsyncMock
from unittest.mock import patch
```

**Message Format:**

```
Mock import detected: unittest.mock - Use dependency injection instead (pass dependencies as constructor/function parameters)
```

### 2. Legacy mock Library

Detects imports from the legacy `mock` library:

```python
import mock
from mock import Mock
```

**Message Format:**

```
Mock import detected: mock - Use dependency injection instead (pass dependencies as constructor/function parameters)
```

### 3. pytest-mock Imports

Detects imports from `pytest_mock`:

```python
import pytest_mock
from pytest_mock import mocker
```

**Message Format:**

```
Mock import detected: pytest_mock - Use dependency injection instead (pass dependencies as constructor/function parameters)
```

### 4. mocker Fixture

Detects usage of the `mocker` fixture in pytest tests:

```python
def test_example(mocker):
    mocker.patch('some.module')
```

**Message Format:**

```
pytest-mock 'mocker' fixture detected - Use dependency injection instead (pass dependencies as test function parameters)
```

## Return Value Structure

### Violation Dictionary

Each violation is a dictionary with two keys:

```python
{
    "line": int,      # Line number (1-indexed)
    "message": str,   # Human-readable description
}
```

**Field Details:**

| Field | Type | Description |
|-------|------|-------------|
| `line` | `int` | Line number where the violation was detected (1-indexed) |
| `message` | `str` | Description of what was detected and recommended fix |

## Usage Examples

### Basic Detection

```python
from mockbuster import detect_mocks

code = """
from unittest.mock import Mock
"""

violations = detect_mocks(code)
assert len(violations) == 1
assert violations[0]["line"] == 2
assert "unittest.mock" in violations[0]["message"]
```

### Clean Code

```python
from mockbuster import detect_mocks

code = """
def test_addition():
    assert 1 + 1 == 2
"""

violations = detect_mocks(code)
assert len(violations) == 0
```

### Multiple Violations

```python
from mockbuster import detect_mocks

code = """
from unittest.mock import Mock
from unittest.mock import patch

def test_example(mocker):
    mock_obj = Mock()
"""

violations = detect_mocks(code)
assert len(violations) == 3  # Two imports + one fixture
```

### Handling Syntax Errors

If the code has syntax errors, an empty list is returned:

```python
from mockbuster import detect_mocks

code = "def invalid syntax here"
violations = detect_mocks(code)
assert len(violations) == 0  # Empty - can't parse
```

### Integrating with File Reading

```python
from pathlib import Path
from mockbuster import detect_mocks

def scan_file(file_path: Path) -> list[dict[str, str | int]]:
    """Scan a Python file for mocking usage."""
    code = file_path.read_text()
    return detect_mocks(code)

violations = scan_file(Path("tests/test_example.py"))
for v in violations:
    print(f"Line {v['line']}: {v['message']}")
```

### Integrating with Directory Scanning

```python
from pathlib import Path
from mockbuster import detect_mocks

def scan_directory(dir_path: Path) -> dict[Path, list[dict[str, str | int]]]:
    """Scan all Python files in a directory."""
    results = {}

    for py_file in dir_path.rglob("*.py"):
        code = py_file.read_text()
        violations = detect_mocks(code)
        if violations:
            results[py_file] = violations

    return results

all_violations = scan_directory(Path("tests"))
for file_path, violations in all_violations.items():
    print(f"\n{file_path}")
    for v in violations:
        print(f"  Line {v['line']}: {v['message']}")
```

## Type Hints

Full type signature:

```python
def detect_mocks(code: str) -> list[dict[str, str | int]]:
    ...
```

## Implementation Details

- Uses Python's `ast` module for parsing
- Safe - does not execute code
- Handles syntax errors gracefully
- Detects imports and function parameters
- NASA05 compliant with defensive assertions

## See Also

- [CLI Reference](cli.md) - Command-line interface
- [Detected Patterns](patterns.md) - Complete pattern list
- [How-to Guides](../howto/index.md) - Practical examples
