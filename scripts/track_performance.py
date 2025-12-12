#!/usr/bin/env python3
"""
Performance Tracker Script for BIST Analyst Screener Module.

This script tracks the performance of signals by calculating:
- +1 day price change
- +3 day price change  
- +7 day price change

Run daily via cron job after market close (e.g., 19:00 Turkish time).

Usage:
    python scripts/track_performance.py
    python scripts/track_performance.py --days 30  # Track last 30 days of signals
    python scripts/track_performance.py --telegram  # Send summary to Telegram
"""

import sys
import os
from datetime import datetime, timedelta, date
from decimal import Decimal
from typing import List, Dict, Any, Optional
import argparse

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from backend.core.database import get_db_session, engine
from backend.modules.screener.models import SignalHistory, SignalPerformance


def get_signals_to_track(days_back: int = 30) -> List[Dict[str, Any]]:
    """
    Get signals that need performance tracking.
    
    Args:
        days_back: How many days back to look for signals
        
    Returns:
        List of signals needing performance updates
    """
    cutoff_date = date.today() - timedelta(days=days_back)
    
    with get_db_session() as session:
        # Get signals without performance data or with incomplete data
        query = text("""
            SELECT 
                sh.id,
                sh.symbol,
                sh.signal_type,
                sh.signal_date,
                sh.price_at_signal,
                sp.id as perf_id,
                sp.price_1d,
                sp.price_3d,
                sp.price_7d
            FROM signal_history sh
            LEFT JOIN signal_performance sp ON sh.id = sp.signal_id
            WHERE sh.signal_date >= :cutoff_date
              AND sh.signal_date <= :today
              AND (
                  sp.id IS NULL 
                  OR (sp.price_1d IS NULL AND sh.signal_date <= :date_1d_ago)
                  OR (sp.price_3d IS NULL AND sh.signal_date <= :date_3d_ago)
                  OR (sp.price_7d IS NULL AND sh.signal_date <= :date_7d_ago)
              )
            ORDER BY sh.signal_date DESC
        """)
        
        today = date.today()
        result = session.execute(query, {
            'cutoff_date': cutoff_date,
            'today': today,
            'date_1d_ago': today - timedelta(days=1),
            'date_3d_ago': today - timedelta(days=3),
            'date_7d_ago': today - timedelta(days=7)
        })
        
        signals = []
        for row in result:
            signals.append({
                'id': row.id,
                'symbol': row.symbol,
                'signal_type': row.signal_type,
                'signal_date': row.signal_date,
                'price_at_signal': float(row.price_at_signal) if row.price_at_signal else None,
                'perf_id': row.perf_id,
                'price_1d': float(row.price_1d) if row.price_1d else None,
                'price_3d': float(row.price_3d) if row.price_3d else None,
                'price_7d': float(row.price_7d) if row.price_7d else None
            })
        
        return signals


def get_price_on_date(symbol: str, target_date: date) -> Optional[float]:
    """
    Get closing price for a symbol on a specific date.
    If exact date not found, try next trading day (up to 3 days).
    
    Args:
        symbol: Stock symbol
        target_date: Date to get price for
        
    Returns:
        Closing price or None if not found
    """
    with get_db_session() as session:
        # Try exact date first, then next 3 trading days
        query = text("""
            SELECT close, date
            FROM market_data
            WHERE symbol = :symbol
              AND date >= :target_date
              AND date <= :max_date
            ORDER BY date ASC
            LIMIT 1
        """)
        
        result = session.execute(query, {
            'symbol': symbol,
            'target_date': target_date,
            'max_date': target_date + timedelta(days=5)  # Account for weekends
        }).fetchone()
        
        if result:
            return float(result.close)
        
        return None


def calculate_gain(price_at_signal: float, price_later: float) -> float:
    """
    Calculate percentage gain.
    
    Args:
        price_at_signal: Original signal price
        price_later: Price at later date
        
    Returns:
        Percentage gain (e.g., 5.25 for +5.25%)
    """
    if not price_at_signal or price_at_signal == 0:
        return 0.0
    return round(((price_later - price_at_signal) / price_at_signal) * 100, 2)


def update_signal_performance(signal: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update performance data for a single signal.
    
    Args:
        signal: Signal dictionary
        
    Returns:
        Updated performance data
    """
    signal_date = signal['signal_date']
    symbol = signal['symbol']
    price_at_signal = signal['price_at_signal']
    today = date.today()
    
    updates = {
        'signal_id': signal['id'],
        'price_1d': signal['price_1d'],
        'price_3d': signal['price_3d'],
        'price_7d': signal['price_7d'],
        'gain_1d': None,
        'gain_3d': None,
        'gain_7d': None
    }
    
    if not price_at_signal:
        return updates
    
    # Calculate +1 day performance
    date_1d = signal_date + timedelta(days=1)
    if updates['price_1d'] is None and date_1d <= today:
        price = get_price_on_date(symbol, date_1d)
        if price:
            updates['price_1d'] = price
            updates['gain_1d'] = calculate_gain(price_at_signal, price)
    elif updates['price_1d']:
        updates['gain_1d'] = calculate_gain(price_at_signal, updates['price_1d'])
    
    # Calculate +3 day performance
    date_3d = signal_date + timedelta(days=3)
    if updates['price_3d'] is None and date_3d <= today:
        price = get_price_on_date(symbol, date_3d)
        if price:
            updates['price_3d'] = price
            updates['gain_3d'] = calculate_gain(price_at_signal, price)
    elif updates['price_3d']:
        updates['gain_3d'] = calculate_gain(price_at_signal, updates['price_3d'])
    
    # Calculate +7 day performance
    date_7d = signal_date + timedelta(days=7)
    if updates['price_7d'] is None and date_7d <= today:
        price = get_price_on_date(symbol, date_7d)
        if price:
            updates['price_7d'] = price
            updates['gain_7d'] = calculate_gain(price_at_signal, price)
    elif updates['price_7d']:
        updates['gain_7d'] = calculate_gain(price_at_signal, updates['price_7d'])
    
    return updates


def save_performance(signal: Dict[str, Any], perf_data: Dict[str, Any]) -> bool:
    """
    Save or update performance data in database.
    
    Args:
        signal: Original signal data
        perf_data: Calculated performance data
        
    Returns:
        True if saved successfully
    """
    with get_db_session() as session:
        if signal['perf_id']:
            # Update existing record
            perf = session.query(SignalPerformance).filter(
                SignalPerformance.id == signal['perf_id']
            ).first()
            
            if perf:
                if perf_data['price_1d'] is not None:
                    perf.price_1d = perf_data['price_1d']
                    perf.gain_1d = perf_data['gain_1d']
                if perf_data['price_3d'] is not None:
                    perf.price_3d = perf_data['price_3d']
                    perf.gain_3d = perf_data['gain_3d']
                if perf_data['price_7d'] is not None:
                    perf.price_7d = perf_data['price_7d']
                    perf.gain_7d = perf_data['gain_7d']
        else:
            # Create new record
            perf = SignalPerformance(
                signal_id=signal['id'],
                price_1d=perf_data['price_1d'],
                price_3d=perf_data['price_3d'],
                price_7d=perf_data['price_7d'],
                gain_1d=perf_data['gain_1d'],
                gain_3d=perf_data['gain_3d'],
                gain_7d=perf_data['gain_7d']
            )
            session.add(perf)
        
        session.commit()
        return True


def get_performance_summary() -> Dict[str, Any]:
    """
    Get performance summary statistics.
    
    Returns:
        Summary dictionary with win rates and average gains
    """
    with get_db_session() as session:
        query = text("""
            SELECT 
                sh.signal_type,
                COUNT(*) as total_signals,
                COUNT(sp.gain_1d) as tracked_1d,
                COUNT(sp.gain_3d) as tracked_3d,
                COUNT(sp.gain_7d) as tracked_7d,
                AVG(sp.gain_1d) as avg_gain_1d,
                AVG(sp.gain_3d) as avg_gain_3d,
                AVG(sp.gain_7d) as avg_gain_7d,
                SUM(CASE WHEN sp.gain_1d > 0 THEN 1 ELSE 0 END) as wins_1d,
                SUM(CASE WHEN sp.gain_3d > 0 THEN 1 ELSE 0 END) as wins_3d,
                SUM(CASE WHEN sp.gain_7d > 0 THEN 1 ELSE 0 END) as wins_7d
            FROM signal_history sh
            LEFT JOIN signal_performance sp ON sh.id = sp.signal_id
            WHERE sh.signal_date >= :cutoff_date
            GROUP BY sh.signal_type
            ORDER BY sh.signal_type
        """)
        
        cutoff = date.today() - timedelta(days=30)
        result = session.execute(query, {'cutoff_date': cutoff})
        
        summary = {
            'period': '30 days',
            'generated_at': datetime.now().isoformat(),
            'by_signal_type': []
        }
        
        for row in result:
            tracked_1d = row.tracked_1d or 0
            tracked_3d = row.tracked_3d or 0
            tracked_7d = row.tracked_7d or 0
            
            summary['by_signal_type'].append({
                'signal_type': row.signal_type,
                'total_signals': row.total_signals,
                'performance': {
                    '1d': {
                        'tracked': tracked_1d,
                        'avg_gain': round(float(row.avg_gain_1d), 2) if row.avg_gain_1d else None,
                        'win_rate': round((row.wins_1d / tracked_1d) * 100, 1) if tracked_1d > 0 else None,
                        'wins': row.wins_1d or 0
                    },
                    '3d': {
                        'tracked': tracked_3d,
                        'avg_gain': round(float(row.avg_gain_3d), 2) if row.avg_gain_3d else None,
                        'win_rate': round((row.wins_3d / tracked_3d) * 100, 1) if tracked_3d > 0 else None,
                        'wins': row.wins_3d or 0
                    },
                    '7d': {
                        'tracked': tracked_7d,
                        'avg_gain': round(float(row.avg_gain_7d), 2) if row.avg_gain_7d else None,
                        'win_rate': round((row.wins_7d / tracked_7d) * 100, 1) if tracked_7d > 0 else None,
                        'wins': row.wins_7d or 0
                    }
                }
            })
        
        return summary


def format_telegram_message(summary: Dict[str, Any]) -> str:
    """
    Format performance summary for Telegram.
    
    Args:
        summary: Performance summary dictionary
        
    Returns:
        Formatted message string
    """
    msg = "📊 *BIST Analyst - Performans Raporu*\n"
    msg += f"📅 Son 30 Gün\n"
    msg += "━" * 30 + "\n\n"
    
    for item in summary['by_signal_type']:
        signal_type = item['signal_type']
        total = item['total_signals']
        perf = item['performance']
        
        msg += f"*{signal_type}* ({total} sinyal)\n"
        
        # +1 Day
        if perf['1d']['tracked'] > 0:
            win_rate = perf['1d']['win_rate'] or 0
            avg_gain = perf['1d']['avg_gain'] or 0
            emoji = "🟢" if avg_gain > 0 else "🔴"
            msg += f"  +1G: {emoji} %{avg_gain:+.1f} (WR: %{win_rate:.0f})\n"
        
        # +3 Day
        if perf['3d']['tracked'] > 0:
            win_rate = perf['3d']['win_rate'] or 0
            avg_gain = perf['3d']['avg_gain'] or 0
            emoji = "🟢" if avg_gain > 0 else "🔴"
            msg += f"  +3G: {emoji} %{avg_gain:+.1f} (WR: %{win_rate:.0f})\n"
        
        # +7 Day
        if perf['7d']['tracked'] > 0:
            win_rate = perf['7d']['win_rate'] or 0
            avg_gain = perf['7d']['avg_gain'] or 0
            emoji = "🟢" if avg_gain > 0 else "🔴"
            msg += f"  +7G: {emoji} %{avg_gain:+.1f} (WR: %{win_rate:.0f})\n"
        
        msg += "\n"
    
    msg += "━" * 30 + "\n"
    msg += "WR = Win Rate (Kazanma Oranı)\n"
    msg += f"🕐 {datetime.now().strftime('%d.%m.%Y %H:%M')}"
    
    return msg


def send_telegram(message: str) -> bool:
    """
    Send message to Telegram.
    
    Args:
        message: Message to send
        
    Returns:
        True if sent successfully
    """
    try:
        from scripts.telegram_bot import send_telegram_message
        return send_telegram_message(message)
    except ImportError:
        print("⚠️  Telegram bot module not found")
        return False
    except Exception as e:
        print(f"⚠️  Telegram error: {e}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Track signal performance')
    parser.add_argument('--days', type=int, default=30, help='Days back to track (default: 30)')
    parser.add_argument('--telegram', action='store_true', help='Send summary to Telegram')
    parser.add_argument('--summary-only', action='store_true', help='Only show summary, do not update')
    args = parser.parse_args()
    
    print("=" * 60)
    print("📊 BIST Analyst - Performance Tracker")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    if not args.summary_only:
        # Get signals to track
        print(f"\n🔍 Finding signals from last {args.days} days...")
        signals = get_signals_to_track(args.days)
        print(f"   Found {len(signals)} signals to track")
        
        if signals:
            # Update performance for each signal
            print("\n📈 Updating performance data...")
            updated = 0
            errors = 0
            
            for signal in signals:
                try:
                    perf_data = update_signal_performance(signal)
                    
                    # Only save if we have new data
                    has_new_data = (
                        (perf_data['price_1d'] and not signal['price_1d']) or
                        (perf_data['price_3d'] and not signal['price_3d']) or
                        (perf_data['price_7d'] and not signal['price_7d'])
                    )
                    
                    if has_new_data:
                        save_performance(signal, perf_data)
                        updated += 1
                        
                        # Show progress
                        gains = []
                        if perf_data['gain_1d'] is not None:
                            gains.append(f"+1d: {perf_data['gain_1d']:+.1f}%")
                        if perf_data['gain_3d'] is not None:
                            gains.append(f"+3d: {perf_data['gain_3d']:+.1f}%")
                        if perf_data['gain_7d'] is not None:
                            gains.append(f"+7d: {perf_data['gain_7d']:+.1f}%")
                        
                        if gains:
                            print(f"   ✓ {signal['symbol']} ({signal['signal_type']}): {', '.join(gains)}")
                
                except Exception as e:
                    errors += 1
                    print(f"   ⚠️  Error updating {signal['symbol']}: {e}")
            
            print(f"\n✅ Updated {updated} signals, {errors} errors")
    
    # Show summary
    print("\n" + "=" * 60)
    print("📊 PERFORMANCE SUMMARY")
    print("=" * 60)
    
    summary = get_performance_summary()
    
    for item in summary['by_signal_type']:
        signal_type = item['signal_type']
        total = item['total_signals']
        perf = item['performance']
        
        print(f"\n{signal_type} ({total} signals)")
        print("-" * 40)
        
        for period in ['1d', '3d', '7d']:
            p = perf[period]
            if p['tracked'] > 0:
                avg = p['avg_gain'] or 0
                wr = p['win_rate'] or 0
                emoji = "🟢" if avg > 0 else "🔴"
                print(f"  +{period}: {emoji} Avg: {avg:+.2f}% | Win Rate: {wr:.1f}% ({p['wins']}/{p['tracked']})")
            else:
                print(f"  +{period}: ⏳ No data yet")
    
    # Send to Telegram if requested
    if args.telegram:
        print("\n📱 Sending to Telegram...")
        msg = format_telegram_message(summary)
        if send_telegram(msg):
            print("   ✓ Sent successfully")
        else:
            print("   ⚠️  Failed to send")
    
    print("\n" + "=" * 60)
    print("✅ Performance tracking complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()

