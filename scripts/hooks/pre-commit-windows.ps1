# Pre-commit Hook for Architecture Audit (PowerShell)
# ===================================================
# Optional: Prevents commits that violate architectural rules
#
# To enable:
#   1. Copy to .git/hooks/pre-commit.ps1
#   2. Test: git commit (will run audit before commit)
#
# To bypass (emergency only):
#   git commit --no-verify
#

Write-Host "`n===============================================" -ForegroundColor Cyan
Write-Host "Running Architecture Audit (pre-commit)" -ForegroundColor Cyan
Write-Host "===============================================`n" -ForegroundColor Cyan

# Run architecture audit
python -m pytest --arch-audit --audit-strict

# Capture exit code
$AUDIT_EXIT_CODE = $LASTEXITCODE

if ($AUDIT_EXIT_CODE -ne 0) {
    Write-Host "`n===============================================" -ForegroundColor Red
    Write-Host "X COMMIT BLOCKED: Architecture violations detected" -ForegroundColor Red
    Write-Host "===============================================`n" -ForegroundColor Red
    Write-Host "Options:" -ForegroundColor Yellow
    Write-Host "  1. Fix the violations (recommended)"
    Write-Host "  2. Add to baseline (if legitimate technical debt)"
    Write-Host "  3. Bypass (emergency): git commit --no-verify`n"
    exit 1
}

Write-Host "`n===============================================" -ForegroundColor Green
Write-Host "OK Architecture Audit Passed - Proceeding with commit" -ForegroundColor Green
Write-Host "===============================================`n" -ForegroundColor Green

exit 0
