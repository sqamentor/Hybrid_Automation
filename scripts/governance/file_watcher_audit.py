#!/usr/bin/env python3
"""
File System Watcher - Auto Audit on Changes
============================================

Monitors Python files for changes and automatically triggers architecture audit.
Maintains audit history and generates change reports.

Usage:
    python scripts/governance/file_watcher_audit.py --watch
    python scripts/governance/file_watcher_audit.py --watch --auto-fix
    python scripts/governance/file_watcher_audit.py --watch --strict
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

# Add governance to path
sys.path.insert(0, str(Path(__file__).parent))

from framework_audit_engine import FrameworkAuditEngine, AuditResult, Violation
from framework_report_generator import generate_markdown_report

# Audit history directory
HISTORY_DIR = Path("artifacts/audit_history")
HISTORY_DIR.mkdir(parents=True, exist_ok=True)


class AuditHistory:
    """Track audit history for change analysis"""
    
    def __init__(self, history_file: Path = HISTORY_DIR / "audit_history.json"):
        self.history_file = history_file
        self.history: List[Dict] = self._load_history()
    
    def _load_history(self) -> List[Dict]:
        """Load existing audit history"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_audit(self, result: AuditResult, changed_files: List[str]):
        """Save audit result to history"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'files_changed': changed_files,
            'files_scanned': result.files_scanned,
            'total_violations': len(result.violations),
            'blocking_violations': result.blocking_count,
            'warning_violations': result.warning_count,
            'info_violations': result.info_count,
            'passed': result.passed,
            'violations_by_category': self._group_violations(result.violations)
        }
        
        self.history.append(entry)
        
        # Keep last 1000 entries
        if len(self.history) > 1000:
            self.history = self.history[-1000:]
        
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, indent=2)
    
    def _group_violations(self, violations: List[Violation]) -> Dict[str, int]:
        """Group violations by category"""
        grouped = {}
        for v in violations:
            category = v.rule.split('/')[0] if '/' in v.rule else v.rule
            grouped[category] = grouped.get(category, 0) + 1
        return grouped
    
    def get_recent(self, count: int = 10) -> List[Dict]:
        """Get recent audit entries"""
        return self.history[-count:] if self.history else []
    
    def get_trend_analysis(self) -> Dict:
        """Analyze violation trends"""
        if not self.history:
            return {
                'total_audits': 0,
                'avg_violations': 0,
                'trend': 'no data'
            }
        
        recent_10 = self.history[-10:]
        older_10 = self.history[-20:-10] if len(self.history) >= 20 else []
        
        recent_avg = sum(e['total_violations'] for e in recent_10) / len(recent_10)
        older_avg = sum(e['total_violations'] for e in older_10) / len(older_10) if older_10 else recent_avg
        
        if recent_avg < older_avg * 0.9:
            trend = 'improving'
        elif recent_avg > older_avg * 1.1:
            trend = 'degrading'
        else:
            trend = 'stable'
        
        return {
            'total_audits': len(self.history),
            'avg_violations': recent_avg,
            'trend': trend,
            'recent_avg': recent_avg,
            'older_avg': older_avg
        }


class ChangeTracker:
    """Track file changes for audit reporting"""
    
    def __init__(self):
        self.changed_files: Set[Path] = set()
        self.last_audit_time: float = time.time()
        self.debounce_seconds: float = 2.0  # Wait 2 seconds after last change
    
    def add_change(self, file_path: Path):
        """Track a file change"""
        # Only track Python files in relevant directories
        if file_path.suffix == '.py':
            if any(part in file_path.parts for part in ['tests', 'pages', 'framework', 'utils']):
                self.changed_files.add(file_path)
                self.last_audit_time = time.time()
    
    def should_audit(self) -> bool:
        """Check if enough time has passed for debouncing"""
        if not self.changed_files:
            return False
        return (time.time() - self.last_audit_time) >= self.debounce_seconds
    
    def get_changes(self) -> List[str]:
        """Get changed files and reset"""
        files = [str(f) for f in self.changed_files]
        self.changed_files.clear()
        return files


class AuditFileSystemHandler(FileSystemEventHandler):
    """Handle file system events and trigger audits"""
    
    def __init__(self, engine: FrameworkAuditEngine, history: AuditHistory, 
                 tracker: ChangeTracker, strict: bool = False):
        self.engine = engine
        self.history = history
        self.tracker = tracker
        self.strict = strict
        self.audit_count = 0
    
    def on_modified(self, event: FileSystemEvent):
        """Handle file modification"""
        if not event.is_directory:
            file_path = Path(event.src_path)
            self.tracker.add_change(file_path)
    
    def on_created(self, event: FileSystemEvent):
        """Handle file creation"""
        if not event.is_directory:
            file_path = Path(event.src_path)
            self.tracker.add_change(file_path)
    
    def trigger_audit_if_ready(self):
        """Check if audit should be triggered"""
        if self.tracker.should_audit():
            self.run_audit()
    
    def run_audit(self):
        """Execute architecture audit"""
        changed_files = self.tracker.get_changes()
        
        if not changed_files:
            return
        
        self.audit_count += 1
        
        print("\n" + "="*70)
        print(f"AUTO-AUDIT TRIGGERED (Run #{self.audit_count})")
        print("="*70)
        print(f"\nFiles changed ({len(changed_files)}):")
        for f in changed_files:
            print(f"  - {f}")
        print("\nRunning architecture audit...")
        
        # Run audit
        result = self.engine.audit()
        
        # Save to history
        self.history.save_audit(result, changed_files)
        
        # Generate report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = HISTORY_DIR / f"audit_{timestamp}.md"
        
        # Add change context to report
        self._generate_change_report(result, changed_files, report_path)
        
        # Display results
        self._display_results(result)
        
        # Generate trend analysis
        trend = self.history.get_trend_analysis()
        self._display_trend(trend)
        
        # Strict mode: exit on violations
        if self.strict and not result.passed:
            print("\n" + "="*70)
            print("[STRICT MODE] AUDIT FAILED - STOPPING WATCHER")
            print("="*70)
            sys.exit(1)
    
    def _generate_change_report(self, result: AuditResult, changed_files: List[str], 
                                output_path: Path):
        """Generate report with change context"""
        report = []
        
        report.append("# Architecture Audit Report (Auto-Generated)")
        report.append(f"\n**Trigger:** File change detection")
        report.append(f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Status:** {'✅ PASSED' if result.passed else '❌ FAILED'}")
        
        report.append(f"\n## Changes Detected ({len(changed_files)})")
        for f in changed_files:
            report.append(f"- {f}")
        
        report.append(f"\n## Audit Summary")
        report.append(f"- Files Scanned: {result.files_scanned}")
        report.append(f"- Total Violations: {len(result.violations)}")
        report.append(f"- Blocking: {result.blocking_count}")
        report.append(f"- Warnings: {result.warning_count}")
        report.append(f"- Info: {result.info_count}")
        
        if result.violations:
            report.append(f"\n## Violations")
            
            # Check if violations are in changed files
            changed_set = set(changed_files)
            new_violations = [v for v in result.violations if v.file in changed_set]
            existing_violations = [v for v in result.violations if v.file not in changed_set]
            
            if new_violations:
                report.append(f"\n### ⚠️ NEW Violations (in changed files)")
                for v in new_violations[:20]:  # Limit display
                    report.append(f"\n**{v.file}** (Line {v.line})")
                    report.append(f"- Rule: `{v.rule}`")
                    report.append(f"- Severity: {v.severity.value}")
                    report.append(f"- {v.message}")
                    if v.fix_suggestion:
                        report.append(f"- 💡 Fix: {v.fix_suggestion}")
            
            if existing_violations:
                report.append(f"\n### Existing Violations (not in changed files)")
                report.append(f"Count: {len(existing_violations)}")
        else:
            report.append(f"\n✅ No violations detected")
        
        # Write report
        output_path.write_text('\n'.join(report), encoding='utf-8')
        
        # Also update main report
        main_report = Path("artifacts/framework_audit_report.md")
        generate_markdown_report(result, main_report)
    
    def _display_results(self, result: AuditResult):
        """Display audit results in terminal"""
        print("\n" + "-"*70)
        print("AUDIT RESULTS")
        print("-"*70)
        
        if result.passed:
            print("Status: ✅ PASSED")
        else:
            print("Status: ❌ FAILED")
        
        print(f"\nFiles Scanned: {result.files_scanned}")
        print(f"Total Violations: {len(result.violations)}")
        print(f"  - Blocking: {result.blocking_count}")
        print(f"  - Warnings: {result.warning_count}")
        print(f"  - Info: {result.info_count}")
        
        if result.violations:
            # Show summary by category
            categories = {}
            for v in result.violations:
                cat = v.rule.split('/')[0] if '/' in v.rule else v.rule
                categories[cat] = categories.get(cat, 0) + 1
            
            print("\nViolations by Category:")
            for cat, count in sorted(categories.items()):
                print(f"  - {cat}: {count}")
        
        print("-"*70)
    
    def _display_trend(self, trend: Dict):
        """Display trend analysis"""
        print("\n" + "-"*70)
        print("TREND ANALYSIS")
        print("-"*70)
        print(f"Total Audits Run: {trend['total_audits']}")
        print(f"Average Violations: {trend['avg_violations']:.1f}")
        
        if trend['trend'] == 'improving':
            print(f"Trend: ✅ IMPROVING")
        elif trend['trend'] == 'degrading':
            print(f"Trend: ⚠️ DEGRADING")
        else:
            print(f"Trend: → STABLE")
        
        print("-"*70)


class FileWatcherAudit:
    """Main file watcher audit coordinator"""
    
    def __init__(self, strict: bool = False):
        self.engine = FrameworkAuditEngine()
        self.history = AuditHistory()
        self.tracker = ChangeTracker()
        self.handler = AuditFileSystemHandler(self.engine, self.history, self.tracker, strict)
        self.observer = Observer()
        self.strict = strict
    
    def start(self, watch_paths: List[Path] = None):
        """Start watching for file changes"""
        if watch_paths is None:
            # Default paths to watch
            watch_paths = [
                Path("tests"),
                Path("pages"),
                Path("framework"),
                Path("utils")
            ]
        
        # Filter to existing paths
        watch_paths = [p for p in watch_paths if p.exists()]
        
        if not watch_paths:
            print("ERROR: No valid paths to watch")
            return
        
        print("\n" + "="*70)
        print("FILE WATCHER AUDIT - STARTING")
        print("="*70)
        print("\nMonitoring directories:")
        for path in watch_paths:
            print(f"  - {path}")
            self.observer.schedule(self.handler, str(path), recursive=True)
        
        print(f"\nStrict Mode: {'ENABLED' if self.strict else 'DISABLED'}")
        print("Debounce: 2 seconds after last change")
        print("\nAudit will auto-trigger when Python files change...")
        print("Press Ctrl+C to stop\n")
        print("="*70)
        
        # Run initial audit
        print("\n[INITIAL] Running baseline audit...")
        self.handler.tracker.add_change(Path("tests"))  # Trigger initial
        self.handler.run_audit()
        
        # Start observer
        self.observer.start()
        
        try:
            while True:
                time.sleep(1)
                # Check if audit should be triggered
                self.handler.trigger_audit_if_ready()
        except KeyboardInterrupt:
            print("\n\nStopping file watcher...")
            self.observer.stop()
        
        self.observer.join()
        
        print("\n" + "="*70)
        print("FILE WATCHER AUDIT - STOPPED")
        print("="*70)
        
        # Final summary
        trend = self.history.get_trend_analysis()
        print(f"\nTotal Audits Run: {self.handler.audit_count}")
        print(f"Average Violations: {trend['avg_violations']:.1f}")
        print(f"Trend: {trend['trend'].upper()}")
        print(f"\nAudit history: {self.history.history_file}")
        print(f"Report archive: {HISTORY_DIR}/")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="File Watcher Audit")
    parser.add_argument('--watch', action='store_true', help='Start file watcher')
    parser.add_argument('--strict', action='store_true', 
                       help='Exit on first violation (strict mode)')
    parser.add_argument('--history', action='store_true', 
                       help='Show audit history')
    parser.add_argument('--trend', action='store_true', 
                       help='Show trend analysis')
    
    args = parser.parse_args()
    
    if args.history:
        history = AuditHistory()
        recent = history.get_recent(20)
        
        print("\n" + "="*70)
        print("AUDIT HISTORY (Last 20)")
        print("="*70)
        
        for entry in recent:
            status = "✅ PASS" if entry['passed'] else "❌ FAIL"
            print(f"\n{entry['timestamp']} - {status}")
            print(f"  Files Changed: {len(entry['files_changed'])}")
            print(f"  Violations: {entry['total_violations']} " +
                  f"(Blocking: {entry['blocking_violations']})")
            if entry['violations_by_category']:
                print(f"  Categories: {', '.join(entry['violations_by_category'].keys())}")
        
        return
    
    if args.trend:
        history = AuditHistory()
        trend = history.get_trend_analysis()
        
        print("\n" + "="*70)
        print("TREND ANALYSIS")
        print("="*70)
        print(f"\nTotal Audits: {trend['total_audits']}")
        print(f"Average Violations (recent): {trend['avg_violations']:.1f}")
        print(f"Trend: {trend['trend'].upper()}")
        
        if trend['trend'] == 'improving':
            print("\n✅ Code quality is IMPROVING")
        elif trend['trend'] == 'degrading':
            print("\n⚠️ Code quality is DEGRADING - take action")
        else:
            print("\n→ Code quality is STABLE")
        
        return
    
    if args.watch:
        watcher = FileWatcherAudit(strict=args.strict)
        watcher.start()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
