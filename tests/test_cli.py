from pathlib import Path

from typer.testing import CliRunner

from mockbuster.cli import app

runner = CliRunner()


def test_scan_file_with_mocks(tmp_path: Path):
    test_file = tmp_path / "test_mocks.py"
    test_file.write_text("""
from unittest.mock import Mock

def test_foo():
    mock_obj = Mock()
""")

    result = runner.invoke(app, [str(test_file)])
    assert result.exit_code == 0
    assert "unittest.mock" in result.stdout


def test_scan_file_clean(tmp_path: Path):
    test_file = tmp_path / "test_clean.py"
    test_file.write_text("""
def test_foo():
    assert 1 + 1 == 2
""")

    result = runner.invoke(app, [str(test_file)])
    assert result.exit_code == 0
    assert "No mocking" in result.stdout


def test_scan_strict_mode(tmp_path: Path):
    test_file = tmp_path / "test_mocks.py"
    test_file.write_text("""
from unittest.mock import patch

@patch('some.module')
def test_bar():
    pass
""")

    result = runner.invoke(app, [str(test_file), "--strict"])
    assert result.exit_code == 1
    assert "Found" in result.stdout
