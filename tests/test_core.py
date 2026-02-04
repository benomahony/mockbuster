from mockbuster.core import detect_mocks


def test_detect_mocks_unittest_mock():
    code = """
from unittest.mock import Mock

def test_foo():
    mock_obj = Mock()
"""
    violations = detect_mocks(code)
    assert len(violations) == 1
    assert violations[0]["line"] == 5  # Detects usage, not import
    assert "Mock()" in violations[0]["message"]


def test_detect_mocks_clean_code():
    code = """
def test_clean():
    result = 1 + 1
    assert result == 2
"""
    violations = detect_mocks(code)
    assert len(violations) == 0


def test_detect_mocks_magic_mock():
    code = """
from unittest.mock import MagicMock

def test_foo():
    magic = MagicMock()
"""
    violations = detect_mocks(code)
    assert len(violations) == 1
    assert violations[0]["line"] == 5  # Detects usage, not import
    assert "MagicMock()" in violations[0]["message"]


def test_detect_mocks_async_mock():
    code = """
from unittest.mock import AsyncMock

async def test_foo():
    mock = AsyncMock()
"""
    violations = detect_mocks(code)
    assert len(violations) == 1


def test_detect_mocks_patch_decorator():
    code = """
from unittest.mock import patch

@patch('some.module')
def test_foo(mock_module):
    pass
"""
    violations = detect_mocks(code)
    assert len(violations) == 1
    assert violations[0]["line"] == 4  # Detects decorator usage, not import
    assert "patch" in violations[0]["message"]


def test_detect_mocks_old_mock_library():
    code = """
import mock

def test_foo():
    m = mock.Mock()
"""
    violations = detect_mocks(code)
    assert len(violations) == 1
    assert violations[0]["line"] == 5  # Detects usage, not import
    assert "Mock()" in violations[0]["message"]


def test_detect_mocks_pytest_mock_import():
    code = """
import pytest_mock

def test_foo(mocker):
    mocker.patch('something')
"""
    violations = detect_mocks(code)
    # Should detect both the import and the mocker fixture
    assert len(violations) == 2


def test_detect_mocks_multiple_imports():
    code = """
from unittest.mock import Mock, patch, MagicMock

def test_foo():
    m = Mock()
"""
    violations = detect_mocks(code)
    assert len(violations) == 1  # Only detects actual usage
    assert violations[0]["line"] == 5
    assert "Mock()" in violations[0]["message"]


def test_detect_mocks_mocker_fixture_only():
    code = """
def test_foo(mocker):
    mocker.patch('something')
"""
    violations = detect_mocks(code)
    assert len(violations) == 2  # mocker fixture + mocker.patch() call
    assert any(v["line"] == 2 and "mocker" in v["message"] for v in violations)
    assert any(v["line"] == 3 and "patch()" in v["message"] for v in violations)


def test_detect_mocks_no_false_positive_on_mockbuster():
    code = """
from mockbuster import detect_mocks

def test_foo():
    violations = detect_mocks("code")
"""
    violations = detect_mocks(code)
    assert len(violations) == 0


def test_detect_mocks_with_same_line_ignore():
    """Test that same-line ignore comments suppress violations."""
    code = """
from unittest.mock import Mock  # mockbuster: ignore

def test_foo():
    pass
"""
    violations = detect_mocks(code)
    assert len(violations) == 0


def test_detect_mocks_with_previous_line_ignore():
    """Test that previous-line ignore comments suppress multi-line imports."""
    code = """
# mockbuster: ignore
from unittest.mock import (
    Mock,
    MagicMock,
    patch,
)

def test_foo():
    pass
"""
    violations = detect_mocks(code)
    assert len(violations) == 0


def test_detect_mocks_partial_ignore():
    """Test that ignores only affect specific lines."""
    code = """
import unittest.mock

def test_foo():
    m = Mock()  # mockbuster: ignore

def test_bar():
    p = unittest.mock.patch('module')
"""
    violations = detect_mocks(code)
    assert len(violations) == 1
    assert violations[0]["line"] == 8  # patch() call not ignored
    assert "patch()" in violations[0]["message"]


def test_detect_mocks_respect_ignores_false():
    """Test that violations are still reported when respect_ignores=False."""
    code = """
def test_foo():
    m = Mock()  # mockbuster: ignore
"""
    violations = detect_mocks(code, respect_ignores=False)
    assert len(violations) == 1
    assert violations[0]["line"] == 3
    assert "Mock()" in violations[0]["message"]


def test_detect_mocks_mocker_fixture_ignore():
    """Test that mocker fixture can be ignored."""
    code = """
def test_with_mocker(mocker):  # mockbuster: ignore
    pass
"""
    violations = detect_mocks(code)
    assert len(violations) == 0


def test_detect_mocks_ignore_only_target_line():
    """Test that ignore comments don't affect other lines."""
    code = """
from unittest.mock import Mock  # mockbuster: ignore

def test_foo(mocker):
    pass
"""
    violations = detect_mocks(code)
    assert len(violations) == 1
    assert violations[0]["line"] == 4
    assert "mocker" in violations[0]["message"]


def test_detect_mocks_monkeypatch_fixture():
    """Test detection of monkeypatch fixture."""
    code = """
def test_foo(monkeypatch):
    monkeypatch.setattr(module, "func", fake_func)
"""
    violations = detect_mocks(code)
    assert len(violations) == 1
    assert violations[0]["line"] == 2
    assert "monkeypatch" in violations[0]["message"]


def test_detect_mocks_monkeypatch_with_other_fixtures():
    """Test monkeypatch detection with other fixtures."""
    code = """
def test_foo(monkeypatch, tmp_path):
    monkeypatch.setenv("VAR", "value")
"""
    violations = detect_mocks(code)
    assert len(violations) == 1
    assert "monkeypatch" in violations[0]["message"]


def test_detect_mocks_both_mocker_and_monkeypatch():
    """Test detection of both mocker and monkeypatch."""
    code = """
def test_foo(mocker, monkeypatch):
    pass
"""
    violations = detect_mocks(code)
    assert len(violations) == 2
    assert all(v["line"] == 2 for v in violations)
    messages = " ".join(v["message"] for v in violations)
    assert "mocker" in messages
    assert "monkeypatch" in messages
