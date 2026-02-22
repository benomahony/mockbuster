# Configuration Reference

mockbuster can be configured via `pyproject.toml` in your project root.

## `[tool.mockbuster]`

Add a `[tool.mockbuster]` section to your project's `pyproject.toml`:

```toml
[tool.mockbuster]
disable = ["fixtures"]
```

mockbuster walks up from the scanned path to find the nearest `pyproject.toml`.

---

## Options

### `disable`

A list of detection categories to skip. Violations in disabled categories are never reported.

**Type:** `list[str]`

**Default:** `[]` (all categories enabled)

**Valid values:**

| Value | What it controls |
|---|---|
| `"mock_classes"` | `Mock()`, `MagicMock()`, `AsyncMock()`, `PropertyMock()`, etc. instantiations |
| `"patch"` | `@patch` decorators, `patch()` calls, `with patch(...):` context managers |
| `"fixtures"` | `mocker` and `monkeypatch` pytest fixture arguments |

**Example — disable fixture detection only:**

```toml
[tool.mockbuster]
disable = ["fixtures"]
```

**Example — disable multiple categories:**

```toml
[tool.mockbuster]
disable = ["mock_classes", "patch"]
```

---

## CLI override

The `--disable` flag mirrors the config option and can be repeated. CLI flags are merged with any `pyproject.toml` config — you can add more disabled categories at runtime but cannot re-enable ones disabled in config.

```bash
mockbuster tests/ --disable patch
mockbuster tests/ --disable mock_classes --disable fixtures
```

See [CLI Reference](cli.md) for full option details.

---

## Config discovery

mockbuster searches for `pyproject.toml` by walking up from the scanned path:

1. If a file is scanned, search starts from its parent directory.
2. If a directory is scanned, search starts from that directory.
3. Walks up through parent directories until `pyproject.toml` is found or the filesystem root is reached.
4. If no `pyproject.toml` is found, or it has no `[tool.mockbuster]` section, all categories are enabled.

---

## Validation

Unknown category names raise a configuration error and exit with code 1:

```
Configuration error: Unknown category 'typo' in pyproject.toml. Valid categories: fixtures, mock_classes, patch
```

The same validation applies to `--disable` CLI flags.

---

## Examples

### Allow `monkeypatch` for environment variable setup

Teams that use `monkeypatch.setenv` for environment configuration but want to ban all mock objects:

```toml
[tool.mockbuster]
disable = ["fixtures"]
```

### Gradual adoption: disable everything, enable one category at a time

Start with all categories disabled, then remove entries as you refactor:

```toml
[tool.mockbuster]
disable = ["mock_classes", "patch", "fixtures"]
```

Remove one entry per sprint as you clean up that category.
