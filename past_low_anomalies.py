#!/usr/bin/env python3
"""
Generate a list of LOW anomalies using year-over-year comparison.
"""

import csv
import os
import sys
import argparse
from datetime import datetime, timedelta
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


def find_prior_year_date(target_date, data_by_date):
    """
    Find the corresponding date from the prior year.
    Looks for the same day of week in roughly the same week of the year.

    Args:
        target_date: The date to find a prior year match for
        data_by_date: Dictionary mapping date objects to data entries

    Returns:
        The prior year's date object, or None if not found
    """
    # Start by trying exactly one year ago
    prior_year = target_date.year - 1
    target_day_of_week = target_date.weekday()

    # Try the exact date first (same month/day, prior year)
    try:
        candidate = target_date.replace(year=prior_year)
        if candidate in data_by_date and candidate.weekday() == target_day_of_week:
            return candidate
    except ValueError:
        # Handle leap year edge case (Feb 29)
        pass

    # Search within +/- 3 days to find same day of week
    for offset in range(-3, 4):
        try:
            candidate = target_date.replace(year=prior_year) + timedelta(days=offset)
            if candidate in data_by_date and candidate.weekday() == target_day_of_week:
                return candidate
        except ValueError:
            continue

    return None


def analyze_csv(csv_file, query_name, date_column, count_column,
                threshold_z=-2.5, threshold_min=5000, today=None, query_description="",
                min_date=None, yoy_threshold_pct=-50):
    """
    Analyze a single CSV file for year-over-year anomalies.

    Args:
        csv_file: Path to CSV file
        query_name: Name of the query for reporting
        date_column: Name of the date column
        count_column: Name of the count column
        threshold_z: Z-score threshold (deprecated, kept for compatibility)
        threshold_min: Minimum count threshold (absolute floor)
        today: Current date (for filtering future dates)
        query_description: Description of the query
        min_date: Minimum date to include in analysis (datetime object)
        yoy_threshold_pct: Year-over-year decrease threshold (default: -50%)

    Returns:
        List of anomaly dictionaries
    """
    if today is None:
        today = datetime(2026, 2, 2)

    if min_date is None:
        min_date = datetime(2025, 1, 1)  # Default to 2025-01-01 for YoY comparison

    # Check if CSV file exists
    if not os.path.exists(csv_file):
        print(f"WARNING: CSV file not found: {csv_file}")
        return []

    # Read data into both list and dictionary for easy lookup
    data = []
    data_by_date = {}

    try:
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                date_obj = parse_date(row['playdatekey'])
                count = int(row['count'])
                day_name = get_day_name(date_obj)
                entry = {
                    'date': date_obj,
                    'date_str': date_obj.strftime('%Y%m%d'),
                    'count': count,
                    'day_name': day_name
                }
                data.append(entry)
                data_by_date[date_obj] = entry
    except Exception as e:
        print(f"ERROR reading {csv_file}: {e}")
        return []

    if not data:
        print(f"WARNING: No data found in {csv_file}")
        return []

    # Find year-over-year anomalies
    yoy_anomalies = []

    for entry in data:
        # Skip future dates
        if entry['date'] >= today:
            continue

        # Skip dates before minimum date
        if entry['date'] < min_date:
            continue

        current_count = entry['count']

        # Check absolute threshold first
        if current_count < threshold_min:
            # Find prior year for context, but flag anyway
            prior_date = find_prior_year_date(entry['date'], data_by_date)
            prior_count = data_by_date[prior_date]['count'] if prior_date else 0

            yoy_anomalies.append({
                **entry,
                'query_name': query_name,
                'query_description': query_description,
                'prior_year_date': prior_date.strftime('%Y%m%d') if prior_date else 'N/A',
                'prior_year_count': prior_count,
                'yoy_change': current_count - prior_count if prior_date else 0,
                'yoy_pct': ((current_count - prior_count) / prior_count * 100) if (prior_date and prior_count > 0) else 0,
                'reason': 'Below minimum threshold'
            })
            continue

        # Find prior year's corresponding date
        prior_date = find_prior_year_date(entry['date'], data_by_date)

        if prior_date is None:
            # No prior year data available
            continue

        prior_count = data_by_date[prior_date]['count']

        if prior_count == 0:
            continue

        # Calculate year-over-year change
        yoy_change = current_count - prior_count
        yoy_pct = (yoy_change / prior_count) * 100

        # Flag if decrease exceeds threshold
        if yoy_pct <= yoy_threshold_pct:
            yoy_anomalies.append({
                **entry,
                'query_name': query_name,
                'query_description': query_description,
                'prior_year_date': prior_date.strftime('%Y%m%d'),
                'prior_year_count': prior_count,
                'yoy_change': yoy_change,
                'yoy_pct': yoy_pct,
                'reason': 'Year-over-year decrease'
            })

    # Sort by date
    yoy_anomalies.sort(key=lambda x: x['date'])

    return yoy_anomalies


def print_anomalies(anomalies, query_name, query_description):
    """Print anomalies for a single query."""
    if not anomalies:
        print("No anomalies found.")
        return

    print(f"{'Date':<12} {'Day':<10} {'Count':>10} {'Prior Year':>12} {'YoY Change':>12} {'YoY %':>8}")
    print("-" * 80)

    for entry in anomalies:
        prior_date_short = entry.get('prior_year_date', 'N/A')
        if prior_date_short != 'N/A' and len(prior_date_short) == 8:
            # Format as MM/DD/YY for readability
            prior_date_short = f"{prior_date_short[4:6]}/{prior_date_short[6:8]}/{prior_date_short[2:4]}"

        print(f"{entry['date_str']:<12} {entry['day_name']:<10} {entry['count']:>10,} "
              f"{entry.get('prior_year_count', 0):>12,} {entry.get('yoy_change', 0):>12,} "
              f"{entry.get('yoy_pct', 0):>7.1f}%")

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
            prior_info = f"vs {item.get('prior_year_count', 0):,}" if item.get('prior_year_count') else ""
            print(f"  {item['date_str']} ({item['day_name']:<9}): {item['count']:>8,} {prior_info} ({item.get('yoy_pct', 0):+.1f}%)")


def main():
    """Run anomaly analysis on all queries."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Analyze CSV files for year-over-year anomalies',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Console output only
  python3 past_low_anomalies.py

  # Generate HTML report
  python3 past_low_anomalies.py --html

  # Generate HTML report with custom filename
  python3 past_low_anomalies.py --html --output my_report.html

  # Filter for specific date range
  python3 past_low_anomalies.py --min-date 2025-01-01
        """
    )
    parser.add_argument('--html', action='store_true',
                       help='Generate HTML report')
    parser.add_argument('--output', '-o', type=str, default='reports/anomaly_report.html',
                       help='HTML output filename (default: reports/anomaly_report.html)')
    parser.add_argument('--min-date', type=str, default='2025-01-01',
                       help='Minimum date to include (YYYY-MM-DD format, default: 2025-01-01 for YoY comparison)')

    args = parser.parse_args()

    # Today's date
    TODAY = datetime(2026, 2, 2)

    # Parse minimum date
    try:
        MIN_DATE = datetime.strptime(args.min_date, '%Y-%m-%d')
    except ValueError:
        print(f"ERROR: Invalid min-date format: {args.min_date}. Expected YYYY-MM-DD")
        return 1

    # Load queries from JSON
    try:
        queries = load_queries("queries.json")
    except Exception as e:
        print(f"ERROR: Failed to load queries: {e}")
        return 1

    print(f"Date range: {MIN_DATE.strftime('%Y-%m-%d')} to {TODAY.strftime('%Y-%m-%d')}")
    print()

    all_anomalies = []
    anomalies_by_query = {}
    query_descriptions = {}

    # Process each query
    for query in queries:
        query_descriptions[query['name']] = query.get('description', query['name'])

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
            query.get('description', query['name']),
            MIN_DATE  # Pass minimum date filter
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
            # Ensure reports directory exists
            import os
            output_dir = os.path.dirname(args.output)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)

            output_file = generate_html_report(
                anomalies_by_query,
                args.output,
                query_descriptions=query_descriptions
            )
            print(f"\n✓ HTML report generated: {output_file}")
        except Exception as e:
            print(f"\n✗ Error generating HTML report: {e}")
            return 1

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
