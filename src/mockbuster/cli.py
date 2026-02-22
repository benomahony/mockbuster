import os
from pathlib import Path

import typer
from rich.console import Console

from mockbuster.baseline import build_baseline, filter_baselined, load_baseline, write_baseline
from mockbuster.config import VALID_CATEGORIES, load_config
from mockbuster.core import detect_mocks

app = typer.Typer(
    help="Lint and detect mocking usage in Python tests",
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)
console = Console()

DEFAULT_TESTS_PATH = Path("tests/")


@app.command()
def scan(
    path: Path = typer.Argument(default=DEFAULT_TESTS_PATH, help="File or directory to scan"),
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
    assert path.exists(), f"Path does not exist: {path}"
    assert os.access(path, os.R_OK), f"Path is not readable: {path}"

    start_dir = path if path.is_dir() else path.parent
    try:
        config = load_config(start_dir=start_dir)
    except ValueError as e:
        console.print(f"[red]Configuration error: {e}[/red]")
        raise typer.Exit(1)

    baseline_path = config.baseline_path

    merged = config.disabled_categories | set(disable)
    unknown = merged - VALID_CATEGORIES
    if unknown:
        console.print(
            f"[red]Error: Unknown category '{next(iter(unknown))}'. "
            f"Valid categories: {', '.join(sorted(VALID_CATEGORIES))}[/red]"
        )
        raise typer.Exit(1)

    disabled_categories = frozenset(merged)

    if path.is_file():
        files = [path]
    elif path.is_dir():
        files = sorted(path.rglob("*.py"))
    else:
        console.print(f"[red]Error: {path} is not a valid file or directory[/red]")
        raise typer.Exit(1)

    # Collect all violations keyed by path string
    violations_by_file: dict[str, list[dict]] = {}
    for file in files:
        code = file.read_text()
        violations = detect_mocks(code, disabled_categories=disabled_categories)
        if violations:
            file_key = str(file)
            violations_by_file[file_key] = violations

    # --update-baseline: write and exit
    if update_baseline:
        baseline_data = build_baseline(violations_by_file)

        # Preserve entries for files outside the current scan so that running
        # --update-baseline on a subpath does not wipe the rest of the baseline.
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
        return

    # Load baseline (unless --no-baseline)
    baseline = {} if no_baseline else load_baseline(baseline_path)

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


if __name__ == "__main__":
    app()
