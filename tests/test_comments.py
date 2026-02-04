"""Tests for mockbuster comment parsing."""

from mockbuster.comments import extract_ignored_lines


def test_extract_same_line_ignore() -> None:
    """Test basic same-line ignore comment."""
    code = "from unittest.mock import Mock  # mockbuster: ignore"
    result = extract_ignored_lines(code)
    assert 1 in result, "Same-line ignore should mark line 1"
    assert len(result) == 1, "Should only mark one line"


def test_extract_previous_line_ignore() -> None:
    """Test comment before import statement."""
    code = "# mockbuster: ignore\nfrom unittest.mock import Mock"
    result = extract_ignored_lines(code)
    assert 2 in result, "Previous-line ignore should mark line 2"
    assert 1 in result, "Comment line itself should also be marked"


def test_extract_multiple_ignores() -> None:
    """Test multiple ignore comments in same file."""
    code = """# mockbuster: ignore
from unittest.mock import Mock

from unittest.mock import patch  # mockbuster: ignore

def test_foo(mocker):  # mockbuster: ignore
    pass
"""
    result = extract_ignored_lines(code)
    assert 1 in result, "First comment line should be marked"
    assert 2 in result, "First import should be marked"
    assert 4 in result, "Second import should be marked"
    assert 6 in result, "Function def should be marked"


def test_extract_case_insensitive() -> None:
    """Test case-insensitive pattern matching."""
    code = """from unittest.mock import Mock  # MOCKBUSTER: IGNORE
from unittest.mock import patch  # MockBuster: Ignore
from unittest.mock import MagicMock  # mockbuster: ignore
"""
    result = extract_ignored_lines(code)
    assert 1 in result, "Uppercase should work"
    assert 2 in result, "Mixed case should work"
    assert 3 in result, "Lowercase should work"


def test_extract_whitespace_variations() -> None:
    """Test flexible whitespace handling."""
    code = """from unittest.mock import Mock  #mockbuster:ignore
from unittest.mock import patch  #  mockbuster:  ignore
from unittest.mock import MagicMock  # mockbuster : ignore
"""
    result = extract_ignored_lines(code)
    assert 1 in result, "No spaces should work"
    assert 2 in result, "Multiple spaces should work"
    assert 3 in result, "Space before colon should work"


def test_extract_no_ignores() -> None:
    """Test file with no ignore comments."""
    code = """from unittest.mock import Mock
from unittest.mock import patch
# Some other comment
"""
    result = extract_ignored_lines(code)
    assert len(result) == 0, "Should return empty set"
    assert isinstance(result, set), "Should return a set"


def test_extract_partial_match_rejected() -> None:
    """Test that partial matches are rejected."""
    code = """from unittest.mock import Mock  # mockbuster:ignoreme
from unittest.mock import patch  # mockbuster ignore
from unittest.mock import MagicMock  # mock buster: ignore
"""
    result = extract_ignored_lines(code)
    assert len(result) == 0, "Partial matches should not be recognized"


def test_extract_multiline_import_ignore() -> None:
    """Test previous-line ignore with multi-line import."""
    code = """# mockbuster: ignore
from unittest.mock import (
    Mock,
    MagicMock,
    patch,
)
"""
    result = extract_ignored_lines(code)
    assert 1 in result, "Comment line should be marked"
    assert 2 in result, "First line of import should be marked"


def test_extract_empty_code() -> None:
    """Test empty string input."""
    result = extract_ignored_lines("")
    assert len(result) == 0, "Empty code should return empty set"
    assert isinstance(result, set), "Should return a set"


def test_extract_syntax_error_graceful() -> None:
    """Test graceful handling of syntax errors."""
    code = """from unittest.mock import Mock  # mockbuster: ignore
def broken(
"""
    result = extract_ignored_lines(code)
    assert isinstance(result, set), "Should return a set even on error"


def test_extract_comment_in_string_not_matched() -> None:
    """Test that comment-like strings are not matched."""
    code = '''x = "# mockbuster: ignore"
y = """
# mockbuster: ignore
"""
'''
    result = extract_ignored_lines(code)
    assert len(result) == 0, "Strings should not be treated as comments"


def test_extract_ignore_with_blank_lines() -> None:
    """Test previous-line ignore with blank lines between."""
    code = """# mockbuster: ignore

from unittest.mock import Mock
"""
    result = extract_ignored_lines(code)
    assert 1 in result, "Comment line should be marked"
    assert 3 in result, "Import after blank line should be marked"
