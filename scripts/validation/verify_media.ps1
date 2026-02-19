#!/usr/bin/env powershell
# Quick Test - Verify Screenshot & Video Recording
# ================================================

Write-Host "`n" -NoNewline
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 78) -ForegroundColor Cyan
Write-Host "SCREENSHOT & VIDEO RECORDING - VERIFICATION TEST" -ForegroundColor Cyan -NoNewline
Write-Host "`n" -NoNewline
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 78) -ForegroundColor Cyan
Write-Host "`n"

# Get initial counts
$screenshotsDir = "tests\bookslot\screenshots"
$videosDir = "videos"

$screenshotsBefore = (Get-ChildItem -Path $screenshotsDir -Filter "*.png" -ErrorAction SilentlyContinue).Count
$videosBefore = (Get-ChildItem -Path $videosDir -Filter "*.webm" -ErrorAction SilentlyContinue).Count

Write-Host "📊 Initial State:" -ForegroundColor Yellow
Write-Host "   Screenshots: $screenshotsBefore files in $screenshotsDir"
Write-Host "   Videos: $videosBefore files in $videosDir"
Write-Host ""

# Run single test
Write-Host "🚀 Running test: test_basic_info_page_loads" -ForegroundColor Green
Write-Host ("-" * 80) -ForegroundColor Gray

pytest tests/bookslot/test_bookslot_basicinfo_page1.py::TestBasicInfoPage::test_basic_info_page_loads -v --alluredir=allure-results

Write-Host ("-" * 80) -ForegroundColor Gray
Write-Host ""

# Get final counts
$screenshotsAfter = (Get-ChildItem -Path $screenshotsDir -Filter "*.png" -ErrorAction SilentlyContinue).Count
$videosAfter = (Get-ChildItem -Path $videosDir -Filter "*.webm" -ErrorAction SilentlyContinue).Count

$screenshotsCreated = $screenshotsAfter - $screenshotsBefore
$videosCreated = $videosAfter - $videosBefore

# Report results
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 78) -ForegroundColor Cyan
Write-Host "📊 RESULTS" -ForegroundColor Cyan
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 78) -ForegroundColor Cyan
Write-Host ""

if ($screenshotsCreated -gt 0) {
    Write-Host "✅ Screenshots: $screenshotsCreated new file(s) created" -ForegroundColor Green
    Write-Host "   Location: $screenshotsDir"
    $latestScreenshot = Get-ChildItem -Path $screenshotsDir -Filter "*.png" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($latestScreenshot) {
        Write-Host "   Latest: $($latestScreenshot.Name)"
    }
} else {
    Write-Host "❌ Screenshots: No new files created" -ForegroundColor Red
    Write-Host "   Expected location: $screenshotsDir"
}

Write-Host ""

if ($videosCreated -gt 0) {
    Write-Host "✅ Videos: $videosCreated new file(s) created" -ForegroundColor Green
    Write-Host "   Location: $videosDir"
    $latestVideo = Get-ChildItem -Path $videosDir -Filter "*.webm" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($latestVideo) {
        Write-Host "   Latest: $($latestVideo.Name)"
        $sizeMB = [math]::Round($latestVideo.Length / 1MB, 2)
        Write-Host "   Size: $sizeMB MB"
    }
} else {
    Write-Host "❌ Videos: No new files created" -ForegroundColor Red
    Write-Host "   Expected location: $videosDir"
}

Write-Host ""

# Check Allure results
if (Test-Path "allure-results") {
    $allureFiles = (Get-ChildItem -Path "allure-results" -Filter "*-result.json").Count
    Write-Host "📝 Allure: $allureFiles result file(s)" -ForegroundColor Cyan
    Write-Host "   Run: allure serve allure-results"
}

Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 78) -ForegroundColor Cyan

if ($screenshotsCreated -gt 0 -and $videosCreated -gt 0) {
    Write-Host "✅ SUCCESS: Both screenshots and videos are working!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. View screenshots: ls $screenshotsDir"
    Write-Host "  2. View videos: ls $videosDir"
    Write-Host "  3. Open Allure report: allure serve allure-results"
    exit 0
} elseif ($screenshotsCreated -gt 0) {
    Write-Host "⚠️  PARTIAL: Screenshots work, but videos not created" -ForegroundColor Yellow
    Write-Host "   Check Playwright installation and video recording configuration"
    exit 1
} elseif ($videosCreated -gt 0) {
    Write-Host "⚠️  PARTIAL: Videos work, but screenshots not created" -ForegroundColor Yellow
    Write-Host "   Check save_screenshot() function in test file"
    exit 1
} else {
    Write-Host "❌ FAILED: Neither screenshots nor videos were created" -ForegroundColor Red
    Write-Host "   Check test execution logs above for errors"
    exit 1
}

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 78) -ForegroundColor Cyan
