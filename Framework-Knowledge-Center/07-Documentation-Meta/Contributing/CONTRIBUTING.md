# Contributing to Enterprise Automation Framework

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

---

## 🚀 Quick Start for Contributors

### 1. Fork & Clone
```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/automation.git
cd automation
```

### 2. Set Up Development Environment
```bash
# Install development dependencies
make install-dev

# Or manually
pip install -e ".[dev]"
pre-commit install
```

### 3. Create a Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b bugfix/issue-number-description
```

### 4. Make Changes & Test
```bash
# Make your changes...

# Run tests
make test

# Check code quality
make quality

# Format code
make format
```

### 5. Commit & Push
```bash
git add .
git commit -m "feat: add new feature"  # See commit guidelines below
git push origin feature/your-feature-name
```

### 6. Create Pull Request
Go to GitHub and create a Pull Request from your branch to `main`.

---

## 📋 Development Workflow

### Setting Up Your Environment

**Required:**
- Python 3.12+
- Git

**Installation:**
```bash
# Clone the repository
git clone https://github.com/lokendrasingh/automation.git
cd automation

# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode with all dependencies
pip install -e ".[dev]"

# Install Playwright browsers
playwright install chromium

# Set up pre-commit hooks
pre-commit install
```

---

## ✅ Code Quality Standards

### 1. **Code Formatting**
We use **Black** and **Ruff** for consistent code formatting:

```bash
# Format code
make format

# Check formatting
make format-check
```

**Style Rules:**
- Line length: 100 characters
- Use Black's default style
- Sort imports with isort (integrated in Ruff)

### 2. **Linting**
We use **Ruff** for fast linting:

```bash
# Run linter
make lint

# Auto-fix issues
make lint-fix
```

### 3. **Type Checking**
We use **mypy** for static type checking:

```bash
# Run type checker
make type-check
```

**Type Hints Requirements:**
- All new functions must have type hints
- Use `typing` module for complex types
- Document return types

Example:
```python
from typing import Optional, List, Dict

def process_data(
    items: List[Dict[str, str]], 
    config: Optional[Dict[str, Any]] = None
) -> List[str]:
    """Process items with optional configuration."""
    ...
```

### 4. **Security**
We use **Bandit** for security checks:

```bash
# Run security scan
make security
```

### 5. **Pre-commit Hooks**
All checks run automatically before commit:

```bash
# Run manually
make pre-commit

# Update hooks
make pre-commit-update
```

---

## 🧪 Testing Guidelines

### Running Tests

```bash
# All tests
make test

# Specific test
pytest tests/test_example.py -v

# With coverage
make test-coverage

# Fast (no human behavior)
make test-fast

# Parallel execution
make test-parallel
```

### Writing Tests

**Structure:**
```python
import pytest
from playwright.sync_api import Page

@pytest.mark.bookslot
@pytest.mark.smoke
def test_feature_name(page: Page, smart_actions, fake_bookslot_data):
    """Test description.
    
    Given: Initial state
    When: Action performed
    Then: Expected outcome
    """
    # Arrange
    url = "https://example.com"
    
    # Act
    smart_actions.navigate(url, "Page Name")
    smart_actions.click(page.locator("#button"), "Button")
    
    # Assert
    assert page.locator(".success").is_visible()
```

**Best Practices:**
- ✅ Use descriptive test names: `test_user_can_login_with_valid_credentials`
- ✅ Use fixtures for reusable setup
- ✅ Use markers to categorize tests
- ✅ Keep tests independent (no shared state)
- ✅ Use smart_actions for UI interactions
- ✅ Use fake_data fixtures instead of hardcoded data
- ❌ Avoid `time.sleep()` - use smart_actions or wait_for methods

---

## 📝 Commit Message Guidelines

We follow [Conventional Commits](https://www.conventionalcommits.org/) specification.

### Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements
- `ci`: CI/CD changes

### Examples

**Feature:**
```
feat(ui): add self-healing locator support

Implements automatic fallback locators when primary locator fails.
Uses CSS, XPath, and text-based strategies.

Closes #123
```

**Bug Fix:**
```
fix(api): handle timeout errors gracefully

Previously, timeout errors would crash the test.
Now they are caught and logged with retry logic.

Fixes #456
```

**Documentation:**
```
docs(readme): update installation instructions

Add Python 3.12 requirement and clarify setup steps.
```

### Rules
- Use present tense: "add" not "added"
- Use imperative mood: "fix" not "fixes"
- First line max 72 characters
- Reference issues: `Closes #123` or `Fixes #456`
- Breaking changes: Add `BREAKING CHANGE:` in footer

---

## 🏗️ Project Structure

Understanding the structure helps you contribute effectively:

```
framework/
├── api/           # API testing modules
├── core/          # Core utilities (smart_actions, exceptions)
├── ui/            # UI engines (Playwright, Selenium)
├── database/      # Database validation
├── ai/            # AI integration
├── visual/        # Visual regression
├── security/      # Security testing
├── accessibility/ # Accessibility testing
└── mobile/        # Mobile testing

pages/             # Page Object Models
tests/             # Test suites
config/            # Configuration files
utils/             # Helper utilities
docs/              # Documentation
```

---

## 🎯 Areas to Contribute

### 🐛 Bug Fixes
- Check [open issues](https://github.com/lokendrasingh/automation/issues)
- Look for `good-first-issue` label
- Reproduce the bug first
- Add test case that fails
- Fix the bug
- Verify test passes

### ✨ New Features
- Discuss in an issue first
- Follow existing patterns
- Add tests for new features
- Update documentation
- Add example usage

### 📚 Documentation
- Improve README
- Add code examples
- Write tutorials
- Fix typos
- Add docstrings

### 🧪 Tests
- Increase test coverage
- Add edge case tests
- Improve test performance
- Add integration tests

### 🎨 Code Quality
- Refactor complex code
- Add type hints
- Improve error messages
- Optimize performance

---

## 🔍 Code Review Process

### For Contributors

**Before Submitting PR:**
- ✅ All tests pass
- ✅ Code formatted (black, ruff)
- ✅ Type checked (mypy)
- ✅ No linting errors
- ✅ Documentation updated
- ✅ CHANGELOG updated (if applicable)

**PR Description Should Include:**
- What changed?
- Why did it change?
- How to test it?
- Screenshots (if UI changes)
- Related issues

**Template:**
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Existing tests pass
- [ ] New tests added
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings

## Related Issues
Closes #123
```

### For Reviewers

**Check:**
- ✅ Code quality and style
- ✅ Test coverage
- ✅ Documentation completeness
- ✅ Performance impact
- ✅ Security implications
- ✅ Backward compatibility

**Feedback Guidelines:**
- Be respectful and constructive
- Explain the "why" behind suggestions
- Approve when ready, request changes if needed
- Use GitHub's suggestion feature for code

---

## 🎨 Style Guide

### Python Style

**Follow PEP 8 with modifications:**
- Line length: 100 (not 79)
- Use Black's formatting
- Type hints required for new code

**Naming Conventions:**
```python
# Classes: PascalCase
class SmartActions:
    pass

# Functions/Methods: snake_case
def navigate_to_page():
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRIES = 3

# Private: _leading_underscore
def _internal_helper():
    pass

# Type Variables: PascalCase with T suffix
from typing import TypeVar
T = TypeVar('T')
```

**Docstrings:**
```python
def function(arg1: str, arg2: int = 0) -> bool:
    """Short one-line description.
    
    Longer description if needed, explaining behavior,
    edge cases, and important details.
    
    Args:
        arg1: Description of arg1
        arg2: Description of arg2 (default: 0)
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When arg1 is empty
        
    Example:
        >>> function("test", 5)
        True
    """
    ...
```

### Import Order
```python
# Standard library
import os
import sys
from typing import Dict, List

# Third-party
import pytest
from playwright.sync_api import Page

# Local
from framework.core import SmartActions
from pages.bookslot import BookslotPage
```

---

## 🐛 Bug Report Template

When reporting bugs, use this template:

```markdown
**Describe the bug**
Clear description of the bug

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '....'
3. See error

**Expected behavior**
What should happen

**Actual behavior**
What actually happens

**Screenshots**
If applicable

**Environment:**
- OS: [e.g., Windows 11]
- Python Version: [e.g., 3.12.1]
- Framework Version: [e.g., 1.0.0]
- Browser: [e.g., Chromium 120]

**Additional context**
Any other relevant information
```

---

## 💡 Feature Request Template

```markdown
**Is your feature request related to a problem?**
Description of the problem

**Describe the solution you'd like**
Clear description of desired solution

**Describe alternatives you've considered**
Other approaches you've thought about

**Additional context**
Mockups, examples, or related issues
```

---

## 📊 Code Coverage

We aim for **>80%** code coverage.

```bash
# Generate coverage report
make test-coverage

# View HTML report
open htmlcov/index.html  # macOS
start htmlcov/index.html # Windows
```

**Coverage Requirements:**
- New features: Must have tests
- Bug fixes: Add regression test
- Refactoring: Maintain or improve coverage

---

## 🔐 Security

### Reporting Security Issues

**DO NOT** open public issues for security vulnerabilities.

Instead, email: qa.lokendra@gmail.com

Include:
- Description of vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

---

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

## 🙏 Recognition

Contributors will be:
- Added to AUTHORS file
- Mentioned in release notes
- Thanked in CHANGELOG

---

## ❓ Questions?

- 📧 Email: qa.lokendra@gmail.com
- 💬 GitHub Discussions
- 🐛 GitHub Issues

---

## 🎉 Thank You!

Every contribution, no matter how small, makes this project better!

**Happy Contributing! 🚀**
