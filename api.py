"""
Flask REST API - BIST Analyst Backend
Provides endpoints for signals, market data, and system status
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy import create_engine, text
from config import DB_CONNECTION_STR
import pandas as pd
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

engine = create_engine(DB_CONNECTION_STR)

# =========================================================================
# HEALTH & STATUS
# =========================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """API health check"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'database': 'connected'
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """System statistics"""
    try:
        with engine.connect() as conn:
            ticker_count = conn.execute(text("SELECT COUNT(*) FROM tickers")).scalar()
            data_count = conn.execute(text("SELECT COUNT(*) FROM market_data")).scalar()
            latest_date = conn.execute(text("SELECT MAX(date) FROM market_data")).scalar()
            
        return jsonify({
            'tickers': ticker_count,
            'total_bars': data_count,
            'latest_data_date': str(latest_date) if latest_date else None,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =========================================================================
# SIGNALS
# =========================================================================

@app.route('/api/signals/latest', methods=['GET'])
def get_latest_signals():
    """Get latest scan results"""
    try:
        # Run scanner and return results
        from scanner_xtumy import run_scanner
        results_df = run_scanner()
        
        if results_df is None or len(results_df) == 0:
            return jsonify({
                'count': 0,
                'signals': [],
                'timestamp': datetime.now().isoformat()
            })
        
        # Convert to dict
        signals = results_df.to_dict('records')
        
        # Format dates
        for sig in signals:
            if 'Date' in sig:
                sig['Date'] = str(sig['Date'])
        
        return jsonify({
            'count': len(signals),
            'signals': signals,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/signals/history', methods=['GET'])
def get_signal_history():
    """
    Get historical signals (if signal_history table exists)
    Query params:
    - days: Number of days to look back (default: 7)
    - signal_type: Filter by signal type
    """
    days = request.args.get('days', 7, type=int)
    signal_type = request.args.get('signal_type', None)
    
    # TODO: Implement signal history tracking
    return jsonify({
        'message': 'Signal history tracking not yet implemented',
        'suggestion': 'Use /api/signals/latest for current signals'
    }), 501

# =========================================================================
# TICKERS
# =========================================================================

@app.route('/api/tickers', methods=['GET'])
def get_tickers():
    """Get all tickers"""
    try:
        query = "SELECT ticker, exchange, last_updated FROM tickers ORDER BY ticker"
        df = pd.read_sql(query, engine)
        
        tickers = df.to_dict('records')
        
        return jsonify({
            'count': len(tickers),
            'tickers': tickers
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =========================================================================
# MARKET DATA
# =========================================================================

@app.route('/api/market-data/<symbol>', methods=['GET'])
def get_market_data(symbol):
    """
    Get OHLCV data for a symbol
    Query params:
    - days: Number of days (default: 30)
    """
    days = request.args.get('days', 30, type=int)
    
    try:
        query = text("""
            SELECT date, open, high, low, close, volume
            FROM market_data
            WHERE symbol = :symbol
            AND date > NOW() - INTERVAL ':days days'
            ORDER BY date ASC
        """)
        
        df = pd.read_sql(query, engine, params={'symbol': symbol.upper(), 'days': days})
        
        if df.empty:
            return jsonify({
                'error': f'No data found for {symbol}'
            }), 404
        
        # Convert to records
        data = df.to_dict('records')
        
        # Format dates
        for row in data:
            row['date'] = str(row['date'])
        
        return jsonify({
            'symbol': symbol.upper(),
            'count': len(data),
            'data': data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =========================================================================
# HOLIDAYS
# =========================================================================

@app.route('/api/holidays', methods=['GET'])
def get_holidays():
    """
    Get BIST holidays
    Query params:
    - year: Filter by year (default: current year)
    """
    year = request.args.get('year', datetime.now().year, type=int)
    
    try:
        query = text("""
            SELECT holiday_date, holiday_name, status, closing_time
            FROM bist_holidays
            WHERE year = :year
            ORDER BY holiday_date
        """)
        
        df = pd.read_sql(query, engine, params={'year': year})
        
        holidays = df.to_dict('records')
        
        # Format dates and times
        for h in holidays:
            h['holiday_date'] = str(h['holiday_date'])
            if h['closing_time']:
                h['closing_time'] = str(h['closing_time'])
        
        return jsonify({
            'year': year,
            'count': len(holidays),
            'holidays': holidays
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =========================================================================
# RUN SERVER
# =========================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 BIST Analyst REST API")
    print("=" * 60)
    print("📍 Endpoints:")
    print("   GET  /api/health               - Health check")
    print("   GET  /api/stats                - System statistics")
    print("   GET  /api/signals/latest       - Latest scan results")
    print("   GET  /api/signals/history      - Signal history")
    print("   GET  /api/tickers              - All tickers")
    print("   GET  /api/market-data/<symbol> - OHLCV data")
    print("   GET  /api/holidays             - Holiday calendar")
    print("=" * 60)
    print("🌐 Starting server on http://localhost:5000")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)

