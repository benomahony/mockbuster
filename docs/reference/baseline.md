# Baseline Reference

The baseline feature lets teams adopt mockbuster on an existing codebase without having to fix every violation immediately. A baseline file records the current violation counts; future runs only report violations that exceed those counts.

## Quick start

```bash
# 1. Record all current violations as the baseline
mockbuster tests/ --update-baseline

# 2. Commit the baseline file alongside your code
git add .mockbuster-baseline.json && git commit -m "Add mockbuster baseline"

# 3. From now on, only new violations are reported
mockbuster tests/
```

---

## Baseline file

The baseline is stored as `.mockbuster-baseline.json` in the same directory as your `pyproject.toml`. It tracks violation counts per file per category:

```json
{
  "tests/test_payments.py": {
    "mock_classes": 3,
    "patch": 1
  },
  "tests/test_users.py": {
    "fixtures": 2
  }
}
```

Commit this file to version control so all team members share the same baseline.

---

## How it works

On a normal run mockbuster loads the baseline and, for each file, suppresses up to the baselined count per category. Violations beyond the recorded count are reported as new.

| Actual count vs baseline | Behaviour |
|---|---|
| Equal to baseline | All suppressed — no output for this file |
| Exceeds baseline | Excess violations reported |
| Less than baseline (fixed some) | Silently absorbed — baseline is stale, run `--update-baseline` to shrink it |

---

## CLI flags

### `--update-baseline`

Scan all files, record the current violation counts as the new baseline, and exit 0. Use this after fixing violations to shrink the baseline, or when first adopting mockbuster.

```bash
mockbuster tests/ --update-baseline
```

Output:
```
Baseline written: 14 violation(s) across 3 file(s) suppressed.
```

### `--no-baseline`

Ignore the baseline file for this run and report all violations. Useful for auditing the full state of the codebase.

```bash
mockbuster tests/ --no-baseline
```

---

## Configuration

Override the baseline file path in `pyproject.toml`:

```toml
[tool.mockbuster]
baseline = "config/.mockbuster-baseline.json"
```

The path is relative to the directory containing `pyproject.toml`. The default is `.mockbuster-baseline.json` next to `pyproject.toml`.

---

## Gradual adoption workflow

1. Run `mockbuster tests/ --update-baseline` to suppress all existing violations.
2. Commit `.mockbuster-baseline.json`.
3. Add `mockbuster tests/ --strict` to CI — it will only fail on **new** violations.
4. Refactor files one by one to remove mock usage.
5. After fixing a file, re-run `--update-baseline` to shrink the baseline (or remove the file's entry manually).
6. Once the baseline is empty (`{}`), remove it and run without `--update-baseline` for full enforcement.

---

## See Also

- [CLI Reference](cli.md) — all options
- [Configuration](configuration.md) — `pyproject.toml` options
- [CI Integration](../howto/ci-integration.md) — using the baseline in CI
