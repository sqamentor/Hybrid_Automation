#!/usr/bin/env python3
"""
Audit Dashboard - Visualize Governance Trends
==============================================

Interactive HTML dashboard showing audit trends, violation patterns,
and compliance metrics over time.

Usage:
    python scripts/governance/audit_dashboard.py
    python scripts/governance/audit_dashboard.py --open
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List
import webbrowser


class AuditDashboard:
    """Generate audit dashboard with trends and metrics."""
    
    def __init__(self):
        self.history_file = Path("artifacts/audit_history/audit_history.json")
        self.commit_history_file = Path("artifacts/commit_history/commit_audit_log.json")
        self.output_file = Path("artifacts/audit_dashboard.html")
    
    def load_data(self) -> Dict:
        """Load all audit data."""
        data = {
            'watcher_audits': [],
            'commit_audits': [],
            'current_status': {}
        }
        
        # Load watcher audit history
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data['watcher_audits'] = json.load(f)
            except:
                pass
        
        # Load commit audit history
        if self.commit_history_file.exists():
            try:
                with open(self.commit_history_file, 'r', encoding='utf-8') as f:
                    data['commit_audits'] = json.load(f)
            except:
                pass
        
        return data
    
    def calculate_metrics(self, data: Dict) -> Dict:
        """Calculate dashboard metrics."""
        metrics = {
            'total_audits': 0,
            'total_commits_checked': 0,
            'blocked_commits': 0,
            'avg_violations': 0,
            'trend': 'no data',
            'categories': {},
            'daily_stats': [],
            'top_violated_files': {},
            'compliance_score': 0
        }
        
        # Watcher audits
        watcher = data['watcher_audits']
        commits = data['commit_audits']
        
        metrics['total_audits'] = len(watcher)
        metrics['total_commits_checked'] = len(commits)
        metrics['blocked_commits'] = sum(1 for c in commits if not c.get('passed', True))
        
        # Calculate average violations
        if watcher:
            metrics['avg_violations'] = sum(
                a.get('total_violations', 0) for a in watcher
            ) / len(watcher)
        
        # Category distribution
        for audit in watcher:
            for cat, count in audit.get('violations_by_category', {}).items():
                metrics['categories'][cat] = metrics['categories'].get(cat, 0) + count
        
        # Trend calculation
        if len(watcher) >= 10:
            recent = watcher[-10:]
            older = watcher[-20:-10] if len(watcher) >= 20 else watcher[:10]
            
            recent_avg = sum(a.get('total_violations', 0) for a in recent) / len(recent)
            older_avg = sum(a.get('total_violations', 0) for a in older) / len(older)
            
            if recent_avg < older_avg * 0.9:
                metrics['trend'] = 'improving'
            elif recent_avg > older_avg * 1.1:
                metrics['trend'] = 'degrading'
            else:
                metrics['trend'] = 'stable'
        
        # Daily stats (last 30 days)
        metrics['daily_stats'] = self._calculate_daily_stats(watcher)
        
        # Top violated files
        metrics['top_violated_files'] = self._calculate_top_files(watcher + commits)
        
        # Compliance score (0-100)
        if metrics['total_audits'] > 0:
            passed = sum(1 for a in watcher if a.get('passed', False))
            metrics['compliance_score'] = int((passed / metrics['total_audits']) * 100)
        
        return metrics
    
    def _calculate_daily_stats(self, audits: List[Dict]) -> List[Dict]:
        """Calculate daily audit statistics."""
        daily = {}
        
        for audit in audits:
            try:
                date = datetime.fromisoformat(audit['timestamp']).date()
                date_str = date.isoformat()
                
                if date_str not in daily:
                    daily[date_str] = {
                        'date': date_str,
                        'audits': 0,
                        'violations': 0
                    }
                
                daily[date_str]['audits'] += 1
                daily[date_str]['violations'] += audit.get('total_violations', 0)
            except:
                pass
        
        # Get last 30 days
        today = datetime.now().date()
        last_30 = []
        
        for i in range(30):
            date = today - timedelta(days=29 - i)
            date_str = date.isoformat()
            
            if date_str in daily:
                last_30.append(daily[date_str])
            else:
                last_30.append({
                    'date': date_str,
                    'audits': 0,
                    'violations': 0
                })
        
        return last_30
    
    def _calculate_top_files(self, all_audits: List[Dict]) -> Dict[str, int]:
        """Calculate most frequently violated files."""
        file_counts = {}
        
        for audit in all_audits:
            for violation in audit.get('violations', []):
                file_path = violation.get('file', 'unknown')
                file_counts[file_path] = file_counts.get(file_path, 0) + 1
        
        # Get top 10
        sorted_files = sorted(file_counts.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_files[:10])
    
    def generate_html(self, metrics: Dict) -> str:
        """Generate HTML dashboard."""
        
        # Prepare chart data
        daily_labels = [d['date'] for d in metrics['daily_stats']]
        daily_audits = [d['audits'] for d in metrics['daily_stats']]
        daily_violations = [d['violations'] for d in metrics['daily_stats']]
        
        category_labels = list(metrics['categories'].keys())
        category_values = list(metrics['categories'].values())
        
        # Trend color
        trend_colors = {
            'improving': '#10b981',
            'degrading': '#ef4444',
            'stable': '#f59e0b',
            'no data': '#6b7280'
        }
        trend_color = trend_colors.get(metrics['trend'], '#6b7280')
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Architecture Audit Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        .header {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        .header h1 {{
            color: #667eea;
            margin-bottom: 10px;
        }}
        .header p {{
            color: #6b7280;
        }}
        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        .metric-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .metric-card h3 {{
            color: #6b7280;
            font-size: 14px;
            font-weight: 500;
            margin-bottom: 10px;
            text-transform: uppercase;
        }}
        .metric-card .value {{
            font-size: 36px;
            font-weight: bold;
            color: #1f2937;
        }}
        .metric-card .subtext {{
            color: #9ca3af;
            font-size: 14px;
            margin-top: 5px;
        }}
        .chart-container {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        .chart-container h2 {{
            margin-bottom: 20px;
            color: #1f2937;
        }}
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 20px;
        }}
        .trend-indicator {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 14px;
            color: white;
            background-color: {trend_color};
        }}
        .file-list {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .file-item {{
            display: flex;
            justify-content: space-between;
            padding: 15px;
            border-bottom: 1px solid #e5e7eb;
        }}
        .file-item:last-child {{
            border-bottom: none;
        }}
        .file-item .filename {{
            color: #1f2937;
            font-family: monospace;
        }}
        .file-item .count {{
            color: #ef4444;
            font-weight: bold;
        }}
        canvas {{
            max-height: 300px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏗️ Architecture Audit Dashboard</h1>
            <p>Real-time monitoring of code quality and compliance</p>
            <p style="margin-top: 10px; color: #9ca3af;">
                Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </p>
        </div>

        <div class="metrics">
            <div class="metric-card">
                <h3>Total Audits</h3>
                <div class="value">{metrics['total_audits']}</div>
                <div class="subtext">File watcher + commit checks</div>
            </div>
            
            <div class="metric-card">
                <h3>Compliance Score</h3>
                <div class="value">{metrics['compliance_score']}%</div>
                <div class="subtext">Passing audit rate</div>
            </div>
            
            <div class="metric-card">
                <h3>Avg Violations</h3>
                <div class="value">{metrics['avg_violations']:.1f}</div>
                <div class="subtext">Per audit run</div>
            </div>
            
            <div class="metric-card">
                <h3>Trend</h3>
                <div class="value">
                    <span class="trend-indicator">{metrics['trend'].upper()}</span>
                </div>
                <div class="subtext">Recent 10 vs previous 10</div>
            </div>
            
            <div class="metric-card">
                <h3>Commits Checked</h3>
                <div class="value">{metrics['total_commits_checked']}</div>
                <div class="subtext">{metrics['blocked_commits']} blocked</div>
            </div>
        </div>

        <div class="charts-grid">
            <div class="chart-container">
                <h2>📈 Daily Audit Activity (Last 30 Days)</h2>
                <canvas id="dailyChart"></canvas>
            </div>
            
            <div class="chart-container">
                <h2>📊 Violations by Category</h2>
                <canvas id="categoryChart"></canvas>
            </div>
        </div>

        <div class="chart-container">
            <h2>📉 Violation Trend (Last 30 Days)</h2>
            <canvas id="trendChart"></canvas>
        </div>

        <div class="file-list">
            <h2 style="margin-bottom: 20px;">🔥 Most Violated Files</h2>
            {"".join(
                f'<div class="file-item"><span class="filename">{file}</span><span class="count">{count} violations</span></div>'
                for file, count in metrics['top_violated_files'].items()
            ) if metrics['top_violated_files'] else '<p style="color: #9ca3af;">No data available</p>'}
        </div>
    </div>

    <script>
        // Daily Activity Chart
        const dailyCtx = document.getElementById('dailyChart').getContext('2d');
        new Chart(dailyCtx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(daily_labels)},
                datasets: [{{
                    label: 'Audits Run',
                    data: {json.dumps(daily_audits)},
                    backgroundColor: 'rgba(102, 126, 234, 0.8)',
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                scales: {{
                    y: {{ beginAtZero: true }}
                }}
            }}
        }});

        // Category Chart
        const categoryCtx = document.getElementById('categoryChart').getContext('2d');
        new Chart(categoryCtx, {{
            type: 'doughnut',
            data: {{
                labels: {json.dumps(category_labels)},
                datasets: [{{
                    data: {json.dumps(category_values)},
                    backgroundColor: [
                        'rgba(239, 68, 68, 0.8)',
                        'rgba(245, 158, 11, 0.8)',
                        'rgba(16, 185, 129, 0.8)',
                        'rgba(59, 130, 246, 0.8)',
                        'rgba(139, 92, 246, 0.8)',
                        'rgba(236, 72, 153, 0.8)',
                        'rgba(14, 165, 233, 0.8)'
                    ]
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true
            }}
        }});

        // Trend Chart
        const trendCtx = document.getElementById('trendChart').getContext('2d');
        new Chart(trendCtx, {{
            type: 'line',
            data: {{
                labels: {json.dumps(daily_labels)},
                datasets: [{{
                    label: 'Violations',
                    data: {json.dumps(daily_violations)},
                    borderColor: 'rgba(239, 68, 68, 1)',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    fill: true,
                    tension: 0.4
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                scales: {{
                    y: {{ beginAtZero: true }}
                }}
            }}
        }});
    </script>
</body>
</html>"""
        
        return html
    
    def generate(self, open_browser: bool = False):
        """Generate dashboard."""
        print("\n" + "="*70)
        print("GENERATING AUDIT DASHBOARD")
        print("="*70)
        
        print("\nLoading audit data...")
        data = self.load_data()
        
        print("Calculating metrics...")
        metrics = self.calculate_metrics(data)
        
        print("Generating HTML...")
        html = self.generate_html(metrics)
        
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        self.output_file.write_text(html, encoding='utf-8')
        
        print(f"\n✅ Dashboard generated: {self.output_file}")
        print(f"\nMetrics:")
        print(f"  - Total Audits: {metrics['total_audits']}")
        print(f"  - Compliance Score: {metrics['compliance_score']}%")
        print(f"  - Average Violations: {metrics['avg_violations']:.1f}")
        print(f"  - Trend: {metrics['trend'].upper()}")
        print("="*70)
        
        if open_browser:
            print("\nOpening dashboard in browser...")
            webbrowser.open(f"file://{self.output_file.absolute()}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate Audit Dashboard")
    parser.add_argument('--open', action='store_true', help='Open in browser')
    
    args = parser.parse_args()
    
    dashboard = AuditDashboard()
    dashboard.generate(open_browser=args.open)


if __name__ == '__main__':
    main()
