# Test Framework Dependency Installer
# Installs missing dependencies for the Test Automation Framework
# Run with: .\install_missing_dependencies.ps1

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host "  TEST FRAMEWORK DEPENDENCY INSTALLER" -ForegroundColor Green
Write-Host ("=" * 71) -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "[INFO] Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
Write-Host "       $pythonVersion" -ForegroundColor Gray

# Ask user what to install
Write-Host "`n[QUESTION] What would you like to install?" -ForegroundColor Cyan
Write-Host "  1. Critical dependencies only (playwright, loguru, anthropic)" -ForegroundColor White
Write-Host "  2. Critical + Optional (recommended)" -ForegroundColor White
Write-Host "  3. All dependencies from requirements.txt" -ForegroundColor White
Write-Host "  4. Custom selection" -ForegroundColor White
$choice = Read-Host "`nEnter choice (1-4)"

switch ($choice) {
    "1" {
        Write-Host "`n[STEP 1/3] Installing CRITICAL dependencies..." -ForegroundColor Yellow
        pip install playwright>=1.40.0 loguru>=0.7.2 anthropic>=0.18.0 pytest-playwright>=0.4.3
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "       OK - Critical packages installed" -ForegroundColor Green
        } else {
            Write-Host "       ERROR - Installation failed" -ForegroundColor Red
            exit 1
        }
        
        Write-Host "`n[STEP 2/3] Installing Playwright browsers..." -ForegroundColor Yellow
        playwright install
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "       OK - Playwright browsers installed" -ForegroundColor Green
        } else {
            Write-Host "       WARNING - Browser installation may have issues" -ForegroundColor Yellow
        }
        
        Write-Host "`n[STEP 3/3] Verifying installation..." -ForegroundColor Yellow
        python -c "import playwright; import loguru; import anthropic; print('All critical dependencies verified')" 2>$null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "       OK - Verification passed" -ForegroundColor Green
        } else {
            Write-Host "       WARNING - Some imports failed, check manually" -ForegroundColor Yellow
        }
    }
    
    "2" {
        Write-Host "`n[STEP 1/4] Installing CRITICAL dependencies..." -ForegroundColor Yellow
        pip install playwright>=1.40.0 loguru>=0.7.2 anthropic>=0.18.0 pytest-playwright>=0.4.3
        
        Write-Host "`n[STEP 2/4] Installing OPTIONAL dependencies..." -ForegroundColor Yellow
        pip install pytest-timeout>=2.1.0 imagehash>=4.3.1 pymysql>=1.1.0 psycopg2-binary>=2.9.9 mimesis>=12.1.0
        
        Write-Host "`n[STEP 3/4] Installing Playwright browsers..." -ForegroundColor Yellow
        playwright install
        
        Write-Host "`n[STEP 4/4] Verifying installation..." -ForegroundColor Yellow
        python -c "import playwright; import loguru; import anthropic; print('Installation verified')" 2>$null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "       OK - All dependencies installed successfully" -ForegroundColor Green
        }
    }
    "3" {
        Write-Host "`n[STEP 1/3] Installing ALL dependencies from requirements.txt..." -ForegroundColor Yellow
        pip install -r requirements.txt
        
        Write-Host "`n[STEP 2/3] Installing Playwright browsers..." -ForegroundColor Yellow
        playwright install
        
        Write-Host "`n[STEP 3/3] Verifying installation..." -ForegroundColor Yellow
        python -c "import playwright; print('Playwright OK')" 2>$null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "       OK - All dependencies installed successfully" -ForegroundColor Green
        }
    }
    
    "4" {
        Write-Host "`n[CUSTOM INSTALLATION]" -ForegroundColor Cyan
        
        $installPlaywright = Read-Host "Install Playwright? (y/n)"
        $installLoguru = Read-Host "Install Loguru? (y/n)"
        $installAnthropic = Read-Host "Install Anthropic (Claude)? (y/n)"
        $installOptional = Read-Host "Install Optional packages? (y/n)"
        
        $packages = @()
        if ($installPlaywright -eq "y") { $packages += "playwright>=1.40.0", "pytest-playwright>=0.4.3" }
        if ($installLoguru -eq "y") { $packages += "loguru>=0.7.2" }
        if ($installAnthropic -eq "y") { $packages += "anthropic>=0.18.0" }
        if ($installOptional -eq "y") { 
            $packages += "pytest-timeout>=2.1.0", "imagehash>=4.3.1", "pymysql>=1.1.0", "psycopg2-binary>=2.9.9", "mimesis>=12.1.0"
        }
        
        if ($packages.Count -gt 0) {
            Write-Host "`nInstalling: $($packages -join ', ')" -ForegroundColor Yellow
            pip install $packages
        }
        
        if ($installPlaywright -eq "y") {
            Write-Host "`nInstalling Playwright browsers..." -ForegroundColor Yellow
            playwright install
        }
    }
    
    default {
        Write-Host "`n[ERROR] Invalid choice. Exiting." -ForegroundColor Red
        exit 1
    }
}

# Final summary
Write-Host "`n" -NoNewline
Write-Host ("=" * 71) -ForegroundColor Cyan
Write-Host "  INSTALLATION COMPLETE" -ForegroundColor Green
Write-Host ("=" * 71) -ForegroundColor Cyan

Write-Host "`n[NEXT STEPS]" -ForegroundColor Cyan
Write-Host "  1. Test the framework:" -ForegroundColor White
Write-Host "     python -c `"from framework.intelligence import AIValidationSuggester; print('Framework OK')`"" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. Run dependency status check:" -ForegroundColor White
Write-Host "     python check_dependencies.py" -ForegroundColor Gray
Write-Host ""
Write-Host "  3. Review documentation:" -ForegroundColor White
Write-Host "     - DEPENDENCY_STATUS.md (full status report)" -ForegroundColor Gray
Write-Host "     - README.md (framework guide)" -ForegroundColor Gray
Write-Host ""
Write-Host "  4. Configure AI providers (optional):" -ForegroundColor White
Write-Host "     `$env:OPENAI_API_KEY = `"sk-your-key-here`"" -ForegroundColor Gray
Write-Host "     `$env:ANTHROPIC_API_KEY = `"sk-ant-your-key-here`"" -ForegroundColor Gray
Write-Host ""

Write-Host "[SUCCESS] Framework is ready to use!" -ForegroundColor Green
Write-Host ""
