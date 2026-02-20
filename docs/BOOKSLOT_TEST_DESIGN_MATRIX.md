# Bookslot Test Design Matrix (POM + Sequential Flow)

## Goal
Design test cases for a sequential booking journey where each page depends on the previous one (except Basic Info), while keeping automation stable and maintainable.

---

## 1) Recommended Test Layers

### Layer A: Page-Level Tests (Independent)
- Validate a single page's rules and controls.
- Reach target page using a navigation precondition helper in the same test (not by depending on another test).
- Run in parallel where safe.

### Layer B: End-to-End Flow Tests (Sequential)
- Validate complete business journey in one test:
  `Basic Info -> Event Type -> Scheduler -> Personal Info -> Referral -> Insurance -> Success`.
- Keep count low (critical happy paths + a few negatives).
- Prefer serial execution.

### Layer C: Integration/Workflow Tests
- Add UI->API->DB validations for critical checkpoints only.

---

## 2) Page-wise Test Design Matrix

| Page | Smoke | Validation | Regression | In E2E | Notes |
|---|---|---|---|---|---|
| Basic Info (P1) | Load page, required fields visible | Name/email/phone/required checks | Localization + field behavior | Yes | Entry page, no precondition required |
| Event Type (P2) | Page loads after P1 Next | Selection required, option mapping | Option combinations | Yes | Navigate via helper from P1 |
| Scheduler (P3) | Slot grid visible | AM/PM, slot required, no slot edge cases | Time-slot variations | Yes | Use deterministic slot strategy |
| Personal Info (P4) | Form visible | DOB/address/city/state/zip validation | Boundary and format checks | Yes | Reach via helper to reduce duplication |
| Referral (P5) | Options visible | Selection behavior, optional/required rules | Source variants | Yes | Keep assertions on rules only |
| Insurance (P6) | Insurance form visible | Member ID/group/payer validations | Payer variations | Yes | Data-driven cases preferred |
| Success (P7) | Confirmation visible | Booking reference/state checks | UI consistency checks | Yes | Keep success assertions minimal + stable |

---

## 3) Suggested Suite Composition

### PR / Quick Pipeline
- P1 smoke + one critical downstream page smoke (e.g., P6).
- 1 critical E2E happy path.

### Nightly
- All page-level validations for P1-P7.
- 3-5 E2E variants (AM/PM, referral, payer).

### Release / Pre-prod
- Full page regression.
- Critical E2E pack.
- Integration validations (UI->API->DB) for key checkpoints.

---

## 4) Marker Strategy

Use marker combinations consistently:
- Project/engine: `bookslot`, `playwright`, `modern_spa`
- Type: `smoke`, `validation`, `regression`, `e2e`
- Priority: `critical`, `high`, `medium`
- Sequence control: `ui_sequential` for tests that must not run in parallel

Example marker intent:
- Page validations: `@pytest.mark.validation`
- Full flow: `@pytest.mark.e2e @pytest.mark.critical @pytest.mark.ui_sequential`

---

## 5) Execution Guidelines

1. Avoid test-to-test dependency.
2. Build preconditions inside fixtures/helpers.
3. Keep E2E set small and business-focused.
4. Run page-level tests parallel; E2E serial when flaky/sequence-sensitive.
5. Keep assertions in tests, not page objects.

---

## 6) Example Execution Matrix

- **Fast check:**
  - Page smoke tests + 1 E2E critical
- **Functional check:**
  - All page validations + limited E2E
- **Full regression:**
  - All page regression + E2E + integrations

---

## 7) Anti-Patterns to Avoid

- One test class that tries to validate every page in one huge test.
- Making P2 test depend on P1 test result.
- Duplicating full navigation steps in every page test without helper reuse.
- Too many E2E variants causing long and flaky pipelines.
