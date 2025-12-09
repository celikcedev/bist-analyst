"""
XTUMY V27 Trading Strategy - Pine Script exact Python translation.

This strategy identifies 6 types of buy signals based on EMA trends, 
RSI momentum, volume analysis, and Fibonacci levels.
"""
import pandas as pd
import numpy as np
from typing import List
from pydantic import Field

from backend.modules.screener.strategies.base import BaseStrategy, StrategyParameters, SignalResult
from backend.modules.screener.strategies.registry import StrategyRegistry


class XTUMYV27Parameters(StrategyParameters):
    """
    Parameters for XTUMY V27 strategy.
    
    All default values match the original Pine Script implementation.
    """
    pbWaitBars: int = Field(3, ge=1, le=10, description="Trend oturma süresi (bar)")
    pullPct: float = Field(2.0, ge=0.1, le=10.0, description="EMA'ya yakınlık toleransı (%)")
    volMult: float = Field(1.2, ge=0.5, le=3.0, description="Hacim çarpanı")
    rsiMin: int = Field(45, ge=30, le=70, description="Minimum RSI değeri")
    fibLen: int = Field(144, ge=50, le=250, description="Fibonacci uzunluğu (bar)")
    cooldown: int = Field(10, ge=5, le=30, description="Cooldown süresi (bar)")
    slopeTh: float = Field(0.05, ge=0.01, le=0.2, description="Minimum EMA eğim eşiği")
    adxThresh: int = Field(20, ge=15, le=30, description="ADX eşik değeri")
    emaShortLen: int = Field(20, ge=10, le=50, description="Kısa EMA periyodu")
    emaLongLen: int = Field(50, ge=30, le=100, description="Uzun EMA periyodu")
    rsiPeriod: int = Field(14, ge=7, le=21, description="RSI periyodu")
    adxPeriod: int = Field(14, ge=7, le=21, description="ADX periyodu")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "pbWaitBars": 3,
                "pullPct": 2.0,
                "volMult": 1.2,
                "rsiMin": 45,
                "fibLen": 144,
                "cooldown": 10,
                "slopeTh": 0.05,
                "adxThresh": 20,
                "emaShortLen": 20,
                "emaLongLen": 50,
                "rsiPeriod": 14,
                "adxPeriod": 14
            }
        }
    }


@StrategyRegistry.register
class XTUMYV27Strategy(BaseStrategy):
    """
    XTUMY V27 Trading Strategy
    
    Identifies 7 types of signals:
    1. KURUMSAL DİP - Silent accumulation in bear structure
    2. TREND BAŞLANGIÇ - EMA50 breakout
    3. PULLBACK AL - EMA50 retest after trend establishment
    4. DİP AL - Fibonacci bottom (0.000 level)
    5. ALTIN KIRILIM - Golden ratio (0.618) breakout
    6. ZİRVE KIRILIMI - ATH resistance breakout
    7. DİRENÇ REDDİ - Resistance rejection warning
    """
    
    def calculate_signals(self, df: pd.DataFrame) -> List[SignalResult]:
        """Calculate XTUMY V27 signals for given OHLCV data."""
        # Validate input
        self.validate_dataframe(df, min_rows=60)
        
        # Create a copy to avoid modifying original
        df = df.copy()
        
        # Calculate indicators
        df = self._calculate_indicators(df)
        
        # Check signals on last bar only
        signals = []
        
        if len(df) < 3:  # Need at least 3 bars for comparisons
            return signals
        
        curr = df.iloc[-1]
        prev = df.iloc[-2]
        
        # NaN check
        if pd.isna([curr['EMA50'], curr['EMA20'], curr['rsi'], curr['rsiMA']]).any():
            return signals
        
        # Signal 1: KURUMSAL DİP
        signal = self._check_kurumsal_dip(df, curr, prev)
        if signal:
            signals.append(signal)
        
        # Signal 2: TREND BAŞLANGIÇ
        signal = self._check_trend_baslangic(df, curr, prev)
        if signal:
            signals.append(signal)
        
        # Signal 3: PULLBACK AL
        signal = self._check_pullback_al(df, curr, prev, signals)
        if signal:
            signals.append(signal)
        
        # Signal 4: DİP AL
        signal = self._check_dip_al(df, curr, prev, signals)
        if signal:
            signals.append(signal)
        
        # Signal 5: ALTIN KIRILIM
        signal = self._check_altin_kirilim(df, curr, prev)
        if signal:
            signals.append(signal)
        
        # Signal 6: ZİRVE KIRILIMI
        signal = self._check_zirve_kirilimi(df, curr, prev)
        if signal:
            signals.append(signal)
        
        # Signal 7: DİRENÇ REDDİ
        signal = self._check_direnc_reddi(df, curr, prev)
        if signal:
            signals.append(signal)
        
        return signals
    
    def _calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all required technical indicators."""
        params = self.params
        
        # EMAs
        df['EMA50'] = df['close'].ewm(span=params.emaLongLen, adjust=False).mean()
        df['EMA20'] = df['close'].ewm(span=params.emaShortLen, adjust=False).mean()
        
        # RSI
        df['rsi'] = self._calculate_rsi(df['close'], params.rsiPeriod)
        df['rsiMA'] = df['rsi'].rolling(params.rsiPeriod).mean()
        
        # Volume
        df['avgVol'] = df['volume'].rolling(20).mean()
        
        # ADX and Directional Indicators
        df['diplus'], df['diminus'], df['adx'] = self._calculate_adx(df, params.adxPeriod)
        
        # EMA Slope
        df['emaSlope'] = (df['EMA50'] - df['EMA50'].shift(1)) / df['EMA50'].shift(1) * 100
        df['isSlopePositive'] = df['emaSlope'] > 0
        df['isSlopeStrong'] = df['emaSlope'] > params.slopeTh
        df['isTrendStrong'] = df['adx'] > params.adxThresh
        
        # Fibonacci Walls
        df['wall_top'] = df['high'].rolling(params.fibLen).max().shift(1)
        df['wall_low'] = df['low'].rolling(params.fibLen).min().shift(1)
        df['wall_diff'] = df['wall_top'] - df['wall_low']
        df['wall_gold'] = df['wall_low'] + (df['wall_diff'] * 0.618)
        
        return df
    
    @staticmethod
    def _calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI using Wilder's method."""
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).ewm(alpha=1/period, adjust=False).mean()
        loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/period, adjust=False).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def _calculate_adx(df: pd.DataFrame, period: int = 14) -> tuple:
        """Calculate ADX and Directional Indicators."""
        high, low, close = df['high'], df['low'], df['close']
        
        # True Range
        tr = pd.concat([
            high - low,
            abs(high - close.shift()),
            abs(low - close.shift())
        ], axis=1).max(axis=1)
        atr = tr.ewm(alpha=1/period, adjust=False).mean()
        
        # Directional Movement
        up_move = high - high.shift()
        down_move = low.shift() - low
        
        plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
        minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)
        
        plus_di = 100 * pd.Series(plus_dm, index=df.index).ewm(alpha=1/period, adjust=False).mean() / atr
        minus_di = 100 * pd.Series(minus_dm, index=df.index).ewm(alpha=1/period, adjust=False).mean() / atr
        
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.ewm(alpha=1/period, adjust=False).mean()
        
        return plus_di, minus_di, adx
    
    def _check_kurumsal_dip(self, df: pd.DataFrame, curr: pd.Series, prev: pd.Series) -> SignalResult:
        """Check for KURUMSAL DİP signal."""
        # Bear structure: EMA20 < EMA50
        isBearStructure = curr['EMA20'] < curr['EMA50']
        
        # Crossover: Price crosses above EMA20
        crossEMA20 = (prev['close'] <= prev['EMA20']) and (curr['close'] > curr['EMA20'])
        
        # RSI momentum
        rsiStrong = (curr['rsi'] > curr['rsiMA']) and (curr['rsi'] > prev['rsi'])
        
        # Stable volume: 0.3x - 1.5x
        volStable = (curr['volume'] > curr['avgVol'] * 0.3) and (curr['volume'] < curr['avgVol'] * 1.5)
        
        # Green candle
        greenCandle = curr['close'] > curr['open']
        
        if isBearStructure and crossEMA20 and rsiStrong and volStable and greenCandle:
            return SignalResult(
                symbol=curr['symbol'],
                signal_type='KURUMSAL DİP',
                signal_date=str(curr['date'])[:10],
                price=float(curr['close']),
                rsi=round(float(curr['rsi']), 2),
                adx=round(float(curr['adx']), 2),
                metadata={'trend': 'Ayı Yapısında Sessiz Toplama'}
            )
        return None
    
    def _check_trend_baslangic(self, df: pd.DataFrame, curr: pd.Series, prev: pd.Series) -> SignalResult:
        """Check for TREND BAŞLANGIÇ signal."""
        if len(df) < 3:
            return None
        
        prev_prev = df.iloc[-3]
        
        # Crossover happened 1 bar ago
        crossHappened = (prev_prev['close'] <= prev_prev['EMA50']) and (prev['close'] > prev['EMA50'])
        
        # Volume was strong and green on crossover bar
        volWasStrongAndGreen = (prev['volume'] > prev['avgVol']) and (prev['close'] > prev['open'])
        
        # Current bar still above EMA50
        stayedHigh = curr['close'] >= curr['EMA50']
        
        # Current bar is green
        isSignalBarGreen = curr['close'] > curr['open']
        
        # DI+ > DI-
        isDirectionUp = curr['diplus'] > curr['diminus']
        
        buyBreakout = (crossHappened and volWasStrongAndGreen and stayedHigh and 
                      isSignalBarGreen and isDirectionUp)
        
        if buyBreakout:
            return SignalResult(
                symbol=curr['symbol'],
                signal_type='TREND BAŞLANGIÇ',
                signal_date=str(curr['date'])[:10],
                price=float(curr['close']),
                rsi=round(float(curr['rsi']), 2),
                adx=round(float(curr['adx']), 2),
                metadata={'trend': 'EMA50 Kırılımı (1 Bar Önce)'}
            )
        return None
    
    def _check_pullback_al(self, df: pd.DataFrame, curr: pd.Series, prev: pd.Series, 
                          existing_signals: List[SignalResult]) -> SignalResult:
        """Check for PULLBACK AL signal."""
        params = self.params
        
        # Calculate bars since last EMA50 crossover
        barsSinceUp, barsSinceDown = None, None
        for i in range(len(df) - 1, 0, -1):
            if barsSinceUp is None:
                if df.iloc[i-1]['close'] <= df.iloc[i-1]['EMA50'] and df.iloc[i]['close'] > df.iloc[i]['EMA50']:
                    barsSinceUp = len(df) - 1 - i
            if barsSinceDown is None:
                if df.iloc[i-1]['close'] >= df.iloc[i-1]['EMA50'] and df.iloc[i]['close'] < df.iloc[i]['EMA50']:
                    barsSinceDown = len(df) - 1 - i
            if barsSinceUp is not None and barsSinceDown is not None:
                break
        
        # In uptrend?
        isInUptrend = (barsSinceUp is not None) and (barsSinceDown is None or barsSinceUp < barsSinceDown)
        isTrendMature = isInUptrend and (barsSinceUp >= params.pbWaitBars)
        
        if not isTrendMature:
            return None
        
        # Pine Script PULLBACK logic - LOW only check
        touchLimit = curr['EMA50'] * (1 + params.pullPct/100)
        didTouchToday = curr['low'] <= touchLimit
        
        if len(df) >= 3:
            prev2 = df.iloc[-3]
            prev_touchLimit = prev['EMA50'] * (1 + params.pullPct/100)
            didTouchYesterday = prev['low'] <= prev_touchLimit
            yesterdayWasDown = prev['close'] < prev2['close']
            isValidContact = didTouchToday or (didTouchYesterday and yesterdayWasDown)
        else:
            isValidContact = didTouchToday
        
        # Pullback conditions
        isDirectionUp = curr['diplus'] > curr['diminus']
        isVolOk = curr['volume'] > (curr['avgVol'] * params.volMult)
        
        rawPullback = (isValidContact and 
                      (curr['close'] > curr['EMA50']) and 
                      (curr['close'] > curr['open']) and 
                      curr['isSlopePositive'] and 
                      curr['isTrendStrong'] and 
                      (curr['rsi'] > params.rsiMin) and 
                      isVolOk and 
                      (curr['close'] > prev['low']) and 
                      isDirectionUp)
        
        # Avoid conflict with TREND BAŞLANGIÇ
        has_trend_baslangic = any(s.signal_type == 'TREND BAŞLANGIÇ' for s in existing_signals)
        
        if rawPullback and not has_trend_baslangic:
            return SignalResult(
                symbol=curr['symbol'],
                signal_type='PULLBACK AL',
                signal_date=str(curr['date'])[:10],
                price=float(curr['close']),
                rsi=round(float(curr['rsi']), 2),
                adx=round(float(curr['adx']), 2),
                metadata={'trend': 'EMA50 Retesti'}
            )
        return None
    
    def _check_dip_al(self, df: pd.DataFrame, curr: pd.Series, prev: pd.Series,
                     existing_signals: List[SignalResult]) -> SignalResult:
        """Check for DİP AL signal."""
        if pd.isna(curr['wall_low']):
            return None
        
        buyDip = ((curr['low'] <= curr['wall_low'] * 1.02) and 
                  (curr['close'] > curr['open']) and 
                  (curr['rsi'] > prev['rsi']) and 
                  (curr['diplus'] > curr['diminus']))
        
        # Avoid conflict with PULLBACK AL
        has_pullback = any(s.signal_type == 'PULLBACK AL' for s in existing_signals)
        
        if buyDip and not has_pullback:
            return SignalResult(
                symbol=curr['symbol'],
                signal_type='DİP AL',
                signal_date=str(curr['date'])[:10],
                price=float(curr['close']),
                rsi=round(float(curr['rsi']), 2),
                adx=round(float(curr['adx']), 2),
                metadata={'trend': f'Fibonacci Dibi ({curr["wall_low"]:.2f})'}
            )
        return None
    
    def _check_altin_kirilim(self, df: pd.DataFrame, curr: pd.Series, prev: pd.Series) -> SignalResult:
        """Check for ALTIN KIRILIM signal."""
        params = self.params
        
        if pd.isna(curr['wall_gold']):
            return None
        
        # Crossover check
        breakGold = (prev['close'] <= prev['wall_gold']) and (curr['close'] > curr['wall_gold'])
        
        # Cooldown check - only count VALID signals (with all conditions met)
        cooldown_ok = True
        if len(df) >= params.cooldown:
            for i in range(1, params.cooldown + 1):
                past_bar = df.iloc[-1 - i]
                past_prev = df.iloc[-2 - i] if len(df) > (1 + i) else None
                if past_prev is not None and not pd.isna(past_bar['wall_gold']) and not pd.isna(past_prev['wall_gold']):
                    # Check if there was a VALID (complete) signal in cooldown period
                    past_crossover = (past_prev['close'] <= past_prev['wall_gold']) and (past_bar['close'] > past_bar['wall_gold'])
                    if past_crossover:
                        # Check if ALL other conditions were also met (volume, bullish, DI+)
                        past_valid = (
                            (past_bar['volume'] > (past_bar['avgVol'] * params.volMult)) and
                            (past_bar['close'] > past_bar['open']) and
                            (past_bar['diplus'] > past_bar['diminus'])
                        )
                        if past_valid:
                            cooldown_ok = False
                            break
        
        isGoldBreakValid = (breakGold and 
                           (curr['volume'] > (curr['avgVol'] * params.volMult)) and 
                           (curr['close'] > curr['open']) and 
                           (curr['diplus'] > curr['diminus']) and 
                           cooldown_ok)
        
        if isGoldBreakValid:
            return SignalResult(
                symbol=curr['symbol'],
                signal_type='ALTIN KIRILIM',
                signal_date=str(curr['date'])[:10],
                price=float(curr['close']),
                rsi=round(float(curr['rsi']), 2),
                adx=round(float(curr['adx']), 2),
                metadata={'trend': f'0.618 Kırıldı ({curr["wall_gold"]:.2f})'}
            )
        return None
    
    def _check_zirve_kirilimi(self, df: pd.DataFrame, curr: pd.Series, prev: pd.Series) -> SignalResult:
        """Check for ZİRVE KIRILIMI signal."""
        params = self.params
        
        if pd.isna(curr['wall_top']):
            return None
        
        # Crossover check
        breakTop = (prev['close'] <= prev['wall_top']) and (curr['close'] > curr['wall_top'])
        
        # Cooldown check - only count VALID signals (with all conditions met)
        cooldown_ok = True
        if len(df) >= params.cooldown:
            for i in range(1, params.cooldown + 1):
                past_bar = df.iloc[-1 - i]
                past_prev = df.iloc[-2 - i] if len(df) > (1 + i) else None
                if past_prev is not None and not pd.isna(past_bar['wall_top']) and not pd.isna(past_prev['wall_top']):
                    # Check if there was a VALID (complete) signal in cooldown period
                    past_crossover = (past_prev['close'] <= past_prev['wall_top']) and (past_bar['close'] > past_bar['wall_top'])
                    if past_crossover:
                        # Check if ALL other conditions were also met (volume, bullish, DI+)
                        past_valid = (
                            (past_bar['volume'] > (past_bar['avgVol'] * params.volMult)) and
                            (past_bar['close'] > past_bar['open']) and
                            (past_bar['diplus'] > past_bar['diminus'])
                        )
                        if past_valid:
                            cooldown_ok = False
                            break
        
        isResBreakValid = (breakTop and 
                          (curr['volume'] > (curr['avgVol'] * params.volMult)) and 
                          (curr['close'] > curr['open']) and 
                          (curr['diplus'] > curr['diminus']) and 
                          cooldown_ok)
        
        if isResBreakValid:
            return SignalResult(
                symbol=curr['symbol'],
                signal_type='ZİRVE KIRILIMI',
                signal_date=str(curr['date'])[:10],
                price=float(curr['close']),
                rsi=round(float(curr['rsi']), 2),
                adx=round(float(curr['adx']), 2),
                metadata={'trend': f'Direnç Aşıldı ({curr["wall_top"]:.2f})'}
            )
        return None
    
    def _check_direnc_reddi(self, df: pd.DataFrame, curr: pd.Series, prev: pd.Series) -> SignalResult:
        """Check for DİRENÇ REDDİ (Resistance Rejection) warning signal.
        
        IMPORTANT: Pine Script alertcondition uses ONLY isRejection, not the full warningSignal.
        TradingView Screener follows alertcondition, so we only check isRejection here.
        
        Pine Script alertcondition:
        alertcondition(isRejection, title="XTUMY V27: DİRENÇ REDDİ", message="{{ticker}} - Satış Baskısı!")
        """
        if pd.isna(curr['wall_top']):
            return None
        
        # Pine Script alertcondition uses ONLY isRejection
        # isRejection = (high >= wall_top) and (close < wall_top)
        isRejection = (curr['high'] >= curr['wall_top']) and (curr['close'] < curr['wall_top'])
        
        if isRejection:
            return SignalResult(
                symbol=curr['symbol'],
                signal_type='DİRENÇ REDDİ',
                signal_date=str(curr['date'])[:10],
                price=float(curr['close']),
                rsi=round(float(curr['rsi']), 2),
                adx=round(float(curr['adx']), 2),
                metadata={'warning': f'Direnç Reddi ({curr["wall_top"]:.2f})'}
            )
        return None
    
    @classmethod
    def get_default_parameters(cls) -> XTUMYV27Parameters:
        """Return default parameters for XTUMY V27."""
        return XTUMYV27Parameters()
    
    @classmethod
    def get_display_name(cls) -> str:
        """Get display name."""
        return "XTUMY V27"
    
    @classmethod
    def get_description(cls) -> str:
        """Get strategy description."""
        return """XTUMY V27 - Multi-Signal Trading Strategy
        
Identifies 6 types of buy signals based on EMA trends, RSI momentum, 
volume analysis, and Fibonacci levels. 100% mathematically compatible 
with TradingView Pine Script implementation."""
