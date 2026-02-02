#!/usr/bin/env python3
"""
Generate HTML reports for anomaly analysis results.
"""

from datetime import datetime
from typing import List, Dict


def generate_html_report(anomalies_by_query: Dict[str, List[Dict]],
                        output_file: str = "anomaly_report.html",
                        report_date: datetime = None) -> str:
    """
    Generate a styled HTML report from anomaly analysis results.

    Args:
        anomalies_by_query: Dictionary mapping query names to lists of anomaly dicts
        output_file: Output HTML filename
        report_date: Date the report was generated (default: now)

    Returns:
        Path to the generated HTML file
    """
    if report_date is None:
        report_date = datetime.now()

    # Calculate summary statistics
    total_anomalies = sum(len(anomalies) for anomalies in anomalies_by_query.values())
    num_queries = len(anomalies_by_query)

    # Group anomalies by year-month for each query
    def group_by_month(anomalies):
        from itertools import groupby
        grouped = {}
        for year_month, group in groupby(anomalies, key=lambda x: x['date_str'][:6]):
            grouped[year_month] = list(group)
        return grouped

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Anomaly Analysis Report - {report_date.strftime('%Y-%m-%d')}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 2.5em;
            font-weight: 700;
            margin-bottom: 10px;
        }}

        .header .date {{
            font-size: 1.1em;
            opacity: 0.9;
        }}

        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 40px;
            background: #f8f9fa;
        }}

        .summary-card {{
            background: white;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            text-align: center;
            transition: transform 0.2s;
        }}

        .summary-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.15);
        }}

        .summary-card .number {{
            font-size: 3em;
            font-weight: 700;
            color: #667eea;
            margin-bottom: 10px;
        }}

        .summary-card .label {{
            font-size: 1.1em;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        .content {{
            padding: 40px;
        }}

        .query-section {{
            margin-bottom: 50px;
        }}

        .query-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px 30px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}

        .query-header h2 {{
            font-size: 1.8em;
            margin-bottom: 5px;
        }}

        .query-header .description {{
            opacity: 0.9;
            font-size: 1.1em;
        }}

        .query-stats {{
            display: flex;
            gap: 20px;
            margin-top: 15px;
            flex-wrap: wrap;
        }}

        .query-stats .stat {{
            background: rgba(255, 255, 255, 0.2);
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.95em;
        }}

        .anomaly-table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            border-radius: 8px;
            overflow: hidden;
        }}

        .anomaly-table thead {{
            background: #667eea;
            color: white;
        }}

        .anomaly-table th {{
            padding: 15px;
            text-align: left;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.85em;
            letter-spacing: 1px;
        }}

        .anomaly-table th.right {{
            text-align: right;
        }}

        .anomaly-table tbody tr {{
            border-bottom: 1px solid #e9ecef;
            transition: background-color 0.2s;
        }}

        .anomaly-table tbody tr:hover {{
            background-color: #f8f9fa;
        }}

        .anomaly-table tbody tr:last-child {{
            border-bottom: none;
        }}

        .anomaly-table td {{
            padding: 12px 15px;
        }}

        .anomaly-table td.right {{
            text-align: right;
            font-family: 'Courier New', monospace;
        }}

        .severity-high {{
            color: #dc3545;
            font-weight: 600;
        }}

        .severity-medium {{
            color: #fd7e14;
            font-weight: 600;
        }}

        .severity-low {{
            color: #ffc107;
            font-weight: 600;
        }}

        .month-group {{
            margin-bottom: 30px;
        }}

        .month-header {{
            background: #f8f9fa;
            padding: 15px 20px;
            border-left: 4px solid #667eea;
            margin-bottom: 15px;
            font-weight: 600;
            font-size: 1.2em;
            color: #495057;
        }}

        .no-anomalies {{
            text-align: center;
            padding: 40px;
            color: #6c757d;
            font-size: 1.1em;
        }}

        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #6c757d;
            border-top: 1px solid #dee2e6;
        }}

        @media print {{
            body {{
                background: white;
                padding: 0;
            }}

            .container {{
                box-shadow: none;
            }}

            .summary-card:hover,
            .anomaly-table tbody tr:hover {{
                transform: none;
                background-color: white;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Anomaly Analysis Report</h1>
            <div class="date">Generated on {report_date.strftime('%B %d, %Y at %I:%M %p')}</div>
        </div>

        <div class="summary">
            <div class="summary-card">
                <div class="number">{total_anomalies}</div>
                <div class="label">Total Anomalies</div>
            </div>
            <div class="summary-card">
                <div class="number">{num_queries}</div>
                <div class="label">Queries Analyzed</div>
            </div>
"""

    # Add average anomalies per query
    avg_anomalies = total_anomalies / num_queries if num_queries > 0 else 0
    html += f"""            <div class="summary-card">
                <div class="number">{avg_anomalies:.1f}</div>
                <div class="label">Avg per Query</div>
            </div>
        </div>
"""

    # Add query sections
    html += """        <div class="content">
"""

    for query_name, anomalies in anomalies_by_query.items():
        if not anomalies:
            continue

        query_desc = anomalies[0].get('query_description', query_name) if anomalies else query_name

        # Calculate query statistics
        severe_count = sum(1 for a in anomalies if a['pct_diff'] < -95)
        moderate_count = sum(1 for a in anomalies if -95 <= a['pct_diff'] < -85)
        mild_count = len(anomalies) - severe_count - moderate_count

        html += f"""            <div class="query-section">
                <div class="query-header">
                    <h2>{query_name}</h2>
                    <div class="description">{query_desc}</div>
                    <div class="query-stats">
                        <div class="stat">📊 {len(anomalies)} anomalies found</div>
                        <div class="stat">🔴 {severe_count} severe (&lt;-95%)</div>
                        <div class="stat">🟠 {moderate_count} moderate (-95% to -85%)</div>
                        <div class="stat">🟡 {mild_count} mild (&gt;-85%)</div>
                    </div>
                </div>
"""

        # Group by month
        grouped = group_by_month(anomalies)

        for year_month in sorted(grouped.keys()):
            items = grouped[year_month]
            year = year_month[:4]
            month = year_month[4:6]
            month_name = datetime.strptime(month, '%m').strftime('%B')

            html += f"""                <div class="month-group">
                    <div class="month-header">{month_name} {year} ({len(items)} anomalies)</div>
                    <table class="anomaly-table">
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Day</th>
                                <th class="right">Actual Count</th>
                                <th class="right">Expected</th>
                                <th class="right">Z-Score</th>
                                <th class="right">% Difference</th>
                            </tr>
                        </thead>
                        <tbody>
"""

            for item in items:
                # Determine severity class
                pct_diff = item['pct_diff']
                if pct_diff < -95:
                    severity_class = "severity-high"
                elif pct_diff < -85:
                    severity_class = "severity-medium"
                else:
                    severity_class = "severity-low"

                html += f"""                            <tr>
                                <td>{item['date_str']}</td>
                                <td>{item['day_name']}</td>
                                <td class="right">{item['count']:,}</td>
                                <td class="right">{item['expected']:,.0f}</td>
                                <td class="right">{item['z_score']:.2f}</td>
                                <td class="right {severity_class}">{item['pct_diff']:.1f}%</td>
                            </tr>
"""

            html += """                        </tbody>
                    </table>
                </div>
"""

        html += """            </div>
"""

    # Add footer
    html += f"""        </div>

        <div class="footer">
            <p>Generated by EZ Links Rounds Data Analysis System</p>
            <p>Report includes anomalies with z-score &lt; -2.5 or count &lt; 5000</p>
        </div>
    </div>
</body>
</html>
"""

    # Write to file
    with open(output_file, 'w') as f:
        f.write(html)

    return output_file


def main():
    """Test HTML report generation."""
    # Sample data for testing
    sample_anomalies = [
        {
            'date_str': '20240115',
            'day_name': 'Monday',
            'count': 2812,
            'expected': 24817,
            'z_score': -1.05,
            'pct_diff': -88.7,
            'query_name': 'test_query',
            'query_description': 'Test Query Description'
        }
    ]

    anomalies_by_query = {'test_query': sample_anomalies}
    output_file = generate_html_report(anomalies_by_query)
    print(f"Test HTML report generated: {output_file}")


if __name__ == '__main__':
    main()
