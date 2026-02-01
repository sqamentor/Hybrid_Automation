# 📚 Framework Knowledge Center - Complete Documentation Index

**Welcome to the Enterprise Hybrid Automation Framework Knowledge Center**

This comprehensive documentation covers every aspect of the framework, from getting started to advanced features and strict architectural rules.

---

## 🎯 Quick Navigation

| Category | Description |
|----------|-------------|
| [🚀 Getting Started](#-getting-started) | Installation, setup, first test |
| [🏗️ Core Concepts](#️-core-concepts) | Architecture, smart actions, engine selection |
| [📄 Page Object Model](#-page-object-model) | POM architecture, rules, best practices |
| [🧪 Testing Features](#-testing-features) | UI, API, DB, Visual, Accessibility, Security |
| [⚙️ Configuration](#️-configuration) | Environments, projects, settings |
| [🔧 Advanced Features](#-advanced-features) | AI, intelligence, self-healing |
| [🏛️ Governance](#️-governance) | Architecture audit, enforcement, CI/CD |
| [📊 Reporting](#-reporting) | Allure, HTML, logging, traces |
| [🛠️ Utilities](#️-utilities) | Fake data, logger, helpers |
| [📜 Rules & Standards](#-rules--standards) | Mandatory rules, anti-patterns, best practices |
| [🎓 Tutorials](#-tutorials) | Step-by-step guides |
| [❓ Troubleshooting](#-troubleshooting) | Common issues and solutions |

---

## 🚀 Getting Started

### Installation & Setup
- **[Installation Guide](01-Getting-Started/Installation-Guide.md)**
  - System requirements
  - Installation steps
  - Verification
  - Troubleshooting

- **[Quick Start Guide](01-Getting-Started/Quick-Start-Guide.md)**
  - Run your first test in 30 seconds
  - Basic concepts
  - CLI usage

- **[First Test Tutorial](01-Getting-Started/First-Test-Tutorial.md)**
  - Write your first test step-by-step
  - Understand fixtures
  - Basic assertions

- **[Project Structure Overview](01-Getting-Started/Project-Structure-Overview.md)**
  - Directory layout
  - File organization
  - Naming conventions

---

## 🏗️ Core Concepts

### Architecture & Design
- **[Architecture Overview](02-Core-Concepts/Architecture-Overview.md)**
  - High-level architecture
  - Design patterns
  - Component interaction
  - Data flow

- **[Engine Selection System](02-Core-Concepts/Engine-Selection-System.md)**
  - Playwright vs Selenium decision logic
  - 20+ decision rules with priority
  - YAML configuration
  - Custom overrides
  - Decision caching

- **[Smart Actions](02-Core-Concepts/Smart-Actions.md)**
  - Context-aware action wrappers
  - Automatic delays
  - Human behavior integration
  - Usage patterns
  - API reference

- **[Execution Flow Orchestrator](02-Core-Concepts/Execution-Flow-Orchestrator.md)**
  - UI → API → DB flow
  - Execution context
  - Evidence collection
  - Flow configuration

- **[Project Manager](02-Core-Concepts/Project-Manager.md)**
  - Multi-project support
  - Project detection
  - Environment awareness
  - Dynamic project creation

- **[Human Behavior Simulation](02-Core-Concepts/Human-Behavior-Simulation.md)**
  - Realistic mouse movements
  - Context-aware typing
  - Natural scrolling
  - Configuration options
  - Intensity levels

- **[Workflow Orchestrator](02-Core-Concepts/Workflow-Orchestrator.md)**
  - Test workflow management
  - Step coordination
  - Error handling
  - Retry logic

---

## 📄 Page Object Model

### POM Architecture & Rules
- **[POM Architecture](03-Page-Object-Model/POM-Architecture.md)**
  - POM principles
  - Class structure
  - Locator strategies
  - Method organization

- **[POM Rules & Compliance](03-Page-Object-Model/POM-Rules-And-Compliance.md)**
  - Mandatory rules
  - Forbidden patterns
  - Compliance checks
  - Enforcement

- **[POM Best Practices](03-Page-Object-Model/POM-Best-Practices.md)**
  - Design guidelines
  - Maintainability tips
  - Reusability patterns
  - Common pitfalls

- **[Base Page Class](03-Page-Object-Model/Base-Page-Class.md)**
  - BasePage contract
  - Common methods
  - Human behavior integration
  - Implementation guide

- **[BookSlot Pages](03-Page-Object-Model/Projects/BookSlot-Pages.md)**
  - All BookSlot page objects
  - Usage examples
  - Page flow

- **[CallCenter Pages](03-Page-Object-Model/Projects/CallCenter-Pages.md)**
  - All CallCenter page objects
  - Usage examples
  - Page flow

- **[PatientIntake Pages](03-Page-Object-Model/Projects/PatientIntake-Pages.md)**
  - All PatientIntake page objects
  - Usage examples
  - Page flow

---

## 🧪 Testing Features

### UI Testing
- **[UI Testing Overview](04-Testing-Features/UI-Testing/UI-Testing-Overview.md)**
  - Playwright engine
  - Selenium engine
  - Engine switching
  - Best practices

- **[Playwright Engine](04-Testing-Features/UI-Testing/Playwright-Engine.md)**
  - Features and capabilities
  - Auto-waiting
  - Network interception
  - API testing integration

- **[Selenium Engine](04-Testing-Features/UI-Testing/Selenium-Engine.md)**
  - Features and capabilities
  - WebDriver management
  - Legacy browser support
  - iframe handling

- **[Self-Healing Locators](04-Testing-Features/UI-Testing/Self-Healing-Locators.md)**
  - Auto-recovery strategies
  - Fallback locators
  - Configuration
  - Performance impact

- **[UI Factory](04-Testing-Features/UI-Testing/UI-Factory.md)**
  - Factory pattern implementation
  - Engine instantiation
  - Configuration
  - Extensibility

### API Testing
- **[API Testing Overview](04-Testing-Features/API-Testing/API-Testing-Overview.md)**
  - API client features
  - Request/response tracking
  - Authentication
  - Assertion helpers

- **[API Client](04-Testing-Features/API-Testing/API-Client.md)**
  - REST API testing
  - HTTP methods
  - Headers and auth
  - Response validation

- **[API Interceptor](04-Testing-Features/API-Testing/API-Interceptor.md)**
  - Network interception
  - Request modification
  - Response mocking
  - Audit logging

- **[Async API Client](04-Testing-Features/API-Testing/Async-API-Client.md)**
  - Asynchronous testing
  - Concurrent requests
  - Performance testing

- **[GraphQL Client](04-Testing-Features/API-Testing/GraphQL-Client.md)**
  - GraphQL queries
  - Mutations
  - Subscriptions
  - Schema validation

- **[WebSocket Testing](04-Testing-Features/API-Testing/WebSocket-Testing.md)**
  - WebSocket connections
  - Real-time testing
  - Message validation

### Database Testing
- **[Database Testing Overview](04-Testing-Features/Database-Testing/Database-Testing-Overview.md)**
  - DB validation strategies
  - Connection management
  - Query execution

- **[DB Client](04-Testing-Features/Database-Testing/DB-Client.md)**
  - Connection setup
  - SQL execution
  - Transaction management

- **[DB Validator](04-Testing-Features/Database-Testing/DB-Validator.md)**
  - Data validation
  - Assertion helpers
  - Common queries

- **[Query Builder](04-Testing-Features/Database-Testing/Query-Builder.md)**
  - Fluent SQL construction
  - Type safety
  - Complex queries

- **[Async DB Client](04-Testing-Features/Database-Testing/Async-DB-Client.md)**
  - Asynchronous queries
  - Connection pooling
  - Performance optimization

### Visual Testing
- **[Visual Regression Testing](04-Testing-Features/Visual-Testing/Visual-Regression.md)**
  - Screenshot comparison
  - Diff generation
  - Baseline management
  - Ignore regions

### Accessibility Testing
- **[Accessibility Testing](04-Testing-Features/Accessibility-Testing/Accessibility-Testing.md)**
  - WCAG 2.1 AA/AAA compliance
  - Automated checks
  - Accessibility report
  - Remediation guide

### Security Testing
- **[Security Testing](04-Testing-Features/Security-Testing/Security-Testing.md)**
  - OWASP ZAP integration
  - Vulnerability scanning
  - Security report
  - Risk assessment

### Performance Testing
- **[Performance Monitoring](04-Testing-Features/Performance-Testing/Performance-Monitoring.md)**
  - Page load metrics
  - Resource timing
  - Core Web Vitals
  - Performance budgets

### Mobile Testing
- **[Mobile Testing](04-Testing-Features/Mobile-Testing/Mobile-Testing.md)**
  - Device emulation
  - Responsive testing
  - Touch actions
  - Mobile-specific tests

---

## ⚙️ Configuration

### Configuration Management
- **[Configuration Guide](05-Configuration/Configuration-Guide.md)**
  - Configuration sources
  - Priority order
  - Environment variables
  - YAML configs

- **[Environment Management](05-Configuration/Environment-Management.md)**
  - Dev, Staging, Production
  - Environment selection
  - Environment-specific settings
  - Secrets management

- **[Project Management](05-Configuration/Project-Management.md)**
  - Multi-project setup
  - Project detection
  - Project-specific configs
  - Adding new projects

- **[Engine Decision Matrix](05-Configuration/Engine-Decision-Matrix.md)**
  - YAML configuration
  - Priority-based rules
  - Confidence scoring
  - Custom overrides

- **[Human Behavior Configuration](05-Configuration/Human-Behavior-Configuration.md)**
  - Behavior profiles
  - Intensity levels
  - Custom behaviors
  - Enable/disable controls

- **[Settings Management](05-Configuration/Settings-Management.md)**
  - Settings.py overview
  - Configuration loading
  - Settings validation
  - Default values

---

## 🔧 Advanced Features

### AI & Intelligence
- **[AI Provider Factory](06-Advanced-Features/AI/AI-Provider-Factory.md)**
  - OpenAI integration
  - Anthropic Claude integration
  - Provider selection
  - Fallback strategies

- **[Natural Language Test Generation](06-Advanced-Features/AI/NL-Test-Generator.md)**
  - Plain English to tests
  - Test generation
  - Code templates

- **[AI Auto-Validation](06-Advanced-Features/Intelligence/AI-Auto-Validation.md)**
  - Automatic validation suggestions
  - CRUD pattern detection
  - API validation generation
  - DB validation generation

- **[Self-Healing System](06-Advanced-Features/Intelligence/Self-Healing-System.md)**
  - Locator recovery
  - Fallback strategies
  - Healing history
  - Success metrics

- **[ML Test Optimizer](06-Advanced-Features/Intelligence/ML-Test-Optimizer.md)**
  - Predictive test selection
  - Smart retry logic
  - Failure analysis
  - Test prioritization

- **[Pattern Recognition](06-Advanced-Features/Intelligence/Pattern-Recognition.md)**
  - Test pattern learning
  - Anomaly detection
  - Trend analysis

### Recording & Generation
- **[Test Recording](06-Advanced-Features/Recording/Test-Recording.md)**
  - Browser recording
  - Code generation
  - Cleanup and optimization

---

## 🏛️ Governance

### Architecture Audit & Enforcement
- **[Governance System Overview](07-Governance/Governance-System-Overview.md)**
  - System architecture
  - Enforcement layers
  - Audit workflow

- **[Audit Rules](07-Governance/Audit-Rules.md)**
  - Complete rule catalog
  - Rule categories
  - Severity levels
  - Violation examples

- **[Framework Audit Engine](07-Governance/Framework-Audit-Engine.md)**
  - AST-based analysis
  - Violation detection
  - Baseline management
  - Report generation

- **[Pre-Commit Hooks](07-Governance/Pre-Commit-Hooks.md)**
  - Hook installation
  - Commit blocking
  - Bypass scenarios
  - Troubleshooting

- **[File Watcher](07-Governance/File-Watcher.md)**
  - Real-time monitoring
  - Auto-audit on changes
  - Strict mode
  - History tracking

- **[CI/CD Integration](07-Governance/CICD-Integration.md)**
  - GitHub Actions workflow
  - Status checks
  - PR blocking
  - Report artifacts

- **[Baseline Allow-List](07-Governance/Baseline-Allow-List.md)**
  - Technical debt management
  - Expiration tracking
  - Baseline rules
  - Audit trail

- **[Fix Suggestions](07-Governance/Fix-Suggestions.md)**
  - Automated suggestions
  - Remediation guidance
  - Code examples

- **[AI Explainer](07-Governance/AI-Explainer.md)**
  - Violation explanations
  - Educational content
  - Best practice guidance

---

## 📊 Reporting

### Test Reporting & Observability
- **[Reporting Overview](08-Reporting/Reporting-Overview.md)**
  - Report types
  - Configuration
  - Best practices

- **[Allure Reports](08-Reporting/Allure-Reports.md)**
  - Setup and configuration
  - Test history
  - Trends and metrics
  - Custom categories

- **[HTML Reports](08-Reporting/HTML-Reports.md)**
  - Pytest-HTML integration
  - Screenshots embedding
  - Video embedding
  - Custom CSS

- **[Logging](08-Reporting/Logging.md)**
  - Loguru configuration
  - Log levels
  - File rotation
  - Structured logging

- **[Audit Logger](08-Reporting/Audit-Logger.md)**
  - Compliance tracking
  - Request/response logs
  - Audit trail
  - Report generation

- **[Video Recording](08-Reporting/Video-Recording.md)**
  - Video capture
  - Failure highlights
  - Storage management

- **[Screenshots](08-Reporting/Screenshots.md)**
  - Auto-screenshots
  - Failure capture
  - Comparison screenshots

- **[Traces](08-Reporting/Traces.md)**
  - Playwright traces
  - Trace viewer
  - Debug information

---

## 🛠️ Utilities

### Test Data & Helpers
- **[Fake Data Generator](09-Utilities/Fake-Data-Generator.md)**
  - Data generation strategies
  - BookSlot data
  - Custom generators
  - Data persistence

- **[Logger Utility](09-Utilities/Logger-Utility.md)**
  - Logger setup
  - Usage patterns
  - Custom formatting
  - Integration

- **[Flow Helpers](09-Utilities/Flow-Helpers.md)**
  - Common workflows
  - Reusable actions
  - Helper functions

---

## 📜 Rules & Standards

### Mandatory Rules & Guidelines
- **[Strict Rules - MUST FOLLOW](10-Rules-And-Standards/Strict-Rules.md)**
  - Page Object Model rules
  - Engine mixing rules
  - Test structure rules
  - Human behavior rules
  - Data management rules
  - Import rules
  - Naming conventions

- **[Anti-Patterns - AVOID](10-Rules-And-Standards/Anti-Patterns.md)**
  - Direct locators in tests
  - Manual delays
  - Hardcoded data
  - Mixing engines
  - God tests
  - Poor naming

- **[Common Mistakes](10-Rules-And-Standards/Common-Mistakes.md)**
  - Frequent errors
  - Why they happen
  - How to fix
  - Prevention strategies

- **[Best Practices](10-Rules-And-Standards/Best-Practices.md)**
  - Code organization
  - Test design
  - Performance optimization
  - Maintainability

- **[Code Standards](10-Rules-And-Standards/Code-Standards.md)**
  - Python style guide
  - Type hints
  - Docstrings
  - Comments

- **[Testing Standards](10-Rules-And-Standards/Testing-Standards.md)**
  - Test naming
  - Test organization
  - Assertion patterns
  - Test data

---

## 🎓 Tutorials

### Step-by-Step Guides
- **[Tutorial 1: Your First Test](11-Tutorials/Tutorial-01-First-Test.md)**
  - Setup environment
  - Write basic test
  - Run and verify

- **[Tutorial 2: Using Smart Actions](11-Tutorials/Tutorial-02-Smart-Actions.md)**
  - Smart action basics
  - Human behavior
  - Advanced usage

- **[Tutorial 3: Page Object Model](11-Tutorials/Tutorial-03-POM.md)**
  - Create page object
  - Define locators
  - Write page methods

- **[Tutorial 4: Multi-Layer Testing](11-Tutorials/Tutorial-04-Multi-Layer.md)**
  - UI + API + DB
  - Validation strategies
  - Evidence collection

- **[Tutorial 5: Fake Data Generation](11-Tutorials/Tutorial-05-Fake-Data.md)**
  - Generate test data
  - Custom generators
  - Data fixtures

- **[Tutorial 6: Visual Regression](11-Tutorials/Tutorial-06-Visual-Regression.md)**
  - Setup baselines
  - Compare screenshots
  - Handle differences

- **[Tutorial 7: API Testing](11-Tutorials/Tutorial-07-API-Testing.md)**
  - REST API tests
  - Authentication
  - Response validation

- **[Tutorial 8: Database Testing](11-Tutorials/Tutorial-08-DB-Testing.md)**
  - DB connections
  - Query execution
  - Data validation

---

## ❓ Troubleshooting

### Common Issues & Solutions
- **[Troubleshooting Guide](12-Troubleshooting/Troubleshooting-Guide.md)**
  - Installation issues
  - Test failures
  - Configuration problems
  - Performance issues

- **[FAQ](12-Troubleshooting/FAQ.md)**
  - Frequently asked questions
  - Quick answers
  - Common scenarios

- **[Debug Guide](12-Troubleshooting/Debug-Guide.md)**
  - Debugging strategies
  - Tools and techniques
  - Common patterns

- **[Error Messages](12-Troubleshooting/Error-Messages.md)**
  - Error catalog
  - Meaning and causes
  - Solutions

---

## 📖 Reference

### API Reference
- **[Fixtures Reference](13-Reference/Fixtures-Reference.md)**
  - All pytest fixtures
  - Parameters
  - Usage examples

- **[Markers Reference](13-Reference/Markers-Reference.md)**
  - All test markers
  - When to use
  - Examples

- **[CLI Reference](13-Reference/CLI-Reference.md)**
  - Command-line options
  - Configuration flags
  - Examples

- **[Configuration Reference](13-Reference/Configuration-Reference.md)**
  - All config options
  - Default values
  - Override methods

---

## 🔄 Migration Guides

### Version Upgrades
- **[Migration Guide v0.x to v1.0](14-Migration/Migration-V0-to-V1.md)**
  - Breaking changes
  - New features
  - Step-by-step migration

---

## 📝 Changelog

### Release Notes
- **[Changelog](15-Changelog/CHANGELOG.md)**
  - Version history
  - Features added
  - Bug fixes
  - Breaking changes

---

## 🎯 Quick Reference Cards

### Cheat Sheets
- **[Quick Reference - Smart Actions](Quick-Reference/Smart-Actions-Cheat-Sheet.md)**
- **[Quick Reference - POM Rules](Quick-Reference/POM-Rules-Cheat-Sheet.md)**
- **[Quick Reference - Pytest Commands](Quick-Reference/Pytest-Commands-Cheat-Sheet.md)**
- **[Quick Reference - Configuration](Quick-Reference/Configuration-Cheat-Sheet.md)**

---

## 📞 Getting Help

### Support Channels
- **Documentation** - Check this Knowledge Center first
- **GitHub Issues** - Report bugs or request features
- **GitHub Discussions** - Ask questions, share ideas
- **Email** - qa.lokendra@gmail.com
- **Website** - [www.sqamentor.com](https://www.sqamentor.com)

---

## 🌟 Contributing

Interested in contributing? See:
- [Contributing Guide](../CONTRIBUTING.md)
- [Code of Conduct](../CODE_OF_CONDUCT.md)
- [Development Setup](01-Getting-Started/Development-Setup.md)

---

**Last Updated:** February 1, 2026  
**Framework Version:** 1.0.0  
**Documentation Version:** 1.0.0

---

**Built with ❤️ by the SQA Mentor Team**

**"Complete Knowledge for Intelligent Testing"**
