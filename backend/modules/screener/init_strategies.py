"""
Initialize strategies and their default parameters in the database.
This should be run when the application starts or when adding new strategies.
"""
from backend.core.database import get_db_session
from backend.modules.screener.models import Strategy, StrategyParameter
from backend.modules.screener.strategies.registry import StrategyRegistry
from backend.modules.screener.strategies.xtumy_v27 import XTUMYV27Strategy

# Parameter metadata for XTUMY V27
XTUMY_V27_PARAM_METADATA = {
    # Main Trend Settings
    'trend_ema_length': {
        'display_name': 'Trend EMA Uzunluğu (Ana Trend)',
        'display_group': 'ANA TREND AYARLARI',
        'display_order': 1
    },
    'min_ema_slope': {
        'display_name': 'Minimum EMA Eğimi',
        'display_group': 'ANA TREND AYARLARI',
        'display_order': 2
    },
    
    # Power & Direction Filters
    'adx_threshold': {
        'display_name': 'ADX Eşiği (Trend Gücü)',
        'display_group': 'GÜÇ VE YÖN FİLTRELERİ',
        'display_order': 3
    },
    'di_direction_control': {
        'display_name': 'DI+ > DI- Şartı (Yön Kontrolü)',
        'display_group': 'GÜÇ VE YÖN FİLTRELERİ',
        'display_order': 4
    },
    'min_rsi_for_buy': {
        'display_name': 'Minimum RSI (AL için)',
        'display_group': 'GÜÇ VE YÖN FİLTRELERİ',
        'display_order': 5
    },
    
    # Fibo Breakout Settings
    'fibo_length': {
        'display_name': 'Fibo Uzunluğu / Periyot',
        'display_group': 'FİBO KIRILIM AYARLARI',
        'display_order': 6
    },
    'fibo_visual_length': {
        'display_name': 'Çizgi Görsel Uzunluğu (Bar)',
        'display_group': 'FİBO KIRILIM AYARLARI',
        'display_order': 7
    },
    'fibo_signal_cooldown': {
        'display_name': 'Fibo Sinyal Soğuma Süresi (Bar)',
        'display_group': 'FİBO KIRILIM AYARLARI',
        'display_order': 8
    },
    
    # Pullback Settings
    'pbWaitBars': {
        'display_name': 'Trend Oturma Süresi (Bar)',
        'display_group': 'PULLBACK (GERİ ÇEKİLME) AYARLARI',
        'display_order': 9
    },
    'pullPct': {
        'display_name': "EMA'ya Yakınlık Toleransı (%)",
        'display_group': 'PULLBACK (GERİ ÇEKİLME) AYARLARI',
        'display_order': 10
    },
    'breakout_slope': {
        'display_name': 'Hacim Çarpanı (Breakout için)',
        'display_group': 'PULLBACK (GERİ ÇEKİLME) AYARLARI',
        'display_order': 11
    },
    
    # Dip Settings
    'shortPeriod': {
        'display_name': 'Kısa Vade EMA (Kurumsal İz)',
        'display_group': 'KURUMSAL DİP (SESSİZ TOPLAMA) AYARLARI',
        'display_order': 12
    },
    
    # Alert Settings
    'show_momentum_loss': {
        'display_name': 'Momentum Kaybı / Red (X) Göster',
        'display_group': 'UYARI AYARLARI',
        'display_order': 13
    },
}


def init_strategy_in_db(strategy_class, param_metadata: dict):
    """
    Initialize a strategy and its default parameters in the database.
    
    Args:
        strategy_class: Strategy class (e.g., XTUMYV27Strategy)
        param_metadata: Dict with parameter metadata (display_name, display_group, etc.)
    """
    with get_db_session() as session:
        strategy_name = strategy_class.get_name()
        
        # Check if strategy exists
        strategy = session.query(Strategy).filter(Strategy.name == strategy_name).first()
        
        if not strategy:
            # Create strategy
            strategy = Strategy(
                name=strategy_name,
                display_name=strategy_class.get_display_name(),
                description=strategy_class.get_description(),
                python_class=f"backend.modules.screener.strategies.xtumy_v27.{strategy_name}",
                is_active=True
            )
            session.add(strategy)
            session.flush()  # Get strategy.id
            print(f"✓ Created strategy: {strategy_name}")
        else:
            print(f"✓ Strategy already exists: {strategy_name}")
        
        # Get default parameters
        default_params = strategy_class.get_default_parameters()
        param_dict = default_params.model_dump()
        
        # Get parameter types from Pydantic model class (not instance)
        param_types = {}
        for field_name, field_info in default_params.__class__.model_fields.items():
            param_type = 'str'
            if field_info.annotation == int:
                param_type = 'int'
            elif field_info.annotation == float:
                param_type = 'float'
            elif field_info.annotation == bool:
                param_type = 'bool'
            param_types[field_name] = param_type
        
        # Create default parameters for user_id=1 if they don't exist
        user_id = 1
        
        for param_name, param_value in param_dict.items():
            existing = session.query(StrategyParameter).filter(
                StrategyParameter.user_id == user_id,
                StrategyParameter.strategy_id == strategy.id,
                StrategyParameter.parameter_name == param_name
            ).first()
            
            if not existing:
                metadata = param_metadata.get(param_name, {})
                
                new_param = StrategyParameter(
                    user_id=user_id,
                    strategy_id=strategy.id,
                    parameter_name=param_name,
                    parameter_value=param_value,
                    parameter_type=param_types.get(param_name, 'str'),
                    display_name=metadata.get('display_name', param_name),
                    display_group=metadata.get('display_group', 'GENEL AYARLAR'),
                    display_order=metadata.get('display_order', 999),
                    is_default=True
                )
                session.add(new_param)
                print(f"  ✓ Added parameter: {param_name} = {param_value}")
        
        session.commit()
        print(f"✅ Strategy {strategy_name} initialized successfully!\n")


def init_all_strategies():
    """Initialize all registered strategies in the database."""
    print("=" * 60)
    print("Initializing strategies in database...")
    print("=" * 60)
    
    # Initialize XTUMY V27
    init_strategy_in_db(XTUMYV27Strategy, XTUMY_V27_PARAM_METADATA)
    
    print("=" * 60)
    print("✅ All strategies initialized!")
    print("=" * 60)


if __name__ == '__main__':
    init_all_strategies()
