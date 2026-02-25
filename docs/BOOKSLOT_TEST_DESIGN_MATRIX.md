# Bookslot Test Design Matrix (POM + 7-Step Sequential Flow + URL Testing)

## 📋 IMPLEMENTATION STATUS

| Component | Status | Details |
|---|---|---|
| Layer A: Page-Level Tests | ✅ **COMPLETED** | All 7 pages (P1-P7) with Smoke, Validation, Regression test classes |
| Layer B: E2E Flow Tests | ✅ **COMPLETED** | E2E tests with proper markers (e2e, critical, ui_sequential) |
| Layer C: Integration Tests | ❌ **AVOIDED** | UI->API->DB validations explicitly excluded per user requirement |
| **Layer D: URL Testing** | ✅ **COMPLETED** | **101 URL workflow tests across P1-P7 pages** |
| Navigation Preconditions | ✅ **COMPLETED** | All fixtures (at_basic_info through at_success) implemented |
| Marker Strategy | ✅ **COMPLETED** | All markers implemented (bookslot, smoke, validation, regression, e2e, critical, ui_sequential, negative, workflow_persistence) |
| Component Coverage (6 checks) | ⚠️ **PARTIAL** | Visible, Enabled, Input, Validation, Navigation - implemented. State behavior - partial |
| Accessibility Testing | ⚠️ **PARTIAL** | Only P1 has accessibility tests. P2-P7 missing accessibility class |
| **Test Count** | ✅ **240 TESTS** | **Page Tests: 139** (P1: 31, P2: 12, P3: 15, P4: 13, P5: 12, P6: 13, P7: 16, E2E: ~27) + **URL Tests: 101** (P1: 10, P2: 11, P3: 11, P4: 11, P5: 11, P6: 11, P7: 11, Parametrized: ~25) |

### 🎉 NEWLY COMPLETED ITEMS (2026-02-25)

#### ✅ Layer D: URL Testing Infrastructure (101 tests)

**Files Created:**
1. **Microservices Layer** (397 lines)
   - `framework/microservices/url_testing_service.py`
   - URLTestingService, URLDataService, URLValidationService
   - Health checks, lifecycle management, event-driven architecture

2. **Testing Utilities** (745 lines)
   - `framework/testing/url_data_manager.py` (198 lines) - Data orchestration
   - `framework/testing/url_builder.py` (274 lines) - URL construction
   - `framework/testing/url_validator.py` (273 lines) - Multi-level validation

3. **Test Data** (642 lines)
   - `test_data/bookslot/bookslot_workflows.json` - 35 workflow test cases

4. **Configuration** (254+ lines)
   - `config/url_testing.yaml` - Service configuration
   - `config/projects.yaml` - Extended with url_testing section

5. **Fixtures** (182 lines added)
   - `tests/bookslot/fixtures/__init__.py` - 13 new URL testing fixtures
   - Session-scoped services, function-scoped utilities, data fixtures

6. **Test Suites** (1,850+ lines)
   - `tests/bookslot/url_testing/test_workflow_urls_p1.py` (297 lines) - 10 tests
   - `tests/bookslot/url_testing/test_workflow_urls_p2.py` (288 lines) - 11 tests
   - `tests/bookslot/url_testing/test_workflow_urls_p3.py` (311 lines) - 11 tests
   - `tests/bookslot/url_testing/test_workflow_urls_p4.py` (294 lines) - 11 tests
   - `tests/bookslot/url_testing/test_workflow_urls_p5.py` (335 lines) - 11 tests
   - `tests/bookslot/url_testing/test_workflow_urls_p6.py` (300 lines) - 11 tests
   - `tests/bookslot/url_testing/test_workflow_urls_p7.py` (326 lines) - 11 tests

**Total New Code:** ~4,000 lines across 16 files (12 new + 4 enhanced)

**Test Coverage:**
- ✅ Query string parameter validation (P1-P7)
- ✅ Form prefilling from URL parameters
- ✅ Workflow ID persistence and extraction
- ✅ Multiple parameter combinations (parametrized tests)
- ✅ Invalid parameter handling (negative tests)
- ✅ Performance validation (<5s load time threshold)
- ✅ URL parsing and component extraction
- ✅ State persistence after page refresh
- ✅ Data-driven testing (multiple scenarios per page)
- ✅ Special characters and encoding
- ✅ Multi-channel notifications (email/SMS)
- ✅ Complex workflow scenarios

**Architecture Compliance:**
- ✅ Extends BaseService pattern from framework
- ✅ Follows Manager/Builder/Validator patterns
- ✅ Centralized fixture system (no new conftest.py)
- ✅ Reuses existing data loading utilities
- ✅ Zero conflicts with existing 139 tests
- ✅ Allure reporting integration
- ✅ Comprehensive logging and error handling
- ✅ Type hints throughout

**Validation Results:**
- ✅ **101 tests collected successfully** (`pytest --collect-only`)
- ✅ Zero import errors after logger fixes
- ✅ All pytest markers registered in pytest.ini
- ✅ No conflicts with existing test structure

### ⏳ PENDING ITEMS

1. **Accessibility Tests for P2-P7** (Only P1 has `TestBasicInfoAccessibility` class)
   - Add `TestEventTypeAccessibility` class to test_p2_event_type.py
   - Add `TestSchedulerAccessibility` class to test_p3_scheduler.py
   - Add `TestPersonalInfoAccessibility` class to test_p4_personal_info.py
   - Add `TestReferralAccessibility` class to test_p5_referral.py
   - Add `TestInsuranceAccessibility` class to test_p6_insurance.py
   - Add `TestSuccessAccessibility` class to test_p7_success.py

2. **Complete State Behavior Testing** (Section 2, Point 5)
   - Verify selected/unselected states for all radio buttons
   - Verify checked/unchecked states for all checkboxes
   - Verify active/inactive states for all toggles
   - Verify focus/blur states for all form fields

3. **Extended Data-Driven Coverage** (Section 4, Regression column)
   - Localization testing for P1 (multiple languages if supported)
   - Extended option permutation testing for P2, P5
   - Extended slot/date combination testing for P3
   - Extended payer/provider matrix testing for P6

---

## Goal
Design test cases for Bookslot's **7-step sequential flow** where each page depends on the previous page (except Basic Info), while keeping tests stable, maintainable, and fast in CI.

**7-step user journey:**
`Basic Info (P1) -> Event Type (P2) -> Scheduler (P3) -> Personal Info (P4) -> Referral (P5) -> Insurance (P6) -> Success (P7)`

---

## 1) Recommended Test Layers

### ✅ Layer A: Component/Page-Level Tests (primary) - **IMPLEMENTED**
- Validate one page's controls and rules (visibility, clickability, field behavior, validation messages).
- Reach target page through a reusable **navigation precondition** in the same test.
- No dependency between test cases.
- Can run in parallel for speed.
- **Status:** All 7 pages implemented with test files (test_p1_basic_info.py through test_p7_success.py)

### ✅ Layer B: Sequential E2E Journey Tests (small, critical set) - **IMPLEMENTED**
- Validate business journey across all 7 steps in a single test.
- Keep only a few critical paths (happy path + selected negatives).
- Run serial when sequence-sensitive.
- **Status:** E2E tests implemented in tests/bookslot/e2e/ (test_happy_path.py, test_complete_journeys.py)

### ❌ Layer C: Integration/Workflow Tests - **AVOIDED (PER USER REQUIREMENT)**
- ~~Add UI -> API -> DB validations for critical checkpoints only.~~
- **Status:** EXPLICITLY EXCLUDED - Not implemented per user decision to avoid integration testing layer

---

## 2) Mandatory Component Coverage per Page

For **every interactive component** on a page, include these checks as applicable:

1. **✅ Visible**: element is rendered and visible. - **IMPLEMENTED**
2. **✅ Enabled/Clickable**: user can click/select/focus. - **IMPLEMENTED**
3. **✅ Input behavior**: accepts valid values. - **IMPLEMENTED**
4. **✅ Validation behavior**: rejects invalid/empty when required. - **IMPLEMENTED**
5. **⚠️ State behavior**: selected/unselected, checked/unchecked, active/inactive. - **PARTIAL** (needs more comprehensive coverage)
6. **✅ Navigation effect**: Next/Back causes expected transition (or blocks if invalid). - **IMPLEMENTED**

### Example rule for radio buttons
If a page has **6 radio buttons**, test should verify:
- All 6 are visible.
- All 6 are clickable/selectable.
- Single-select behavior is correct (if expected).
- Required validation when none selected.

This is the standard for "all component testing part" on each page.

---

## 3) Precondition Navigation Map (for specific page testing) - ✅ **FULLY IMPLEMENTED**

When testing a specific downstream page, always prepare it via upstream pages in setup/helper:

| Target Page to Test | Required Precondition Path | Fixture Name | Status |
|---|---|---|---|
| P1 Basic Info | None (entry page) | `at_basic_info` | ✅ Implemented |
| P2 Event Type | P1 completed | `at_event_type` | ✅ Implemented |
| P3 Scheduler | P1 + P2 completed | `at_scheduler` | ✅ Implemented |
| P4 Personal Info | P1 + P2 + P3 completed | `at_personal_info` | ✅ Implemented |
| P5 Referral | P1 + P2 + P3 + P4 completed | `at_referral` | ✅ Implemented |
| P6 Insurance | P1 + P2 + P3 + P4 + P5 completed | `at_insurance` | ✅ Implemented |
| P7 Success | P1 + P2 + P3 + P4 + P5 + P6 completed | `at_success` | ✅ Implemented |

**Location:** All fixtures implemented in `tests/bookslot/conftest.py`

### Specific answer to your example
If you want to test **Personal Info page (P4)**, yes: you must navigate from **Basic Info -> Event Type -> Scheduler -> Personal Info** before validating P4 components.

---

## 4) Page-wise Test Design Matrix (Smoke/Validation/Regre Test Count | Status |
|---|---|---|---|---|---|---|
| P1 Basic Info | Page loads, key fields visible | Name/email/phone required + format | Localization, edge data, **accessibility** | Yes | 31 tests | ✅ Full + Accessibility |
| P2 Event Type | Options visible and selectable | Required selection rules | Option permutations | Yes | 12 tests | ⚠️ Missing accessibility |
| P3 Scheduler | Slot section loads | Slot required, AM/PM behavior | Slot/date combinations | Yes | 15 tests | ⚠️ Missing accessibility |
| P4 Personal Info | Form + key fields visible | DOB/address/city/state/zip rules | Boundary and data variation | Yes | 13 tests | ⚠️ Missing accessibility |
| P5 Referral | Referral controls visible | Required/optional logic | Source combinations | Yes | 12 tests | ⚠️ Missing accessibility |
| P6 Insurance | Insurance fields visible | Member/ID/group/payer validation | Payer/provider matrix | Yes | 13 tests | ⚠️ Missing accessibility |
| P7 Success | Confirmation visible | Success state assertions | UI consistency and key data display | Yes | 16 tests | ⚠️ Missing accessibility |
| **E2E Tests** | **Happy path** | **Complete journeys** | **Variants (AM/PM, payer types)** | **-** | **~6 tests** | ✅ Implemented |

**Total Test Count:** 139 tests (133 page-level + 6 E2E)

### ⏳ Pending Enhancements:
- **Accessibility Tests:** Add accessibility test classes to P2-P7 (similar to P1's `TestBasicInfoAccessibility`)
- **Extended Regression:** Localization testing for P1, extended permutations for P2/P5/P6
| P6 Insurance | Insurance fields visible | Member/ID/group/payer validation | Payer/provider matrix | Yes |
| P7 Success | Confirmation visible | Success state assertions | UI consistency and key data display | Yes |

---

## 5) Best Strategy by Test Type

## A) Sanity (fast confidence)
Use for PR and quick checks:
- 1 smoke test per high-risk page (typically P1, P3, P6).
- 1 critical full E2E happy path (P1->P7).
- Keep runtime short.

## B) Regression (full confidence)
Use nightly/release:
- Full component coverage for all pages P1-P7.
- Data-driven validations for fields/options.
- 3-5 E2E variants (AM/PM, referral types, payer types).
- Add integration checkpoints where business-critical.

## C) Specific Page Testing
When goal is only one - ✅ **FULLY IMPLEMENTED**

Use markers consistently:
- ✅ **Project/engine:** `bookslot`, `playwright` - **IMPLEMENTED**
- ✅ **Test intent:** `smoke`, `validation`, `regression`, `e2e` - **IMPLEMENTED**
- ✅ **Priority:** `critical`, `high`, `medium` - **IMPLEMENTED**
- ✅ **Sequence control:** `ui_sequential` for tests that must not run in parallel - **IMPLEMENTED**

**Current Implementation:**
- Page component tests marked with: `@pytest.mark.bookslot`, `@pytest.mark.p{X}_{page_name}`, `@pytest.mark.{smoke|validation|regression}`, `@pytest.mark.{critical|high|medium}`
- E2E tests marked with: `@pytest.mark.e2e`, `@pytest.mark.critical`, `@pytest.mark.ui_sequential`
## 6) Marker Strategy

Use markers consistently:
- Project/engine: `bookslot`, `playwright`, `modern_spa`
- Test intent: `smoke`, `validation`, `regression`, `e2e`
- Priority: `critical`, `high`, `medium`
- Sequence control: `ui_sequential` for tests that must not run in parallel

Suggested intent:
- Page component tests: `validation` (and `smoke` subset)
- Full sequential flow: `e2e critical ui_sequential`

---

## 7) Execution Guidelines

1. **No test-to-test dependency** (independent tests only).
2. Put flow setup in fixture/helper (precondition builder).
3. Keep assertions in test layer; page objects stay action-focused.
4. Run page suites parallel where safe; run sequence-sensitive E2E serial.
5. Keep E2E count small to control flakiness and execution time.

---

## 8) Anti-Patterns to Avoid

- One giant test trying to verify all page components for all 7 pages.
- Depending on "P1 test pass" before running "P2 test".
- Repeating long navigation in every test without helper reuse.
- Adding too many E2E variants and making pipeline unstable.

---

## 9) Answer to "Is this already in document or not?"

Previously, the document had high-level strategy only. It did **not** explicitly define:
- per-component checks (visible + clickable + state + validation),
- the precondition navigation map for each target page,
- explicit sanity vs regression vs specific-page guidance.

This updated version includes all of these explicitly and tracks implementation status.

---

## 10) URL Query String Testing Integration - ⏳ **PLANNED**

### Overview

Bookslot requires comprehensive URL testing to validate:
- **Multiple Workflow IDs** (6+ workflows per environment)
- **Query Parameters** (language, source, patient_type, utm_campaign, etc.)
- **Environment-Specific URLs** (staging vs production)
- **URL Format Flexibility** (query string, path-based, hybrid)

### Architecture: Hybrid Data-Driven Approach

```
┌────────────────────────────────────────────────────────────┐
│              URL TESTING SYSTEM (HYBRID)                   │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  PRIMARY MODE: Manual Test Data (Excel/CSV/JSON/YAML)     │
│  ✅ QA team creates test data in Excel                    │
│  ✅ No coding required to add new test cases              │
│  ✅ Test data version controlled                          │
│                                                            │
│  SECONDARY MODE: Auto-Generation (YAML Config)            │
│  ✅ Fallback when test data file not available            │
│  ✅ Cartesian product / Pairwise combinations             │
│  ✅ Dependency rules and exclusions                       │
│                                                            │
│  VALIDATION: 4-Level Comprehensive                        │
│  ✅ Level 1: HTTP 200 status check                        │
│  ✅ Level 2: Expected elements present                    │
│  ✅ Level 3: No error messages                            │
│  ✅ Level 4: Page-specific validation                     │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### Test Data Structure (Excel Format - QA Friendly)

| workflow_id | environment | page_name | language | source | patient_type | insurance_verified | utm_campaign | expected_result | description |
|---|---|---|---|---|---|---|---|---|---|
| WF001 | staging | P1 | en | web | new | true | summer_promo | success | New patient web booking |
| WF002 | staging | P1 | es | mobile | returning | false | default | success | Returning mobile user |
| WF003 | staging | P2 | en | tablet | vip | true | urgent_care | success | VIP urgent care |
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

### URL Test Coverage Matrix

| Page | Workflow Tests | Parameter Tests | Total URL Tests | Status |
|---|---|---|---|---|
| P1 Basic Info | 6 workflows × query params | language, source, patient_type | ~36 tests | ⏳ Planned |
| P2 Event Type | 6 workflows × query params | language, source | ~36 tests | ⏳ Planned |
| P3 Scheduler | 6 workflows × query params | language, source, slot preferences | ~42 tests | ⏳ Planned |
| P4 Personal Info | 6 workflows × query params | language, source | ~36 tests | ⏳ Planned |
| P5 Referral | 6 workflows × query params | language, source, referral_source | ~42 tests | ⏳ Planned |
| P6 Insurance | 6 workflows × query params | language, source, insurance_verified | ~42 tests | ⏳ Planned |
| P7 Success | 6 workflows × query params | language, source | ~36 tests | ⏳ Planned |
| **TOTAL** | **42 workflow-page combos** | **6+ query parameters** | **~270 URL tests** | ⏳ Planned |

### Query Parameters to Test

| Parameter | Values | Description | Applies To |
|---|---|---|---|
| `workflow_id` | WF001-WF006 (staging)<br>WF_PROD001-006 (prod) | Workflow identifier | All pages |
| `language` | en, es, fr | UI language | All pages |
| `source` | web, mobile, tablet | Traffic source | All pages |
| `patient_type` | new, returning, vip | Patient classification | P1, P4, P5 |
| `insurance_verified` | true, false | Insurance pre-verification | P6 |
| `utm_campaign` | summer_promo, default, urgent_care, wellness | Marketing campaign | P1 |
| `referral_source` | google, facebook, direct, referral, physician | Referral source | P5 |

### URL Format Support (Future-Proof)

| Format | URL Pattern | Example | Status |
|---|---|---|---|
| **Query String** | `domain.com?workflow_id=X&param=Y` | `bookslot.com?workflow_id=WF001&lang=en` | ✅ Primary |
| Path Parameter | `domain.com/workflow/X?param=Y` | `bookslot.com/workflow/WF001?lang=en` | 🔮 Future |
| Path-Based | `domain.com/X/booking?param=Y` | `bookslot.com/WF001/booking?lang=en` | 🔮 Future |
| Hybrid | `domain.com/X?param=Y` | `bookslot.com/WF001?lang=en` | 🔮 Future |

### Integration with Existing Tests (Zero Conflict Design)

**Principle:** Enhance existing architecture without breaking changes

| Existing Component | Enhancement | Method | Impact |
|---|---|---|---|
| Navigation Fixtures | Add workflow_id parameter | `at_basic_info(workflow_id=None)` | ✅ Backward compatible |
| Page Objects | Accept optional url | `navigate(url=None)` | ✅ Already implemented |
| Test Files | New URL test suite | `tests/bookslot/url_testing/` | ✅ Additive only |
| conftest.py | New URL fixtures | `url_test_case`, `url_builder`, `url_validator` | ✅ No existing fixture changes |

### Implementation Phases

**Phase 1: Infrastructure (Days 1-2)**
- Create URL testing framework components
- Models, builders, validators, data loaders

**Phase 2: Test Data (Day 3)**
- Create Excel template for QA team
- Populate initial test data (42+ workflow-page combinations)
- Create YAML config (fallback mode)

**Phase 3: Fixture Enhancement (Day 4)**
- Add URL fixtures to conftest.py
- Enhance navigation helpers (backward compatible)
- Update documentation

**Phase 4: Test Creation (Days 5-6)**
- Create URL tests for all 7 pages
- Query parameter combination tests
- Integration with existing test suite

**Phase 5: Validation (Day 7)**
- Run full test suite (existing + URL tests)
- Performance testing
- QA training and documentation

### Expected Outcomes

**Test Count:**
- Before: 139 tests (page-level + E2E)
- After: ~410 tests (139 existing + 270 URL tests)
- Increase: +195%

**Coverage:**
- ✅ All 7 pages × 6 workflows = 42 workflow-page combinations
- ✅ 6+ query parameters systematically tested
- ✅ Environment-specific testing (staging, production)
- ✅ URL validation before every test execution

**Team Empowerment:**
- ✅ QA team can add test cases in Excel (no coding)
- ✅ Developers have auto-generation fallback
- ✅ Multiple data formats supported (Excel, CSV, JSON, YAML)
- ✅ Future-proof for URL format changes

### Marker Strategy for URL Tests

**New markers for URL testing:**
- `@pytest.mark.url_testing` - All URL-related tests
- `@pytest.mark.workflow_urls` - Workflow ID specific tests
- `@pytest.mark.query_params` - Query parameter tests
- `@pytest.mark.url_validation` - URL validation tests

**Usage in test execution:**
```bash
# Run all URL tests
pytest tests/bookslot/url_testing/ -m url_testing

# Run workflow URL tests only
pytest tests/bookslot/url_testing/ -m workflow_urls

# Run query parameter tests only
pytest tests/bookslot/url_testing/ -m query_params

# Run URL tests for specific page
pytest tests/bookslot/url_testing/test_workflow_urls_p1.py
```

### Test Data Maintenance

**For QA Team (No coding required):**
1. Open `test_data/bookslot/bookslot_workflows.xlsx`
2. Add new row with workflow_id, environment, page_name, and query parameters
3. Save file
4. Run `pytest tests/bookslot/url_testing/` - new test case automatically included

**For Developers (Auto-generation mode):**
1. Edit `config/url_testing/bookslot_urls.yaml`
2. Add new workflow_id or query parameter values
3. Run `pytest tests/bookslot/url_testing/ --mode=auto`
4. System generates combinations automatically

### Documentation References

- **Implementation Plan**: [BOOKSLOT_URL_TESTING_IMPLEMENTATION_PLAN.md](BOOKSLOT_URL_TESTING_IMPLEMENTATION_PLAN.md)
- **QA Guide**: `docs/QA_GUIDE_URL_TESTING.md` (to be created in Phase 5)
- **URL Testing Design**: [../Framework-Knowledge-Center/04-Test-Data-Management/URL_QUERY_STRING_TESTING_DESIGN.md](../Framework-Knowledge-Center/04-Test-Data-Management/URL_QUERY_STRING_TESTING_DESIGN.md)
- **Quick Reference**: [../Framework-Knowledge-Center/04-Test-Data-Management/URL_TESTING_QUICK_REFERENCE.md](../Framework-Knowledge-Center/04-Test-Data-Management/URL_TESTING_QUICK_REFERENCE.md)

---

## 11) Test Execution Guidelines (Updated with URL Testing)

### Execution Strategy by Test Type

**A) Smoke Tests (Fast Confidence Check)**
```bash
# Existing page smoke tests
pytest tests/bookslot/pages/ -m smoke --env=staging

# URL smoke tests (critical workflows only)
pytest tests/bookslot/url_testing/ -m "url_testing and smoke" --env=staging

# Expected runtime: ~5 minutes
```

**B) Regression Tests (Full Coverage)**
```bash
# All page tests
pytest tests/bookslot/pages/ -m regression --env=staging

# All URL tests
pytest tests/bookslot/url_testing/ -m url_testing --env=staging

# Expected runtime: ~15 minutes
```

**C) Full Test Suite**
```bash
# Everything (139 existing + 270 URL tests = 409 tests)
pytest tests/bookslot/ --env=staging --html=reports/bookslot_full_report.html

# Expected runtime: ~20 minutes
```

**D) URL-Specific Testing**
```bash
# Test specific workflow across all pages
pytest tests/bookslot/url_testing/ -k "WF001" --env=staging

# Test specific query parameter combinations
pytest tests/bookslot/url_testing/test_query_parameters.py --env=staging

# Test specific page URL variations
pytest tests/bookslot/url_testing/test_workflow_urls_p1.py --env=staging
```

### Parallel Execution (Performance Optimization)

**Safe for parallel:**
- ✅ All page component tests (existing 133 tests)
- ✅ All URL validation tests (270 URL tests)
- ✅ Query parameter combination tests

**Requires serial execution:**
- ⚠️ E2E flow tests (6 tests with `@pytest.mark.ui_sequential`)

```bash
# Run with parallel workers (fast)
pytest tests/bookslot/ --env=staging -n 4  # 4 parallel workers

# Run URL tests only (parallel safe)
pytest tests/bookslot/url_testing/ --env=staging -n 8  # 8 parallel workers
```

---

