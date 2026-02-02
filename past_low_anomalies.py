#!/usr/bin/env python3
"""
Generate a list of LOW anomalies from the PAST only across multiple queries.
"""

import csv
import os
import sys
import argparse
from datetime import datetime
from collections import defaultdict
import statistics
from query_loader import load_queries


def parse_date(date_str):
    """Parse date string in multiple formats."""
    # Try YYYYMMDD format first (e.g., '20240101')
    try:
        return datetime.strptime(date_str, '%Y%m%d')
    except ValueError:
        pass

    # Try YYYY-MM-DD format (e.g., '2024-01-01')
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        pass

    # If both fail, raise error
    raise ValueError(f"Unable to parse date: {date_str}. Expected format: YYYYMMDD or YYYY-MM-DD")


def get_day_name(date_obj):
    """Get day of week name."""
    return date_obj.strftime('%A')


def calculate_z_score(value, mean, std_dev):
    """Calculate z-score with zero stdev handling."""
    if std_dev == 0:
        return 0
    return (value - mean) / std_dev


def analyze_csv(csv_file, query_name, date_column, count_column,
                threshold_z=-2.5, threshold_min=5000, today=None, query_description=""):
    """
    Analyze a single CSV file for anomalies.

    Args:
        csv_file: Path to CSV file
        query_name: Name of the query for reporting
        date_column: Name of the date column
        count_column: Name of the count column
        threshold_z: Z-score threshold for anomaly detection
        threshold_min: Minimum count threshold
        today: Current date (for filtering future dates)
        query_description: Description of the query

    Returns:
        List of anomaly dictionaries
    """
    if today is None:
        today = datetime(2026, 2, 2)

    # Check if CSV file exists
    if not os.path.exists(csv_file):
        print(f"WARNING: CSV file not found: {csv_file}")
        return []

    # Read data
    data = []
    try:
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                date_obj = parse_date(row['playdatekey'])
                count = int(row['count'])
                day_name = get_day_name(date_obj)
                data.append({
                    'date': date_obj,
                    'date_str': date_obj.strftime('%Y%m%d'),  # Normalize to YYYYMMDD format
                    'count': count,
                    'day_name': day_name
                })
    except Exception as e:
        print(f"ERROR reading {csv_file}: {e}")
        return []

    if not data:
        print(f"WARNING: No data found in {csv_file}")
        return []

    # Group by day of week
    day_of_week_counts = defaultdict(list)
    for entry in data:
        day_of_week_counts[entry['day_name']].append(entry['count'])

    # Calculate stats
    day_stats = {}
    for day, counts in day_of_week_counts.items():
        day_stats[day] = {
            'mean': statistics.mean(counts),
            'stdev': statistics.stdev(counts) if len(counts) > 1 else 0,
        }

    # Find LOW anomalies from the PAST only
    past_low_anomalies = []

    for entry in data:
        # Skip future dates
        if entry['date'] >= today:
            continue

        day = entry['day_name']
        count = entry['count']
        stats = day_stats[day]
        z_score = calculate_z_score(count, stats['mean'], stats['stdev'])

        # Only include LOW anomalies (z-score < threshold_z OR count < threshold_min)
        if z_score < threshold_z or count < threshold_min:
            past_low_anomalies.append({
                **entry,
                'query_name': query_name,
                'query_description': query_description,
                'z_score': z_score,
                'expected': stats['mean'],
                'pct_diff': ((count - stats['mean']) / stats['mean']) * 100 if stats['mean'] != 0 else 0
            })

    # Sort by date
    past_low_anomalies.sort(key=lambda x: x['date'])

    return past_low_anomalies


def print_anomalies(anomalies, query_name, query_description):
    """Print anomalies for a single query."""
    if not anomalies:
        print("No anomalies found.")
        return

    print(f"{'Date':<12} {'Day':<10} {'Count':>10} {'Expected':>10} {'Z-Score':>8} {'% Diff':>8}")
    print("-" * 80)

    for entry in anomalies:
        print(f"{entry['date_str']:<12} {entry['day_name']:<10} {entry['count']:>10,} "
              f"{entry['expected']:>10.0f} {entry['z_score']:>8.2f} {entry['pct_diff']:>7.1f}%")

    print(f"\nTotal anomalies: {len(anomalies)}")

    # Group by time periods for easier analysis
    print("\n\nGROUPED BY YEAR/MONTH:")
    print("-" * 80)
    from itertools import groupby

    for year_month, group in groupby(anomalies, key=lambda x: x['date_str'][:6]):
        items = list(group)
        year = year_month[:4]
        month = year_month[4:6]
        print(f"\n{year}-{month} ({len(items)} anomalies):")
        for item in items:
            print(f"  {item['date_str']} ({item['day_name']:<9}): {item['count']:>8,}")


def main():
    """Run anomaly analysis on all queries."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Analyze CSV files for past low anomalies',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Console output only
  python3 past_low_anomalies.py

  # Generate HTML report
  python3 past_low_anomalies.py --html

  # Generate HTML report with custom filename
  python3 past_low_anomalies.py --html --output my_report.html
        """
    )
    parser.add_argument('--html', action='store_true',
                       help='Generate HTML report')
    parser.add_argument('--output', '-o', type=str, default='anomaly_report.html',
                       help='HTML output filename (default: anomaly_report.html)')

    args = parser.parse_args()

    # Today's date
    TODAY = datetime(2026, 2, 2)

    # Load queries from JSON
    try:
        queries = load_queries("queries.json")
    except Exception as e:
        print(f"ERROR: Failed to load queries: {e}")
        return 1

    all_anomalies = []
    anomalies_by_query = {}

    # Process each query
    for query in queries:
        print(f"\n{'='*80}")
        print(f"ANALYZING: {query['name']}")
        print(f"Description: {query['description']}")
        print(f"CSV: {query['csv_file']}")
        print(f"Thresholds: z-score < {query['anomaly_threshold_z']}, count < {query['anomaly_threshold_min']}")
        print(f"{'='*80}\n")

        anomalies = analyze_csv(
            query['csv_file'],
            query['name'],
            query['date_column'],
            query['count_column'],
            query.get('anomaly_threshold_z', -2.5),
            query.get('anomaly_threshold_min', 5000),
            TODAY,
            query.get('description', query['name'])
        )

        # Print anomalies for this query
        print_anomalies(anomalies, query['name'], query['description'])

        all_anomalies.extend(anomalies)
        anomalies_by_query[query['name']] = anomalies

    # Summary
    print(f"\n{'='*80}")
    print(f"SUMMARY")
    print(f"{'='*80}")
    print(f"Total anomalies found: {len(all_anomalies)} across {len(queries)} queries")

    # Count by query
    from collections import Counter
    query_counts = Counter(a['query_name'] for a in all_anomalies)
    print(f"\nAnomalies by query:")
    for query_name, count in query_counts.items():
        print(f"  {query_name}: {count}")

    print(f"{'='*80}")

    # Generate HTML report if requested
    if args.html:
        try:
            from html_report import generate_html_report
            output_file = generate_html_report(anomalies_by_query, args.output)
            print(f"\n✓ HTML report generated: {output_file}")
        except Exception as e:
            print(f"\n✗ Error generating HTML report: {e}")
            return 1

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
