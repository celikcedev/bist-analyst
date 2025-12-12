"""
REST API routes for screener module.
"""
from flask import Blueprint, jsonify, request
from datetime import datetime, date, timedelta
from typing import Optional, List
from sqlalchemy import text, func
from pydantic import BaseModel, Field, ValidationError
import traceback

from backend.core.database import get_db_session
from backend.modules.screener.models import Strategy, StrategyParameter, SignalHistory, SignalPerformance
from backend.modules.screener.scanner import ScanEngine
from backend.modules.screener.strategies.registry import StrategyRegistry


# ============================================================================
# REQUEST/RESPONSE MODELS (Pydantic)
# ============================================================================

class ScanRequest(BaseModel):
    """Request model for POST /api/screener/scan"""
    strategy_name: str = Field(..., description="Name of registered strategy (e.g., XTUMYV27Strategy)")
    user_id: int = Field(default=1, ge=1, description="User ID")
    save_to_db: bool = Field(default=True, description="Whether to save signals to database")
    symbols: Optional[List[str]] = Field(default=None, description="Optional list of symbols to scan")
    signal_types: Optional[List[str]] = Field(default=None, description="Optional list of signal types to filter")


class UpdateParametersRequest(BaseModel):
    """Request model for PUT /api/screener/strategies/:name/parameters"""
    user_id: int = Field(default=1, ge=1, description="User ID")
    parameters: dict = Field(..., description="Strategy parameters to update")

# Create blueprint
screener_bp = Blueprint('screener', __name__, url_prefix='/api/screener')


@screener_bp.route('/strategies', methods=['GET'])
def list_strategies():
    """
    List all available strategies.
    
    GET /api/screener/strategies
    
    Returns:
        {
            "strategies": [
                {
                    "id": 1,
                    "name": "XTUMYV27Strategy",
                    "display_name": "XTUMY V27",
                    "description": "...",
                    "is_active": true
                }
            ]
        }
    """
    try:
        with get_db_session() as session:
            strategies = session.query(Strategy).filter(Strategy.is_active == True).all()
            
            result = []
            for strategy in strategies:
                result.append({
                    'id': strategy.id,
                    'name': strategy.name,
                    'display_name': strategy.display_name,
                    'description': strategy.description,
                    'python_class': strategy.python_class,
                    'is_active': strategy.is_active
                })
            
            return jsonify({'strategies': result}), 200
    
    except Exception as e:
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500


@screener_bp.route('/strategies/<strategy_name>/parameters', methods=['GET'])
def get_strategy_parameters(strategy_name: str):
    """
    Get parameters for a strategy.
    
    GET /api/screener/strategies/:name/parameters?user_id=1
    
    Query params:
        user_id: User ID (default: 1)
    
    Returns:
        {
            "strategy_id": 1,
            "strategy_name": "XTUMYV27Strategy",
            "parameters": [
                {
                    "id": 1,
                    "parameter_name": "pbWaitBars",
                    "parameter_value": 3,
                    "parameter_type": "int",
                    "display_name": "Trend Oturma Süresi (Bar)",
                    "display_group": "PULLBACK (GERİ ÇEKİLME) AYARLARI",
                    "display_order": 1
                },
                ...
            ]
        }
    """
    try:
        user_id = request.args.get('user_id', 1, type=int)
        
        with get_db_session() as session:
            # Get strategy
            strategy = session.query(Strategy).filter(Strategy.name == strategy_name).first()
            
            if not strategy:
                return jsonify({'error': f'Strategy {strategy_name} not found'}), 404
            
            strategy_id = strategy.id
            
            # Get user parameters
            params_db = session.query(StrategyParameter).filter(
                StrategyParameter.user_id == user_id,
                StrategyParameter.strategy_id == strategy_id
            ).order_by(StrategyParameter.display_order).all()
            
            if not params_db:
                # No custom parameters, return empty list (frontend will handle defaults)
                return jsonify({
                    'strategy_id': strategy_id,
                    'strategy_name': strategy.name,
                    'parameters': [],
                    'is_default': True
                }), 200
            
            # Build parameter list with metadata
            params_list = []
            for param in params_db:
                params_list.append({
                    'id': param.id,
                    'strategy_id': param.strategy_id,
                    'parameter_name': param.parameter_name,
                    'parameter_value': param.parameter_value,
                    'parameter_type': param.parameter_type,
                    'display_name': param.display_name,
                    'display_group': param.display_group,
                    'display_order': param.display_order
                })
            
            return jsonify({
                'strategy_id': strategy_id,
                'strategy_name': strategy.name,
                'parameters': params_list,
                'is_default': False
            }), 200
    
    except Exception as e:
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500


@screener_bp.route('/strategies/<strategy_name>/parameters', methods=['PUT'])
def update_strategy_parameters(strategy_name: str):
    """
    Update parameters for a strategy.
    
    PUT /api/screener/strategies/:name/parameters
    
    Body:
        {
            "user_id": 1,
            "parameters": {
                "pbWaitBars": 5,
                "pullPct": 3.0,
                ...
            }
        }
    
    Returns:
        {
            "message": "Parameters updated successfully",
            "strategy_id": 1,
            "strategy_name": "XTUMYV27Strategy",
            "updated_count": 12
        }
    """
    try:
        data = request.get_json()
        
        # Validate request with Pydantic
        try:
            update_request = UpdateParametersRequest(**data)
        except ValidationError as e:
            return jsonify({
                'error': 'Invalid request data',
                'details': e.errors()
            }), 400
        
        with get_db_session() as session:
            # Get strategy
            strategy = session.query(Strategy).filter(Strategy.name == strategy_name).first()
            
            if not strategy:
                return jsonify({
                    'error': f'Strategy "{strategy_name}" not found',
                    'available_strategies': list(StrategyRegistry._strategies.keys())
                }), 404
            
            strategy_id = strategy.id
            
            # Validate parameters using strategy's Pydantic model
            try:
                strategy_class = StrategyRegistry.get_strategy(strategy.name)
                params_class = strategy_class.get_default_parameters().__class__
                validated_params = params_class(**update_request.parameters)
            except KeyError:
                return jsonify({
                    'error': f'Strategy "{strategy_name}" not found in registry'
                }), 404
            except ValidationError as e:
                return jsonify({
                    'error': 'Invalid strategy parameters',
                    'details': e.errors()
                }), 400
            
            # Update or create parameters
            updated_count = 0
            for param_name, param_value in validated_params.model_dump().items():
                # Check if exists
                existing = session.query(StrategyParameter).filter(
                    StrategyParameter.user_id == update_request.user_id,
                    StrategyParameter.strategy_id == strategy_id,
                    StrategyParameter.parameter_name == param_name
                ).first()
                
                if existing:
                    existing.parameter_value = param_value
                else:
                    new_param = StrategyParameter(
                        user_id=update_request.user_id,
                        strategy_id=strategy_id,
                        parameter_name=param_name,
                        parameter_value=param_value,
                        is_default=False
                    )
                    session.add(new_param)
                
                updated_count += 1
            
            session.commit()
            
            return jsonify({
                'message': 'Parameters updated successfully',
                'strategy_id': strategy_id,
                'strategy_name': strategy.name,
                'user_id': update_request.user_id,
                'updated_count': updated_count
            }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'details': str(e),
            'traceback': traceback.format_exc()
        }), 500


@screener_bp.route('/scan', methods=['POST'])
def run_scan():
    """
    Run a scan with a strategy.
    
    POST /api/screener/scan
    
    Body:
        {
            "strategy_name": "XTUMYV27Strategy",
            "user_id": 1,
            "save_to_db": true,
            "symbols": ["THYAO", "ASELS"],  // optional
            "signal_types": ["PULLBACK AL", "DİP AL"]  // optional - filter by signal types
        }
    
    Returns:
        {
            "message": "Scan completed",
            "strategy": "XTUMYV27Strategy",
            "signals_found": 38,
            "signals": [...]
        }
    """
    try:
        data = request.get_json()
        
        # Validate request with Pydantic
        try:
            scan_request = ScanRequest(**data)
        except ValidationError as e:
            return jsonify({
                'error': 'Invalid request data',
                'details': e.errors()
            }), 400
        
        # Create scan engine
        try:
            scan_engine = ScanEngine(scan_request.strategy_name, scan_request.user_id)
        except KeyError:
            return jsonify({
                'error': f'Strategy "{scan_request.strategy_name}" not found',
                'available_strategies': list(StrategyRegistry._strategies.keys())
            }), 404
        
        # Run scan with signal type filter
        signals = scan_engine.run_scan(
            save_to_db=scan_request.save_to_db, 
            symbols=scan_request.symbols,
            signal_types=scan_request.signal_types
        )
        
        return jsonify({
            'message': 'Scan completed',
            'strategy': scan_request.strategy_name,
            'user_id': scan_request.user_id,
            'signals_found': len(signals),
            'signals': signals
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'details': str(e),
            'traceback': traceback.format_exc()
        }), 500


@screener_bp.route('/signals', methods=['GET'])
def get_signals():
    """
    Get signals with filtering and pagination.
    
    GET /api/screener/signals?user_id=1&strategy_id=1&signal_type=KURUMSAL+DİP&date_from=2025-12-01&limit=50&offset=0
    
    Query params:
        user_id: User ID (default: 1)
        strategy_id: Filter by strategy ID
        signal_type: Filter by signal type
        date_from: Filter signals from date (YYYY-MM-DD)
        date_to: Filter signals to date (YYYY-MM-DD)
        rsi_min: Minimum RSI
        rsi_max: Maximum RSI
        adx_min: Minimum ADX
        adx_max: Maximum ADX
        limit: Number of results (default: 50)
        offset: Pagination offset (default: 0)
    
    Returns:
        {
            "signals": [...],
            "total": 150,
            "limit": 50,
            "offset": 0
        }
    """
    try:
        # Parse query params
        user_id = request.args.get('user_id', 1, type=int)
        strategy_id = request.args.get('strategy_id', type=int)
        signal_type = request.args.get('signal_type', type=str)
        date_from = request.args.get('date_from', type=str)
        date_to = request.args.get('date_to', type=str)
        rsi_min = request.args.get('rsi_min', type=float)
        rsi_max = request.args.get('rsi_max', type=float)
        adx_min = request.args.get('adx_min', type=float)
        adx_max = request.args.get('adx_max', type=float)
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        with get_db_session() as session:
            # Build query
            query = session.query(SignalHistory).filter(SignalHistory.user_id == user_id)
            
            if strategy_id:
                query = query.filter(SignalHistory.strategy_id == strategy_id)
            
            if signal_type:
                query = query.filter(SignalHistory.signal_type == signal_type)
            
            if date_from:
                query = query.filter(SignalHistory.signal_date >= date_from)
            
            if date_to:
                query = query.filter(SignalHistory.signal_date <= date_to)
            
            if rsi_min is not None:
                query = query.filter(SignalHistory.rsi >= rsi_min)
            
            if rsi_max is not None:
                query = query.filter(SignalHistory.rsi <= rsi_max)
            
            if adx_min is not None:
                query = query.filter(SignalHistory.adx >= adx_min)
            
            if adx_max is not None:
                query = query.filter(SignalHistory.adx <= adx_max)
            
            # Get total count
            total = query.count()
            
            # Apply pagination and order
            signals = query.order_by(SignalHistory.signal_date.desc(), SignalHistory.created_at.desc()) \
                          .limit(limit).offset(offset).all()
            
            # Format results
            result = []
            for signal in signals:
                result.append({
                    'id': signal.id,
                    'symbol': signal.symbol,
                    'signal_type': signal.signal_type,
                    'signal_date': str(signal.signal_date),
                    'price': float(signal.price_at_signal) if signal.price_at_signal else None,
                    'rsi': float(signal.rsi) if signal.rsi else None,
                    'adx': float(signal.adx) if signal.adx else None,
                    'metadata': signal.signal_metadata,
                    'created_at': signal.created_at.isoformat() if signal.created_at else None
                })
            
            return jsonify({
                'signals': result,
                'total': total,
                'limit': limit,
                'offset': offset
            }), 200
    
    except Exception as e:
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500


@screener_bp.route('/signals/<int:signal_id>', methods=['GET'])
def get_signal(signal_id: int):
    """
    Get a single signal by ID.
    
    GET /api/screener/signals/:id
    
    Returns:
        {
            "id": 1,
            "symbol": "THYAO",
            "signal_type": "KURUMSAL DİP",
            ...
        }
    """
    try:
        with get_db_session() as session:
            signal = session.query(SignalHistory).filter(SignalHistory.id == signal_id).first()
            
            if not signal:
                return jsonify({'error': 'Signal not found'}), 404
            
            result = {
                'id': signal.id,
                'user_id': signal.user_id,
                'strategy_id': signal.strategy_id,
                'symbol': signal.symbol,
                'signal_type': signal.signal_type,
                'signal_date': str(signal.signal_date),
                'price': float(signal.price_at_signal) if signal.price_at_signal else None,
                'rsi': float(signal.rsi) if signal.rsi else None,
                'adx': float(signal.adx) if signal.adx else None,
                'metadata': signal.signal_metadata,
                'created_at': signal.created_at.isoformat() if signal.created_at else None
            }
            
            return jsonify(result), 200
    
    except Exception as e:
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500


# ============================================================================
# PERFORMANCE TRACKING ENDPOINTS
# ============================================================================

@screener_bp.route('/performance/summary', methods=['GET'])
def get_performance_summary():
    """
    Get performance summary for all signal types.
    
    GET /api/screener/performance/summary?days=30&user_id=1
    
    Query params:
        days: Number of days to look back (default: 30)
        user_id: User ID (default: 1)
    
    Returns:
        {
            "period_days": 30,
            "generated_at": "2025-12-12T10:00:00",
            "summary": {
                "total_signals": 150,
                "tracked_signals": 120,
                "overall_win_rate_7d": 65.5,
                "overall_avg_gain_7d": 2.35
            },
            "by_signal_type": [...]
        }
    """
    try:
        days = request.args.get('days', 30, type=int)
        user_id = request.args.get('user_id', 1, type=int)
        cutoff_date = date.today() - timedelta(days=days)
        
        with get_db_session() as session:
            # Query performance by signal type
            query = text("""
                SELECT 
                    sh.signal_type,
                    COUNT(DISTINCT sh.id) as total_signals,
                    COUNT(sp.gain_1d) as tracked_1d,
                    COUNT(sp.gain_3d) as tracked_3d,
                    COUNT(sp.gain_7d) as tracked_7d,
                    AVG(sp.gain_1d) as avg_gain_1d,
                    AVG(sp.gain_3d) as avg_gain_3d,
                    AVG(sp.gain_7d) as avg_gain_7d,
                    SUM(CASE WHEN sp.gain_1d > 0 THEN 1 ELSE 0 END) as wins_1d,
                    SUM(CASE WHEN sp.gain_3d > 0 THEN 1 ELSE 0 END) as wins_3d,
                    SUM(CASE WHEN sp.gain_7d > 0 THEN 1 ELSE 0 END) as wins_7d,
                    MAX(sp.gain_1d) as best_1d,
                    MAX(sp.gain_3d) as best_3d,
                    MAX(sp.gain_7d) as best_7d,
                    MIN(sp.gain_1d) as worst_1d,
                    MIN(sp.gain_3d) as worst_3d,
                    MIN(sp.gain_7d) as worst_7d
                FROM signal_history sh
                LEFT JOIN signal_performance sp ON sh.id = sp.signal_id
                WHERE sh.signal_date >= :cutoff_date
                  AND sh.user_id = :user_id
                GROUP BY sh.signal_type
                ORDER BY sh.signal_type
            """)
            
            result = session.execute(query, {
                'cutoff_date': cutoff_date,
                'user_id': user_id
            })
            
            by_signal_type = []
            total_signals = 0
            total_tracked_7d = 0
            total_wins_7d = 0
            sum_gain_7d = 0
            
            for row in result:
                tracked_1d = row.tracked_1d or 0
                tracked_3d = row.tracked_3d or 0
                tracked_7d = row.tracked_7d or 0
                wins_1d = row.wins_1d or 0
                wins_3d = row.wins_3d or 0
                wins_7d = row.wins_7d or 0
                
                total_signals += row.total_signals
                total_tracked_7d += tracked_7d
                total_wins_7d += wins_7d
                if row.avg_gain_7d:
                    sum_gain_7d += float(row.avg_gain_7d) * tracked_7d
                
                by_signal_type.append({
                    'signal_type': row.signal_type,
                    'total_signals': row.total_signals,
                    'performance': {
                        '1d': {
                            'tracked': tracked_1d,
                            'avg_gain': round(float(row.avg_gain_1d), 2) if row.avg_gain_1d else None,
                            'win_rate': round((wins_1d / tracked_1d) * 100, 1) if tracked_1d > 0 else None,
                            'wins': wins_1d,
                            'best': round(float(row.best_1d), 2) if row.best_1d else None,
                            'worst': round(float(row.worst_1d), 2) if row.worst_1d else None
                        },
                        '3d': {
                            'tracked': tracked_3d,
                            'avg_gain': round(float(row.avg_gain_3d), 2) if row.avg_gain_3d else None,
                            'win_rate': round((wins_3d / tracked_3d) * 100, 1) if tracked_3d > 0 else None,
                            'wins': wins_3d,
                            'best': round(float(row.best_3d), 2) if row.best_3d else None,
                            'worst': round(float(row.worst_3d), 2) if row.worst_3d else None
                        },
                        '7d': {
                            'tracked': tracked_7d,
                            'avg_gain': round(float(row.avg_gain_7d), 2) if row.avg_gain_7d else None,
                            'win_rate': round((wins_7d / tracked_7d) * 100, 1) if tracked_7d > 0 else None,
                            'wins': wins_7d,
                            'best': round(float(row.best_7d), 2) if row.best_7d else None,
                            'worst': round(float(row.worst_7d), 2) if row.worst_7d else None
                        }
                    }
                })
            
            # Calculate overall stats
            overall_win_rate = round((total_wins_7d / total_tracked_7d) * 100, 1) if total_tracked_7d > 0 else None
            overall_avg_gain = round(sum_gain_7d / total_tracked_7d, 2) if total_tracked_7d > 0 else None
            
            return jsonify({
                'period_days': days,
                'generated_at': datetime.now().isoformat(),
                'summary': {
                    'total_signals': total_signals,
                    'tracked_signals': total_tracked_7d,
                    'overall_win_rate_7d': overall_win_rate,
                    'overall_avg_gain_7d': overall_avg_gain
                },
                'by_signal_type': by_signal_type
            }), 200
    
    except Exception as e:
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500


@screener_bp.route('/performance/top-performers', methods=['GET'])
def get_top_performers():
    """
    Get top and worst performing signals.
    
    GET /api/screener/performance/top-performers?days=30&limit=10&period=7d
    
    Query params:
        days: Number of days to look back (default: 30)
        limit: Number of results (default: 10)
        period: Performance period - 1d, 3d, or 7d (default: 7d)
        user_id: User ID (default: 1)
    
    Returns:
        {
            "period": "7d",
            "top_gainers": [...],
            "top_losers": [...]
        }
    """
    try:
        days = request.args.get('days', 30, type=int)
        limit = request.args.get('limit', 10, type=int)
        period = request.args.get('period', '7d', type=str)
        user_id = request.args.get('user_id', 1, type=int)
        cutoff_date = date.today() - timedelta(days=days)
        
        # Validate period
        if period not in ['1d', '3d', '7d']:
            return jsonify({'error': 'Invalid period. Use 1d, 3d, or 7d'}), 400
        
        gain_column = f'gain_{period}'
        price_column = f'price_{period}'
        
        with get_db_session() as session:
            # Top gainers
            gainers_query = text(f"""
                SELECT 
                    sh.id,
                    sh.symbol,
                    sh.signal_type,
                    sh.signal_date,
                    sh.price_at_signal,
                    sp.{price_column} as price_later,
                    sp.{gain_column} as gain
                FROM signal_history sh
                JOIN signal_performance sp ON sh.id = sp.signal_id
                WHERE sh.signal_date >= :cutoff_date
                  AND sh.user_id = :user_id
                  AND sp.{gain_column} IS NOT NULL
                ORDER BY sp.{gain_column} DESC
                LIMIT :limit
            """)
            
            gainers = session.execute(gainers_query, {
                'cutoff_date': cutoff_date,
                'user_id': user_id,
                'limit': limit
            })
            
            top_gainers = []
            for row in gainers:
                top_gainers.append({
                    'id': row.id,
                    'symbol': row.symbol,
                    'signal_type': row.signal_type,
                    'signal_date': str(row.signal_date),
                    'price_at_signal': float(row.price_at_signal) if row.price_at_signal else None,
                    'price_later': float(row.price_later) if row.price_later else None,
                    'gain': float(row.gain) if row.gain else None
                })
            
            # Top losers
            losers_query = text(f"""
                SELECT 
                    sh.id,
                    sh.symbol,
                    sh.signal_type,
                    sh.signal_date,
                    sh.price_at_signal,
                    sp.{price_column} as price_later,
                    sp.{gain_column} as gain
                FROM signal_history sh
                JOIN signal_performance sp ON sh.id = sp.signal_id
                WHERE sh.signal_date >= :cutoff_date
                  AND sh.user_id = :user_id
                  AND sp.{gain_column} IS NOT NULL
                ORDER BY sp.{gain_column} ASC
                LIMIT :limit
            """)
            
            losers = session.execute(losers_query, {
                'cutoff_date': cutoff_date,
                'user_id': user_id,
                'limit': limit
            })
            
            top_losers = []
            for row in losers:
                top_losers.append({
                    'id': row.id,
                    'symbol': row.symbol,
                    'signal_type': row.signal_type,
                    'signal_date': str(row.signal_date),
                    'price_at_signal': float(row.price_at_signal) if row.price_at_signal else None,
                    'price_later': float(row.price_later) if row.price_later else None,
                    'gain': float(row.gain) if row.gain else None
                })
            
            return jsonify({
                'period': period,
                'days_back': days,
                'top_gainers': top_gainers,
                'top_losers': top_losers
            }), 200
    
    except Exception as e:
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500


@screener_bp.route('/signals/<int:signal_id>/performance', methods=['GET'])
def get_signal_performance(signal_id: int):
    """
    Get performance data for a specific signal.
    
    GET /api/screener/signals/:id/performance
    
    Returns:
        {
            "signal": {...},
            "performance": {...}
        }
    """
    try:
        with get_db_session() as session:
            # Get signal
            signal = session.query(SignalHistory).filter(
                SignalHistory.id == signal_id
            ).first()
            
            if not signal:
                return jsonify({'error': 'Signal not found'}), 404
            
            # Get performance
            performance = session.query(SignalPerformance).filter(
                SignalPerformance.signal_id == signal_id
            ).first()
            
            signal_data = {
                'id': signal.id,
                'symbol': signal.symbol,
                'signal_type': signal.signal_type,
                'signal_date': str(signal.signal_date),
                'price_at_signal': float(signal.price_at_signal) if signal.price_at_signal else None,
                'rsi': float(signal.rsi) if signal.rsi else None,
                'adx': float(signal.adx) if signal.adx else None
            }
            
            if performance:
                perf_data = {
                    'price_1d': float(performance.price_1d) if performance.price_1d else None,
                    'price_3d': float(performance.price_3d) if performance.price_3d else None,
                    'price_7d': float(performance.price_7d) if performance.price_7d else None,
                    'gain_1d': float(performance.gain_1d) if performance.gain_1d else None,
                    'gain_3d': float(performance.gain_3d) if performance.gain_3d else None,
                    'gain_7d': float(performance.gain_7d) if performance.gain_7d else None,
                    'updated_at': performance.updated_at.isoformat() if performance.updated_at else None
                }
            else:
                perf_data = None
            
            return jsonify({
                'signal': signal_data,
                'performance': perf_data
            }), 200
    
    except Exception as e:
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500


@screener_bp.route('/performance/by-symbol', methods=['GET'])
def get_performance_by_symbol():
    """
    Get performance statistics grouped by symbol.
    
    GET /api/screener/performance/by-symbol?days=30&min_signals=2
    
    Query params:
        days: Number of days to look back (default: 30)
        min_signals: Minimum signals to include (default: 1)
        user_id: User ID (default: 1)
        limit: Max results (default: 50)
    
    Returns:
        {
            "symbols": [...]
        }
    """
    try:
        days = request.args.get('days', 30, type=int)
        min_signals = request.args.get('min_signals', 1, type=int)
        user_id = request.args.get('user_id', 1, type=int)
        limit = request.args.get('limit', 50, type=int)
        cutoff_date = date.today() - timedelta(days=days)
        
        with get_db_session() as session:
            query = text("""
                SELECT 
                    sh.symbol,
                    COUNT(DISTINCT sh.id) as total_signals,
                    ARRAY_AGG(DISTINCT sh.signal_type) as signal_types,
                    AVG(sp.gain_7d) as avg_gain_7d,
                    SUM(CASE WHEN sp.gain_7d > 0 THEN 1 ELSE 0 END) as wins_7d,
                    COUNT(sp.gain_7d) as tracked_7d,
                    MAX(sp.gain_7d) as best_gain,
                    MIN(sp.gain_7d) as worst_gain
                FROM signal_history sh
                LEFT JOIN signal_performance sp ON sh.id = sp.signal_id
                WHERE sh.signal_date >= :cutoff_date
                  AND sh.user_id = :user_id
                GROUP BY sh.symbol
                HAVING COUNT(DISTINCT sh.id) >= :min_signals
                ORDER BY AVG(sp.gain_7d) DESC NULLS LAST
                LIMIT :limit
            """)
            
            result = session.execute(query, {
                'cutoff_date': cutoff_date,
                'user_id': user_id,
                'min_signals': min_signals,
                'limit': limit
            })
            
            symbols = []
            for row in result:
                tracked = row.tracked_7d or 0
                wins = row.wins_7d or 0
                
                symbols.append({
                    'symbol': row.symbol,
                    'total_signals': row.total_signals,
                    'signal_types': list(row.signal_types) if row.signal_types else [],
                    'avg_gain_7d': round(float(row.avg_gain_7d), 2) if row.avg_gain_7d else None,
                    'win_rate_7d': round((wins / tracked) * 100, 1) if tracked > 0 else None,
                    'tracked_7d': tracked,
                    'best_gain': round(float(row.best_gain), 2) if row.best_gain else None,
                    'worst_gain': round(float(row.worst_gain), 2) if row.worst_gain else None
                })
            
            return jsonify({
                'period_days': days,
                'symbols': symbols
            }), 200
    
    except Exception as e:
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500
