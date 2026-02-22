import os
from pathlib import Path

import typer
from rich.console import Console

from mockbuster.baseline import build_baseline, filter_baselined, load_baseline, write_baseline
from mockbuster.config import VALID_CATEGORIES, load_config
from mockbuster.core import detect_mocks

app = typer.Typer(
    help="Lint and detect mocking usage in Python tests",
    context_settings={"help_option_names": ["-h", "--help"]},
)
console = Console()


def _validate_categories(merged: frozenset[str] | set[str]) -> None:
    assert VALID_CATEGORIES, "VALID_CATEGORIES must not be empty"
    assert isinstance(merged, (frozenset, set)), "merged must be a set or frozenset"
    unknown = merged - VALID_CATEGORIES
    if unknown:
        console.print(
            f"[red]Error: Unknown category '{next(iter(unknown))}'. "
            f"Valid categories: {', '.join(sorted(VALID_CATEGORIES))}[/red]"
        )
        raise typer.Exit(1)


def _collect_files(effective_paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for p in effective_paths:
        assert p.exists(), f"Path does not exist: {p}"
        assert os.access(p, os.R_OK), f"Path is not readable: {p}"
        if p.is_file():
            files.append(p)
        elif p.is_dir():
            files.extend(sorted(p.rglob("*.py")))
        else:
            console.print(f"[red]Error: {p} is not a valid file or directory[/red]")
            raise typer.Exit(1)
    return files


def _collect_violations(
    files: list[Path], disabled_categories: frozenset[str]
) -> dict[str, list[dict]]:
    assert isinstance(files, list), "files must be a list"
    assert isinstance(disabled_categories, frozenset), "disabled_categories must be a frozenset"
    violations_by_file: dict[str, list[dict]] = {}
    for file in files:
        code = file.read_text()
        violations = detect_mocks(code, disabled_categories=disabled_categories)
        if violations:
            violations_by_file[str(file)] = violations
    return violations_by_file


def _handle_update_baseline(
    violations_by_file: dict[str, list[dict]], files: list[Path], baseline_path: Path
) -> None:
    assert isinstance(violations_by_file, dict), "violations_by_file must be a dict"
    assert isinstance(baseline_path, Path), "baseline_path must be a Path"
    baseline_data = build_baseline(violations_by_file)
    existing = load_baseline(baseline_path)
    scanned_keys = {str(f) for f in files}
    for file_key, counts in existing.items():
        if file_key not in scanned_keys:
            baseline_data[file_key] = counts
    write_baseline(baseline_data, baseline_path)
    total = sum(sum(counts.values()) for counts in baseline_data.values())
    console.print(
        f"[green]Baseline written: {total} violation(s) across "
        f"{len(baseline_data)} file(s) suppressed.[/green]"
    )


def _report_violations(
    violations_by_file: dict[str, list[dict]],
    baseline: dict,
    strict: bool,
) -> None:
    assert isinstance(violations_by_file, dict), "violations_by_file must be a dict"
    assert isinstance(baseline, dict), "baseline must be a dict"
    total_violations = 0
    total_suppressed = 0
    for file_key, violations in violations_by_file.items():
        if baseline:
            visible, suppressed = filter_baselined(violations, file_key, baseline)
            total_suppressed += suppressed
        else:
            visible = violations
        if visible:
            console.print(f"\n[yellow]{file_key}[/yellow]")
            for violation in visible:
                console.print(f"  Line {violation['line']}: {violation['message']}")
                total_violations += 1
    if total_violations > 0:
        suppressed_note = f"  [{total_suppressed} baselined]" if total_suppressed else ""
        console.print(f"\n[red]Found {total_violations} mock usage(s){suppressed_note}[/red]")
        if strict:
            raise typer.Exit(1)
    elif total_suppressed > 0:
        console.print(
            f"[green]No new mocking usage detected[/green] "
            f"[dim]({total_suppressed} baselined)[/dim]"
        )
    else:
        console.print("[green]No mocking usage detected[/green]")


@app.command()
def scan(
    paths: list[Path] | None = typer.Argument(default=None, help="Files or directories to scan"),
    strict: bool = typer.Option(False, "--strict", help="Exit with error code if mocks found"),
    disable: list[str] = typer.Option(
        [],
        "--disable",
        help="Disable a category (mock_classes, patch, fixtures). Repeatable.",
    ),
    update_baseline: bool = typer.Option(
        False,
        "--update-baseline",
        help="Record all current violations as the baseline and exit.",
    ),
    no_baseline: bool = typer.Option(
        False,
        "--no-baseline",
        help="Ignore the baseline file and report all violations.",
    ),
) -> None:
    """Scan Python files for mocking usage."""
    try:
        config = load_config(start_dir=Path.cwd())
    except ValueError as e:
        console.print(f"[red]Configuration error: {e}[/red]")
        raise typer.Exit(1)

    merged = config.disabled_categories | set(disable)
    _validate_categories(merged)

    disabled_categories = frozenset(merged)
    assert disabled_categories.issubset(VALID_CATEGORIES), "all disabled categories must be valid"
    effective_paths = paths if paths else [config.default_path]
    assert effective_paths, "at least one path must be provided"
    files = _collect_files(effective_paths)
    violations_by_file = _collect_violations(files, disabled_categories)

    if update_baseline:
        _handle_update_baseline(violations_by_file, files, config.baseline_path)
        return

    baseline = {} if no_baseline else load_baseline(config.baseline_path)
    _report_violations(violations_by_file, baseline, strict)


if __name__ == "__main__":
    app()
