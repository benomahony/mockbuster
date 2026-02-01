# Explanation

Understanding the concepts and philosophy behind mockbuster.

## Contents

- **[Why Avoid Mocks?](why-no-mocks.md)** - The problems with mocking and why we should avoid it
- **[Dependency Injection Explained](dependency-injection.md)** - Understanding dependency injection as an alternative
- **[Philosophy: Real Implementations vs Mocks](philosophy.md)** - The testing philosophy behind mockbuster

## Core Principles

1. **Tests should use real implementations** - Even if they're simple test doubles
2. **Dependencies should be explicit** - Passed through constructors or function parameters
3. **Mocks hide design problems** - If code is hard to test without mocks, it needs better design
4. **Fast tests without mocks** - Use simple fakes instead of complex mock setups

## Quick Summary

### The Problem with Mocks

Mocks couple tests to implementation details, making refactoring difficult and tests brittle.

### The Solution

Use dependency injection to make code testable with simple, real implementations (fakes) instead of mocks.

### The Benefit

- Tests are clearer and more maintainable
- Production code is more flexible
- Refactoring is easier
- Dependencies are explicit

## Further Reading

- [Why Avoid Mocks?](why-no-mocks.md) - Detailed explanation
- [Dependency Injection](dependency-injection.md) - How it works
- [Philosophy](philosophy.md) - The bigger picture
