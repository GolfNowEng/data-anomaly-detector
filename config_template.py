# Database Configuration
# Copy this file to config.py and update with your actual values

# SQL Server connection details
SERVER = "your-server-name.database.windows.net"  # e.g., "localhost" or "server.domain.com"
DATABASE = "your-database-name"
TABLE = "your-table-name"

# Column names in your table
DATE_COLUMN = "playdatekey"  # Column containing the date (YYYYMMDD format)
COUNT_COLUMN = "count"        # Column containing the count value

# Authentication
USE_WINDOWS_AUTH = True  # Set to False to use SQL Server authentication

# Only needed if USE_WINDOWS_AUTH = False
USERNAME = "your-username"
PASSWORD = "your-password"

# SQL Query Templates
# Use {date_column}, {count_column}, {table}, {start_date}, {end_date} as placeholders

# Base query - can include JOINs, WHERE clauses, etc.
BASE_QUERY = """
SELECT {date_column}, {count_column}
FROM {table}
"""

# Query with date filtering (will be used when start_date or end_date is provided)
# The WHERE clause will be automatically added based on start_date/end_date parameters
FILTERED_QUERY = """
SELECT {date_column}, {count_column}
FROM {table}
WHERE {{where_clause}}
"""

# Query to get the latest date
MAX_DATE_QUERY = """
SELECT MAX({date_column})
FROM {table}
"""

# Order by clause
ORDER_BY = "ORDER BY {date_column}"
