"""
Base classes for trading strategies using Pydantic for parameter validation.
"""
from pydantic import BaseModel, Field, ConfigDict
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import date
import pandas as pd


class StrategyParameters(BaseModel):
    """
    Base class for all strategy parameters.
    All strategy-specific parameters should inherit from this class.
    """
    model_config = ConfigDict(
        extra='forbid',  # Reject any extra fields not defined in schema
        json_schema_extra={"example": {}}
    )


class SignalResult(BaseModel):
    """
    Standardized signal output from strategies.
    """
    symbol: str = Field(..., description="Stock ticker symbol")
    signal_type: str = Field(..., description="Type of buy signal")
    signal_date: str = Field(..., description="Date of signal (YYYY-MM-DD)")
    price: float = Field(..., gt=0, description="Price at signal")
    rsi: Optional[float] = Field(None, ge=0, le=100, description="RSI value")
    adx: Optional[float] = Field(None, ge=0, le=100, description="ADX value")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional signal data")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "symbol": "THYAO",
                "signal_type": "KURUMSAL DİP",
                "signal_date": "2025-12-07",
                "price": 188.50,
                "rsi": 48.5,
                "adx": 22.3,
                "metadata": {"trend": "Ayı Yapısında Sessiz Toplama"}
            }
        }
    )


class BaseStrategy(ABC):
    """
    Abstract base class for all trading strategies.
    
    All strategies must:
    1. Define a StrategyParameters subclass
    2. Implement calculate_signals() method
    3. Implement get_default_parameters() class method
    """
    
    def __init__(self, params: StrategyParameters):
        """
        Initialize strategy with parameters.
        
        Args:
            params: Validated strategy parameters
        """
        # Create immutable copy of parameters
        self.params = params.model_copy(deep=True)
    
    @abstractmethod
    def calculate_signals(self, df: pd.DataFrame) -> List[SignalResult]:
        """
        Calculate buy signals for given OHLCV data.
        
        Args:
            df: DataFrame with columns [symbol, date, open, high, low, close, volume]
                Data should be sorted by date ascending.
        
        Returns:
            List of SignalResult objects for detected buy signals.
            
        Raises:
            ValueError: If DataFrame is missing required columns or has insufficient data.
        """
        pass
    
    @classmethod
    @abstractmethod
    def get_default_parameters(cls) -> StrategyParameters:
        """
        Return default parameters for this strategy.
        
        Returns:
            StrategyParameters instance with default values.
        """
        pass
    
    @classmethod
    def get_name(cls) -> str:
        """
        Get strategy name (can be overridden).
        
        Returns:
            Strategy name (defaults to class name).
        """
        return cls.__name__
    
    @classmethod
    def get_display_name(cls) -> str:
        """
        Get human-readable strategy name (can be overridden).
        
        Returns:
            Display name for UI.
        """
        return cls.get_name()
    
    @classmethod
    def get_description(cls) -> str:
        """
        Get strategy description (can be overridden).
        
        Returns:
            Strategy description.
        """
        return cls.__doc__ or "No description available."
    
    def validate_dataframe(self, df: pd.DataFrame, min_rows: int = 60) -> None:
        """
        Validate that DataFrame has required columns and sufficient data.
        
        Args:
            df: DataFrame to validate
            min_rows: Minimum number of rows required
            
        Raises:
            ValueError: If validation fails
        """
        required_columns = ['symbol', 'date', 'open', 'high', 'low', 'close', 'volume']
        missing_columns = set(required_columns) - set(df.columns)
        
        if missing_columns:
            raise ValueError(f"DataFrame missing required columns: {missing_columns}")
        
        if len(df) < min_rows:
            raise ValueError(f"Insufficient data: {len(df)} rows (minimum {min_rows} required)")
        
        # Check for NaN values in critical columns
        critical_cols = ['close', 'high', 'low', 'volume']
        nan_cols = [col for col in critical_cols if df[col].isna().any()]
        if nan_cols:
            raise ValueError(f"DataFrame contains NaN values in columns: {nan_cols}")
