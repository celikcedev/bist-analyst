#!/usr/bin/env python3
"""
Wrapper script to run market data update with correct Python path.
"""
import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now import and run the updater
from backend.modules.market_data.updater import run_daily_update

if __name__ == '__main__':
    print("=" * 60)
    print("📊 BIST Market Data Update")
    print("=" * 60)
    run_daily_update()
