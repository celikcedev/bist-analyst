# Strategies package initialization
from backend.modules.screener.strategies.base import BaseStrategy, StrategyParameters, SignalResult
from backend.modules.screener.strategies.registry import StrategyRegistry

# Import all strategies to trigger @register decorators
from backend.modules.screener.strategies import xtumy_v27

__all__ = ['BaseStrategy', 'StrategyParameters', 'SignalResult', 'StrategyRegistry']
