from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

VALID_CATEGORIES: frozenset[str] = frozenset({"mock_classes", "patch", "fixtures"})


@dataclass
class MockbusterConfig:
    disabled_categories: frozenset[str] = field(default_factory=frozenset)


def load_config(start_dir: Path | None = None) -> MockbusterConfig:
    """Load mockbuster configuration from pyproject.toml.

    Walks up from start_dir until a pyproject.toml is found.

    Args:
        start_dir: Directory to start searching from. Defaults to cwd.

    Returns:
        MockbusterConfig with disabled_categories populated from config.

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

            section = data.get("tool", {}).get("mockbuster", {})
            if not section:
                return MockbusterConfig()

            disable_list = section.get("disable", [])
            assert isinstance(disable_list, list), "tool.mockbuster.disable must be a list"

            for name in disable_list:
                if name not in VALID_CATEGORIES:
                    raise ValueError(
                        f"Unknown category '{name}' in pyproject.toml. "
                        f"Valid categories: {', '.join(sorted(VALID_CATEGORIES))}"
                    )

            return MockbusterConfig(disabled_categories=frozenset(disable_list))

    return MockbusterConfig()
