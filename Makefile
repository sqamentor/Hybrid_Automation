# ============================================================================
# MAKEFILE - Project Automation Commands
# Python 3.12+ Enterprise Automation Framework
# ============================================================================
# Usage: make <target>
# Example: make install
# ============================================================================

.PHONY: help install install-dev test test-parallel test-coverage lint format type-check security clean docs run-bookslot

# Default target
.DEFAULT_GOAL := help

# ============================================================================
# VARIABLES
# ============================================================================

PYTHON := python
PIP := $(PYTHON) -m pip
PYTEST := $(PYTHON) -m pytest
BLACK := $(PYTHON) -m black
RUFF := $(PYTHON) -m ruff
MYPY := $(PYTHON) -m mypy
PRE_COMMIT := pre-commit

# ============================================================================
# HELP
# ============================================================================

help: ## Show this help message
	@echo "=================================="
	@echo "Enterprise Automation Framework"
	@echo "=================================="
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""

# ============================================================================
# INSTALLATION
# ============================================================================

install: ## Install core dependencies
	$(PIP) install --upgrade pip
	$(PIP) install -e .
	playwright install chromium
	@echo "✅ Core installation complete!"

install-dev: ## Install with development dependencies
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[dev]"
	playwright install chromium firefox webkit
	$(PRE_COMMIT) install
	@echo "✅ Development installation complete!"

install-all: ## Install all optional dependencies
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[all]"
	playwright install chromium firefox webkit
	$(PRE_COMMIT) install
	@echo "✅ Full installation complete!"

install-ai: ## Install with AI features
	$(PIP) install -e ".[ai]"
	@echo "✅ AI features installed!"

# ============================================================================
# TESTING
# ============================================================================

test: ## Run all tests
	$(PYTEST) -v

test-fast: ## Run tests without human behavior (fast)
	$(PYTEST) -v --disable-human-behavior

test-parallel: ## Run tests in parallel
	$(PYTEST) -v -n auto

test-bookslot: ## Run bookslot tests only
	$(PYTEST) recorded_tests/bookslot/ -v

test-integration: ## Run integration tests
	$(PYTEST) tests/integration/ -v

test-ui: ## Run UI tests only
	$(PYTEST) -v -m ui_only

test-api: ## Run API tests only
	$(PYTEST) -v -m api_only

test-coverage: ## Run tests with coverage report
	$(PYTEST) --cov=framework --cov=pages --cov=utils --cov-report=html --cov-report=term
	@echo "📊 Coverage report: htmlcov/index.html"

test-headed: ## Run tests with visible browser
	$(PYTEST) -v --headed

test-specific: ## Run specific test (Usage: make test-specific TEST=test_name)
	$(PYTEST) -v -k "$(TEST)"

# ============================================================================
# CODE QUALITY
# ============================================================================

lint: ## Run ruff linter
	$(RUFF) check .

lint-fix: ## Run ruff linter with auto-fix
	$(RUFF) check . --fix

format: ## Format code with black and ruff
	$(BLACK) .
	$(RUFF) format .
	@echo "✅ Code formatted!"

format-check: ## Check code formatting without changes
	$(BLACK) --check .
	$(RUFF) format --check .

type-check: ## Run mypy type checker
	$(MYPY) framework pages utils

security: ## Run security checks
	$(PYTHON) -m bandit -r framework pages utils -c pyproject.toml

pre-commit: ## Run all pre-commit hooks
	$(PRE_COMMIT) run --all-files

pre-commit-update: ## Update pre-commit hooks
	$(PRE_COMMIT) autoupdate

# ============================================================================
# QUALITY GATES (CI/CD)
# ============================================================================

quality: lint type-check security ## Run all quality checks
	@echo "✅ All quality checks passed!"

ci: install-dev quality test-coverage ## Run complete CI pipeline
	@echo "✅ CI pipeline complete!"

# ============================================================================
# CLEANING
# ============================================================================

clean: ## Remove build artifacts and cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf build/ dist/ htmlcov/ .coverage
	@echo "✅ Cleaned!"

clean-logs: ## Remove logs and test artifacts
	rm -rf logs/ reports/ screenshots/ videos/ traces/ allure-results/
	@echo "✅ Logs cleaned!"

clean-all: clean clean-logs ## Remove everything
	rm -rf .venv/ venv/
	@echo "✅ Everything cleaned!"

# ============================================================================
# DOCUMENTATION
# ============================================================================

docs: ## Build documentation
	@echo "📚 Building documentation..."
	@echo "⚠️  Not implemented yet"

docs-serve: ## Serve documentation locally
	@echo "📚 Serving documentation..."
	@echo "⚠️  Not implemented yet"

# ============================================================================
# RUNNING TESTS (Convenience)
# ============================================================================

run-bookslot: ## Quick run bookslot test
	$(PYTEST) recorded_tests/bookslot/test_bookslot_complete_workflow.py -v --headed

run-demo: ## Run demo tests
	$(PYTEST) examples/ -v

# ============================================================================
# DEPENDENCY MANAGEMENT
# ============================================================================

deps-update: ## Show outdated dependencies
	$(PIP) list --outdated

deps-tree: ## Show dependency tree
	$(PIP) install pipdeptree
	pipdeptree

# ============================================================================
# VERSION & RELEASE
# ============================================================================

version: ## Show current version
	@grep "version" pyproject.toml | head -1 | cut -d'"' -f2

bump-patch: ## Bump patch version (1.0.0 -> 1.0.1)
	@echo "Bumping patch version..."
	@echo "⚠️  Not implemented yet - use commitizen"

bump-minor: ## Bump minor version (1.0.0 -> 1.1.0)
	@echo "Bumping minor version..."
	@echo "⚠️  Not implemented yet - use commitizen"

bump-major: ## Bump major version (1.0.0 -> 2.0.0)
	@echo "Bumping major version..."
	@echo "⚠️  Not implemented yet - use commitizen"

# ============================================================================
# DOCKER
# ============================================================================

docker-build: ## Build Docker image
	docker build -t automation-framework:latest -f docker/Dockerfile .

docker-run: ## Run tests in Docker
	docker-compose -f docker/docker-compose.yml up --abort-on-container-exit

# ============================================================================
# PROJECT INFO
# ============================================================================

info: ## Show project information
	@echo "=================================="
	@echo "Project: Enterprise Automation Framework"
	@echo "Author: Lokendra Singh"
	@echo "Python: $(shell $(PYTHON) --version)"
	@echo "Version: $(shell make version)"
	@echo "=================================="
	@echo ""
	@$(PIP) show enterprise-automation-framework 2>/dev/null || echo "⚠️  Package not installed (run: make install)"
