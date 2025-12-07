"""
Market data models for tickers and OHLCV data.
"""
from sqlalchemy import Column, Integer, String, Numeric, BigInteger, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.sql import func
from backend.core.database import Base


class Ticker(Base):
    """Stock ticker symbols."""
    __tablename__ = 'tickers'
    
    symbol = Column(String(20), primary_key=True)
    name = Column(String(255))
    type = Column(String(50))
    user_id = Column(Integer, ForeignKey('users.id'), default=1, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    updated_at = Column(DateTime(timezone=False), default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_tickers_user', 'user_id', 'is_active'),
    )


class MarketData(Base):
    """OHLCV market data."""
    __tablename__ = 'market_data'
    
    symbol = Column(String(20), ForeignKey('tickers.symbol'), primary_key=True, nullable=False)
    date = Column(DateTime(timezone=False), primary_key=True, nullable=False)
    open = Column(Numeric)
    high = Column(Numeric)
    low = Column(Numeric)
    close = Column(Numeric)
    volume = Column(BigInteger)
    data_source = Column(String(50), default='tvdatafeed')
    is_adjusted = Column(Boolean, default=False)
    
    __table_args__ = (
        Index('idx_data_symbol', 'symbol'),
        Index('idx_data_date', 'date'),
    )
