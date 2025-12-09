#!/bin/bash

# BIST Analyst - Cron Job Setup Script
# This script helps setup automated daily market data updates and scans

echo "============================================================"
echo "📅 BIST Analyst - Cron Job Setup"
echo "============================================================"
echo ""

# Get project directory
PROJECT_DIR="/Users/ademcelik/Desktop/bist_analyst"
VENV_PATH="$PROJECT_DIR/.venv/bin/activate"

# Check if venv exists
if [ ! -f "$VENV_PATH" ]; then
    echo "❌ Error: Virtual environment not found at $VENV_PATH"
    exit 1
fi

echo "Project Directory: $PROJECT_DIR"
echo ""

# Cron job entries
CRON_UPDATE="35 18 * * 1-5 cd $PROJECT_DIR && source $VENV_PATH && python3 run_data_update.py >> logs/data_update_cron.log 2>&1"
CRON_SCAN="40 18 * * 1-5 cd $PROJECT_DIR && source $VENV_PATH && python3 scripts/run_scan.py XTUMYV27Strategy >> logs/scan_cron.log 2>&1"

echo "Suggested Cron Jobs:"
echo "------------------------------------------------------------"
echo ""
echo "1. Daily Market Data Update (Mon-Fri at 18:35)"
echo "   - Fetches latest daily bars"
echo "   - Upserts only new data"
echo "   - Logs to: logs/data_update_cron.log"
echo ""
echo "$CRON_UPDATE"
echo ""
echo "------------------------------------------------------------"
echo ""
echo "2. Daily Signal Scan (Mon-Fri at 18:40)"
echo "   - Runs XTUMY V27 strategy"
echo "   - Saves signals to database"
echo "   - Sends Telegram notifications (if enabled)"
echo "   - Logs to: logs/scan_cron.log"
echo ""
echo "$CRON_SCAN"
echo ""
echo "============================================================"
echo ""
echo "📝 To install these cron jobs:"
echo ""
echo "1. Edit crontab:"
echo "   crontab -e"
echo ""
echo "2. Add these lines:"
echo "   (Press 'i' to insert, then paste)"
echo ""
echo "   # BIST Analyst - Daily Updates"
echo "   $CRON_UPDATE"
echo ""
echo "   # BIST Analyst - Daily Scan"
echo "   $CRON_SCAN"
echo ""
echo "3. Save and exit:"
echo "   Press ESC, then type :wq and press ENTER"
echo ""
echo "============================================================"
echo ""
echo "💡 Tips:"
echo "   - Make sure logs/ directory exists"
echo "   - Test manually first:"
echo "     cd $PROJECT_DIR && source $VENV_PATH && python3 run_data_update.py"
echo ""
echo "   - View cron logs:"
echo "     tail -f logs/data_update_cron.log"
echo "     tail -f logs/scan_cron.log"
echo ""
echo "   - List current cron jobs:"
echo "     crontab -l"
echo ""
echo "============================================================"
