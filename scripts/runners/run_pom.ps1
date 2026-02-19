# ============================================================================
# POM Test Runner - Easy Launcher
# ============================================================================
# This script provides a simple way to launch the POM test execution CLI
# 
# Usage:
#   .\run_pom.ps1                    # Launch interactive CLI
#   .\run_pom.ps1 -Quick             # Quick mode with defaults
#   .\run_pom.ps1 -Help              # Show help
# ============================================================================

param(
    [switch]$Quick,
    [switch]$Help,
    [string]$Project,
    [string]$Environment,
    [string]$Browser
)

# Colors
function Write-Success { param($Message) Write-Host "✓ $Message" -ForegroundColor Green }
function Write-Error { param($Message) Write-Host "✗ $Message" -ForegroundColor Red }
function Write-Info { param($Message) Write-Host "ℹ $Message" -ForegroundColor Cyan }
function Write-Warning { param($Message) Write-Host "⚠ $Message" -ForegroundColor Yellow }

# Banner
function Show-Banner {
    Write-Host ""
    Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "   🎯 POM TEST EXECUTION LAUNCHER" -ForegroundColor Cyan
    Write-Host "   Interactive Page Object Model Test Runner" -ForegroundColor Cyan
    Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host ""
}

# Help
function Show-Help {
    Show-Banner
    Write-Host "USAGE:" -ForegroundColor Yellow
    Write-Host "  .\run_pom.ps1                    Launch interactive CLI" -ForegroundColor White
    Write-Host "  .\run_pom.ps1 -Quick             Quick mode with defaults" -ForegroundColor White
    Write-Host "  .\run_pom.ps1 -Help              Show this help" -ForegroundColor White
    Write-Host ""
    Write-Host "PARAMETERS:" -ForegroundColor Yellow
    Write-Host "  -Project <name>                  Project: bookslot, callcenter, patientintake" -ForegroundColor White
    Write-Host "  -Environment <env>               Environment: staging, production" -ForegroundColor White
    Write-Host "  -Browser <browser>               Browser: chromium, firefox, webkit, chrome, msedge" -ForegroundColor White
    Write-Host "  -Quick                           Skip prompts, use defaults" -ForegroundColor White
    Write-Host ""
    Write-Host "EXAMPLES:" -ForegroundColor Yellow
    Write-Host "  .\run_pom.ps1" -ForegroundColor Green
    Write-Host "    → Interactive mode with all options" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  .\run_pom.ps1 -Quick" -ForegroundColor Green
    Write-Host "    → Quick execution with defaults (bookslot, staging, chromium)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  .\run_pom.ps1 -Project bookslot -Environment production" -ForegroundColor Green
    Write-Host "    → Run bookslot tests on production (interactive for other options)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "FEATURES:" -ForegroundColor Yellow
    Write-Host "  ✓ Pre-flight validation" -ForegroundColor Green
    Write-Host "  ✓ Interactive project/environment selection" -ForegroundColor Green
    Write-Host "  ✓ Browser configuration" -ForegroundColor Green
    Write-Host "  ✓ Test scope selection" -ForegroundColor Green
    Write-Host "  ✓ Human behavior simulation" -ForegroundColor Green
    Write-Host "  ✓ Parallel execution options" -ForegroundColor Green
    Write-Host "  ✓ HTML & Allure reports" -ForegroundColor Green
    Write-Host ""
    Write-Host "For detailed guide, see: POM_CLI_GUIDE.md" -ForegroundColor Cyan
    Write-Host ""
    exit 0
}

# Validation
function Test-Prerequisites {
    Write-Info "Checking prerequisites..."
    
    $issues = @()
    
    # Check Python
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Python installed: $pythonVersion"
        } else {
            $issues += "Python not found"
            Write-Error "Python not found"
        }
    } catch {
        $issues += "Python not found"
        Write-Error "Python not found"
    }
    
    # Check pytest
    try {
        $pytestVersion = pytest --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "pytest installed"
        } else {
            $issues += "pytest not installed"
            Write-Error "pytest not installed"
        }
    } catch {
        $issues += "pytest not installed"
        Write-Error "pytest not installed"
    }
    
    # Check Playwright
    try {
        $playwrightVersion = playwright --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Playwright installed"
        } else {
            $issues += "Playwright not installed"
            Write-Warning "Playwright not installed"
        }
    } catch {
        $issues += "Playwright not installed"
        Write-Warning "Playwright not installed"
    }
    
    # Check CLI script
    if (Test-Path "run_pom_tests_cli.py") {
        Write-Success "POM CLI script found"
    } else {
        $issues += "run_pom_tests_cli.py not found"
        Write-Error "run_pom_tests_cli.py not found"
    }
    
    Write-Host ""
    
    if ($issues.Count -gt 0) {
        Write-Warning "Found $($issues.Count) issue(s)"
        
        $continue = Read-Host "Continue anyway? (y/N)"
        if ($continue -ne 'y' -and $continue -ne 'Y') {
            Write-Info "Execution cancelled"
            exit 1
        }
    } else {
        Write-Success "All prerequisites satisfied!"
    }
    
    Write-Host ""
}

# Quick Mode
function Start-QuickMode {
    Write-Info "Quick Mode: Using defaults..."
    Write-Host "  Project: bookslot" -ForegroundColor Cyan
    Write-Host "  Environment: staging" -ForegroundColor Cyan
    Write-Host "  Browser: chromium" -ForegroundColor Cyan
    Write-Host "  Mode: headed" -ForegroundColor Cyan
    Write-Host "  Human Behavior: enabled" -ForegroundColor Cyan
    Write-Host ""
    
    $continue = Read-Host "Continue with these defaults? (Y/n)"
    if ($continue -eq 'n' -or $continue -eq 'N') {
        Write-Info "Switching to interactive mode..."
        return $false
    }
    
    Write-Host ""
    Write-Info "Launching tests..."
    
    # Build quick command
    $command = "pytest tests/integration --project=bookslot --env=staging --browser=chromium -m human_like -v --html=reports/pom_quick_test_$(Get-Date -Format 'yyyyMMdd_HHmmss').html --self-contained-html"
    
    Write-Host "Command: $command" -ForegroundColor Green
    Write-Host ""
    
    # Execute
    Invoke-Expression $command
    
    return $true
}

# Main
function Main {
    Show-Banner
    
    # Handle help
    if ($Help) {
        Show-Help
    }
    
    # Run prerequisites check
    Test-Prerequisites
    
    # Handle quick mode
    if ($Quick) {
        $executed = Start-QuickMode
        if ($executed) {
            exit $LASTEXITCODE
        }
    }
    
    # Launch interactive CLI
    Write-Info "Launching interactive POM CLI..."
    Write-Host ""
    
    try {
        # Build args if provided
        $args = @()
        if ($Project) { $args += "--project=$Project" }
        if ($Environment) { $args += "--env=$Environment" }
        if ($Browser) { $args += "--browser=$Browser" }
        
        # Launch Python CLI
        if ($args.Count -gt 0) {
            # Note: The Python CLI doesn't support direct args yet, so this is for future enhancement
            python run_pom_tests_cli.py
        } else {
            python run_pom_tests_cli.py
        }
    } catch {
        Write-Error "Failed to launch CLI: $_"
        exit 1
    }
}

# Entry point
Main
