# EZ Links Rounds Data Analysis

Python tools for querying SQL Server database and analyzing ezlrounds data for anomalies.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install ODBC Driver for SQL Server:**
   - **Windows**: Usually already installed
   - **macOS**: `brew install microsoft/mssql-release/msodbcsql17`
   - **Linux**: Follow [Microsoft's instructions](https://docs.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server)

3. **Configure database connection:**
   ```bash
   cp config_template.py config.py
   # Edit config.py with your database details
   ```

## Usage

### Option 1: Update CSV and Run Analysis
```bash
python3 update_and_analyze.py
```
This will:
1. Connect to your SQL Server database
2. Pull new data since the last CSV update
3. Run anomaly analysis on the updated data

### Option 2: Use the Database Module Directly
```python
from db_query import EZLinksRoundsDB

# Connect to database
db = EZLinksRoundsDB("server-name", "database-name", use_windows_auth=True)

try:
    if db.connect():
        # Update existing CSV with new data
        db.update_csv("table-name")

        # Or refresh entire CSV
        # db.refresh_full_csv("table-name")

        # Or query specific date range
        data = db.query_rounds_data(
            "table-name",
            start_date="20240101",
            end_date="20240131"
        )
finally:
    db.disconnect()
```

### Option 3: Run Anomaly Analysis Only
```bash
python3 past_low_anomalies.py
```
Analyzes the existing `ezlrounds.csv` file for anomalies.

## Files

- **db_query.py** - Database connection and query module
- **past_low_anomalies.py** - Anomaly detection script (past low values only)
- **analyze_anomalies.py** - Full anomaly detection with statistics
- **update_and_analyze.py** - Combined script to update data and analyze
- **config_template.py** - Template for database configuration
- **requirements.txt** - Python dependencies

## Database Methods

### `connect()`
Establish connection to SQL Server database.

### `query_rounds_data(table_name, date_column, count_column, start_date, end_date)`
Query rounds data with optional date filtering.

### `update_csv(table_name, csv_file)`
Intelligently update CSV by appending only new records since the last date in the CSV.

### `refresh_full_csv(table_name, csv_file)`
Replace CSV with all data from database.

### `get_latest_date(table_name, date_column)`
Get the most recent date in the database.

## Configuration

Update `config.py` with your database details:

```python
SERVER = "your-server.database.windows.net"
DATABASE = "your-database-name"
TABLE = "your-table-name"
DATE_COLUMN = "playdatekey"
COUNT_COLUMN = "count"
USE_WINDOWS_AUTH = True  # or False for SQL auth
```

### Custom SQL Queries

You can customize the SQL queries in `config.py` to handle complex schemas, JOINs, or additional filtering:

```python
# Example: Simple query (default behavior if not specified)
BASE_QUERY = """
SELECT {date_column}, {count_column}
FROM {table}
"""

# Example: Query with JOIN
BASE_QUERY = """
SELECT r.{date_column}, SUM(r.{count_column}) as {count_column}
FROM {table} r
INNER JOIN courses c ON r.course_id = c.id
WHERE c.active = 1
GROUP BY r.{date_column}
"""

# Example: Query with additional filtering
FILTERED_QUERY = """
SELECT {date_column}, {count_column}
FROM {table}
WHERE {where_clause}
  AND status = 'completed'
"""

# Example: Custom ORDER BY
ORDER_BY = "ORDER BY {date_column} DESC"

# Example: Custom MAX query
MAX_DATE_QUERY = """
SELECT MAX({date_column})
FROM {table}
WHERE status = 'completed'
"""
```

**Available placeholders:**
- `{date_column}` - Date column name from config
- `{count_column}` - Count column name from config
- `{table}` - Table name from config
- `{where_clause}` - Auto-generated WHERE clause for date filtering

**Note:** If you don't specify custom queries in config, the default queries will be used.

## Authentication Options

**Windows Authentication** (default):
```python
db = EZLinksRoundsDB(server, database, use_windows_auth=True)
```

**SQL Server Authentication**:
```python
db = EZLinksRoundsDB(server, database,
                     username="user",
                     password="pass",
                     use_windows_auth=False)
```

## Anomaly Detection

The analysis identifies days with abnormally low counts by:
1. Calculating expected counts for each day of week
2. Computing z-scores for each day
3. Flagging days with z-score < -2.5 or count < 5000
4. Considering day-of-week patterns (weekends typically have higher counts)

## Next Steps

Once configured, please provide:
1. Your SQL Server hostname/IP
2. Database name
3. Table name
4. Column names (if different from "playdatekey" and "count")
5. Authentication method preference
