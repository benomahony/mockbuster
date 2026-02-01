# How-to Guides

Practical guides for common tasks with mockbuster.

## Available Guides

### Testing Without Mocks

- **[Refactor Tests to Remove Mocks](refactor-tests.md)** - Step-by-step guide to removing mocks from existing tests
- **[Use Dependency Injection](dependency-injection.md)** - Implement dependency injection patterns for testability
- **[Handle Third-Party APIs](third-party-apis.md)** - Test code that calls external services without mocks

### Integration

- **[Integrate with CI/CD](ci-integration.md)** - Add mockbuster to your continuous integration pipeline

## Quick Tips

- Start with one test file at a time
- Use protocols/ABCs to define interfaces
- Create simple test doubles (fakes) instead of mocks
- Inject dependencies through constructors or function parameters
- Run mockbuster in `--strict` mode in CI to prevent regressions
