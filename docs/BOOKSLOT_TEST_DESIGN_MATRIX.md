# Bookslot Test Design Matrix (POM + 7-Step Sequential Flow)

## Goal
Design test cases for Bookslot's **7-step sequential flow** where each page depends on the previous page (except Basic Info), while keeping tests stable, maintainable, and fast in CI.

**7-step user journey:**
`Basic Info (P1) -> Event Type (P2) -> Scheduler (P3) -> Personal Info (P4) -> Referral (P5) -> Insurance (P6) -> Success (P7)`

---

## 1) Recommended Test Layers

### Layer A: Component/Page-Level Tests (primary)
- Validate one page's controls and rules (visibility, clickability, field behavior, validation messages).
- Reach target page through a reusable **navigation precondition** in the same test.
- No dependency between test cases.
- Can run in parallel for speed.

### Layer B: Sequential E2E Journey Tests (small, critical set)
- Validate business journey across all 7 steps in a single test.
- Keep only a few critical paths (happy path + selected negatives).
- Run serial when sequence-sensitive.

### Layer C: Integration/Workflow Tests
- Add UI -> API -> DB validations for critical checkpoints only.

---

## 2) Mandatory Component Coverage per Page

For **every interactive component** on a page, include these checks as applicable:

1. **Visible**: element is rendered and visible.
2. **Enabled/Clickable**: user can click/select/focus.
3. **Input behavior**: accepts valid values.
4. **Validation behavior**: rejects invalid/empty when required.
5. **State behavior**: selected/unselected, checked/unchecked, active/inactive.
6. **Navigation effect**: Next/Back causes expected transition (or blocks if invalid).

### Example rule for radio buttons
If a page has **6 radio buttons**, test should verify:
- All 6 are visible.
- All 6 are clickable/selectable.
- Single-select behavior is correct (if expected).
- Required validation when none selected.

This is the standard for "all component testing part" on each page.

---

## 3) Precondition Navigation Map (for specific page testing)

When testing a specific downstream page, always prepare it via upstream pages in setup/helper:

| Target Page to Test | Required Precondition Path |
|---|---|
| P1 Basic Info | None (entry page) |
| P2 Event Type | P1 completed |
| P3 Scheduler | P1 + P2 completed |
| P4 Personal Info | P1 + P2 + P3 completed |
| P5 Referral | P1 + P2 + P3 + P4 completed |
| P6 Insurance | P1 + P2 + P3 + P4 + P5 completed |
| P7 Success | P1 + P2 + P3 + P4 + P5 + P6 completed |

### Specific answer to your example
If you want to test **Personal Info page (P4)**, yes: you must navigate from **Basic Info -> Event Type -> Scheduler -> Personal Info** before validating P4 components.

---

## 4) Page-wise Test Design Matrix (Smoke/Validation/Regression)

| Page | Sanity/Smoke | Validation | Regression | In E2E |
|---|---|---|---|---|
| P1 Basic Info | Page loads, key fields visible | Name/email/phone required + format | Localization, edge data | Yes |
| P2 Event Type | Options visible and selectable | Required selection rules | Option permutations | Yes |
| P3 Scheduler | Slot section loads | Slot required, AM/PM behavior | Slot/date combinations | Yes |
| P4 Personal Info | Form + key fields visible | DOB/address/city/state/zip rules | Boundary and data variation | Yes |
| P5 Referral | Referral controls visible | Required/optional logic | Source combinations | Yes |
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
When goal is only one page (e.g., P4):
- Use navigation helper to reach P4.
- Execute P4 component suite only.
- Do not re-test complete journey inside every P4 test.

---

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

This updated version includes all of these explicitly.
