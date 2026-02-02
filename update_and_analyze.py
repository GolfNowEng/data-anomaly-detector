#!/usr/bin/env python3
"""
Update data from database and run anomaly analysis.
"""

import sys
from db_query import EZLinksRoundsDB
from past_low_anomalies import *  # Import the analysis functions


def update_and_analyze(server: str, database: str, table: str,
                      date_column: str = "playdatekey",
                      count_column: str = "count",
                      use_windows_auth: bool = True,
                      username: str = None, password: str = None,
                      base_query: str = None,
                      filtered_query: str = None,
                      order_by: str = None,
                      max_date_query: str = None):
    """
    Pull latest data from database and run anomaly analysis.

    Args:
        server: SQL Server hostname
        database: Database name
        table: Table name
        date_column: Date column name
        count_column: Count column name
        use_windows_auth: Use Windows authentication
        username: SQL Server username (if not using Windows auth)
        password: SQL Server password (if not using Windows auth)
        base_query: Optional custom SQL query template
        filtered_query: Optional custom SQL query with WHERE clause
        order_by: Optional ORDER BY clause
        max_date_query: Optional custom MAX query
    """
    print("=" * 80)
    print("UPDATING DATA FROM DATABASE")
    print("=" * 80)

    # Connect to database
    db = EZLinksRoundsDB(server, database, username, password, use_windows_auth)

    try:
        if db.connect():
            # Update CSV with latest data
            db.update_csv(
                table,
                date_column=date_column,
                count_column=count_column,
                base_query=base_query,
                filtered_query=filtered_query,
                order_by=order_by,
                max_date_query=max_date_query
            )
            print("\nCSV file updated successfully!")
        else:
            print("Failed to connect to database")
            return False
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
        TABLE = getattr(config, 'TABLE', None)  # Optional since queries are hardcoded
        DATE_COLUMN = getattr(config, 'DATE_COLUMN', 'playdatekey')
        COUNT_COLUMN = getattr(config, 'COUNT_COLUMN', 'count')
        USE_WINDOWS_AUTH = config.USE_WINDOWS_AUTH
        USERNAME = getattr(config, 'USERNAME', None)
        PASSWORD = getattr(config, 'PASSWORD', None)

        # Load query templates from config
        BASE_QUERY = getattr(config, 'BASE_QUERY', None)
        FILTERED_QUERY = getattr(config, 'FILTERED_QUERY', None)
        ORDER_BY = getattr(config, 'ORDER_BY', None)
        MAX_DATE_QUERY = getattr(config, 'MAX_DATE_QUERY', None)

        print(f"Loaded configuration:")
        print(f"  Server: {SERVER}")
        print(f"  Database: {DATABASE}")
        if TABLE:
            print(f"  Table: {TABLE}")
        print(f"  Date Column: {DATE_COLUMN}")
        print(f"  Count Column: {COUNT_COLUMN}")
        print(f"  Auth: {'Windows' if USE_WINDOWS_AUTH else 'SQL Server'}")
        print(f"  Custom Queries: {'Yes' if BASE_QUERY else 'No'}")
        print()

        success = update_and_analyze(
            SERVER, DATABASE, TABLE or "N/A",
            date_column=DATE_COLUMN,
            count_column=COUNT_COLUMN,
            use_windows_auth=USE_WINDOWS_AUTH,
            username=USERNAME,
            password=PASSWORD,
            base_query=BASE_QUERY,
            filtered_query=FILTERED_QUERY,
            order_by=ORDER_BY,
            max_date_query=MAX_DATE_QUERY
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
