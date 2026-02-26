# Media Capture System

**Canonical source for all screenshot, video recording, and report naming documentation.**
Merges: `Screenshot-Video-Implementation.md` · `DYNAMIC_VIDEO_NAMING_IMPLEMENTATION.md` · `Video-Naming-Update-Report.md` · `DYNAMIC_REPORT_NAMING_IMPLEMENTATION.md`

**Status:** ✅ Complete
**Last Updated:** 2026-02-19

---

## Overview

The framework automatically captures visual evidence for all tests:

| Capture Type | Format | Naming Pattern | Trigger |
|-------------|--------|----------------|---------|
| **Video** | WEBM (VP8, 1920×1080) | `project_Env_DDMMYYYY_HHMMSS.webm` | Every test |
| **Screenshot** | PNG (full page) | `test_name_YYYYMMDD_HHMMSS.png` | On demand / failure |
| **HTML Report** | HTML (self-contained) | `project_Env_DDMMYYYY_HHMMSS.html` | Every test run |

All media is automatically attached to Allure reports and saved to the filesystem.

---

## Naming Conventions

### Video Files

**Format:** `{project}_{Environment}_{DDMMYYYY}_{HHMMSS}.webm`

**Examples:**
```
bookslot_Staging_19022026_143052.webm
patientintake_Production_20022026_091530.webm
callcenter_QA_21022026_152045.webm
```

**Auto-increment on collision** (if two tests run in the same second):
```
bookslot_Staging_19022026_143052.webm      # First test
bookslot_Staging_19022026_143052_1.webm    # Second test (same second)
bookslot_Staging_19022026_143052_2.webm    # Third test
```

Safety limit: maximum 100 increments per timestamp.

### Screenshots

**Format:** `{test_name}_{YYYYMMDD_HHMMSS}.png`

**Examples:**
```
basic_info_page_loaded_20260202_131108.png
email_validation_user@example.com_20260202_131053.png
```

### HTML Reports

**Format:** `{project}_{Environment}_{DDMMYYYY}_{HHMMSS}.html`

**Examples:**
```
bookslot_Staging_19022026_143052.html
patientintake_Production_20022026_091530.html
```

Video and HTML report names use the **exact same convention** — making it trivial to correlate a report with its recording.

### Why DDMMYYYY?
- Human-readable (day-first is intuitive)
- Windows filesystem safe (no colons or slashes)
- Consistent underscore separators throughout (`_`)
- Chronological sorting works naturally at the second level

---

## Implementation

### Video Recording — Core Setup

**Location:** `conftest.py` (root) and `tests/conftest.py`

Video recording is enabled at the browser context level. The root `conftest.py` overrides the default `context` fixture to enable video for all tests using pytest-playwright's `page` fixture:

```python
# conftest.py (root) — applies to all tests using `page`
@pytest.fixture
def context(browser, tmp_path):
    videos_dir = Path("videos")
    videos_dir.mkdir(exist_ok=True)
    ctx = browser.new_context(
        record_video_dir=str(videos_dir),
        record_video_size={"width": 1920, "height": 1080}
    )
    yield ctx
    ctx.close()
```

For custom fixtures (`bookslot_page`, `patientintake_page`) in `tests/conftest.py`:

```python
@pytest.fixture
def bookslot_page(shared_browser, env, project):
    videos_dir = Path("videos")
    videos_dir.mkdir(exist_ok=True)
    context = shared_browser.new_context(
        record_video_dir=str(videos_dir),
        record_video_size={"width": 1920, "height": 1080}
    )
    page = context.new_page()
    yield page
    # Teardown: rename video, attach to Allure
    page.close()
    video_path_obj = Path(page.video.path()) if page.video else None
    if video_path_obj and video_path_obj.exists():
        new_path = generate_unique_video_filename(project, env, str(videos_dir))
        try:
            video_path_obj.rename(new_path)
            video_path = str(new_path)
        except Exception as e:
            logger.warning(f"Could not rename video: {e}")
            video_path = str(video_path_obj)
        if video_path:
            with open(video_path, "rb") as f:
                allure.attach(f.read(), name="Test Video", attachment_type=allure.attachment_type.WEBM)
    context.close()
```

### Video Naming Function

**Location:** `conftest.py` (root)

```python
def generate_unique_video_filename(
    project: str,
    environment: str,
    videos_dir: str,
    extension: str = "webm"
) -> Path:
    """
    Generate unique video filename: project_Environment_DDMMYYYY_HHMMSS.webm
    Auto-increments (_1, _2, ...) if file already exists (max 100).
    """
    timestamp = datetime.now().strftime("%d%m%Y_%H_%M_%S")
    env_cap = environment.capitalize()
    base_name = f"{project}_{env_cap}_{timestamp}"

    videos_path = Path(videos_dir)
    candidate = videos_path / f"{base_name}.{extension}"
    counter = 1
    while candidate.exists() and counter <= 100:
        candidate = videos_path / f"{base_name}_{counter}.{extension}"
        counter += 1
    return candidate
```

### Pytest Hook — Auto-Rename for `page` Fixture

The `pytest_runtest_makereport` hook in root `conftest.py` renames videos for all tests using pytest-playwright's built-in `page` fixture:

```python
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call":
        page = item.funcargs.get("page")
        if page and hasattr(page, "video") and page.video:
            try:
                video_path_obj = Path(page.video.path())
                # Detect project from test file path
                test_path = str(item.fspath)
                project = "unknown"
                for p in ["bookslot", "callcenter", "patientintake"]:
                    if p in test_path.lower():
                        project = p
                        break
                env = item.config.getoption("--env", default="staging")
                new_path = generate_unique_video_filename(project, env, "videos")
                video_path_obj.rename(new_path)
                with open(new_path, "rb") as f:
                    allure.attach(f.read(), name="Test Video",
                                  attachment_type=allure.attachment_type.WEBM)
            except Exception as e:
                logger.warning(f"Video rename failed: {e}")
```

### Screenshot Saving

**Helper function** (used in test files):

```python
def save_screenshot(page, test_name: str, description: str = ""):
    """Save screenshot to filesystem AND attach to Allure report."""
    screenshots_dir = Path("screenshots")
    screenshots_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{test_name}_{timestamp}.png"
    path = screenshots_dir / filename
    page.screenshot(path=str(path), full_page=True)
    with open(path, "rb") as f:
        allure.attach(f.read(), name=description or test_name,
                      attachment_type=allure.attachment_type.PNG)
    return str(path)
```

### Dynamic HTML Report Naming

**Location:** `conftest.py` (root) — `pytest_configure` hook

```python
def generate_unique_report_filename(project: str, environment: str,
                                    reports_dir: str = "reports") -> str:
    """
    Generate unique HTML report filename:
    projectname_EnvironmentName_DDMMYYYY_HHMMSS.html
    """
    timestamp = datetime.now().strftime("%d%m%Y_%H%M%S")
    env_cap = environment.capitalize()
    base_name = f"{project}_{env_cap}_{timestamp}"
    Path(reports_dir).mkdir(exist_ok=True)
    candidate = Path(reports_dir) / f"{base_name}.html"
    counter = 1
    while candidate.exists() and counter <= 100:
        candidate = Path(reports_dir) / f"{base_name}_{counter}.html"
        counter += 1
    return str(candidate)

def pytest_configure(config):
    """Set dynamic HTML report name (only when no custom --html provided)."""
    if not hasattr(config.option, 'htmlpath') or config.option.htmlpath == "reports/test_report.html":
        project = getattr(config.option, 'project', 'unknown') or 'unknown'
        env = getattr(config.option, 'env', 'staging') or 'staging'
        config.option.htmlpath = generate_unique_report_filename(project, env)
```

**`pytest.ini`** — static path removed:
```ini
# Before:
--html=reports/test_report.html

# After:
--self-contained-html
# (dynamic naming handled by conftest.py pytest_configure hook)
```

---

## Directory Structure

```
videos/
├── bookslot_Staging_19022026_143052.webm
├── bookslot_Staging_19022026_143100.webm
├── patientintake_Staging_19022026_143052.webm
└── callcenter_Production_20022026_091530.webm

screenshots/
├── bookslot/
│   ├── basic_info_page_loaded_20260202_131108.png
│   └── email_validation_user@example.com_20260202_131053.png
├── patientintake/
└── callcenter/

reports/
├── bookslot_Staging_19022026_143052.html
├── bookslot_Production_19022026_150030.html
└── patientintake_Staging_20022026_091530.html
```

---

## Files Modified

| File | Change |
|------|--------|
| `conftest.py` (root) | Added `generate_unique_video_filename()`, `generate_unique_report_filename()`, updated `pytest_configure`, updated `pytest_runtest_makereport` hook |
| `tests/conftest.py` | Updated `bookslot_page` and `patientintake_page` fixtures with video recording + dynamic naming; added `env`/`project` parameters |
| `pytest.ini` | Removed static `--html=reports/test_report.html`, kept `--self-contained-html` |
| `config/environments.yaml` | Changed `output_file: "reports/test_report.html"` → `output_dir: "reports"` |

---

## Usage

### Running Tests with Media Capture

```bash
# All media captured automatically
pytest recorded_tests/bookslot/test_bookslot_complete_workflow.py \
  --env=staging --project=bookslot -v

# Multiple tests in same second → auto-increment
pytest tests/ --env=staging --project=bookslot -n 2

# Custom report filename override
pytest tests/ --env=staging --project=bookslot \
  --html=my_custom_report.html --self-contained-html
```

### Verifying Captures

```bash
# Check video files (PowerShell)
Get-ChildItem -Path videos\ -Filter "*.webm" | Select-Object Name, LastWriteTime

# Verify format
Get-ChildItem -Path videos\ -Filter "*.webm" | ForEach-Object {
    if ($_.Name -match '^\w+_\w+_\d{8}_\d{2}_\d{2}_\d{2}(_\d+)?\.webm$') {
        Write-Host "✓ $($_.Name)" -ForegroundColor Green
    }
}

# Generate Allure report to view media
allure serve allure-results
```

---

## Performance Characteristics

| Capture Type | Execution Overhead | Disk Space per Test |
|-------------|-------------------|---------------------|
| Video recording | ~5–10% slower | 1–5 MB per video |
| Screenshot | < 1% | 50–200 KB per screenshot |
| HTML report | Negligible | ~500 KB–2 MB |

---

## Troubleshooting

### No Videos Saved
1. Check `videos/` directory exists
2. Ensure Playwright is installed: `pip install playwright && playwright install`
3. Verify browser context fixture has `record_video_dir` set
4. Videos are only finalized when `context.close()` is called — ensure fixtures properly close context

### Videos Still Have Hash Names
- Cause: Tests not receiving `--env` and `--project` options
- Solution: Pass `--env=staging --project=bookslot` on command line

### Video Rename Fails
- Cause: File permissions or Playwright still writing
- Solution: Check logs for detailed error; `context.close()` must complete before rename

### No Screenshots Saved
1. Check screenshots directory exists
2. Verify `save_screenshot()` is being called (not just `allure.attach(page.screenshot())`)
3. Check for file permission errors in console

### Videos Not in Allure Report
1. Install allure-pytest: `pip install allure-pytest`
2. Delete `allure-results/` and re-run tests
3. Check `pytest_runtest_makereport` hook is executing

---

## Audit Trail

All media capture events are logged to the audit trail:

```json
{
  "event": "video_recording",
  "action": "start",
  "fixture": "bookslot_page",
  "video_dir": "videos",
  "test_name": "tests/bookslot/test_flow.py::test_booking"
}
```

```json
{
  "event": "video_recording",
  "action": "stop",
  "fixture": "bookslot_page",
  "video_path": "videos/bookslot_Staging_19022026_143052.webm",
  "test_name": "tests/bookslot/test_flow.py::test_booking"
}
```

---

## Future Enhancements

- [ ] Video subdirectories by date (`videos/2026-02-19/`)
- [ ] Test name in video filename (`bookslot_Staging_test_login_19022026_143052.webm`)
- [ ] Post-processing / compression for large videos
- [ ] Keep-only-failures mode (delete passing test videos)
- [ ] Cloud upload (S3 / Azure Blob) with links in HTML report
