# mockbuster

A Python linter that detects and reports all uses of mocking in test files.

## Installation

```bash
pip install mockbuster
```

## Usage

### As a library

Detect mocking usage in Python code:

```python
from mockbuster import detect_mocks

code = """
from unittest.mock import Mock

def test_foo():
    mock_obj = Mock()
    assert mock_obj is not None
"""

violations = detect_mocks(code)
assert len(violations) == 1
assert violations[0]["line"] == 2
assert "unittest.mock" in violations[0]["message"]
```

Detect `patch` decorator usage:

```python
from mockbuster import detect_mocks

code = """
from unittest.mock import patch

@patch('some.module')
def test_bar(mock_module):
    pass
"""

violations = detect_mocks(code)
assert len(violations) == 1
assert violations[0]["line"] == 2
assert "patch" in violations[0]["message"]
```

Detect pytest-mock usage:

```python
from mockbuster import detect_mocks

code = """
def test_baz(mocker):
    mocker.patch('some.module')
"""

violations = detect_mocks(code)
assert len(violations) == 1
assert violations[0]["line"] == 2
assert "mocker" in violations[0]["message"]
```

Detect MagicMock usage:

```python
from mockbuster import detect_mocks

code = """
from unittest.mock import MagicMock

def test_qux():
    magic = MagicMock()
"""

violations = detect_mocks(code)
assert len(violations) == 1
```

Clean code with no mocking returns empty list:

```python
from mockbuster import detect_mocks

code = """
def test_clean():
    result = 1 + 1
    assert result == 2
"""

violations = detect_mocks(code)
assert len(violations) == 0
```

### As a CLI

Scan a single file:

```bash
mockbuster tests/test_example.py
```

Scan a directory:

```bash
mockbuster tests/
```

Exit with error code if mocks found:

```bash
mockbuster tests/ --strict
```

## Development

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Run pre-commit hooks
uv run pre-commit run --all-files
```
