# Governance Metrics Dashboard

**Framework:** Hybrid Automation (Playwright + Selenium)  
**Reporting Period:** [Month Year]  
**Generated:** [Date]

---

## Executive Summary

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Architectural Compliance | XX% | 100% | [Status] |
| Blocking Violations | X | 0 | [Status] |
| Total Violations | XX | 0 | [Status] |
| Baseline Entries | X | <5 | [Status] |
| Expired Baselines | X | 0 | [Status] |
| Files Scanned | XXX | - | - |

---

## Violation Trends

### Monthly Trend

| Month | Total Violations | Blocking | Warnings | Info |
|-------|------------------|----------|----------|------|
| [Month] | X | X | X | X |
| [Month-1] | X | X | X | X |
| [Month-2] | X | X | X | X |

### Category Breakdown

| Category | Violations | Change vs Last Month | Top File |
|----------|------------|---------------------|----------|
| engine-mix | X | [+/-X] | [file.py] |
| marker-engine | X | [+/-X] | [file.py] |
| folder-engine | X | [+/-X] | [file.py] |
| pom-compliance | X | [+/-X] | [file.py] |
| test-boundaries | X | [+/-X] | [file.py] |
| structural | X | [+/-X] | [file.py] |
| canonical-flow | X | [+/-X] | [file.py] |

---

## Baseline Status

### Active Baseline Entries

| File | Rule | Owner | Created | Expires | Status |
|------|------|-------|---------|---------|--------|
| [file] | [rule] | [owner] | [date] | [date] | [Status] |

### Baseline Trends

- **Total Entries:** X (target: <5)
- **Expiring This Month:** X
- **Expired (Critical):** X
- **Average Age:** X days

---

## Top Violators

### Files with Most Violations

| Rank | File | Violations | Blocking | Category Mix |
|------|------|------------|----------|--------------|
| 1 | [file.py] | X | X | [categories] |
| 2 | [file.py] | X | X | [categories] |
| 3 | [file.py] | X | X | [categories] |

### Violation Types

| Rule | Count | % of Total | Avg per File |
|------|-------|------------|--------------|
| [rule] | X | XX% | X.X |
| [rule] | X | XX% | X.X |
| [rule] | X | XX% | X.X |

---

## CI/CD Performance

### Build Success Rate

| Week | Builds | Passed | Failed by Audit | Pass Rate |
|------|--------|--------|-----------------|-----------|
| [Week] | X | X | X | XX% |
| [Week-1] | X | X | X | XX% |
| [Week-2] | X | X | X | XX% |

### Audit Performance

- **Average Audit Time:** X.X seconds
- **Files Scanned per Second:** XXX
- **Slowest Category:** [category] (X.X sec)
- **Fastest Category:** [category] (X.X sec)

---

## Team Performance

### Violation Resolution

| Developer/Team | Violations Introduced | Violations Fixed | Net Change |
|----------------|----------------------|------------------|------------|
| [Team A] | X | X | [+/-X] |
| [Team B] | X | X | [+/-X] |

### Commit Rejection Rate

- **Total Commits:** XXX
- **Rejected by Pre-commit:** X (X%)
- **Fixed Before Merge:** X (X%)

---

## Quality Indicators

### Architecture Health Score

```
Compliance: XX/100
├─ No Engine Mixing: XX/100
├─ Marker Consistency: XX/100
├─ POM Compliance: XX/100
├─ Test Boundaries: XX/100
└─ Structural Integrity: XX/100

Overall Health: [Excellent | Good | Fair | Poor]
```

### Technical Debt

- **Baseline Velocity:** X entries/month (added - resolved)
- **Average Resolution Time:** X days
- **Debt Trend:** [Decreasing | Stable | Increasing]

---

## Action Items

### Critical (Immediate)

1. [ ] Fix X blocking violations in [file]
2. [ ] Resolve expired baseline entries (X files)
3. [ ] Address [specific critical issue]

### High Priority (This Sprint)

1. [ ] Reduce test-boundaries violations by X%
2. [ ] Migrate [X] baseline entries (expiring soon)
3. [ ] Refactor top violator files

### Medium Priority (This Month)

1. [ ] Team training on POM compliance
2. [ ] Update pre-commit hooks adoption
3. [ ] Document common violation patterns

---

## Recommendations

### For Development Teams

- **Focus Area:** [Category with most violations]
- **Training Need:** [Topic]
- **Code Review:** Pay attention to [specific rule]

### For Architecture

- **Rule Adjustment:** Consider [adjustment if needed]
- **Documentation:** Update [specific docs]
- **Tooling:** Improve [specific tool]

### For Leadership

- **Celebrate:** [Achievement]
- **Address:** [Concern]
- **Invest:** [Resource need]

---

## Historical Comparison

### Year-over-Year

| Quarter | Violations | Compliance Rate | Baseline Entries |
|---------|------------|-----------------|------------------|
| Q1 [Year] | X | XX% | X |
| Q1 [Year-1] | X | XX% | X |
| **Change** | **[+/-X]** | **[+/-X%]** | **[+/-X]** |

---

## Appendix: Data Collection

### How to Generate This Report

```bash
# Run audit and save JSON
pytest --arch-audit --audit-report=artifacts/audit.json

# Extract metrics
python scripts/reporting/extract_metrics.py artifacts/audit.json

# Update this template with data
```

### Automation

- **Frequency:** Weekly/Monthly
- **Distribution:** Email to team leads
- **Dashboard:** [Link if available]

---

## Notes

- All data based on automated scans
- Baseline entries reviewed monthly
- Trends calculated vs previous period
- Action items prioritized by severity

---

**Last Updated:** [Date]  
**Next Review:** [Date]  
**Report Owner:** [Name/Team]
