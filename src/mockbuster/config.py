from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from mockbuster.baseline import DEFAULT_BASELINE_FILENAME

VALID_CATEGORIES: frozenset[str] = frozenset({"mock_classes", "patch", "fixtures"})


@dataclass
class MockbusterConfig:
    disabled_categories: frozenset[str] = field(default_factory=frozenset)
    baseline_path: Path = field(default_factory=lambda: Path(DEFAULT_BASELINE_FILENAME))
    default_path: Path = field(default_factory=lambda: Path("tests/"))


def load_config(start_dir: Path | None = None) -> MockbusterConfig:
    """Load mockbuster configuration from pyproject.toml.

    Walks up from start_dir until a pyproject.toml is found.

    Args:
        start_dir: Directory to start searching from. Defaults to cwd.

    Returns:
        MockbusterConfig populated from config.

    Raises:
        ValueError: If an unknown category name is found in the config.
    """
    search_dir = start_dir if start_dir is not None else Path.cwd()
    assert isinstance(search_dir, Path), "start_dir must be a Path"

    for directory in [search_dir, *search_dir.parents]:
        pyproject = directory / "pyproject.toml"
        if pyproject.exists():
            with pyproject.open("rb") as f:
                data = tomllib.load(f)

            # Always resolve to an absolute path so the baseline lands next to
            # pyproject.toml regardless of where the scan path is.
            pyproject_dir = directory.resolve()

            section = data.get("tool", {}).get("mockbuster", {})
            if not section:
                return MockbusterConfig(
                    baseline_path=pyproject_dir / DEFAULT_BASELINE_FILENAME,
                )

            disable_list = section.get("disable", [])
            assert isinstance(disable_list, list), "tool.mockbuster.disable must be a list"

            for name in disable_list:
                if name not in VALID_CATEGORIES:
                    raise ValueError(
                        f"Unknown category '{name}' in pyproject.toml. "
                        f"Valid categories: {', '.join(sorted(VALID_CATEGORIES))}"
                    )

            baseline_str = section.get("baseline", DEFAULT_BASELINE_FILENAME)
            assert isinstance(baseline_str, str), "tool.mockbuster.baseline must be a string"
            baseline_path = pyproject_dir / baseline_str

            path_str = section.get("path", "tests/")
            assert isinstance(path_str, str), "tool.mockbuster.path must be a string"
            default_path = Path(path_str)

            return MockbusterConfig(
                disabled_categories=frozenset(disable_list),
                baseline_path=baseline_path,
                default_path=default_path,
            )

    return MockbusterConfig(baseline_path=search_dir.resolve() / DEFAULT_BASELINE_FILENAME)
