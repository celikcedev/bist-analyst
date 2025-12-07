"""
REST API routes for market data module.
"""
from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
import traceback

from backend.core.database import get_db_session, engine
from backend.modules.market_data.models import Ticker, MarketData
import pandas as pd

# Create blueprint
market_data_bp = Blueprint('market_data', __name__, url_prefix='/api/market-data')


@market_data_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    Get general statistics.
    
    GET /api/market-data/stats
    
    Returns:
        {
            "tickers_count": 593,
            "latest_data_date": "2025-12-07",
            "data_points": 150000,
            "active_tickers": 590
        }
    """
    try:
        with get_db_session() as session:
            # Count tickers
            tickers_count = session.query(Ticker).count()
            active_tickers = session.query(Ticker).filter(Ticker.is_active == True).count()
            
            # Get latest data date
            query = "SELECT MAX(date) as latest_date, COUNT(*) as data_points FROM market_data"
            result = pd.read_sql(query, engine)
            
            latest_date = result.iloc[0]['latest_date']
            data_points = int(result.iloc[0]['data_points'])
            
            return jsonify({
                'tickers_count': tickers_count,
                'active_tickers': active_tickers,
                'latest_data_date': str(latest_date)[:10] if latest_date else None,
                'data_points': data_points
            }), 200
    
    except Exception as e:
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500


@market_data_bp.route('/tickers', methods=['GET'])
def get_tickers():
    """
    Get list of tickers.
    
    GET /api/market-data/tickers?active_only=true&limit=100&offset=0
    
    Query params:
        active_only: Filter by active tickers (default: true)
        limit: Number of results (default: 100)
        offset: Pagination offset (default: 0)
    
    Returns:
        {
            "tickers": [...],
            "total": 593,
            "limit": 100,
            "offset": 0
        }
    """
    try:
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        with get_db_session() as session:
            query = session.query(Ticker)
            
            if active_only:
                query = query.filter(Ticker.is_active == True)
            
            total = query.count()
            tickers = query.order_by(Ticker.symbol).limit(limit).offset(offset).all()
            
            result = []
            for ticker in tickers:
                result.append({
                    'symbol': ticker.symbol,
                    'name': ticker.name,
                    'type': ticker.type,
                    'is_active': ticker.is_active
                })
            
            return jsonify({
                'tickers': result,
                'total': total,
                'limit': limit,
                'offset': offset
            }), 200
    
    except Exception as e:
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500


@market_data_bp.route('/tickers/<symbol>/data', methods=['GET'])
def get_ticker_data(symbol: str):
    """
    Get OHLCV data for a ticker.
    
    GET /api/market-data/tickers/:symbol/data?days=30
    
    Query params:
        days: Number of days to fetch (default: 30, max: 365)
    
    Returns:
        {
            "symbol": "THYAO",
            "data": [
                {
                    "date": "2025-12-07",
                    "open": 188.0,
                    "high": 192.5,
                    "low": 187.0,
                    "close": 191.2,
                    "volume": 1500000
                },
                ...
            ],
            "count": 30
        }
    """
    try:
        days = min(request.args.get('days', 30, type=int), 365)
        
        # Calculate date range
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Query data
        query = f"""
            SELECT date, open, high, low, close, volume
            FROM market_data
            WHERE symbol = '{symbol}'
              AND date >= '{start_date}'
              AND date <= '{end_date}'
            ORDER BY date ASC
        """
        
        df = pd.read_sql(query, engine)
        
        if df.empty:
            return jsonify({'error': f'No data found for symbol {symbol}'}), 404
        
        # Format data
        data = []
        for _, row in df.iterrows():
            data.append({
                'date': str(row['date'])[:10],
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close']),
                'volume': int(row['volume'])
            })
        
        return jsonify({
            'symbol': symbol,
            'data': data,
            'count': len(data)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500
