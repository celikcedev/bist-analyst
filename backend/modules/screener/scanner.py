"""
Scan engine for executing strategy scans on market data.
"""
import pandas as pd
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from sqlalchemy.orm import Session

from backend.core.database import get_db_session, engine
from backend.modules.screener.strategies.registry import StrategyRegistry
from backend.modules.screener.strategies.base import SignalResult
from backend.modules.screener.models import Strategy, StrategyParameter, SignalHistory


class ScanEngine:
    """
    Engine for executing trading strategy scans.
    
    Handles:
    - Loading strategy from registry
    - Loading parameters from database
    - Fetching market data
    - Executing scan
    - Saving results to database
    """
    
    def __init__(self, strategy_name: str, user_id: int = 1):
        """
        Initialize scan engine.
        
        Args:
            strategy_name: Name of registered strategy
            user_id: User ID for multi-user support
        """
        self.strategy_name = strategy_name
        self.user_id = user_id
        self.strategy_class = StrategyRegistry.get_strategy(strategy_name)
        
    def run_scan(
        self, 
        save_to_db: bool = True, 
        symbols: Optional[List[str]] = None,
        signal_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Run scan on market data.
        
        Args:
            save_to_db: Whether to save results to database
            symbols: Optional list of symbols to scan (None = scan all)
            signal_types: Optional list of signal types to filter (None = all types)
            
        Returns:
            List of signal dictionaries
        """
        # Load parameters
        params = self._load_parameters()
        
        # Create strategy instance
        strategy = self.strategy_class(params)
        
        # Load market data
        df_all = self._load_market_data(symbols)
        
        if df_all.empty:
            print("❌ No market data found")
            return []
        
        # Run scan on each symbol
        all_signals = []
        for symbol, group_df in df_all.groupby('symbol'):
            try:
                signals = strategy.calculate_signals(group_df)
                all_signals.extend(signals)
            except Exception as e:
                print(f"⚠️  Error scanning {symbol}: {e}")
                continue
        
        # Filter by signal types if specified
        if signal_types:
            all_signals = [s for s in all_signals if s.signal_type in signal_types]
            print(f"🔍 Filtered to {len(all_signals)} signals matching types: {signal_types}")
        
        # Save to database if requested
        if save_to_db and all_signals:
            self._save_signals(all_signals)
        
        # Convert to dict format
        return [signal.model_dump() for signal in all_signals]
    
    def _load_parameters(self):
        """Load strategy parameters from database or use defaults."""
        with get_db_session() as session:
            # Get strategy ID
            strategy_db = session.query(Strategy).filter(
                Strategy.name == self.strategy_name
            ).first()
            
            if not strategy_db:
                # Strategy not in DB yet, use defaults
                params = self.strategy_class.get_default_parameters()
                return params
            
            # Load user-specific parameters
            params_db = session.query(StrategyParameter).filter(
                StrategyParameter.user_id == self.user_id,
                StrategyParameter.strategy_id == strategy_db.id
            ).all()
            
            if not params_db:
                # No custom parameters, use defaults
                return self.strategy_class.get_default_parameters()
            
            # Build parameter dict from database
            param_dict = {}
            for param in params_db:
                param_dict[param.parameter_name] = param.parameter_value
            
            # Create and validate parameters
            params_class = self.strategy_class.get_default_parameters().__class__
            params = params_class(**param_dict)
            return params
    
    def _load_market_data(self, symbols: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Load market data from database.
        
        Args:
            symbols: Optional list of symbols to load
            
        Returns:
            DataFrame with OHLCV data
        """
        # Build query
        query = """
            SELECT symbol, date, open, high, low, close, volume
            FROM market_data
            WHERE date > NOW() - INTERVAL '250 days'
        """
        
        if symbols:
            symbols_str = "', '".join(symbols)
            query += f" AND symbol IN ('{symbols_str}')"
        
        query += " ORDER BY symbol, date ASC"
        
        # Execute query
        df = pd.read_sql(query, engine)
        return df
    
    def _save_signals(self, signals: List[SignalResult]) -> None:
        """
        Save signals to database.
        
        Args:
            signals: List of SignalResult objects
        """
        with get_db_session() as session:
            # Get strategy ID
            strategy_db = session.query(Strategy).filter(
                Strategy.name == self.strategy_name
            ).first()
            
            if not strategy_db:
                print(f"⚠️  Strategy '{self.strategy_name}' not found in database")
                return
            
            saved_count = 0
            for signal in signals:
                # Check if signal already exists
                existing = session.query(SignalHistory).filter(
                    SignalHistory.user_id == self.user_id,
                    SignalHistory.strategy_id == strategy_db.id,
                    SignalHistory.symbol == signal.symbol,
                    SignalHistory.signal_date == signal.signal_date,
                    SignalHistory.signal_type == signal.signal_type
                ).first()
                
                if existing:
                    continue  # Skip duplicates
                
                # Create new signal
                signal_db = SignalHistory(
                    user_id=self.user_id,
                    strategy_id=strategy_db.id,
                    symbol=signal.symbol,
                    signal_type=signal.signal_type,
                    signal_date=signal.signal_date,
                    price_at_signal=signal.price,
                    rsi=signal.rsi,
                    adx=signal.adx,
                    signal_metadata=signal.metadata
                )
                session.add(signal_db)
                saved_count += 1
            
            session.commit()
            print(f"✓ Saved {saved_count} new signals to database")
    
    @staticmethod
    def ensure_strategy_in_db(strategy_name: str) -> None:
        """
        Ensure strategy metadata is in database.
        
        Args:
            strategy_name: Name of strategy to register
        """
        strategy_class = StrategyRegistry.get_strategy(strategy_name)
        
        with get_db_session() as session:
            existing = session.query(Strategy).filter(
                Strategy.name == strategy_name
            ).first()
            
            if existing:
                return  # Already registered
            
            # Create strategy entry
            strategy_db = Strategy(
                name=strategy_name,
                display_name=strategy_class.get_display_name(),
                description=strategy_class.get_description(),
                python_class=f"{strategy_class.__module__}.{strategy_class.__name__}",
                is_active=True
            )
            session.add(strategy_db)
            session.commit()
            print(f"✓ Registered strategy '{strategy_name}' in database")
