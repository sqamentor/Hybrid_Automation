# Copilot Instructions for Hybrid Automation Framework

## Project Architecture
- **Multi-app, multi-layer:** Automates Bookslot (patient booking), CallCenter (agent), and PatientIntake (patient portal) as separate modules.
- **Microservice-inspired:** Core logic in `framework/` (microservices, managers, builders, validators). Each service is self-contained and reusable.
- **Test layers:**
  - `tests/bookslot/pages/`: Page-level, independent tests (P1-P7)
  - `tests/bookslot/e2e/`: Sequential, end-to-end flows
  - `tests/bookslot/url_testing/`: URL workflow tests (parametrized, negative, performance)
- **Fixtures:** Centralized in `tests/bookslot/fixtures/__init__.py`—never create new conftest.py files for Bookslot.
- **Test data:** All workflow data in `test_data/bookslot/bookslot_workflows.json` (JSON, not YAML).
- **Config:** All service and test config in `config/` (YAML, INI, TOML). Use `url_testing.yaml` for URL test config.

## Patterns & Conventions
- **Manager/Builder/Validator:** New utilities must follow these patterns (see `framework/testing/`).
- **BaseService:** All microservices extend `BaseService` (`framework/microservices/base.py`).
- **Logging:** Use `get_enterprise_logger()` from `framework.observability.enterprise_logger`.
- **Type hints:** Required for all new code (use `List`, `Dict`, `Optional` from `typing`).
- **Allure:** All tests use Allure decorators for epic/feature/story/severity.
- **Markers:** Register new pytest markers in `pytest.ini` (e.g., `negative`, `workflow_persistence`).
- **No duplicate fixtures:** Always extend `tests/bookslot/fixtures/__init__.py`.

## Developer Workflows
- **Run all tests:** `python -m pytest tests/bookslot/ -v`
- **Run URL tests:** `python -m pytest tests/bookslot/url_testing/ -v`
- **Collect only:** `python -m pytest tests/bookslot/ --collect-only`
- **Parallel:** Use `-n 4` for parallel runs (except E2E, which must be serial)
- **Allure reports:** `python -m pytest --alluredir=allure-results && allure serve allure-results`
- **Test data:** Add new workflows to `test_data/bookslot/bookslot_workflows.json` and update fixtures if needed.

## Integration & External
- **Playwright:** Used for browser automation (see `url_validator.py`).
- **Allure:** Required for reporting.
- **No direct DB/API calls** in Bookslot tests—UI and URL only.
- **SOC2-ready logging:** All logs go through enterprise logger for compliance.

## Examples
- **Manager pattern:** See `framework/testing/url_data_manager.py`
- **Builder pattern:** See `framework/testing/url_builder.py`
- **Validator pattern:** See `framework/testing/url_validator.py`
- **Test suite:** See `tests/bookslot/url_testing/test_workflow_urls_p1.py`

## Special Notes
- **Never create new conftest.py** for Bookslot—extend fixtures only.
- **Never hardcode environment URLs—use config/projects.yaml.**
- **Document new patterns in `docs/` and update test matrix if adding new test types.**

---
For more, see `README.md`, `docs/`, and `Framework-Knowledge-Center/`.
