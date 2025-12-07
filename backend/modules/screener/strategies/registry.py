"""
Strategy registry for dynamic strategy discovery and loading.
"""
from typing import Dict, Type, Optional
from backend.modules.screener.strategies.base import BaseStrategy


class StrategyRegistry:
    """
    Registry for managing trading strategies.
    
    Strategies can be registered using the @register decorator or manually.
    """
    
    _strategies: Dict[str, Type[BaseStrategy]] = {}
    
    @classmethod
    def register(cls, strategy_class: Type[BaseStrategy], name: Optional[str] = None) -> Type[BaseStrategy]:
        """
        Register a strategy class.
        
        Can be used as a decorator:
            @StrategyRegistry.register
            class MyStrategy(BaseStrategy):
                pass
        
        Or called directly:
            StrategyRegistry.register(MyStrategy)
        
        Args:
            strategy_class: Strategy class to register
            name: Optional custom name (defaults to strategy_class.get_name())
            
        Returns:
            The strategy class (for decorator usage)
        """
        strategy_name = name or strategy_class.get_name()
        
        if strategy_name in cls._strategies:
            raise ValueError(f"Strategy '{strategy_name}' is already registered")
        
        if not issubclass(strategy_class, BaseStrategy):
            raise TypeError(f"{strategy_class.__name__} must inherit from BaseStrategy")
        
        cls._strategies[strategy_name] = strategy_class
        return strategy_class
    
    @classmethod
    def get_strategy(cls, name: str) -> Type[BaseStrategy]:
        """
        Get a registered strategy by name.
        
        Args:
            name: Strategy name
            
        Returns:
            Strategy class
            
        Raises:
            KeyError: If strategy not found
        """
        if name not in cls._strategies:
            raise KeyError(f"Strategy '{name}' not found. Available strategies: {list(cls._strategies.keys())}")
        
        return cls._strategies[name]
    
    @classmethod
    def list_strategies(cls) -> Dict[str, Dict[str, str]]:
        """
        List all registered strategies with metadata.
        
        Returns:
            Dictionary mapping strategy names to metadata:
            {
                "XTUMYV27Strategy": {
                    "display_name": "XTUMY V27",
                    "description": "Strategy description...",
                    "python_class": "xtumy_v27.XTUMYV27Strategy"
                }
            }
        """
        return {
            name: {
                "display_name": strategy.get_display_name(),
                "description": strategy.get_description(),
                "python_class": f"{strategy.__module__}.{strategy.__name__}"
            }
            for name, strategy in cls._strategies.items()
        }
    
    @classmethod
    def is_registered(cls, name: str) -> bool:
        """
        Check if a strategy is registered.
        
        Args:
            name: Strategy name
            
        Returns:
            True if registered, False otherwise
        """
        return name in cls._strategies
    
    @classmethod
    def clear(cls) -> None:
        """
        Clear all registered strategies (mainly for testing).
        """
        cls._strategies.clear()
