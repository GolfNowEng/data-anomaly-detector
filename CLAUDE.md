# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Data Anomaly Detector - Python tools for querying SQL Server database and analyzing data for anomalies. The system pulls data from SQL Server, maintains CSV caches, and performs statistical anomaly detection based on year-over-year comparison across multiple configurable queries.

## Architecture

**Data Flow:**
```
config.py (credentials) + queries.json (queries) → query_loader.py →
SQL Server → EZLinksRoundsDB.update_csv() → working-dir/*.csv →
past_low_anomalies.py → Console output OR html_report.py → HTML file
```

**Core Components (in `scripts/` folder):**

| File | Purpose | Key Functions |
|------|---------|---------------|
| `db_query.py` | SQL Server via pyodbc | `EZLinksRoundsDB.update_csv()` at line 208 |
| `query_loader.py` | Validates queries.json | `load_queries()` at line 11 |
| `html_report.py` | HTML report generator | `generate_html_report()` at line 10 |
| `update_and_analyze.py` | Orchestration: DB update + analysis | Main entry point |
| `past_low_anomalies.py` | YoY anomaly detection engine | `analyze_csv()`, `find_prior_year_date()` |
| `run_analysis.sh` | One-command setup and run | Bash script |

**Config files (in root):**

| File | Purpose |
|------|---------|
| `config.py` | Database credentials (gitignored) |
| `config_template.py` | Template for config.py |
| `queries.json` | Query definitions (gitignored) |
| `queries_template.json` | Template for queries.json |

**Gitignored directories:**
- `working-dir/` - CSV cache files (one per query)
- `reports/` - Generated HTML reports

## Common Commands

```bash
# Setup
pip install -r requirements.txt
brew install microsoft/mssql-release/msodbcsql17  # macOS ODBC driver
cp config_template.py config.py && cp queries_template.json queries.json

# One-command setup and run (recommended)
./scripts/run_analysis.sh

# Main workflow - update CSVs and analyze
python3 scripts/update_and_analyze.py                           # All queries, incremental
python3 scripts/update_and_analyze.py --query myquery           # Single query
python3 scripts/update_and_analyze.py --start-date 20240101     # From specific date
python3 scripts/update_and_analyze.py --refresh --start-date 20240101  # Full refresh

# Analysis only (no database update)
python3 scripts/past_low_anomalies.py                           # Console output
python3 scripts/past_low_anomalies.py --html                    # HTML report
python3 scripts/past_low_anomalies.py --html --min-date 2024-01-01  # Custom date filter
```

## Key Design Decisions

**Year-over-year comparison:** Anomaly detection compares each date to the same day-of-week from the prior year. Anomalies flagged when: YoY decrease >= 50% OR count < absolute minimum threshold. This accounts for seasonal patterns.

**CSV caching:** `update_csv()` reads latest date in CSV, queries only newer records, appends. Avoids re-downloading history on each run.

**Multi-query architecture:** queries.json defines multiple data sources (e.g., rounds by course, tier, region). Each maintains separate CSV cache and thresholds.

**Date format support:** Handles both YYYYMMDD (int) and YYYY-MM-DD (string) via `parse_date()` at past_low_anomalies.py:16.

**Authentication:** ODBC switches between Windows auth (`Trusted_Connection=yes`) and SQL auth (`UID/PWD`) based on `use_windows_auth` flag.

## Configuration

**queries.json required fields:**
- `name`, `csv_file`, `date_column`, `count_column`

**queries.json optional fields:**
- `base_query`, `filtered_query` (with `{where_clause}` placeholder), `max_date_query`, `order_by`
- `anomaly_threshold_z` (default: -2.5), `anomaly_threshold_min` (default: 5000)

## Implementation Notes

**Hardcoded dates:** The TODAY constant appears at scripts/past_low_anomalies.py:104 and :275. Update when needed for testing.

**HTML severity levels:** Severe (<-95%, red), Moderate (-85% to -95%, orange), Mild (>-85%, yellow)