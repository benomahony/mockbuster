import ast

# Mock libraries and modules to detect
MOCK_MODULES = {
    "unittest.mock",
    "mock",
    "pytest_mock",
}


def detect_mocks(code: str) -> list[dict[str, str | int]]:
    """Detect mocking usage in Python code.

    Args:
        code: Python source code to analyze

    Returns:
        List of violations with line numbers and messages
    """
    assert code is not None, "Code must not be None"
    assert isinstance(code, str), "Code must be a string"

    violations: list[dict[str, str | int]] = []

    try:
        tree = ast.parse(code)
    except SyntaxError:
        return violations

    for node in ast.walk(tree):
        # Detect imports from unittest.mock or other mock modules
        if isinstance(node, ast.ImportFrom):
            if node.module in MOCK_MODULES:
                assert hasattr(node, "lineno"), "Node must have lineno"
                assert node.lineno > 0, "Line number must be positive"
                msg = f"Mock import detected: {node.module} - Use dependency injection"
                violations.append({"line": node.lineno, "message": msg})

        # Detect direct import of mock module
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in MOCK_MODULES:
                    assert hasattr(node, "lineno"), "Node must have lineno"
                    assert node.lineno > 0, "Line number must be positive"
                    msg = f"Mock import detected: {alias.name} - Use dependency injection"
                    violations.append({"line": node.lineno, "message": msg})

        # Detect mocker fixture usage in function parameters
        elif isinstance(node, ast.FunctionDef):
            for arg in node.args.args:
                if arg.arg == "mocker":
                    assert hasattr(node, "lineno"), "Node must have lineno"
                    assert node.lineno > 0, "Line number must be positive"
                    msg = "pytest-mock 'mocker' fixture detected - Use dependency injection"
                    violations.append({"line": node.lineno, "message": msg})

    return violations
