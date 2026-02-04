"""Comment parsing for mockbuster ignore directives."""

import io
import re
import tokenize


def extract_ignored_lines(code: str) -> set[int]:
    """Extract line numbers that should be ignored based on comments.

    Uses Python's tokenize module to parse comments and identify
    lines with # mockbuster: ignore directives.

    Args:
        code: Python source code to analyze

    Returns:
        Set of line numbers to ignore (1-indexed)
    """
    assert code is not None, "Code must not be None"
    assert isinstance(code, str), "Code must be a string"

    if not code:
        return set()

    ignored_lines: set[int] = set()
    pattern = r"#\s*mockbuster\s*:\s*ignore\b"
    standalone_comment_line: int | None = None
    last_line_with_code: int | None = None

    try:
        tokens = tokenize.generate_tokens(io.StringIO(code).readline)
        for token in tokens:
            assert token is not None, "Token must not be None"
            assert hasattr(token, "type"), "Token must have type attribute"

            if token.type == tokenize.COMMENT:
                if re.search(pattern, token.string, re.IGNORECASE):
                    comment_line = token.start[0]
                    ignored_lines.add(comment_line)
                    # Check if this is a standalone comment (no code before it on same line)
                    if last_line_with_code != comment_line:
                        standalone_comment_line = comment_line
            elif token.type not in (
                tokenize.NEWLINE,
                tokenize.NL,
                tokenize.INDENT,
                tokenize.DEDENT,
                tokenize.ENCODING,
                tokenize.COMMENT,
            ):
                # Non-whitespace token (actual code)
                last_line_with_code = token.start[0]
                # If previous comment was standalone, mark this line
                if standalone_comment_line is not None:
                    ignored_lines.add(token.start[0])
                    standalone_comment_line = None

    except tokenize.TokenError:
        # Handle incomplete or invalid syntax gracefully
        return set()

    return ignored_lines
