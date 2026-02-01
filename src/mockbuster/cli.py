from pathlib import Path

import typer
from rich.console import Console

from mockbuster.core import detect_mocks

app = typer.Typer(
    help="Lint and detect mocking usage in Python tests",
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)
console = Console()


@app.command()
def scan(
    path: Path = typer.Argument(..., help="File or directory to scan"),
    strict: bool = typer.Option(False, "--strict", help="Exit with error code if mocks found"),
) -> None:
    """Scan Python files for mocking usage."""
    assert path is not None, "Path must not be None"
    assert isinstance(path, Path), "Path must be a Path object"

    total_violations = 0

    if path.is_file():
        files = [path]
    elif path.is_dir():
        files = list(path.rglob("*.py"))
    else:
        console.print(f"[red]Error: {path} is not a valid file or directory[/red]")
        raise typer.Exit(1)

    for file in files:
        code = file.read_text()
        violations = detect_mocks(code)

        if violations:
            console.print(f"\n[yellow]{file}[/yellow]")
            for violation in violations:
                console.print(f"  Line {violation['line']}: {violation['message']}")
                total_violations += 1

    if total_violations > 0:
        console.print(f"\n[red]Found {total_violations} mock usage(s)[/red]")
        if strict:
            raise typer.Exit(1)
    else:
        console.print("[green]No mocking usage detected[/green]")


if __name__ == "__main__":
    app()
