#!/usr/bin/env python3
"""
Update data from database and run anomaly analysis across multiple queries.
"""

import sys
from db_query import EZLinksRoundsDB
from query_loader import load_queries


def update_and_analyze(server: str, database: str,
                      use_windows_auth: bool = True,
                      username: str = None, password: str = None):
    """
    Pull latest data from database for all queries and run anomaly analysis.

    Args:
        server: SQL Server hostname
        database: Database name
        use_windows_auth: Use Windows authentication
        username: SQL Server username (if not using Windows auth)
        password: SQL Server password (if not using Windows auth)
    """
    # Load queries from JSON
    try:
        queries = load_queries("queries.json")
    except Exception as e:
        print(f"ERROR: Failed to load queries: {e}")
        return False

    print("=" * 80)
    print("UPDATING DATA FROM DATABASE")
    print("=" * 80)
    print(f"Loaded {len(queries)} queries:")
    for query in queries:
        print(f"  - {query['name']}: {query['description']}")
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

            db.update_csv(
                table_name="N/A",  # Not used when base_query is provided
                csv_file=query['csv_file'],
                date_column=query['date_column'],
                count_column=query['count_column'],
                base_query=query.get('base_query'),
                filtered_query=query.get('filtered_query'),
                order_by=query.get('order_by'),
                max_date_query=query.get('max_date_query')
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
            password=PASSWORD
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
