"""
REST API routes for screener module.
"""
from flask import Blueprint, jsonify, request
from datetime import datetime, date
from typing import Optional
import traceback

from backend.core.database import get_db_session
from backend.modules.screener.models import Strategy, StrategyParameter, SignalHistory
from backend.modules.screener.scanner import ScanEngine
from backend.modules.screener.strategies.registry import StrategyRegistry

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
            "updated_count": 12
        }
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id', 1)
        parameters = data.get('parameters', {})
        
        if not parameters:
            return jsonify({'error': 'No parameters provided'}), 400
        
        with get_db_session() as session:
            # Get strategy
            strategy = session.query(Strategy).filter(Strategy.name == strategy_name).first()
            
            if not strategy:
                return jsonify({'error': f'Strategy {strategy_name} not found'}), 404
            
            strategy_id = strategy.id
            
            # Validate parameters using Pydantic
            strategy_class = StrategyRegistry.get_strategy(strategy.name)
            params_class = strategy_class.get_default_parameters().__class__
            
            try:
                validated_params = params_class(**parameters)
            except Exception as e:
                return jsonify({'error': f'Invalid parameters: {str(e)}'}), 400
            
            # Update or create parameters
            updated_count = 0
            for param_name, param_value in validated_params.model_dump().items():
                # Check if exists
                existing = session.query(StrategyParameter).filter(
                    StrategyParameter.user_id == user_id,
                    StrategyParameter.strategy_id == strategy_id,
                    StrategyParameter.parameter_name == param_name
                ).first()
                
                if existing:
                    existing.parameter_value = param_value
                else:
                    new_param = StrategyParameter(
                        user_id=user_id,
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
                'updated_count': updated_count
            }), 200
    
    except Exception as e:
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500


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
            "signal_types": ["PULLBACK_AL", "DIP_AL"]  // optional - filter by signal types
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
        strategy_name = data.get('strategy_name')
        user_id = data.get('user_id', 1)
        save_to_db = data.get('save_to_db', True)
        symbols = data.get('symbols')  # Optional
        signal_types = data.get('signal_types')  # Optional - NEW!
        
        if not strategy_name:
            return jsonify({'error': 'strategy_name is required'}), 400
        
        # Create scan engine
        scan_engine = ScanEngine(strategy_name, user_id)
        
        # Run scan with signal type filter
        signals = scan_engine.run_scan(
            save_to_db=save_to_db, 
            symbols=symbols,
            signal_types=signal_types
        )
        
        return jsonify({
            'message': 'Scan completed',
            'strategy': strategy_name,
            'signals_found': len(signals),
            'signals': signals
        }), 200
    
    except KeyError as e:
        return jsonify({'error': f'Strategy not found: {str(e)}'}), 404
    except Exception as e:
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500


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
