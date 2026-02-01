# CLI Reference

Complete reference for the mockbuster command-line interface.

## Installation

```bash
pip install mockbuster
```

## Usage

```bash
mockbuster [PATH] [OPTIONS]
```

## Arguments

### PATH

Path to scan for mocking usage. Can be:

- A single Python file
- A directory (scanned recursively)

**Default:** Current directory (`.`)

**Examples:**

```bash
# Scan a single file
mockbuster tests/test_service.py

# Scan a directory
mockbuster tests/

# Scan current directory
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

### Scan Multiple Patterns

Use shell globbing to scan specific patterns:

```bash
mockbuster tests/unit/*.py
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

```yaml
repos:
  - repo: local
    hooks:
      - id: mockbuster
        name: mockbuster
        entry: mockbuster
        language: system
        types: [python]
        files: ^tests/
        args: ["--strict"]
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
