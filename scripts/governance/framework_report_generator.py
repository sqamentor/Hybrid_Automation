#!/usr/bin/env python3
"""
Framework Report Generator
==========================

Generates comprehensive markdown audit reports.

Usage:
    from framework_report_generator import generate_markdown_report
    generate_markdown_report(audit_result, Path("report.md"))
"""

from pathlib import Path
from datetime import datetime
from typing import List
from framework_audit_engine import AuditResult, Violation, Category, Severity


def generate_markdown_report(result: AuditResult, output_path: Path) -> None:
    """Generate comprehensive markdown audit report.

    Args:
        result: AuditResult object from audit run
        output_path: Path where markdown file should be saved
    """
    report = []
    
    # Header
    report.append("# Framework Architecture Audit Report")
    report.append("")
    report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"**Status:** {'✅ PASSED' if result.is_passing() else '❌ FAILED'}")
    report.append("")
    
    # Summary Statistics
    report.append("## Summary")
    report.append("")
    blocking_count = len([v for v in result.violations if v.severity in (Severity.CRITICAL, Severity.ERROR)])
    warning_count = len([v for v in result.violations if v.severity == Severity.WARNING])
    info_count = len([v for v in result.violations if v.severity == Severity.INFO])
    
    report.append(f"- **Files Scanned:** {result.files_scanned}")
    report.append(f"- **Total Violations:** {len(result.violations)}")
    report.append(f"  - **Blocking (Critical/Error):** {blocking_count}")
    report.append(f"  - **Warnings:** {warning_count}")
    report.append(f"  - **Info:** {info_count}")
    report.append("")
    
    # Baseline Information
    if result.baseline_used:
        report.append("### Baseline Information")
        report.append("")
        report.append(f"- **Baseline File:** `{result.baseline_path}`")
        baselined_count = len([v for v in result.violations if v.baselined])
        report.append(f"- **Baselined Violations:** {baselined_count}")
        report.append("")
    
    # Violations by Category
    if result.violations:
        report.append("## Violations by Category")
        report.append("")
        
        # Group by category
        by_category = result.get_violations_by_category()
        
        for category in Category:
            violations = by_category.get(category, [])
            if not violations:
                continue
            
            # Count by severity
            critical = [v for v in violations if v.severity == Severity.CRITICAL]
            errors = [v for v in violations if v.severity == Severity.ERROR]
            warnings = [v for v in violations if v.severity == Severity.WARNING]
            infos = [v for v in violations if v.severity == Severity.INFO]
            
            report.append(f"### {category.value.upper()}")
            report.append("")
            report.append(f"**Total:** {len(violations)} violation(s)")
            if critical:
                report.append(f"- 🚨 **Critical:** {len(critical)}")
            if errors:
                report.append(f"- ❌ **Error:** {len(errors)}")
            if warnings:
                report.append(f"- ⚠️ **Warning:** {len(warnings)}")
            if infos:
                report.append(f"- ℹ️ **Info:** {len(infos)}")
            report.append("")
            
            # List violations (limit to first 50 per category)
            for v in violations[:50]:
                baseline_tag = " **[BASELINED]**" if v.baselined else ""
                severity_icon = {
                    Severity.CRITICAL: "🚨",
                    Severity.ERROR: "❌",
                    Severity.WARNING: "⚠️",
                    Severity.INFO: "ℹ️"
                }[v.severity]
                
                report.append(f"#### {severity_icon} {v.file_path}:{v.line_number}{baseline_tag}")
                report.append("")
                report.append(f"**Rule:** `{v.rule_id}`")
                report.append("")
                report.append(f"**Message:** {v.message}")
                report.append("")
                
                if v.context:
                    report.append("**Context:**")
                    report.append("```python")
                    report.append(v.context.strip())
                    report.append("```")
                    report.append("")
                
                if v.fix_suggestion:
                    report.append("**💡 Suggested Fix:**")
                    report.append("")
                    report.append(v.fix_suggestion)
                    report.append("")
                
                if v.baselined and v.baseline_expires:
                    report.append(f"**⏰ Baseline Expires:** {v.baseline_expires}")
                    report.append("")
                
                report.append("---")
                report.append("")
            
            if len(violations) > 50:
                report.append(f"*... and {len(violations) - 50} more violations in this category*")
                report.append("")
    
    else:
        report.append("## ✅ No Violations Detected")
        report.append("")
        report.append("All architecture rules are satisfied!")
        report.append("")
    
    # Enforcement Status
    report.append("## Enforcement Status")
    report.append("")
    
    if result.is_passing():
        report.append("✅ **AUDIT PASSED** - No blocking violations detected")
    else:
        blocking_violations = result.get_blocking_violations()
        report.append(f"❌ **AUDIT FAILED** - {len(blocking_violations)} blocking violation(s) must be fixed")
    
    report.append("")
    report.append("### Rule Enforcement Levels")
    report.append("")
    report.append("- 🚨 **CRITICAL:** Blocks CI immediately - must fix before merge")
    report.append("- ❌ **ERROR:** Blocks CI - must fix before merge")
    report.append("- ⚠️ **WARNING:** Does not block CI - should fix")
    report.append("- ℹ️ **INFO:** Informational only - consider addressing")
    report.append("")
    
    # Next Steps
    if not result.is_passing():
        report.append("## Next Steps")
        report.append("")
        report.append("1. Review blocking violations above")
        report.append("2. Apply suggested fixes")
        report.append("3. Run local audit: `pytest --arch-audit`")
        report.append("4. Commit fixes and push")
        report.append("")
    
    # Footer
    report.append("---")
    report.append("")
    report.append("*Generated by Framework Architecture Audit System*")
    report.append(f"*Report saved to: `{output_path}`*")
    
    # Write to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text('\n'.join(report), encoding='utf-8')


if __name__ == '__main__':
    print("framework_report_generator.py - Report generation module")
    print("Import this module to use generate_markdown_report()")
