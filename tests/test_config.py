from pathlib import Path

import pytest

from mockbuster.config import load_config


@pytest.mark.parametrize(
    "disable_list,expected",
    [
        ([], frozenset()),
        (["fixtures"], frozenset({"fixtures"})),
        (["mock_classes", "patch"], frozenset({"mock_classes", "patch"})),
        (["mock_classes", "patch", "fixtures"], frozenset({"mock_classes", "patch", "fixtures"})),
    ],
)
def test_load_config_disable(tmp_path, disable_list, expected):
    pyproject = tmp_path / "pyproject.toml"
    if disable_list:
        items = ", ".join(f'"{item}"' for item in disable_list)
        pyproject.write_text(f"[tool.mockbuster]\ndisable = [{items}]\n")
    else:
        pyproject.write_text("[tool.mockbuster]\ndisable = []\n")

    config = load_config(start_dir=tmp_path)
    assert config.disabled_categories == expected


@pytest.mark.parametrize("bad_name", ["mocks", "PATCH", "unknown", "monkeypatch"])
def test_load_config_invalid_category_raises(tmp_path, bad_name):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(f'[tool.mockbuster]\ndisable = ["{bad_name}"]\n')

    with pytest.raises(ValueError, match=bad_name):
        load_config(start_dir=tmp_path)


def test_load_config_no_pyproject(tmp_path):
    config = load_config(start_dir=tmp_path)
    assert config.disabled_categories == frozenset()
    assert config.baseline_path == tmp_path / ".mockbuster-baseline.json"


def test_load_config_pyproject_without_mockbuster_section(tmp_path):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("[tool.ruff]\nline-length = 88\n")

    config = load_config(start_dir=tmp_path)
    assert config.disabled_categories == frozenset()
    assert config.baseline_path == tmp_path / ".mockbuster-baseline.json"


def test_load_config_found_by_walking_up(tmp_path):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[tool.mockbuster]\ndisable = ["fixtures"]\n')

    subdir = tmp_path / "tests" / "unit"
    subdir.mkdir(parents=True)

    config = load_config(start_dir=subdir)
    assert config.disabled_categories == frozenset({"fixtures"})


def test_load_config_default_path_fallback(tmp_path):
    """When path key is absent, default_path falls back to tests/."""
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("[tool.mockbuster]\n")

    config = load_config(start_dir=tmp_path)
    assert config.default_path == Path("tests/")


def test_load_config_custom_path(tmp_path):
    """path key in pyproject.toml is stored as a relative Path."""
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[tool.mockbuster]\npath = "test/"\n')

    config = load_config(start_dir=tmp_path)
    assert config.default_path == Path("test/")


def test_load_config_no_section_default_path(tmp_path):
    """No [tool.mockbuster] section → default_path is tests/."""
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("[tool.ruff]\nline-length = 88\n")

    config = load_config(start_dir=tmp_path)
    assert config.default_path == Path("tests/")
