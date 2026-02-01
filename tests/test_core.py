from mockbuster.core import detect_mocks


def test_detect_mocks_unittest_mock():
    code = """
from unittest.mock import Mock

def test_foo():
    mock_obj = Mock()
"""
    violations = detect_mocks(code)
    assert len(violations) == 1
    assert violations[0]["line"] == 2


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
    assert violations[0]["line"] == 2


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
    assert violations[0]["line"] == 2


def test_detect_mocks_old_mock_library():
    code = """
import mock

def test_foo():
    m = mock.Mock()
"""
    violations = detect_mocks(code)
    assert len(violations) == 1
    assert violations[0]["line"] == 2


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
    pass
"""
    violations = detect_mocks(code)
    assert len(violations) == 1
    assert violations[0]["line"] == 2


def test_detect_mocks_mocker_fixture_only():
    code = """
def test_foo(mocker):
    mocker.patch('something')
"""
    violations = detect_mocks(code)
    assert len(violations) == 1
    assert violations[0]["line"] == 2
    assert "mocker" in violations[0]["message"]


def test_detect_mocks_no_false_positive_on_mockbuster():
    code = """
from mockbuster import detect_mocks

def test_foo():
    violations = detect_mocks("code")
"""
    violations = detect_mocks(code)
    assert len(violations) == 0
