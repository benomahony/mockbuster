from pathlib import Path

from pytest_examples import EvalExample, find_examples


def test_readme_examples():
    """Test all code examples in the documentation."""
    docs_file = Path("docs/tutorial.md")
    assert docs_file.exists(), "docs/tutorial.md must exist"

    examples = list(find_examples(docs_file))
    assert len(examples) > 0, "Should find code examples in tutorial"

    for example in examples:
        if example.in_py_file():
            eval_example = EvalExample.create(example)
            eval_example.run_print_check()
