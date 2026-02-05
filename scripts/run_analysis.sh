#!/bin/bash
#
# Data Anomaly Detector - Setup and Run Script
# Installs dependencies, updates data from database (if possible), and generates HTML report
#

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Project root is parent of scripts directory
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$ROOT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================"
echo "Data Anomaly Detector"
echo "========================================"
echo ""

# Step 1: Check Python
echo -e "${YELLOW}[1/5] Checking Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: python3 not found. Please install Python 3.7+${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}Found: $PYTHON_VERSION${NC}"

# Step 2: Install Python dependencies
echo ""
echo -e "${YELLOW}[2/5] Installing Python dependencies...${NC}"
pip3 install -q -r requirements.txt 2>/dev/null || pip install -q -r requirements.txt
echo -e "${GREEN}Dependencies installed${NC}"

# Step 3: Install ODBC driver (macOS only)
echo ""
echo -e "${YELLOW}[3/5] Checking ODBC driver...${NC}"
if [[ "$OSTYPE" == "darwin"* ]]; then
    if ! brew list msodbcsql18 &>/dev/null && ! brew list msodbcsql17 &>/dev/null; then
        echo "Installing Microsoft ODBC Driver for SQL Server..."
        brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release 2>/dev/null || true
        HOMEBREW_ACCEPT_EULA=Y brew install msodbcsql18 --no-quarantine 2>/dev/null || {
            echo -e "${YELLOW}Warning: Could not install ODBC driver. Database updates will be skipped.${NC}"
        }
    else
        echo -e "${GREEN}ODBC driver already installed${NC}"
    fi
else
    echo "Non-macOS system detected. Ensure ODBC driver is installed manually."
fi

# Step 4: Check configuration files
echo ""
echo -e "${YELLOW}[4/5] Checking configuration...${NC}"
CONFIG_OK=true

if [[ ! -f "config.py" ]]; then
    echo -e "${YELLOW}Warning: config.py not found. Creating from template...${NC}"
    if [[ -f "config_template.py" ]]; then
        cp config_template.py config.py
        echo -e "${YELLOW}Please edit config.py with your database credentials${NC}"
    fi
    CONFIG_OK=false
fi

if [[ ! -f "queries.json" ]]; then
    echo -e "${YELLOW}Warning: queries.json not found. Creating from template...${NC}"
    if [[ -f "queries_template.json" ]]; then
        cp queries_template.json queries.json
        echo -e "${YELLOW}Please edit queries.json with your query definitions${NC}"
    fi
    CONFIG_OK=false
fi

if [[ "$CONFIG_OK" == true ]]; then
    echo -e "${GREEN}Configuration files found${NC}"
fi

# Step 5: Run analysis
echo ""
echo -e "${YELLOW}[5/5] Running analysis...${NC}"
echo ""

# Try to update from database first
DB_UPDATE_SUCCESS=false
if [[ "$CONFIG_OK" == true ]]; then
    echo "Attempting to update data from database..."
    if python3 "$SCRIPT_DIR/update_and_analyze.py" --start-date 20240101 2>/dev/null; then
        DB_UPDATE_SUCCESS=true
        echo -e "${GREEN}Database update successful${NC}"
    else
        echo -e "${YELLOW}Database update failed (ODBC issue or no connection)${NC}"
        echo "Falling back to analysis of existing CSV data..."
    fi
fi

# Run analysis and generate HTML report
echo ""
echo "Generating HTML report..."
if python3 "$SCRIPT_DIR/past_low_anomalies.py" --html; then
    echo ""
    echo -e "${GREEN}========================================"
    echo "Analysis complete!"
    echo "========================================${NC}"
    echo ""
    echo "Report generated: reports/anomaly_report.html"

    # Open report in browser (macOS)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo ""
        read -p "Open report in browser? [Y/n] " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
            open reports/anomaly_report.html
        fi
    fi
else
    echo -e "${RED}Error: Analysis failed${NC}"
    exit 1
fi
