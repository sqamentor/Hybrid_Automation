# Tests Directory Structure

## Overview
Tests are organized by project and test type for better maintainability and project isolation.

```
tests/
├── bookslot/              # Bookslot project tests
│   ├── __init__.py
│   └── test_bookslot_with_fake_data.py
│
├── patientintake/         # PatientIntake project tests
│   ├── __init__.py
│   └── test_patientintake_example.py
│
├── callcenter/            # CallCenter project tests
│   ├── __init__.py
│   └── test_callcenter_example.py
│
├── integration/           # Cross-application integration tests
│   ├── test_bookslot_to_patientintake.py
│   ├── test_three_system_workflow.py
│   └── test_ui_api_db_flow.py
│
├── unit/                  # Unit tests for framework components
│   ├── test_async_config_manager.py
│   ├── test_di_container.py
│   └── ...
│
├── ui/                    # UI-specific tests
│   ├── test_modern_spa.py
│   └── test_legacy_ui.py
│
├── common/                # Common test utilities
│   ├── test_recording_module.py
│   └── test_recording_simple.py
│
├── examples/              # Example/demo tests
│   └── ...
│
└── conftest.py            # Shared fixtures and configuration
```

## Test Categories

### Project-Specific Tests
Each project has its own directory containing tests specific to that application:

- **bookslot/** - Patient appointment booking system tests
- **patientintake/** - Patient data management system tests  
- **callcenter/** - Call center operations tests

### Integration Tests
Tests that span multiple applications and verify cross-system workflows.

### Unit Tests
Component-level tests for framework utilities and modules.

### UI Tests
Tests focused on UI rendering and behavior.

### Common Tests
Shared test utilities and recording/playback functionality.

## Running Tests

### Run project-specific tests:
```bash
# Run all bookslot tests
pytest tests/bookslot/ -v

# Run all patientintake tests
pytest tests/patientintake/ -v

# Run all callcenter tests
pytest tests/callcenter/ -v
```

### Run with POM CLI:
```bash
python run_pom_tests_cli.py
# Then select project (bookslot/patientintake/callcenter)
```

### Run integration tests:
```bash
pytest tests/integration/ -v
```

### Run by marker:
```bash
pytest -m bookslot -v
pytest -m patientintake -v
pytest -m callcenter -v
```

## Test Organization Guidelines

1. **Project Tests** - Place in respective project folder (bookslot/patientintake/callcenter)
2. **Cross-App Tests** - Place in integration/ folder
3. **Framework Tests** - Place in unit/ folder
4. **Shared Utilities** - Place in common/ folder

---
Author: Lokendra Singh  
Email: qa.lokendra@gmail.com  
Website: www.sqamentor.com
