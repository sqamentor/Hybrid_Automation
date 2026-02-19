# Quick Start Script - Launch Interactive Test Launcher (PowerShell)
# This script provides an easy way to start the interactive CLI

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "   HYBRID AUTOMATION FRAMEWORK - Interactive Test Launcher" -ForegroundColor White
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "   Starting interactive mode..." -ForegroundColor Green
Write-Host "   Follow the on-screen prompts to run your tests!" -ForegroundColor Yellow
Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Launch interactive mode
automation

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "   Thank you for using the Hybrid Automation Framework!" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Keep window open
Read-Host -Prompt "Press Enter to exit"
