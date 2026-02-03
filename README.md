# EZ Links Rounds Data Analysis

Python tools for querying SQL Server database and analyzing ezlrounds data for anomalies. The system pulls rounds data from SQL Server, maintains CSV caches, and performs statistical anomaly detection based on day-of-week patterns.

## Features

- **Multi-query support**: Define multiple SQL queries to track different data dimensions
- **Query filtering**: Process specific queries using `--query` parameter
- **CSV-based caching**: Intelligent incremental updates (append only new records)
- **Day-of-week statistics**: Anomaly detection considers weekday patterns
- **Flexible SQL queries**: Support for JOINs, GROUP BY, complex filters, multiple date formats
- **Date range filtering**: Focus on recent data with `--min-date` parameter (default: 2024-01-01)
- **Styled HTML reports**: Professional reports with sticky navigation, color-coded severity, smooth scrolling
- **Command-line flexibility**: Date filters, query selection, HTML/console output options
- **Consolidated reporting**: Analyze anomalies across all queries simultaneously

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
   # Edit config.py with your database credentials
   ```

4. **Configure queries:**
   ```bash
   cp queries_template.json queries.json
   # Edit queries.json with your SQL queries and table details
   ```

## Configuration

### config.py - Database Credentials

Contains only database connection settings:

```python
SERVER = "your-server.database.windows.net"
DATABASE = "your-database-name"
USE_WINDOWS_AUTH = True  # or False for SQL auth
USERNAME = "your-username"  # if USE_WINDOWS_AUTH = False
PASSWORD = "your-password"  # if USE_WINDOWS_AUTH = False
```

### queries.json - Query Definitions

Defines one or more SQL queries to analyze. Each query maintains its own CSV cache in `working-dir/`:

```json
{
  "queries": [
    {
      "name": "total_rounds",
      "description": "Total rounds played daily",
      "csv_file": "working-dir/ezlrounds.csv",
      "date_column": "playdatekey",
      "count_column": "count",
      "base_query": "SELECT {date_column}, {count_column} FROM {table}",
      "filtered_query": "SELECT {date_column}, {count_column} FROM {table} WHERE {where_clause}",
      "max_date_query": "SELECT MAX({date_column}) FROM {table}",
      "order_by": "ORDER BY {date_column}",
      "anomaly_threshold_z": -2.5,
      "anomaly_threshold_min": 5000
    }
  ]
}
```

**Required fields:**
- `name`: Unique query identifier
- `csv_file`: Path to CSV cache file (in working-dir/)
- `date_column`: Column containing date (YYYYMMDD format)
- `count_column`: Column containing count value

**Optional fields:**
- `description`: Human-readable description (defaults to name)
- `base_query`: Custom SQL query template
- `filtered_query`: Query template with {where_clause} placeholder
- `max_date_query`: Query to get latest date
- `order_by`: ORDER BY clause
- `anomaly_threshold_z`: Z-score threshold (default: -2.5)
- `anomaly_threshold_min`: Minimum count threshold (default: 5000)

**Query placeholders:**
- `{date_column}` - Date column name
- `{count_column}` - Count column name
- `{where_clause}` - Auto-generated date filters (for filtered_query)

## Usage

### Main Workflow: Update and Analyze

**Basic incremental update:**
```bash
python3 update_and_analyze.py
```
This will:
1. Connect to SQL Server database
2. Process all queries defined in queries.json
3. Update each CSV with new data since last run (incremental)
4. Run anomaly analysis across all queries
5. Display consolidated report grouped by query

**Get data from a specific start date:**
```bash
# Get data from 2024 onwards (appends to existing CSV)
python3 update_and_analyze.py --start-date 20240101
```

**Get data for a specific date range:**
```bash
# Get only 2024 data
python3 update_and_analyze.py --start-date 20240101 --end-date 20241231
```

**Full refresh with date filter:**
```bash
# Replace CSV with data from 2024 onwards
python3 update_and_analyze.py --start-date 20240101 --refresh
```

**Process specific query only:**
```bash
# Update only the ezlinks_rounds query
python3 update_and_analyze.py --query ezlinks_rounds

# Update multiple specific queries
python3 update_and_analyze.py --query query1 --query query2

# Combine with date filters
python3 update_and_analyze.py --query ezlinks_rounds --start-date 20240101
```

**Command-line options:**
- `--query NAME` - Query name to process (can be specified multiple times, default: all queries)
- `--start-date YYYYMMDD` - Start date filter (e.g., 20240101)
- `--end-date YYYYMMDD` - End date filter (e.g., 20241231)
- `--refresh` - Force full refresh (replace CSV instead of append)

**Update modes:**
- **Incremental (default)**: Appends new records to existing CSV starting from the latest date in the CSV
- **Incremental with start date**: Appends new records starting from specified date (useful for backfilling)
- **Full refresh**: Replaces entire CSV with fresh data from database (use with `--refresh` flag)

### Run Anomaly Analysis Only

**Console output:**
```bash
# Default (analyzes data from 2024-01-01 onwards)
python3 past_low_anomalies.py

# Custom date range
python3 past_low_anomalies.py --min-date 2023-01-01
```

**Generate HTML report:**
```bash
# Generate styled HTML report (default: anomaly_report.html)
python3 past_low_anomalies.py --html

# Specify custom output filename
python3 past_low_anomalies.py --html --output my_report.html

# Filter by date range
python3 past_low_anomalies.py --html --min-date 2024-01-01
```

**Command-line options:**
- `--html` - Generate HTML report
- `--output FILENAME` - Specify output filename (default: anomaly_report.html)
- `--min-date YYYY-MM-DD` - Minimum date to include in analysis (default: 2024-01-01)

The HTML report includes:
- **Sticky top navigation**: Quick links to jump between query sections
- **Executive summary**: Total anomalies across all queries with averages
- **Color-coded severity**: Severe (red, <-95%), Moderate (orange, -85% to -95%), Mild (yellow, >-85%)
- **Interactive tables**: Grouped by query and month with hover effects
- **Professional styling**: Gradient headers, smooth scrolling, responsive design
- **Print-friendly layout**: Navigation hidden, optimized formatting for printing

**Date filtering:**
By default, only anomalies from 2024-01-01 onwards are shown to reduce noise from historical data. This is especially important for queries with long history (e.g., customer data from 1900). You can customize the date range using `--min-date`.

Analyzes existing CSV files in `working-dir/` without updating from database.

### Test Query Configuration
```bash
python3 query_loader.py
```
Validates queries.json and displays loaded configuration.

### Use Database Module Directly
```python
from db_query import EZLinksRoundsDB
from query_loader import load_queries

# Load queries
queries = load_queries("queries.json")

# Connect to database
db = EZLinksRoundsDB("server", "database", use_windows_auth=True)

try:
    if db.connect():
        # Update CSV for each query
        for query in queries:
            db.update_csv(
                table_name="N/A",
                csv_file=query['csv_file'],
                date_column=query['date_column'],
                count_column=query['count_column'],
                base_query=query['base_query'],
                filtered_query=query['filtered_query'],
                order_by=query['order_by'],
                max_date_query=query['max_date_query']
            )
finally:
    db.disconnect()
```

## Query Examples

### Simple Query
```json
{
  "name": "daily_rounds",
  "description": "Daily round counts",
  "csv_file": "working-dir/rounds.csv",
  "date_column": "playdatekey",
  "count_column": "rounds",
  "base_query": "SELECT playdatekey, COUNT(*) as rounds FROM bookings GROUP BY playdatekey",
  "filtered_query": "SELECT playdatekey, COUNT(*) as rounds FROM bookings WHERE {where_clause} GROUP BY playdatekey",
  "max_date_query": "SELECT MAX(playdatekey) FROM bookings",
  "order_by": "ORDER BY playdatekey"
}
```

### Complex Query with JOIN
```json
{
  "name": "rounds_by_membership",
  "description": "Rounds by membership tier",
  "csv_file": "working-dir/membership_rounds.csv",
  "date_column": "play_date",
  "count_column": "round_count",
  "base_query": "SELECT r.play_date, COUNT(*) as round_count FROM rounds r INNER JOIN members m ON r.member_id = m.id WHERE m.tier = 'premium' GROUP BY r.play_date",
  "filtered_query": "SELECT r.play_date, COUNT(*) as round_count FROM rounds r INNER JOIN members m ON r.member_id = m.id WHERE m.tier = 'premium' AND {where_clause} GROUP BY r.play_date",
  "max_date_query": "SELECT MAX(play_date) FROM rounds",
  "order_by": "ORDER BY play_date",
  "anomaly_threshold_z": -2.0,
  "anomaly_threshold_min": 1000
}
```

### Aggregated Query
```json
{
  "name": "revenue_by_date",
  "description": "Total revenue per day",
  "csv_file": "working-dir/revenue.csv",
  "date_column": "transaction_date",
  "count_column": "total_revenue",
  "base_query": "SELECT transaction_date, SUM(amount) as total_revenue FROM transactions WHERE status = 'completed' GROUP BY transaction_date",
  "filtered_query": "SELECT transaction_date, SUM(amount) as total_revenue FROM transactions WHERE status = 'completed' AND {where_clause} GROUP BY transaction_date",
  "max_date_query": "SELECT MAX(transaction_date) FROM transactions WHERE status = 'completed'",
  "order_by": "ORDER BY transaction_date"
}
```

## Architecture

### Core Components

1. **config.py** - Database credentials only
2. **queries.json** - Query definitions (gitignored)
3. **query_loader.py** - Loads and validates queries
4. **db_query.py** - Database abstraction layer (EZLinksRoundsDB class)
5. **update_and_analyze.py** - Orchestration script
6. **past_low_anomalies.py** - Anomaly detection engine
7. **working-dir/** - CSV cache directory (gitignored)

### Data Flow
```
config.py → Database credentials
queries.json → Query definitions
    ↓
query_loader.py → Validates and loads queries
    ↓
db_query.py → Executes SQL queries
    ↓
working-dir/*.csv → CSV caches (one per query)
    ↓
past_low_anomalies.py → Anomaly detection
    ↓
Consolidated report grouped by query
```

## Files

- **config_template.py** - Template for database configuration
- **config.py** - Actual database credentials (gitignored)
- **queries_template.json** - Template for query definitions
- **queries.json** - Actual query definitions (gitignored)
- **query_loader.py** - Query configuration loader
- **db_query.py** - Database connection and query module
- **update_and_analyze.py** - Update data and run analysis
- **past_low_anomalies.py** - Anomaly detection script (past low values only)
- **requirements.txt** - Python dependencies
- **working-dir/** - CSV cache directory (gitignored)

## Anomaly Detection

The analysis identifies days with abnormally low counts by:

1. **Day-of-week grouping**: Groups historical data by day of week (Monday, Tuesday, etc.)
2. **Statistical baseline**: Calculates mean and standard deviation for each day of week
3. **Z-score calculation**: Computes z-score for each day against its day-of-week baseline
4. **Threshold detection**: Flags anomalies using two criteria:
   - Z-score < threshold (default: -2.5)
   - OR count < minimum threshold (default: 5000)
5. **Past-only filtering**: Only analyzes dates before TODAY constant (excludes future dates)

### Why day-of-week statistics?
Golf rounds typically follow weekly patterns (higher on weekends, lower on weekdays). Comparing each day against its specific day-of-week history provides more accurate anomaly detection than comparing against overall averages.

## Multi-Query Benefits

- **Multiple perspectives**: Track different data dimensions simultaneously (e.g., total rounds, rounds by course, rounds by membership tier)
- **Separate thresholds**: Each query can have custom z-score and minimum count thresholds
- **Independent caching**: Each query maintains its own CSV cache for efficient updates
- **Consolidated reporting**: Single analysis run produces comprehensive anomaly report across all queries

## Authentication Options

**Windows Authentication** (default):
```python
USE_WINDOWS_AUTH = True
```

**SQL Server Authentication**:
```python
USE_WINDOWS_AUTH = False
USERNAME = "your-username"
PASSWORD = "your-password"
```

## Troubleshooting

**Error: queries.json not found**
```bash
cp queries_template.json queries.json
# Edit queries.json with your query definitions
```

**Error: config.py not found**
```bash
cp config_template.py config.py
# Edit config.py with your database credentials
```

**CSV files not found**
- The system creates `working-dir/` automatically
- CSV files are created on first run
- Check that queries.json has correct csv_file paths

**Connection errors**
- Verify SERVER and DATABASE in config.py
- Check firewall allows SQL Server port (default: 1433)
- Ensure ODBC driver is installed correctly

## Next Steps

1. Copy config_template.py to config.py and add your database credentials
2. Copy queries_template.json to queries.json and define your queries
3. Run `python3 update_and_analyze.py` to test the system
4. Add more queries to queries.json as needed for different data dimensions
5. Adjust anomaly thresholds per query based on your data patterns
