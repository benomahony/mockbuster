# How to Integrate with CI/CD

This guide shows you how to add mockbuster to your continuous integration pipeline.

## GitHub Actions

Add mockbuster to your GitHub Actions workflow:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v5

      - name: Set up Python
        run: uv python install 3.12

      - name: Install dependencies
        run: uv sync --all-extras

      - name: Run tests
        run: uv run pytest

      - name: Check for mocks
        run: uv run mockbuster tests/ --strict
```

The `--strict` flag ensures the build fails if any mocks are detected.

## GitLab CI

Add to your `.gitlab-ci.yml`:

```yaml
test:
  image: python:3.12
  before_script:
    - pip install uv
    - uv sync --all-extras
  script:
    - uv run pytest
    - uv run mockbuster tests/ --strict
```

## Pre-commit Hook

Add mockbuster as a pre-commit hook to catch mocks before they're committed:

### Installation

```bash
pip install pre-commit
```

### Configuration

Add to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: mockbuster
        name: mockbuster
        entry: uv run mockbuster
        language: system
        types: [python]
        files: ^tests/
        pass_filenames: true
        args: ["--strict"]
```

### Install Hook

```bash
pre-commit install
```

Now mockbuster runs automatically on every commit!

## Jenkins

Add to your `Jenkinsfile`:

```groovy
pipeline {
    agent any

    stages {
        stage('Install') {
            steps {
                sh 'pip install uv'
                sh 'uv sync --all-extras'
            }
        }

        stage('Test') {
            steps {
                sh 'uv run pytest'
            }
        }

        stage('Check Mocks') {
            steps {
                sh 'uv run mockbuster tests/ --strict'
            }
        }
    }
}
```

## CircleCI

Add to `.circleci/config.yml`:

```yaml
version: 2.1

jobs:
  test:
    docker:
      - image: cimg/python:3.12
    steps:
      - checkout
      - run:
          name: Install uv
          command: pip install uv
      - run:
          name: Install dependencies
          command: uv sync --all-extras
      - run:
          name: Run tests
          command: uv run pytest
      - run:
          name: Check for mocks
          command: uv run mockbuster tests/ --strict

workflows:
  test-workflow:
    jobs:
      - test
```

## Azure Pipelines

Add to `azure-pipelines.yml`:

```yaml
trigger:
  - main

pool:
  vmImage: 'ubuntu-latest'

steps:
- task: UsePythonVersion@0
  inputs:
    versionSpec: '3.12'

- script: |
    pip install uv
    uv sync --all-extras
  displayName: 'Install dependencies'

- script: uv run pytest
  displayName: 'Run tests'

- script: uv run mockbuster tests/ --strict
  displayName: 'Check for mocks'
```

## Make Target

Add to your `Makefile` for easy local testing:

```makefile
.PHONY: test check-mocks

test:
 uv run pytest

check-mocks:
 uv run mockbuster tests/ --strict

ci: test check-mocks
```

Run with:

```bash
make ci
```

## Tips

- **Use `--strict` mode** - Fail the build when mocks are detected
- **Run on all branches** - Catch violations early
- **Scan test directories** - Focus on where mocks typically appear
- **Combine with other linters** - Run alongside ruff, mypy, etc.
- **Show output** - Make violations visible in CI logs

## Gradual Adoption

If you have an existing codebase with mocks:

1. **Start in non-strict mode** - Just report violations without failing
2. **Fix one directory at a time** - Refactor incrementally
3. **Add ignored paths** - Temporarily skip certain files
4. **Enable strict mode** - Once all violations are fixed

### Example: Gradual Migration

```yaml
- name: Check for new mocks (non-strict)
  run: uv run mockbuster tests/ || true

- name: Check refactored code (strict)
  run: uv run mockbuster tests/refactored/ --strict
```

## Next Steps

- Read [Refactor Tests](refactor-tests.md) to fix violations
- See [Dependency Injection](dependency-injection.md) for patterns
- Check [CLI Reference](../reference/cli.md) for all options
