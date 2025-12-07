import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from config import DB_CONNECTION_STR
import time
import os

def calculate_rsi(series, period=14):
    """RSI hesaplama (Wilder's method)"""
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).ewm(alpha=1/period, adjust=False).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/period, adjust=False).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_adx(df, period=14):
    """ADX hesaplama"""
    high, low, close = df['high'], df['low'], df['close']
    
    # True Range
    tr = pd.concat([high - low, abs(high - close.shift()), abs(low - close.shift())], axis=1).max(axis=1)
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

def check_signals(df):
    """Tek bir hisse için Pine Script XTUMY V27 sinyallerini kontrol et"""
    if len(df) < 60:  # Minimum veri kontrolü
        return []
    
    # Parametreler (Pine Script'teki input değerleri - EXACT)
    pbWaitBars = 3    # Trend oturma süresi (Line 32)
    pullPct = 2.0     # EMA'ya yakınlık toleransı (%) (Line 33)
    volMult = 1.2     # Hacim çarpanı (Line 34)
    rsiMin = 45       # Minimum RSI (Line 39)
    fibLen = 144      # Fibonacci uzunluğu (Line 42)
    cooldown = 10     # Cooldown süresi (bar) (Line 44)
    slopeTh = 0.05    # Minimum EMA eğimi (Line 20)
    adxThresh = 20    # ADX eşiği (Line 38)
    emaShortLen = 20  # Kısa EMA (Line 25)
    
    # İndikatörler
    df = df.copy()
    df['EMA50'] = df['close'].ewm(span=50, adjust=False).mean()
    df['EMA20'] = df['close'].ewm(span=20, adjust=False).mean()
    df['rsi'] = calculate_rsi(df['close'], 14)
    df['rsiMA'] = df['rsi'].rolling(14).mean()
    df['avgVol'] = df['volume'].rolling(20).mean()
    df['diplus'], df['diminus'], df['adx'] = calculate_adx(df, 14)
    
    # EMA Eğimi
    df['emaSlope'] = (df['EMA50'] - df['EMA50'].shift(1)) / df['EMA50'].shift(1) * 100
    df['isSlopePositive'] = df['emaSlope'] > 0
    df['isSlopeStrong'] = df['emaSlope'] > slopeTh
    df['isTrendStrong'] = df['adx'] > 20
    
    # Fibonacci Duvarları (144 barlık)
    df['wall_top'] = df['high'].rolling(fibLen).max().shift(1)
    df['wall_low'] = df['low'].rolling(fibLen).min().shift(1)
    df['wall_diff'] = df['wall_top'] - df['wall_low']
    df['wall_gold'] = df['wall_low'] + (df['wall_diff'] * 0.618)
    
    signals = []
    
    # SADECE SON BAR'ı kontrol et (en güncel kapanış)
    curr = df.iloc[-1]
    prev = df.iloc[-2]
    
    # NaN kontrolü
    if pd.isna([curr['EMA50'], curr['EMA20'], curr['rsi'], curr['rsiMA']]).any():
        return []
    
    # === SİNYAL 1: KURUMSAL DİP (Silent Accumulation) ===
    # 1. Ayı yapısı: EMA20 < EMA50
    isBearStructure = curr['EMA20'] < curr['EMA50']
    
    # 2. Crossover: Fiyat EMA20'yi yukarı kesiyor
    crossEMA20 = (prev['close'] <= prev['EMA20']) and (curr['close'] > curr['EMA20'])
    
    # 3. RSI momentum: RSI > RSI MA ve yükseliyor
    rsiStrong = (curr['rsi'] > curr['rsiMA']) and (curr['rsi'] > prev['rsi'])
    
    # 4. Hacim stabil: 0.3x - 1.5x arası
    volStable = (curr['volume'] > curr['avgVol'] * 0.3) and (curr['volume'] < curr['avgVol'] * 1.5)
    
    # 5. Yeşil mum
    greenCandle = curr['close'] > curr['open']
    
    if isBearStructure and crossEMA20 and rsiStrong and volStable and greenCandle:
        signals.append({
            'Symbol': curr['symbol'],
            'Date': curr['date'],
            'Close': float(curr['close']),
            'Signal': 'KURUMSAL DİP',
            'Trend': 'Ayı Yapısında Sessiz Toplama',
            'RSI': round(float(curr['rsi']), 2),
            'ADX': round(float(curr['adx']), 2)
        })
    
    # === SİNYAL 2: TREND BAŞLANGIÇ (EMA50 Breakout) ===
    # Pine Script mantığı: confirmBars=1 için 1 BAR ÖNCE crossover olmalı
    # Yani prev bar'da crossover olmuş, curr bar ise koşulları koruyor
    
    # 1. Crossover 1 BAR ÖNCE oldu mu? (confirmBars=1 için)
    if len(df) < 3:
        pass  # Yeterli veri yok
    else:
        prev_prev = df.iloc[-3]  # 2 bar önce
        
        # prev bar'da crossover oldu mu?
        crossHappened = (prev_prev['close'] <= prev_prev['EMA50']) and (prev['close'] > prev['EMA50'])
        
        # prev bar'da hacim güçlü ve yeşil mum muydu?
        volWasStrongAndGreen = (prev['volume'] > prev['avgVol']) and (prev['close'] > prev['open'])
        
        # Son bar (curr) hala EMA50 üstünde mi?
        stayedHigh = curr['close'] >= curr['EMA50']
        
        # Son bar yeşil mum mu?
        isSignalBarGreen = curr['close'] > curr['open']
        
        # DI+ > DI- kontrolü (Pine Script'te useDiCheck=true)
        isDirectionUp = curr['diplus'] > curr['diminus']
        
        # Tüm koşullar sağlanıyor mu?
        buyBreakout = (crossHappened and volWasStrongAndGreen and stayedHigh and 
                      isSignalBarGreen and isDirectionUp)
        
        if buyBreakout:
            signals.append({
                'Symbol': curr['symbol'],
                'Date': curr['date'],
                'Close': float(curr['close']),
                'Signal': 'TREND BAŞLANGIÇ',
                'Trend': 'EMA50 Kırılımı (1 Bar Önce)',
                'RSI': round(float(curr['rsi']), 2),
                'ADX': round(float(curr['adx']), 2)
            })
    
    # === SİNYAL 3: PULLBACK AL (Retest/Geri Çekilme) ===
    # Trend oturduktan sonra EMA50'ye geri çekilme
    
    # Son EMA50 crossover'dan bu yana kaç bar geçti?
    barsSinceUp = None
    barsSinceDown = None
    
    for i in range(len(df) - 1, 0, -1):
        if barsSinceUp is None:
            if df.iloc[i-1]['close'] <= df.iloc[i-1]['EMA50'] and df.iloc[i]['close'] > df.iloc[i]['EMA50']:
                barsSinceUp = len(df) - 1 - i
        if barsSinceDown is None:
            if df.iloc[i-1]['close'] >= df.iloc[i-1]['EMA50'] and df.iloc[i]['close'] < df.iloc[i]['EMA50']:
                barsSinceDown = len(df) - 1 - i
        if barsSinceUp is not None and barsSinceDown is not None:
            break
    
    # Uptrend'de mi? (Son crossover yukarı mı?)
    isInUptrend = (barsSinceUp is not None) and (barsSinceDown is None or barsSinceUp < barsSinceDown)
    isTrendMature = isInUptrend and (barsSinceUp >= pbWaitBars)
    
    if isTrendMature:
        # Pine Script PULLBACK mantığı (EXACT TRANSLATION)
        # Kök Çözüm: Pine Script SADECE LOW kontrolü yapıyor!
        touchLimit = curr['EMA50'] * (1 + pullPct/100)
        
        # didTouchToday = (low <= touchLimit) - Pine Script Line 208
        didTouchToday = curr['low'] <= touchLimit
        
        # didTouchYesterday = (low[1] <= touchLimit[1]) - Pine Script Line 209
        if len(df) >= 3:
            prev = df.iloc[-2]
            prev2 = df.iloc[-3]
            prev_touchLimit = prev['EMA50'] * (1 + pullPct/100)
            didTouchYesterday = prev['low'] <= prev_touchLimit
            yesterdayWasDown = prev['close'] < prev2['close']
            
            # isValidContact = didTouchToday or (didTouchYesterday and yesterdayWasDown)
            isValidContact = didTouchToday or (didTouchYesterday and yesterdayWasDown)
        else:
            isValidContact = didTouchToday
        
        # Pullback koşulları (Pine Script Line 211)
        isDirectionUp = curr['diplus'] > curr['diminus']
        isVolOk = curr['volume'] > (curr['avgVol'] * volMult)
        
        # rawPullback = isTrendMature and isValidContact and (close > emaVal) and (close > open) 
        #               and isSlopePositive and isTrendStrong and (rsi > rsiMin) and isVolOk 
        #               and (close > low[1]) and isDirectionUp
        rawPullback = (isValidContact and 
                      (curr['close'] > curr['EMA50']) and 
                      (curr['close'] > curr['open']) and 
                      curr['isSlopePositive'] and 
                      curr['isTrendStrong'] and 
                      (curr['rsi'] > rsiMin) and 
                      isVolOk and 
                      (curr['close'] > prev['low']) and 
                      isDirectionUp)
        
        # Pine Script State Machine (Lines 213-220)
        # var bool lastWasPull = false
        # if rawPullback and not lastWasPull
        #     lastWasPull := true
        # else if close < emaVal 
        #     lastWasPull := false
        # else if rsi > 70 
        #     lastWasPull := false
        # buyPullback = rawPullback and lastWasPull
        
        # Python'da state machine yok, sadece rawPullback kullanıyoruz
        # State machine sadece tekrar sinyal önlemek için (gerçek zamanlı trading'de gerekli)
        # Bizim use case: Günlük tarama, her gün yeni tarama, state gerekmiyor
        
        # buyPullbackFinal = buyPullback and not buyBreakout (Line 223)
        # TREND BAŞLANGIÇ ile çakışmayı önle
        if rawPullback and not any(s['Signal'] == 'TREND BAŞLANGIÇ' for s in signals):
            signals.append({
                'Symbol': curr['symbol'],
                'Date': curr['date'],
                'Close': float(curr['close']),
                'Signal': 'PULLBACK AL',
                'Trend': 'EMA50 Retesti',
                'RSI': round(float(curr['rsi']), 2),
                'ADX': round(float(curr['adx']), 2)
            })
    
    # === SİNYAL 4: DİP AL (Fibo Dibi) ===
    if not pd.isna(curr['wall_low']):
        buyDip = ((curr['low'] <= curr['wall_low'] * 1.02) and 
                  (curr['close'] > curr['open']) and 
                  (curr['rsi'] > prev['rsi']) and 
                  (curr['diplus'] > curr['diminus']))
        
        # PULLBACK ile çakışma kontrolü
        if buyDip and not any(s['Signal'] == 'PULLBACK AL' for s in signals):
            signals.append({
                'Symbol': curr['symbol'],
                'Date': curr['date'],
                'Close': float(curr['close']),
                'Signal': 'DİP AL',
                'Trend': f'Fibonacci Dibi ({curr["wall_low"]:.2f})',
                'RSI': round(float(curr['rsi']), 2),
                'ADX': round(float(curr['adx']), 2)
            })
    
    # === SİNYAL 5: ALTIN KIRILIM (Golden Ratio 0.618 Break) ===
    if not pd.isna(curr['wall_gold']):
        # Crossover kontrolü
        breakGold = (prev['close'] <= prev['wall_gold']) and (curr['close'] > curr['wall_gold'])
        
        # Cooldown kontrolü - son 10 bar içinde ALTIN KIRILIM sinyali var mı?
        cooldown_ok = True
        if len(df) >= cooldown:
            for i in range(1, cooldown + 1):
                past_bar = df.iloc[-1 - i]
                past_prev = df.iloc[-2 - i] if len(df) > (1 + i) else None
                if past_prev is not None:
                    if (past_prev['close'] <= past_prev['wall_gold']) and (past_bar['close'] > past_bar['wall_gold']):
                        cooldown_ok = False
                        break
        
        isGoldBreakValid = (breakGold and 
                           (curr['volume'] > (curr['avgVol'] * volMult)) and 
                           (curr['close'] > curr['open']) and 
                           (curr['diplus'] > curr['diminus']) and 
                           cooldown_ok)
        
        if isGoldBreakValid:
            signals.append({
                'Symbol': curr['symbol'],
                'Date': curr['date'],
                'Close': float(curr['close']),
                'Signal': 'ALTIN KIRILIM',
                'Trend': f'0.618 Kırıldı ({curr["wall_gold"]:.2f})',
                'RSI': round(float(curr['rsi']), 2),
                'ADX': round(float(curr['adx']), 2)
            })
    
    # === SİNYAL 6: ZİRVE KIRILIMI (Resistance Break) ===
    if not pd.isna(curr['wall_top']):
        # Crossover kontrolü
        breakTop = (prev['close'] <= prev['wall_top']) and (curr['close'] > curr['wall_top'])
        
        # Cooldown kontrolü - son 10 bar içinde ZİRVE KIRILIMI sinyali var mı?
        cooldown_ok = True
        if len(df) >= cooldown:
            for i in range(1, cooldown + 1):
                past_bar = df.iloc[-1 - i]
                past_prev = df.iloc[-2 - i] if len(df) > (1 + i) else None
                if past_prev is not None:
                    if (past_prev['close'] <= past_prev['wall_top']) and (past_bar['close'] > past_bar['wall_top']):
                        cooldown_ok = False
                        break
        
        isResBreakValid = (breakTop and 
                          (curr['volume'] > (curr['avgVol'] * volMult)) and 
                          (curr['close'] > curr['open']) and 
                          (curr['diplus'] > curr['diminus']) and 
                          cooldown_ok)
        
        if isResBreakValid:
            signals.append({
                'Symbol': curr['symbol'],
                'Date': curr['date'],
                'Close': float(curr['close']),
                'Signal': 'ZİRVE KIRILIMI',
                'Trend': f'Direnç Aşıldı ({curr["wall_top"]:.2f})',
                'RSI': round(float(curr['rsi']), 2),
                'ADX': round(float(curr['adx']), 2)
            })
    
    return signals

def run_scanner():
    print("=" * 70)
    print("XTUMY V27 Scanner - Pine Script Uyumlu Versiyon")
    print("=" * 70)
    start_time = time.time()
    
    engine = create_engine(DB_CONNECTION_STR)
    
    query = """
    SELECT * FROM market_data 
    WHERE date > NOW() - INTERVAL '250 days'
    ORDER BY symbol, date ASC
    """
    
    print("\nVeritabanından veri okunuyor...")
    df_all = pd.read_sql(query, engine)
    
    if df_all.empty:
        print("❌ Veri bulunamadı!")
        return
    
    print(f"✓ {len(df_all)} satır yüklendi ({df_all['symbol'].nunique()} hisse)")
    print("\nSinyaller taranıyor...")
    
    all_signals = []
    
    for symbol, group_df in df_all.groupby('symbol'):
        signals = check_signals(group_df)
        all_signals.extend(signals)
    
    end_time = time.time()
    
    # Sonuçları göster
    if all_signals:
        df_results = pd.DataFrame(all_signals)
        
        print(f"\n{'='*70}")
        print(f"✅ {len(all_signals)} SİNYAL BULUNDU")
        print(f"{'='*70}\n")
        
        # Sinyal türüne göre grupla
        for signal_type in df_results['Signal'].unique():
            signal_df = df_results[df_results['Signal'] == signal_type]
            print(f"\n📊 {signal_type} ({len(signal_df)} adet)")
            print("-" * 70)
            for _, row in signal_df.iterrows():
                print(f"  {row['Symbol']:8s} │ {row['Close']:8.2f} TL │ RSI: {row['RSI']:5.1f} │ ADX: {row['ADX']:5.1f} │ {pd.to_datetime(row['Date']).strftime('%Y-%m-%d')}")
        
        print(f"\n{'='*70}")
        print(f"⏱️  Süre: {end_time - start_time:.2f} saniye\n")
        
        return df_results  # Telegram için DataFrame döndür
    else:
        print(f"\n❌ Sinyal bulunamadı.")
        print(f"⏱️  Süre: {end_time - start_time:.2f} saniye\n")
        return None

if __name__ == "__main__":
    import sys
    from telegram_bot import TelegramBot
    
    # Scanner'ı çalıştır ve sonuçları al
    results_df = run_scanner()
    
    # Telegram gönderimi (--telegram flag ile)
    if '--telegram' in sys.argv or os.getenv('ENABLE_TELEGRAM', '').lower() == 'true':
        if results_df is not None and len(results_df) > 0:
            bot = TelegramBot()
            bot.send_scan_results(results_df)

