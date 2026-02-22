# CLI Reference

Complete reference for the mockbuster command-line interface.

## Installation

```bash
pip install mockbuster
```

## Usage

```bash
mockbuster [PATHS]... [OPTIONS]
```

## Arguments

### PATHS

One or more files or directories to scan. Each can be:

- A single Python file
- A directory (scanned recursively for `*.py`)

**Default:** Falls back to `path` configured in `[tool.mockbuster]` (default: `tests/`)

**Examples:**

```bash
# Scan a directory
mockbuster tests/

# Scan a single file
mockbuster tests/test_service.py

# Scan multiple files (e.g. passed by pre-commit)
mockbuster tests/test_a.py tests/test_b.py

# No argument — uses path from pyproject.toml
mockbuster
```

## Options

### --strict

Exit with error code 1 if any violations are found.

**Type:** Flag (no value required)

**Default:** `False` (exit with code 0 regardless of violations)

**Examples:**

```bash
# Fail CI build if mocks found
mockbuster tests/ --strict

# Just report violations (don't fail)
mockbuster tests/
```

### --disable

Disable detection of a specific category. Repeatable.

**Valid values:** `mock_classes`, `patch`, `fixtures`

**Default:** All categories enabled

**Examples:**

```bash
mockbuster tests/ --disable fixtures
mockbuster tests/ --disable mock_classes --disable patch
```

### --update-baseline

Record all current violations as the baseline and exit with code 0.

**Type:** Flag (no value required)

**Default:** `False`

**Example:**

```bash
mockbuster tests/ --update-baseline
```

### --no-baseline

Ignore the baseline file and report all violations.

**Type:** Flag (no value required)

**Default:** `False`

**Example:**

```bash
mockbuster tests/ --no-baseline
```

### --help

Show help message and exit.

**Example:**

```bash
mockbuster --help
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success (no violations or not in strict mode) |
| 1 | Violations found (only in `--strict` mode) |
| 2 | Command-line error (invalid arguments) |

## Output Format

### No Violations

```
No violations found.
```

Exit code: 0

### Violations Found (Non-Strict Mode)

```
tests/test_service.py
  Line 3: Mock import detected: unittest.mock - Use dependency injection instead

Found 1 violation in 1 file.
```

Exit code: 0

### Violations Found (Strict Mode)

```
tests/test_service.py
  Line 3: Mock import detected: unittest.mock - Use dependency injection instead

Found 1 violation in 1 file.
```

Exit code: 1

## Examples

### Basic Scanning

Scan a directory and report violations:

```bash
mockbuster tests/
```

### CI/CD Integration

Fail the build if mocks are detected:

```bash
mockbuster tests/ --strict
```

### Scan Multiple Files

Pass multiple paths directly:

```bash
mockbuster tests/unit/test_foo.py tests/integration/test_bar.py
```

### Combine with Other Tools

Chain with other linters:

```bash
ruff check . && mockbuster tests/ --strict && pytest
```

### Show Full Path

Use with `find` to show full paths:

```bash
find tests -name "*.py" -exec mockbuster {} --strict \;
```

## Integration Examples

### Makefile

```makefile
.PHONY: lint

lint:
 mockbuster tests/ --strict
```

### Pre-commit Hook

Using the published hook (reads test path from `pyproject.toml`):

```yaml
repos:
  - repo: https://github.com/benomahony/mockbuster
    rev: v0.1.3
    hooks:
      - id: mockbuster
```

If your tests are not under `tests/`, set `path` in `pyproject.toml`:

```toml
[tool.mockbuster]
path = "test/"
```

### GitHub Actions

```yaml
- name: Check for mocks
  run: mockbuster tests/ --strict
```

### Shell Script

```bash
#!/bin/bash
set -e

echo "Running mockbuster..."
mockbuster tests/ --strict

if [ $? -eq 0 ]; then
    echo "✓ No mocks detected"
else
    echo "✗ Mocks found - see output above"
    exit 1
fi
```

## See Also

- [API Reference](api.md) - Python API
- [Detected Patterns](patterns.md) - What mockbuster detects
- [CI Integration](../howto/ci-integration.md) - CI/CD examples
