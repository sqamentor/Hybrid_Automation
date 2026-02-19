# Modern Multi-Project CLI Implementation

## Executive Summary

Successfully modernized the CLI to support **multi-project architecture** with **context-aware execution** from any directory, following modern automation standards like Nx, Turborepo, and npm workspaces.

---

## Overview

### What Changed

Transformed the CLI from a basic single-entry pattern to a **modern multi-project framework** with:

1. **Project Discovery** - List, inspect, and detect projects
2. **Context Awareness** - Run from any directory in the workspace
3. **Modern Commands** - `test`, `projects`, `context` subcommands
4. **Root Execution** - Execute commands from anywhere

### Key Features

✅ **Multi-project support** - bookslot, callcenter, patientintake  
✅ **Project auto-detection** - From URL patterns or directory context  
✅ **Workspace awareness** - Detects root even from subdirectories  
✅ **Modern CLI patterns** - Follows Nx, Turborepo, and npm standards  
✅ **Context inspection** - Shows current location and detected project  

---

## Modern CLI Architecture

### Industry Comparison

| Framework | Pattern | Example |
|-----------|---------|---------|
| **Nx** | `nx run project:target` | `nx run api:test` |
| **Turborepo** | `turbo run test --filter=project` | `turbo run test --filter=web` |
| **Lerna** | `lerna run test --scope=project` | `lerna run test --scope=api` |
| **npm workspaces** | `npm run test -w project` | `npm run test -w @app/web` |
| **Our Framework** | `automation test project` | `automation test bookslot --env staging` |

### Our Modern Pattern

```bash
# Project Management
automation projects list              # List all projects
automation projects info bookslot     # Show project details
automation projects detect <url>      # Detect project from URL

# Context Awareness
automation context                    # Show current location/project

# Testing (Modern Shorthand)
automation test bookslot --env staging    # Run project tests
automation run-pom --project bookslot     # Traditional pattern

# Recording
automation record --project bookslot      # Record tests

# Help
automation --help                         # Show all commands
automation projects --help                # Show projects subcommands
```

---

## New Commands

### 1. `automation projects` - Multi-Project Management

Complete project lifecycle management.

#### List All Projects
```bash
automation projects list
```

**Output:**
```
📋 Available Projects:

  📁 bookslot
     ID: BookSlot Appointment System
     Description: Patient appointment booking and slot management system        
     Team: Booking Team

  📁 callcenter
     ID: Call Center Management System
     Description: Call center operations and appointment management
     Team: Call Center Team

  📁 patientintake
     ID: Patient Intake System
     Description: Patient intake and appointment management system
     Team: Patient Services Team

Total: 3 project(s)
```

#### Show Project Details
```bash
automation projects info bookslot
```

**Output:**
```
📁 Project: BookSlot Appointment System

📝 Basic Information:
  ID: bookslot
  Name: BookSlot Appointment System
  Description: Patient appointment booking and slot management system
  Team: Booking Team
  Contact: booking-team@example.com

🌐 URL Patterns (for auto-detection):
  - bookslot.*
  - .*booking.*
  - .*appointment.*book.*

🌍 Environments:
  staging:
    UI URL: https://bookslot-staging.centerforvein.com
    API URL: https://staging-api.centerforvein.com
  production:
    UI URL: https://bookslots.centerforvein.com
    API URL: https://api-prod.centerforvein.com

📂 Directory Structure:
  pages: pages\bookslot ✓
  recorded_tests: recorded_tests\bookslot ✓
  test_data: test_data\bookslot ✓

⚙️  Settings:
  default_timeout: 30000
  requires_verification: True
  has_multi_step_flow: True
```

#### Detect Project from URL
```bash
automation projects detect https://bookslot-staging.centerforvein.com
```

**Output:**
```
🔍 Project Detection Results:

  URL: https://bookslot-staging.centerforvein.com
  Detected Project: bookslot
  Environment: staging
  Full Name: BookSlot Appointment System

📂 Target Directories:
  pages: pages\bookslot
  recorded_tests: recorded_tests\bookslot
  test_data: test_data\bookslot
```

### 2. `automation context` - Workspace Context

Shows current location within the workspace and detected project.

```bash
automation context
```

**Output from root:**
```
📍 Current Context:

  ✓ Inside workspace
  📁 Workspace Root: C:\path\to\Hybrid_Automation  
  📂 Current Dir: .
  ⚠️  No project detected (not in project-specific directory)

📦 Available Projects:
  • bookslot             BookSlot Appointment System
  • callcenter           Call Center Management System
  • patientintake        Patient Intake System
```

**Output from project directory:**
```
📍 Current Context:

  ✓ Inside workspace
  📁 Workspace Root: C:\path\to\Hybrid_Automation  
  📂 Current Dir: pages/bookslot
  🎯 Detected Project: bookslot

📦 Available Projects:
  • bookslot             BookSlot Appointment System ← current
  • callcenter           Call Center Management System
  • patientintake        Patient Intake System
```

### 3. `automation test` - Modern Test Shorthand

Simplified project test execution (maps to `run-pom`).

```bash
# Run specific project
automation test bookslot --env staging

# Interactive mode
automation test
```

---

## Root Execution Capability

### How It Works

The CLI now **detects the workspace root** automatically by searching for marker files:
- `pyproject.toml`
- `pytest.ini`
- `framework/` directory
- `.git` directory

This enables running commands from **any directory** within the workspace.

### Examples

```bash
# From root directory
cd C:\Hybrid_Automation
automation projects list            # ✓ Works

# From project directory
cd C:\Hybrid_Automation\pages\bookslot
automation context                  # ✓ Shows bookslot as current project

# From tests directory
cd C:\Hybrid_Automation\recorded_tests\callcenter
automation test callcenter          # ✓ Works, detects context

# From config directory
cd C:\Hybrid_Automation\config
automation projects info bookslot   # ✓ Works

# From nested subdirectory
cd C:\Hybrid_Automation\pages\bookslot\components
automation context                  # ✓ Still detects bookslot project
```

---

## Project Configuration

### Structure

Projects are defined in `config/projects.yaml`:

```yaml
projects:
  bookslot:
    name: "BookSlot Appointment System"
    description: "Patient appointment booking system"
    
    # URL patterns for auto-detection
    url_patterns:
      - "bookslot.*"
      - ".*booking.*"
    
    # Environments
    environments:
      staging:
        ui_url: "https://bookslot-staging.example.com"
        api_url: "https://api-staging.example.com"
      production:
        ui_url: "https://bookslots.example.com"
        api_url: "https://api.example.com"
    
    # Directory paths
    paths:
      pages: "pages/bookslot"
      recorded_tests: "recorded_tests/bookslot"
      test_data: "test_data/bookslot"
    
    # Settings
    settings:
      default_timeout: 30000
      requires_verification: true
    
    # Ownership
    team: "Booking Team"
    contact: "booking-team@example.com"
```

### Directory Structure

```
Hybrid_Automation/
├── config/
│   └── projects.yaml          # Project definitions
├── framework/
│   ├── cli/
│   │   ├── __init__.py        # Main router
│   │   ├── projects.py        # Project management (NEW)
│   │   ├── context.py         # Context detection (NEW)
│   │   ├── run.py             # General test runner
│   │   ├── run_pom.py         # POM test runner
│   │   ├── record.py          # Recording CLI
│   │   └── simulate.py        # Simulation CLI
│   └── core/
│       └── project_manager.py # Project detection engine
├── pages/
│   ├── bookslot/
│   ├── callcenter/
│   └── patientintake/
├── recorded_tests/
│   ├── bookslot/
│   ├── callcenter/
│   └── patientintake/
└── test_data/
    ├── bookslot/
    ├── callcenter/
    └── patientintake/
```

---

## Technical Implementation

### 1. Project Management CLI (`framework/cli/projects.py`)

**New file** providing:
- `list` - List all projects
- `info <name>` - Show project details
- `detect <url>` - Detect project from URL
- `add` - Add new project (planned)

### 2. Context Detection (`framework/cli/context.py`)

**New file** providing:
- Workspace root detection
- Current project detection from directory
- Context information gathering
- Path resolution from any location

**Key Function:**
```python
class WorkspaceContext:
    def _find_workspace_root(self):
        """Search upward for workspace markers"""
        markers = ['pyproject.toml', 'pytest.ini', 'framework', '.git']
        # Search up to 10 levels for markers
        
    def _detect_current_project(self):
        """Detect project from directory structure"""
        # Check if in pages/, recorded_tests/, test_data/
        # Extract project name from path
```

### 3. Main Router Updates (`framework/cli/__init__.py`)

**Updated** to add:
- `projects` subcommand routing
- `context` subcommand routing
- `test` alias for `run-pom`
- Enhanced help text

**New Routing:**
```python
elif command == 'projects':
    from framework.cli.projects import main as projects_main
    return projects_main(remaining_args)

elif command == 'context':
    from framework.cli.context import print_workspace_info
    print_workspace_info()
    return 0

elif command == 'test':
    # Modern shorthand for project tests
    from framework.cli.run_pom import main as run_pom_main
    return run_pom_main(remaining_args)
```

---

## Usage Examples

### Developer Workflow

#### 1. Explore Projects
```bash
# List all available projects
automation projects list

# Get detailed info about a specific project
automation projects info bookslot

# Check current context
automation context
```

#### 2. Run Tests
```bash
# Interactive mode (recommended for beginners)
automation test

# Direct execution
automation test bookslot --env staging

# Traditional pattern
automation run-pom --project bookslot --env production
```

#### 3. Record Tests
```bash
# Interactive recording with project auto-detection
automation record

# Direct recording for specific project
automation record --project bookslot --url https://bookslot.example.com
```

#### 4. Check Context
```bash
# From any directory
cd pages/bookslot
automation context
# Shows: Detected Project: bookslot

cd recorded_tests/callcenter
automation context
# Shows: Detected Project: callcenter
```

### CI/CD Integration

```bash
# Run tests for specific project in CI
automation test bookslot --env staging --parallel 4 --headless

# Run all projects
for project in bookslot callcenter patientintake; do
  automation test $project --env production
done

# With npm-style workspaces pattern
automation test --project bookslot --env staging
```

---

## Benefits Achieved

### 1. Modern Multi-Project Support
✅ Industry-standard patterns (Nx, Turborepo, npm workspaces)  
✅ Clear project separation and organization  
✅ Easy to add/remove projects  
✅ Project-specific configurations and paths

### 2. Improved Developer Experience  
✅ Context-aware execution from any directory  
✅ No need to remember `cd` to root  
✅ Automatic project detection  
✅ Friendly, informative CLI output

### 3. Better Discoverability
✅ `automation projects list` - See all projects  
✅ `automation projects info` - Learn about each project  
✅ `automation context` - Know where you are  
✅ Clear help text and examples

### 4. Enterprise-Ready
✅ Scalable to many projects  
✅ Team/ownership metadata  
✅ URL-based project detection  
✅ Environment-aware configurations

---

## Future Enhancements

### Planned Features

1. **Interactive Project Creation**
   ```bash
   automation projects add
   ```
   Guided wizard to add new projects

2. **Project Templates**
   ```bash
   automation projects create myproject --template=spa
   ```
   Create project from template

3. **Project Dependencies**
   ```yaml
   dependencies:
     - callcenter
     - patientintake
   ```
   Run dependent projects in order

4. **Workspace Commands**
   ```bash
   automation run-all tests        # Run tests for all projects
   automation lint --all           # Lint all projects
   ```

5. **Project Groups**
   ```yaml
   groups:
     frontend: [bookslot, callcenter]
     backend: [api, database]
   ```
   Group-based operations

---

## Comparison: Before vs After

### Before (Basic CLI)

```bash
# Limited to root directory execution
cd C:\Hybrid_Automation
automation-run

# No project discovery
# Manual project selection required
# No context awareness
```

**Issues:**
- Must be in root directory
- No project listing/discovery
- Separate CLI commands (`automation-run`, `automation-record`)
- No context information

### After (Modern Multi-Project CLI)

```bash
# Run from anywhere
cd C:\Hybrid_Automation\pages\bookslot
automation context              # Shows current project
automation projects list        # Discovers all projects
automation test bookslot        # Modern pattern

# Unified CLI with subcommands
automation projects info bookslot
automation test --project callcenter
automation context
```

**Benefits:**
✅ Run from any directory (root detection)  
✅ Project discovery and inspection  
✅ Context awareness  
✅ Modern commands (`test`, `projects`, `context`)  
✅ Unified CLI entry point

---

## Standards Compliance

### Follows Modern Patterns

| Standard | Implementation |
|----------|----------------|
| **Nx** | `automation test <project>` |
| **Turborepo** | Project filtering and parallel execution |
| **npm workspaces** | `--project` flag for workspace selection |
| **Monorepo tools** | Root detection and context awareness |

### Best Practices Applied

✅ **Single entry point** - `automation` command  
✅ **Subcommand routing** - `projects`, `test`, `context`  
✅ **Workspace root detection** - Run from anywhere  
✅ **Project auto-detection** - From URL or directory  
✅ **Help system** - `--help` for all commands  
✅ **Exit codes** - Proper 0/1/130 codes  
✅ **Error handling** - Graceful failures with messages

---

## Testing

### Manual Testing

```bash
# Test project listing
automation projects list

# Test project info
automation projects info bookslot
automation projects info callcenter
automation projects info patientintake

# Test context detection
cd C:\Hybrid_Automation
automation context

cd pages/bookslot
automation context

cd recorded_tests/callcenter
automation context

# Test project detection from URL
automation projects detect https://bookslot-staging.centerforvein.com
automation projects detect https://callcenter.centerforvein.com

# Test help system
automation --help
automation projects --help
```

### Verified Features

✅ Projects list command  
✅ Project info command  
✅ Project detection from URL  
✅ Context detection from root  
✅ Context detection from project directories  
✅ Workspace root detection  
✅ Help system  
✅ Error handling

---

## Documentation

### Files Created

1. `framework/cli/projects.py` - Project management commands
2. `framework/cli/context.py` - Context detection utilities
3. `Framework-Knowledge-Center/10-Rules-And-Standards/MODERN_MULTI_PROJECT_CLI.md` - This document

### Files Modified

1. `framework/cli/__init__.py` - Added projects, context, test commands
2. `pyproject.toml` - Already has correct entry points

---

## Conclusion

Successfully modernized the CLI to support **multi-project architecture** with **context-aware execution**, aligning with industry standards from Nx, Turborepo, and npm workspaces.

### Key Achievements

✅ **Multi-project support** - List, inspect, detect projects  
✅ **Context awareness** - Run from any directory  
✅ **Modern commands** - `projects`, `context`, `test`  
✅ **Root execution** - Automatic workspace detection  
✅ **Industry standards** - Nx/Turborepo patterns  
✅ **Developer experience** - Intuitive, discoverable CLI

### Impact

- **Scalability**: Easy to add new projects
- **Usability**: Run from anywhere in workspace
- **Discoverability**: Clear project listing and info
- **Maintainability**: Well-organized multi-project structure
- **Enterprise-ready**: Team ownership, environment configs

**Status:** ✅ Complete and Production-Ready

---

**Date Implemented:** February 19, 2026  
**Author:** Lokendra Singh  
**Version:** 2.0.0 (Modern Multi-Project CLI)
