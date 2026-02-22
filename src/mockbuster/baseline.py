from __future__ import annotations

import json
from pathlib import Path

# {relative_file_path: {category: count}}
BaselineData = dict[str, dict[str, int]]

DEFAULT_BASELINE_FILENAME = ".mockbuster-baseline.json"


def load_baseline(path: Path) -> BaselineData:
    """Load baseline data from a JSON file.

    Args:
        path: Path to the baseline file.

    Returns:
        Baseline data dict, or empty dict if file does not exist.
    """
    assert isinstance(path, Path), "path must be a Path"

    if not path.exists():
        return {}

    with path.open() as f:
        data = json.load(f)

    assert isinstance(data, dict), "Baseline file must contain a JSON object"
    return data


def write_baseline(data: BaselineData, path: Path) -> None:
    """Write baseline data to a JSON file.

    Args:
        data: Baseline data to write.
        path: Destination path.
    """
    assert isinstance(data, dict), "data must be a dict"
    assert isinstance(path, Path), "path must be a Path"

    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def build_baseline(violations_by_file: dict[str, list[dict]]) -> BaselineData:
    """Build baseline data from a scan's violations.

    Args:
        violations_by_file: Mapping of file path strings to their violation lists.
            Each violation must have a "category" key.

    Returns:
        BaselineData with per-file, per-category counts.
    """
    assert isinstance(violations_by_file, dict), "violations_by_file must be a dict"

    baseline: BaselineData = {}
    for file_key, violations in violations_by_file.items():
        assert isinstance(file_key, str), "file keys must be strings"
        assert isinstance(violations, list), "violations must be a list"

        counts: dict[str, int] = {}
        for v in violations:
            assert "category" in v, "Each violation must have a 'category' key"
            category = v["category"]
            assert isinstance(category, str), "category must be a string"
            counts[category] = counts.get(category, 0) + 1

        if counts:
            baseline[file_key] = counts

    return baseline


def filter_baselined(
    violations: list[dict],
    file_key: str,
    baseline: BaselineData,
) -> tuple[list[dict], int]:
    """Separate violations into new (unreported) and suppressed (baselined).

    For each category, violations are allowed up to the baselined count.
    Violations beyond that count are returned as new. If the actual count is
    less than the baseline count the excess allowance is silently absorbed.

    Args:
        violations: All violations for this file (must each have "category").
        file_key: The file path string used as the key in baseline.
        baseline: The loaded baseline data.

    Returns:
        Tuple of (new_violations, suppressed_count).
    """
    assert isinstance(violations, list), "violations must be a list"
    assert isinstance(file_key, str), "file_key must be a string"
    assert isinstance(baseline, dict), "baseline must be a dict"

    file_baseline = baseline.get(file_key, {})
    if not file_baseline:
        return violations, 0

    # Group violations by category, preserving order
    by_category: dict[str, list[dict]] = {}
    for v in violations:
        assert "category" in v, "Each violation must have a 'category' key"
        cat = v["category"]
        by_category.setdefault(cat, []).append(v)

    new_violations: list[dict] = []
    suppressed = 0

    for cat, cat_violations in by_category.items():
        allowed = file_baseline.get(cat, 0)
        suppressed += min(allowed, len(cat_violations))
        new_violations.extend(cat_violations[allowed:])

    # Sort new violations by line number to preserve output order
    new_violations.sort(key=lambda v: v["line"])
    return new_violations, suppressed
