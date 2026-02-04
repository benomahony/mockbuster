"""Tests for detecting actual mock usage (not just imports)."""

from mockbuster.core import detect_mocks


def test_detect_mock_instantiation() -> None:
    """Test detection of Mock() instantiation."""
    code = """
def test_foo():
    mock_obj = Mock()
    assert mock_obj.called
"""
    violations = detect_mocks(code)
    assert len(violations) == 1
    assert violations[0]["line"] == 3
    assert "Mock()" in violations[0]["message"]


def test_detect_magic_mock_instantiation() -> None:
    """Test detection of MagicMock() instantiation."""
    code = """
def test_foo():
    magic = MagicMock()
"""
    violations = detect_mocks(code)
    assert len(violations) == 1
    assert violations[0]["line"] == 3
    assert "MagicMock()" in violations[0]["message"]


def test_detect_async_mock_instantiation() -> None:
    """Test detection of AsyncMock() instantiation."""
    code = """
async def test_foo():
    mock = AsyncMock()
"""
    violations = detect_mocks(code)
    assert len(violations) == 1
    assert violations[0]["line"] == 3
    assert "AsyncMock()" in violations[0]["message"]


def test_detect_property_mock_instantiation() -> None:
    """Test detection of PropertyMock() instantiation."""
    code = """
def test_foo():
    prop = PropertyMock()
"""
    violations = detect_mocks(code)
    assert len(violations) == 1
    assert "PropertyMock()" in violations[0]["message"]


def test_detect_patch_decorator() -> None:
    """Test detection of @patch decorator."""
    code = """
@patch('module.function')
def test_foo(mock_func):
    pass
"""
    violations = detect_mocks(code)
    assert len(violations) == 1
    assert violations[0]["line"] == 2
    assert "patch" in violations[0]["message"]


def test_detect_patch_object_decorator() -> None:
    """Test detection of @patch.object decorator."""
    code = """
@patch.object(MyClass, 'method')
def test_foo(mock_method):
    pass
"""
    violations = detect_mocks(code)
    assert len(violations) == 1
    assert "patch" in violations[0]["message"]


def test_detect_multiple_patch_decorators() -> None:
    """Test detection of multiple @patch decorators."""
    code = """
@patch('module.func1')
@patch('module.func2')
def test_foo(mock2, mock1):
    pass
"""
    violations = detect_mocks(code)
    assert len(violations) == 2
    assert violations[0]["line"] == 2
    assert violations[1]["line"] == 3


def test_detect_patch_context_manager() -> None:
    """Test detection of patch as context manager."""
    code = """
def test_foo():
    with patch('module.function'):
        do_something()
"""
    violations = detect_mocks(code)
    assert len(violations) == 1
    assert violations[0]["line"] == 3
    assert "patch" in violations[0]["message"]


def test_detect_patch_object_context_manager() -> None:
    """Test detection of patch.object as context manager."""
    code = """
def test_foo():
    with patch.object(obj, 'attr') as mock_attr:
        do_something()
"""
    violations = detect_mocks(code)
    assert len(violations) == 1
    assert "patch" in violations[0]["message"]


def test_detect_patch_multiple_context_manager() -> None:
    """Test detection of patch.multiple as context manager."""
    code = """
def test_foo():
    with patch.multiple('module', attr1=DEFAULT, attr2=DEFAULT):
        do_something()
"""
    violations = detect_mocks(code)
    assert len(violations) == 1
    assert "patch" in violations[0]["message"]


def test_detect_patch_dict_context_manager() -> None:
    """Test detection of patch.dict as context manager."""
    code = """
def test_foo():
    with patch.dict('os.environ', {'KEY': 'value'}):
        do_something()
"""
    violations = detect_mocks(code)
    assert len(violations) == 1
    assert "patch" in violations[0]["message"]


def test_detect_manual_patch_start() -> None:
    """Test detection of manual patch().start()."""
    code = """
from unittest import mock

def test_foo():
    patcher = mock.patch('module.func')
    mock_func = patcher.start()
"""
    violations = detect_mocks(code)
    # Detects both the import and the patch() call
    assert len(violations) >= 1
    assert any("patch" in v["message"] for v in violations)


def test_detect_unittest_mock_module_usage() -> None:
    """Test detection of unittest.mock.Mock() with module prefix."""
    code = """
import unittest.mock

def test_foo():
    mock = unittest.mock.Mock()
"""
    violations = detect_mocks(code)
    assert len(violations) == 1  # Only detects usage, not import
    assert violations[0]["line"] == 5
    assert "Mock()" in violations[0]["message"]


def test_detect_legacy_mock_usage() -> None:
    """Test detection of mock.Mock() from legacy mock library."""
    code = """
import mock

def test_foo():
    m = mock.Mock()
"""
    violations = detect_mocks(code)
    assert len(violations) == 1  # Only detects usage, not import
    assert violations[0]["line"] == 5
    assert "Mock()" in violations[0]["message"]


def test_detect_mixed_usage() -> None:
    """Test detection of multiple mock usage patterns."""
    code = """
@patch('module.func')
def test_foo(mock_func):
    mock_obj = Mock()
    with patch('other.func'):
        magic = MagicMock()
"""
    violations = detect_mocks(code)
    assert len(violations) == 4  # decorator, Mock(), patch context, MagicMock()


def test_no_false_positive_mock_name() -> None:
    """Test that variables named 'mock' don't trigger detection."""
    code = """
def test_foo():
    mock_data = {'key': 'value'}
    mock = MyClass()
"""
    violations = detect_mocks(code)
    assert len(violations) == 0


def test_no_false_positive_patch_name() -> None:
    """Test that functions named 'patch' don't trigger detection."""
    code = """
def patch(value):
    return value + 1

def test_foo():
    result = patch(5)
"""
    violations = detect_mocks(code)
    assert len(violations) == 0


def test_clean_code_no_violations() -> None:
    """Test that code without mocks has no violations."""
    code = """
def test_foo():
    fake = FakeService()
    result = fake.do_something()
    assert result == "expected"
"""
    violations = detect_mocks(code)
    assert len(violations) == 0
