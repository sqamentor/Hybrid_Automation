"""
E2E Tests (Layer B - End-to-End Sequential Flow)

Complete user journey tests covering all 7 steps.
These tests run sequentially (not parallel) to ensure flow stability.

Test Coverage:
- Happy path (critical)
- AM slot variant
- PM slot variant
- Referral source variants
- Insurance payer variants

Markers:
- @pytest.mark.e2e
- @pytest.mark.ui_sequential (must run serial, not parallel)
- @pytest.mark.critical, high, medium
"""
