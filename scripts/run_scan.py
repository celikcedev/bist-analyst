#!/usr/bin/env python3
"""
CLI wrapper for running scans - backward compatible with cron jobs.

Usage:
    python scripts/run_scan.py --strategy xtumy_v27 --telegram
    python scripts/run_scan.py --strategy XTUMYV27Strategy --save-db
"""
import sys
import os
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.modules.screener.scanner import ScanEngine
from backend.modules.screener.strategies.xtumy_v27 import XTUMYV27Strategy
from scripts.telegram_bot import TelegramBot
import pandas as pd


def format_signals_for_display(signals: list) -> str:
    """Format signals for console output."""
    if not signals:
        return "❌ Sinyal bulunamadı."
    
    # Group by signal type
    df = pd.DataFrame(signals)
    
    output = []
    output.append("=" * 70)
    output.append(f"✅ {len(signals)} SİNYAL BULUNDU")
    output.append("=" * 70)
    
    for signal_type in df['signal_type'].unique():
        signal_df = df[df['signal_type'] == signal_type]
        output.append(f"\n📊 {signal_type} ({len(signal_df)} adet)")
        output.append("-" * 70)
        
        for _, row in signal_df.iterrows():
            signal_date = row['signal_date'][:10] if isinstance(row['signal_date'], str) else str(row['signal_date'])
            output.append(
                f"  {row['symbol']:8s} │ {row['price']:8.2f} TL │ "
                f"RSI: {row.get('rsi', 0):5.1f} │ ADX: {row.get('adx', 0):5.1f} │ {signal_date}"
            )
    
    output.append("=" * 70)
    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description='Run trading strategy scan')
    parser.add_argument('--strategy', type=str, default='XTUMYV27Strategy',
                       help='Strategy name (default: XTUMYV27Strategy)')
    parser.add_argument('--user-id', type=int, default=1,
                       help='User ID (default: 1)')
    parser.add_argument('--telegram', action='store_true',
                       help='Send results to Telegram')
    parser.add_argument('--save-db', action='store_true', default=True,
                       help='Save results to database (default: True)')
    parser.add_argument('--no-save-db', action='store_false', dest='save_db',
                       help='Do not save results to database')
    parser.add_argument('--symbols', type=str, nargs='+',
                       help='Specific symbols to scan (optional)')
    
    args = parser.parse_args()
    
    # Map legacy strategy names
    strategy_name = args.strategy
    if strategy_name.lower() == 'xtumy_v27':
        strategy_name = 'XTUMYV27Strategy'
    
    try:
        print(f"🚀 Starting scan with strategy: {strategy_name}")
        print(f"   User ID: {args.user_id}")
        print(f"   Save to DB: {args.save_db}")
        
        # Ensure strategy is registered in database
        ScanEngine.ensure_strategy_in_db(strategy_name)
        
        # Create scan engine
        scan_engine = ScanEngine(strategy_name, args.user_id)
        
        # Run scan
        signals = scan_engine.run_scan(
            save_to_db=args.save_db,
            symbols=args.symbols
        )
        
        # Print results
        print(format_signals_for_display(signals))
        
        # Send to Telegram if requested
        if args.telegram and signals:
            try:
                bot = TelegramBot()
                df_signals = pd.DataFrame(signals)
                bot.send_scan_results(df_signals)
                print("✓ Results sent to Telegram")
            except Exception as e:
                print(f"⚠️  Failed to send Telegram: {e}")
        
        return 0
    
    except KeyError as e:
        print(f"❌ Strategy '{strategy_name}' not found")
        print(f"   Available strategies: {list(strategy_name for strategy_name in ['XTUMYV27Strategy'])}")
        return 1
    
    except Exception as e:
        print(f"❌ Error running scan: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
