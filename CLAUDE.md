# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

EZ Links Rounds Data Analysis - Python tools for querying SQL Server database and analyzing ezlrounds data for anomalies. The system pulls rounds data from SQL Server, maintains CSV caches, and performs statistical anomaly detection based on day-of-week patterns across multiple configurable queries.

## Architecture

**Core Components:**

1. **config.py** - Database credentials only
   - `SERVER`, `DATABASE`, `USE_WINDOWS_AUTH`, `USERNAME`, `PASSWORD`
   - No query definitions (moved to queries.json)

2. **queries.json** - Query configuration (gitignored)
   - Defines multiple SQL queries to track different data dimensions
   - Each query specifies CSV path, SQL templates, column mappings, anomaly thresholds
   - Supports custom queries with JOINs, GROUP BY, complex filters
   - All CSV files stored in `working-dir/` folder

3. **query_loader.py** - Query configuration loader
   - `load_queries()` function loads and validates queries.json
   - Validates required fields: name, csv_file, date_column, count_column
   - Sets defaults for optional fields
   - Creates working-dir/ if needed

4. **db_query.py** - Database abstraction layer
   - `EZLinksRoundsDB` class handles all SQL Server connectivity via pyodbc
   - Supports both Windows and SQL Server authentication
   - Provides intelligent CSV update (append only new records) vs full refresh
   - `update_csv()` at db_query.py:208 handles incremental updates

5. **update_and_analyze.py** - Orchestration script
   - Loads configuration from config.py (credentials only)
   - Loads queries from queries.json using query_loader
   - Connects to database once and processes all queries
   - Subprocess calls past_low_anomalies.py for analysis
   - Single entry point for the full workflow

6. **past_low_anomalies.py** - Statistical anomaly detection
   - Loads queries from queries.json
   - Analyzes each CSV file independently
   - Calculates day-of-week statistics (mean, stdev)
   - Flags low anomalies using per-query thresholds
   - Only analyzes past dates (hardcoded TODAY reference)
   - Produces consolidated report grouped by query

**Data Flow:**
```
config.py (credentials) + queries.json (queries) → query_loader.py →
SQL Server → EZLinksRoundsDB.update_csv() → working-dir/*.csv →
past_low_anomalies.py → Consolidated anomaly report
```

**Configuration System:**
- `config_template.py` provides structure for database credentials
- `queries_template.json` provides structure for query definitions
- User creates `config.py` and `queries.json` (both gitignored)
- Query definitions include SQL templates, column mappings, anomaly thresholds
- System performs anomaly analysis across multiple queries simultaneously

**Directory Structure:**
- `working-dir/` - Contains all CSV cache files (gitignored)
- Each query maintains its own CSV file in working-dir/
- CSV files are created automatically on first run

## Common Commands

**Setup:**
```bash
# Install dependencies
pip install -r requirements.txt

# Install ODBC Driver (macOS)
brew install microsoft/mssql-release/msodbcsql17

# Configure database connection
cp config_template.py config.py
# Edit config.py with your database credentials

# Configure queries
cp queries_template.json queries.json
# Edit queries.json with your SQL queries
```

**Main workflow:**
```bash
# Update CSVs from database and run analysis
python3 update_and_analyze.py
```

**Individual operations:**
```bash
# Run anomaly analysis only (on existing CSVs)
python3 past_low_anomalies.py

# Test query configuration
python3 query_loader.py

# Direct database operations (edit db_query.py main() function first)
python3 db_query.py
```

## Key Design Decisions

**Multi-query architecture:** queries.json allows defining multiple data sources to track different dimensions (e.g., rounds by course, membership tier, region). Each query maintains its own CSV cache and statistical baseline. Anomaly analysis runs across all queries to provide comprehensive insights.

**CSV-based caching:** The system maintains separate CSV files for each query in working-dir/. `update_csv()` reads the latest date in each CSV and queries only newer records, then appends them. This avoids re-downloading historical data on each run.

**Day-of-week statistics:** Anomaly detection calculates separate mean/stdev for each day of week (Monday, Tuesday, etc.) since weekends typically have higher golf round counts. Each day is compared against its own historical pattern.

**Query separation:** Database credentials are in config.py (server, auth), while query definitions are in queries.json (SQL, columns, thresholds). This separation allows sharing config_template.py while keeping sensitive table names private.

**Date filtering:** The database query layer builds WHERE clauses dynamically based on start_date/end_date parameters. Custom queries can override this with FILTERED_QUERY template that includes a {where_clause} placeholder.

**Authentication flexibility:** The ODBC connection string switches between `Trusted_Connection=yes` (Windows auth) and `UID/PWD` (SQL auth) based on `use_windows_auth` flag. Both use `TrustServerCertificate=yes` for SSL compatibility.

**Working directory:** All CSV files are stored in `working-dir/` folder to keep the repository root clean. The folder is gitignored to avoid committing large data files.

## Configuration Files

**config.py** contains database credentials only:
- SERVER, DATABASE, USE_WINDOWS_AUTH, USERNAME, PASSWORD

**queries.json** defines multiple data queries (gitignored):
- Each query entry specifies SQL templates, column mappings, CSV output path
- `name` - Unique query identifier
- `description` - Human-readable description
- `csv_file` - Path to CSV cache (in working-dir/)
- `date_column` and `count_column` - Column names in query results
- `base_query`, `filtered_query`, `max_date_query`, `order_by` - SQL templates
- `anomaly_threshold_z` and `anomaly_threshold_min` - Detection thresholds
- Custom queries support JOINs, subqueries, aggregations, complex filters
- The {where_clause} placeholder in FILTERED_QUERY gets auto-populated with date filters
- Multiple queries enable tracking different metrics simultaneously

## Important Implementation Details

**query_loader.py:**
- `load_queries()` at query_loader.py:12 loads and validates queries.json
- Ensures required fields are present: name, csv_file, date_column, count_column
- Sets defaults for optional fields: base_query, filtered_query, order_by, thresholds
- Creates working-dir/ if it doesn't exist
- Returns list of validated query dictionaries

**db_query.py:**
- Connection is established lazily in query methods if not already connected
- `query_rounds_data()` at db_query.py:68 builds SQL dynamically based on parameters
- `update_csv()` at db_query.py:208 handles both initial creation and incremental updates
- Results are always returned as list of dicts with keys 'playdatekey' and 'count'

**update_and_analyze.py:**
- Loads database credentials from config.py
- Loads queries from queries.json using query_loader
- Connects to database once and processes all queries sequentially
- Uses subprocess to call past_low_anomalies.py (line 76) rather than importing directly
- Returns exit code 0 on success, 1 on failure for scripting

**past_low_anomalies.py:**
- TODAY constant at line 153 must be manually updated for current date filtering
- `analyze_csv()` at line 31 processes a single CSV file
- Z-score calculation at line 24 handles zero stdev edge case
- Anomaly threshold: z_score < threshold_z OR count < threshold_min (line 106)
- `print_anomalies()` at line 121 formats output grouped by year/month
- Output formatting includes count, expected, z-score, and percent difference
- Produces consolidated report with summary across all queries