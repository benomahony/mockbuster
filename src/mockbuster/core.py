import ast

from mockbuster.comments import extract_ignored_lines

MOCK_CLASSES = {
    "Mock",
    "MagicMock",
    "AsyncMock",
    "PropertyMock",
    "NonCallableMock",
    "NonCallableMagicMock",
}

PATCH_FUNCTIONS = {
    "patch",
}


def _get_mock_class_name(node: ast.expr) -> str | None:
    """Extract mock class name from a Call node.

    Args:
        node: AST node representing the function being called

    Returns:
        Mock class name if detected, None otherwise
    """
    assert node is not None, "Node must not be None"
    assert isinstance(node, ast.expr), "Node must be an expression"

    if isinstance(node, ast.Name) and node.id in MOCK_CLASSES:
        return node.id

    if isinstance(node, ast.Attribute):
        if node.attr in MOCK_CLASSES:
            return node.attr

    return None


def _get_patch_name(node: ast.expr) -> str | None:
    """Extract patch function name from any AST node.

    Handles decorators, context managers, and function calls uniformly.

    Args:
        node: AST node (Name, Attribute, or Call)

    Returns:
        Patch function name if detected, None otherwise
    """
    assert node is not None, "Node must not be None"
    assert isinstance(node, ast.expr), "Node must be an expression"

    if isinstance(node, ast.Name) and node.id in PATCH_FUNCTIONS:
        return node.id

    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name) and node.func.id in PATCH_FUNCTIONS:
            return node.func.id
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name) and node.func.value.id in PATCH_FUNCTIONS:
                return f"{node.func.value.id}.{node.func.attr}"
            if node.func.attr in PATCH_FUNCTIONS:
                return node.func.attr

    if isinstance(node, ast.Attribute):
        if isinstance(node.value, ast.Name) and node.value.id in PATCH_FUNCTIONS:
            return f"{node.value.id}.{node.attr}"
        if node.attr in PATCH_FUNCTIONS:
            return node.attr

    return None


def _check_function_args(node: ast.FunctionDef, violations: list[dict[str, str | int]]) -> None:
    """Check function arguments for mocker/monkeypatch fixtures."""
    assert isinstance(node.args.args, list), "Function args must be a list"
    assert all(hasattr(arg, "arg") for arg in node.args.args), "All args must have arg attribute"

    for arg in node.args.args:
        if arg.arg == "mocker":
            assert node.lineno > 0, "Line number must be positive"
            assert isinstance(arg.arg, str), "Argument name must be a string"
            msg = (
                "pytest-mock 'mocker' fixture detected - "
                "Use real objects, dependency injection, or integration tests"
            )
            violations.append({"line": node.lineno, "message": msg})
        elif arg.arg == "monkeypatch":
            assert node.lineno > 0, "Line number must be positive"
            assert isinstance(arg.arg, str), "Argument name must be a string"
            msg = (
                "pytest 'monkeypatch' fixture detected - "
                "Use real objects, dependency injection, or integration tests"
            )
            violations.append({"line": node.lineno, "message": msg})


def _check_decorators(
    node: ast.FunctionDef, violations: list[dict[str, str | int]], processed_calls: set[int]
) -> None:
    """Check decorators for patch usage."""
    assert isinstance(node.decorator_list, list), "Decorator list must be a list"
    assert isinstance(processed_calls, set), "Processed calls must be a set"

    for decorator in node.decorator_list:
        patch_name = _get_patch_name(decorator)
        if patch_name:
            assert decorator.lineno > 0, "Decorator line number must be positive"
            assert isinstance(patch_name, str) and len(patch_name) > 0, (
                "Patch name must be non-empty string"
            )
            msg = (
                f"@{patch_name} decorator detected - "
                "Use real objects, dependency injection, or integration tests"
            )
            violations.append({"line": decorator.lineno, "message": msg})
            if isinstance(decorator, ast.Call):
                call_id = id(decorator)
                assert call_id not in processed_calls, "Call ID should not be already processed"
                processed_calls.add(call_id)


def _check_calls(
    node: ast.Call, violations: list[dict[str, str | int]], processed_calls: set[int]
) -> None:
    """Check function calls for mock/patch usage."""
    assert hasattr(node, "func"), "Call node must have func attribute"
    assert isinstance(processed_calls, set), "Processed calls must be a set"

    if id(node) in processed_calls:
        return

    mock_class = _get_mock_class_name(node.func)
    if mock_class:
        assert node.lineno > 0, "Call line number must be positive"
        assert isinstance(mock_class, str) and len(mock_class) > 0, (
            "Mock class name must be non-empty string"
        )
        msg = (
            f"{mock_class}() instantiation detected - "
            "Use real objects, dependency injection, or integration tests"
        )
        violations.append({"line": node.lineno, "message": msg})
    elif isinstance(node.func, ast.Attribute):
        patch_name = _get_patch_name(node.func)
        if patch_name:
            assert node.lineno > 0, "Call line number must be positive"
            assert isinstance(patch_name, str) and len(patch_name) > 0, (
                "Patch name must be non-empty string"
            )
            msg = (
                f"{patch_name}() call detected - "
                "Use real objects, dependency injection, or integration tests"
            )
            violations.append({"line": node.lineno, "message": msg})


def _check_with_statements(
    node: ast.With, violations: list[dict[str, str | int]], processed_calls: set[int]
) -> None:
    """Check with statements for patch context managers."""
    assert isinstance(node.items, list), "With items must be a list"
    assert len(node.items) > 0, "With statement must have at least one context manager"

    for item in node.items:
        patch_name = _get_patch_name(item.context_expr)
        if patch_name:
            assert item.context_expr.lineno > 0, "Context manager line number must be positive"
            assert isinstance(patch_name, str) and len(patch_name) > 0, (
                "Patch name must be non-empty string"
            )
            msg = (
                f"{patch_name}() context manager detected - "
                "Use real objects, dependency injection, or integration tests"
            )
            violations.append({"line": item.context_expr.lineno, "message": msg})
            if isinstance(item.context_expr, ast.Call):
                call_id = id(item.context_expr)
                assert call_id not in processed_calls, "Call ID should not be already processed"
                processed_calls.add(call_id)


def detect_mocks(code: str, *, respect_ignores: bool = True) -> list[dict[str, str | int]]:
    """Detect mocking usage in Python code.

    Args:
        code: Python source code to analyze
        respect_ignores: Whether to respect mockbuster: ignore comments

    Returns:
        List of violations with line numbers and messages
    """
    assert code is not None, "Code must not be None"
    assert isinstance(code, str), "Code must be a string"

    violations: list[dict[str, str | int]] = []
    processed_calls: set[int] = set()

    try:
        tree = ast.parse(code)
    except SyntaxError:
        return violations

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            _check_function_args(node, violations)
            _check_decorators(node, violations, processed_calls)
        elif isinstance(node, ast.Call):
            _check_calls(node, violations, processed_calls)
        elif isinstance(node, ast.With):
            _check_with_statements(node, violations, processed_calls)

    if respect_ignores:
        ignored_lines = extract_ignored_lines(code)
        assert isinstance(ignored_lines, set), "Ignored lines must be a set"
        assert all(isinstance(line, int) for line in ignored_lines), (
            "All ignored lines must be integers"
        )
        violations = [v for v in violations if v["line"] not in ignored_lines]

    return violations
