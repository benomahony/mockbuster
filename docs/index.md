# mockbuster

A Python linter that detects and reports all uses of mocking in test files, helping you write better tests with dependency injection instead of mocks.

## Quick Start

```bash
pip install mockbuster
mockbuster tests/
```

## Documentation

This documentation follows the [Diataxis](https://diataxis.fr/) framework:

### Learning-Oriented

- **[Tutorial](tutorial.md)** - Get started with mockbuster and fix your first violation

### Task-Oriented

- **[How-to Guides](howto/index.md)** - Practical guides for common tasks
  - [Refactor tests to remove mocks](howto/refactor-tests.md)
  - [Use dependency injection](howto/dependency-injection.md)
  - [Integrate with CI/CD](howto/ci-integration.md)
  - [Handle third-party APIs](howto/third-party-apis.md)

### Information-Oriented

- **[Reference](reference/index.md)** - Technical documentation
  - [CLI Reference](reference/cli.md)
  - [API Reference](reference/api.md)
  - [Detected Patterns](reference/patterns.md)

### Understanding-Oriented

- **[Explanation](explanation/index.md)** - Concepts and philosophy
  - [Why avoid mocks?](explanation/why-no-mocks.md)
  - [Dependency injection explained](explanation/dependency-injection.md)
  - [Real implementations vs mocks](explanation/philosophy.md)

## Quick Links

- [GitHub Repository](https://github.com/benomahony/mockbuster)
- [PyPI Package](https://pypi.org/project/mockbuster)
- [Report Issues](https://github.com/benomahony/mockbuster/issues)
