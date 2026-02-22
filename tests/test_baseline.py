import json

import pytest
from typer.testing import CliRunner

from mockbuster.baseline import (
    build_baseline,
    filter_baselined,
    load_baseline,
    write_baseline,
)
from mockbuster.cli import app

runner = CliRunner()


# ---------------------------------------------------------------------------
# build_baseline
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "violations_by_file,expected",
    [
        ({}, {}),
        (
            {"tests/test_foo.py": [{"line": 5, "message": "Mock()", "category": "mock_classes"}]},
            {"tests/test_foo.py": {"mock_classes": 1}},
        ),
        (
            {
                "tests/test_foo.py": [
                    {"line": 5, "message": "Mock()", "category": "mock_classes"},
                    {"line": 8, "message": "Mock()", "category": "mock_classes"},
                    {"line": 12, "message": "@patch", "category": "patch"},
                ]
            },
            {"tests/test_foo.py": {"mock_classes": 2, "patch": 1}},
        ),
        (
            {
                "tests/test_a.py": [{"line": 1, "message": "mocker", "category": "fixtures"}],
                "tests/test_b.py": [{"line": 2, "message": "Mock()", "category": "mock_classes"}],
            },
            {
                "tests/test_a.py": {"fixtures": 1},
                "tests/test_b.py": {"mock_classes": 1},
            },
        ),
    ],
)
def test_build_baseline(violations_by_file, expected):
    assert build_baseline(violations_by_file) == expected


# ---------------------------------------------------------------------------
# filter_baselined
# ---------------------------------------------------------------------------


def test_filter_baselined_suppresses_within_count():
    violations = [
        {"line": 5, "message": "Mock()", "category": "mock_classes"},
        {"line": 8, "message": "Mock()", "category": "mock_classes"},
    ]
    baseline = {"tests/test_foo.py": {"mock_classes": 2}}
    new, suppressed = filter_baselined(violations, "tests/test_foo.py", baseline)
    assert new == []
    assert suppressed == 2


def test_filter_baselined_reports_excess():
    violations = [
        {"line": 5, "message": "Mock()", "category": "mock_classes"},
        {"line": 8, "message": "Mock()", "category": "mock_classes"},
        {"line": 11, "message": "Mock()", "category": "mock_classes"},
    ]
    baseline = {"tests/test_foo.py": {"mock_classes": 2}}
    new, suppressed = filter_baselined(violations, "tests/test_foo.py", baseline)
    assert len(new) == 1
    assert suppressed == 2


def test_filter_baselined_stale_baseline_no_error():
    """When actual count is less than baseline, no violations reported and no error."""
    violations = [{"line": 5, "message": "Mock()", "category": "mock_classes"}]
    baseline = {"tests/test_foo.py": {"mock_classes": 5}}  # stale: baseline says 5, only 1 found
    new, suppressed = filter_baselined(violations, "tests/test_foo.py", baseline)
    assert new == []
    assert suppressed == 1


def test_filter_baselined_no_entry_for_file():
    """File not in baseline → all violations reported."""
    violations = [{"line": 5, "message": "Mock()", "category": "mock_classes"}]
    new, suppressed = filter_baselined(violations, "tests/test_foo.py", {})
    assert new == violations
    assert suppressed == 0


def test_filter_baselined_mixed_categories():
    violations = [
        {"line": 1, "message": "mocker", "category": "fixtures"},
        {"line": 5, "message": "Mock()", "category": "mock_classes"},
        {"line": 8, "message": "Mock()", "category": "mock_classes"},
        {"line": 12, "message": "Mock()", "category": "mock_classes"},
    ]
    baseline = {"tests/test_foo.py": {"fixtures": 1, "mock_classes": 2}}
    new, suppressed = filter_baselined(violations, "tests/test_foo.py", baseline)
    assert len(new) == 1
    assert new[0]["category"] == "mock_classes"
    assert suppressed == 3


# ---------------------------------------------------------------------------
# load / write roundtrip
# ---------------------------------------------------------------------------


def test_load_baseline_missing_file(tmp_path):
    result = load_baseline(tmp_path / "nonexistent.json")
    assert result == {}


def test_write_and_load_roundtrip(tmp_path):
    data = {"tests/test_foo.py": {"mock_classes": 3, "patch": 1}}
    path = tmp_path / ".mockbuster-baseline.json"
    write_baseline(data, path)
    loaded = load_baseline(path)
    assert loaded == data


def test_write_baseline_creates_valid_json(tmp_path):
    data = {"tests/test_foo.py": {"fixtures": 2}}
    path = tmp_path / ".mockbuster-baseline.json"
    write_baseline(data, path)
    raw = json.loads(path.read_text())
    assert raw == data


# ---------------------------------------------------------------------------
# CLI integration
# ---------------------------------------------------------------------------


def _write_py(tmp_path, filename, content):
    f = tmp_path / filename
    f.write_text(content)
    return f


def test_cli_update_baseline_creates_file(tmp_path):
    _write_py(tmp_path, "test_foo.py", "def test_foo():\n    m = Mock()\n")
    result = runner.invoke(app, [str(tmp_path), "--update-baseline"])
    assert result.exit_code == 0
    assert "Baseline written" in result.output
    baseline_file = tmp_path / ".mockbuster-baseline.json"
    assert baseline_file.exists()
    data = json.loads(baseline_file.read_text())
    # At least one file recorded
    assert len(data) >= 1


def test_cli_baseline_suppresses_existing_violations(tmp_path):
    _write_py(tmp_path, "test_foo.py", "def test_foo():\n    m = Mock()\n")

    # First: record baseline
    runner.invoke(app, [str(tmp_path), "--update-baseline"])

    # Second run: violations should be suppressed
    result = runner.invoke(app, [str(tmp_path)])
    assert result.exit_code == 0
    assert "No new mocking usage detected" in result.output
    assert "baselined" in result.output


def test_cli_baseline_reports_new_violation(tmp_path):
    _write_py(tmp_path, "test_foo.py", "def test_foo():\n    m = Mock()\n")

    # Record baseline with 1 Mock()
    runner.invoke(app, [str(tmp_path), "--update-baseline"])

    # Add a second Mock() — should trigger 1 new violation
    _write_py(tmp_path, "test_foo.py", "def test_foo():\n    m = Mock()\ndef test_bar():\n    n = Mock()\n")
    result = runner.invoke(app, [str(tmp_path)])
    assert "Found 1 mock usage(s)" in result.output
    assert "baselined" in result.output


def test_cli_update_baseline_subpath_preserves_other_entries(tmp_path):
    """--update-baseline on a subpath must not wipe baseline entries for other files."""
    unit = tmp_path / "unit"
    integration = tmp_path / "integration"
    unit.mkdir()
    integration.mkdir()

    _write_py(unit, "test_unit.py", "def test_u():\n    m = Mock()\n")
    _write_py(integration, "test_integration.py", "def test_i():\n    m = Mock()\n")

    # Baseline the full directory
    runner.invoke(app, [str(tmp_path), "--update-baseline"])

    baseline_file = tmp_path / ".mockbuster-baseline.json"
    full_data = json.loads(baseline_file.read_text())
    assert len(full_data) == 2

    # Re-baseline only the unit subdir
    runner.invoke(app, [str(unit), "--update-baseline"])

    partial_data = json.loads(baseline_file.read_text())
    # Both files must still be present in the baseline
    assert len(partial_data) == 2


def test_cli_no_baseline_shows_all(tmp_path):
    _write_py(tmp_path, "test_foo.py", "def test_foo():\n    m = Mock()\n")

    # Record baseline
    runner.invoke(app, [str(tmp_path), "--update-baseline"])

    # --no-baseline should report all violations
    result = runner.invoke(app, [str(tmp_path), "--no-baseline"])
    assert "Found" in result.output
    assert "Mock()" in result.output
