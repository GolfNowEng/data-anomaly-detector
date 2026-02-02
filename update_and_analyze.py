#!/usr/bin/env python3
"""
Update data from database and run anomaly analysis across multiple queries.
"""

import sys
import argparse
from db_query import EZLinksRoundsDB
from query_loader import load_queries


def update_and_analyze(server: str, database: str,
                      use_windows_auth: bool = True,
                      username: str = None, password: str = None,
                      start_date: str = None, end_date: str = None,
                      force_refresh: bool = False,
                      query_names: list = None):
    """
    Pull latest data from database for all queries and run anomaly analysis.

    Args:
        server: SQL Server hostname
        database: Database name
        use_windows_auth: Use Windows authentication
        username: SQL Server username (if not using Windows auth)
        password: SQL Server password (if not using Windows auth)
        start_date: Optional start date filter (YYYYMMDD format)
        end_date: Optional end date filter (YYYYMMDD format)
        force_refresh: Force full refresh instead of incremental update
        query_names: Optional list of query names to process (default: all queries)
    """
    # Load queries from JSON
    try:
        all_queries = load_queries("queries.json")
    except Exception as e:
        print(f"ERROR: Failed to load queries: {e}")
        return False

    # Filter queries if specific names were provided
    if query_names:
        queries = [q for q in all_queries if q['name'] in query_names]
        if not queries:
            print(f"ERROR: No queries found matching: {', '.join(query_names)}")
            print(f"Available queries: {', '.join([q['name'] for q in all_queries])}")
            return False

        # Check for invalid query names
        found_names = [q['name'] for q in queries]
        invalid_names = [name for name in query_names if name not in found_names]
        if invalid_names:
            print(f"WARNING: Query names not found: {', '.join(invalid_names)}")
            print(f"Available queries: {', '.join([q['name'] for q in all_queries])}")
    else:
        queries = all_queries

    print("=" * 80)
    print("UPDATING DATA FROM DATABASE")
    print("=" * 80)
    print(f"Loaded {len(queries)} queries:")
    for query in queries:
        print(f"  - {query['name']}: {query['description']}")
    if start_date:
        print(f"\nDate filter: start_date >= {start_date}")
    if end_date:
        print(f"Date filter: end_date <= {end_date}")
    if force_refresh:
        print("\nMode: FULL REFRESH (will replace existing CSVs)")
    else:
        print("\nMode: INCREMENTAL UPDATE (will append new records)")
    print()

    # Connect to database once
    db = EZLinksRoundsDB(server, database, username, password, use_windows_auth)

    try:
        if not db.connect():
            print("Failed to connect to database")
            return False

        # Process each query
        for i, query in enumerate(queries, 1):
            print(f"\n[{i}/{len(queries)}] Processing query: {query['name']}")
            print("-" * 80)

            if force_refresh:
                # Full refresh mode - replace entire CSV
                db.refresh_full_csv(
                    table_name="N/A",  # Not used when base_query is provided
                    csv_file=query['csv_file'],
                    date_column=query['date_column'],
                    count_column=query['count_column'],
                    base_query=query.get('base_query'),
                    filtered_query=query.get('filtered_query'),
                    order_by=query.get('order_by'),
                    start_date=start_date,
                    end_date=end_date
                )
            else:
                # Incremental update mode - append new records
                db.update_csv(
                    table_name="N/A",  # Not used when base_query is provided
                    csv_file=query['csv_file'],
                    date_column=query['date_column'],
                    count_column=query['count_column'],
                    base_query=query.get('base_query'),
                    filtered_query=query.get('filtered_query'),
                    order_by=query.get('order_by'),
                    max_date_query=query.get('max_date_query'),
                    force_start_date=start_date,
                    end_date=end_date
                )

        print("\n" + "=" * 80)
        print("CSV files updated successfully!")
        print("=" * 80)

    finally:
        db.disconnect()

    print("\n" + "=" * 80)
    print("RUNNING ANOMALY ANALYSIS")
    print("=" * 80)

    # Run the anomaly analysis (from past_low_anomalies.py)
    import subprocess
    result = subprocess.run(['python3', 'past_low_anomalies.py'],
                          capture_output=True, text=True)
    print(result.stdout)

    if result.returncode != 0:
        print("Error running anomaly analysis:")
        print(result.stderr)
        return False

    return True


if __name__ == '__main__':
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Update data from SQL Server and run anomaly analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Incremental update (all queries)
  python3 update_and_analyze.py

  # Update specific query only
  python3 update_and_analyze.py --query ezlinks_rounds

  # Update multiple specific queries
  python3 update_and_analyze.py --query query1 --query query2

  # Get data from 2024 onwards
  python3 update_and_analyze.py --start-date 20240101

  # Get data for specific date range with specific query
  python3 update_and_analyze.py --query ezlinks_rounds --start-date 20240101 --end-date 20241231

  # Full refresh with date filter
  python3 update_and_analyze.py --start-date 20240101 --refresh
        """
    )
    parser.add_argument('--query', action='append', dest='queries', metavar='NAME',
                       help='Query name to process (can be specified multiple times, default: all queries)')
    parser.add_argument('--start-date', type=str, metavar='YYYYMMDD',
                       help='Start date filter (e.g., 20240101)')
    parser.add_argument('--end-date', type=str, metavar='YYYYMMDD',
                       help='End date filter (e.g., 20241231)')
    parser.add_argument('--refresh', action='store_true',
                       help='Force full refresh (replace CSV instead of append)')

    args = parser.parse_args()

    # Try to load config file
    try:
        import config
        SERVER = config.SERVER
        DATABASE = config.DATABASE
        USE_WINDOWS_AUTH = config.USE_WINDOWS_AUTH
        USERNAME = getattr(config, 'USERNAME', None)
        PASSWORD = getattr(config, 'PASSWORD', None)

        print(f"Loaded configuration:")
        print(f"  Server: {SERVER}")
        print(f"  Database: {DATABASE}")
        print(f"  Auth: {'Windows' if USE_WINDOWS_AUTH else 'SQL Server'}")
        print()

        success = update_and_analyze(
            SERVER, DATABASE,
            use_windows_auth=USE_WINDOWS_AUTH,
            username=USERNAME,
            password=PASSWORD,
            start_date=args.start_date,
            end_date=args.end_date,
            force_refresh=args.refresh,
            query_names=args.queries
        )

    except ImportError:
        print("ERROR: config.py not found!")
        print("Please copy config_template.py to config.py and update with your details.")
        print()
        print("  cp config_template.py config.py")
        print("  # Then edit config.py with your database settings")
        sys.exit(1)

    except AttributeError as e:
        print(f"ERROR: Missing configuration value: {e}")
        print("Please check your config.py file.")
        sys.exit(1)

    sys.exit(0 if success else 1)
