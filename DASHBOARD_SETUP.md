# 📊 Web Dashboard Setup Guide

## Seçenekler

### Seçenek 1: Basit Flask HTML Template (Hızlı Başlangıç)

En basit ve hızlı yol. Flask ile backend ve frontend'i tek bir uygulamada birleştirin.

```bash
cd bist_analyst
mkdir -p templates static/css static/js
```

**templates/index.html:**
```html
<!DOCTYPE html>
<html>
<head>
    <title>BIST Analyst Dashboard</title>
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <div class="container">
        <h1>🚀 BIST Analyst Dashboard</h1>
        <div id="signals"></div>
    </div>
    <script src="/static/js/app.js"></script>
</body>
</html>
```

**api.py'ye ekle:**
```python
@app.route('/')
def index():
    return render_template('index.html')
```

**Avantajlar:**
- Hızlı kurulum
- Tek port
- Basit deployment

**Dezavantajlar:**
- Modern UI framework yok
- SPA değil
- Sınırlı interaktivite

---

### Seçenek 2: Next.js Dashboard (Profesyonel)

Modern, hızlı ve TradingView benzeri profesyonel UI.

#### Kurulum

```bash
# bist_analyst klasörünün dışında
cd /Users/ademcelik/Desktop
npx create-next-app@latest bist-analyst-dashboard
cd bist-analyst-dashboard
npm install axios chart.js react-chartjs-2 @tanstack/react-query
```

#### Konfigürasyon seçenekleri:
```
✔ Would you like to use TypeScript? … Yes
✔ Would you like to use ESLint? … Yes
✔ Would you like to use Tailwind CSS? … Yes
✔ Would you like to use `src/` directory? … Yes
✔ Would you like to use App Router? … Yes
✔ Would you like to customize the default import alias? … No
```

#### Proje Yapısı
```
bist-analyst-dashboard/
├── src/
│   ├── app/
│   │   ├── page.tsx           # Ana sayfa
│   │   ├── layout.tsx         # Layout
│   │   └── api/               # API proxy (opsiyonel)
│   ├── components/
│   │   ├── SignalTable.tsx    # Sinyal tablosu
│   │   ├── SignalCard.tsx     # Sinyal kartı
│   │   ├── ChartWidget.tsx    # TradingView widget
│   │   └── FilterPanel.tsx    # Filtreler
│   ├── hooks/
│   │   └── useSignals.ts      # Custom hooks
│   └── utils/
│       └── api.ts             # API calls
├── public/
│   └── assets/
└── package.json
```

#### Basit Başlangıç Kodu

**src/utils/api.ts:**
```typescript
const API_BASE = 'http://localhost:5000/api';

export async function getLatestSignals() {
  const res = await fetch(`${API_BASE}/signals/latest`);
  if (!res.ok) throw new Error('Failed to fetch signals');
  return res.json();
}

export async function getStats() {
  const res = await fetch(`${API_BASE}/stats`);
  if (!res.ok) throw new Error('Failed to fetch stats');
  return res.json();
}
```

**src/app/page.tsx:**
```typescript
'use client';

import { useEffect, useState } from 'react';
import { getLatestSignals, getStats } from '@/utils/api';

export default function Home() {
  const [signals, setSignals] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [signalsData, statsData] = await Promise.all([
          getLatestSignals(),
          getStats()
        ]);
        setSignals(signalsData.signals);
        setStats(statsData);
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <main className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-4">🚀 BIST Analyst Dashboard</h1>
      
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-white p-4 rounded shadow">
          <p className="text-gray-600">Total Signals</p>
          <p className="text-2xl font-bold">{signals.length}</p>
        </div>
        <div className="bg-white p-4 rounded shadow">
          <p className="text-gray-600">Tickers</p>
          <p className="text-2xl font-bold">{stats?.tickers || 0}</p>
        </div>
        <div className="bg-white p-4 rounded shadow">
          <p className="text-gray-600">Latest Update</p>
          <p className="text-sm">{stats?.latest_data_date}</p>
        </div>
      </div>

      <div className="bg-white rounded shadow">
        <table className="w-full">
          <thead>
            <tr className="border-b">
              <th className="p-4 text-left">Symbol</th>
              <th className="p-4 text-left">Signal</th>
              <th className="p-4 text-left">Price</th>
              <th className="p-4 text-left">RSI</th>
              <th className="p-4 text-left">ADX</th>
            </tr>
          </thead>
          <tbody>
            {signals.map((sig, idx) => (
              <tr key={idx} className="border-b hover:bg-gray-50">
                <td className="p-4 font-bold">{sig.Symbol}</td>
                <td className="p-4">
                  <span className="bg-blue-100 px-2 py-1 rounded text-sm">
                    {sig.Signal}
                  </span>
                </td>
                <td className="p-4">{sig.Close.toFixed(2)} TL</td>
                <td className="p-4">{sig.RSI.toFixed(1)}</td>
                <td className="p-4">{sig.ADX.toFixed(1)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </main>
  );
}
```

#### Çalıştırma

Terminal 1 (Flask API):
```bash
cd /Users/ademcelik/Desktop/bist_analyst
python3.11 api.py
```

Terminal 2 (Next.js):
```bash
cd /Users/ademcelik/Desktop/bist-analyst-dashboard
npm run dev
```

**Erişim:**
- API: http://localhost:5000
- Dashboard: http://localhost:3000

**Avantajlar:**
- Modern, hızlı, responsive
- TradingView benzeri UI yapılabilir
- TypeScript type safety
- SEO friendly (SSR)
- Production-ready

**Dezavantajlar:**
- Kurulum biraz daha uzun
- Node.js gerekiyor
- İki ayrı port

---

### Seçenek 3: Streamlit (Hızlı Prototip)

Python tabanlı, en hızlı yol. Veri bilimcileri için ideal.

```bash
pip install streamlit plotly
```

**dashboard.py:**
```python
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from config import DB_CONNECTION_STR

st.set_page_config(page_title="BIST Analyst", layout="wide")

st.title("🚀 BIST Analyst Dashboard")

# Signals
engine = create_engine(DB_CONNECTION_STR)
query = "SELECT * FROM market_data LIMIT 100"
df = pd.read_sql(query, engine)

st.dataframe(df)
```

**Çalıştırma:**
```bash
streamlit run dashboard.py
```

**Avantajlar:**
- Çok hızlı kurulum
- Python bilgisi yeterli
- Built-in widgets

**Dezavantajlar:**
- Sınırlı customization
- Streamlit branding
- Yavaş olabilir

---

## Önerilen Yol

### Hızlı Test için: **Streamlit**
5 dakikada çalışır duruma gelir.

### Gerçek Dashboard için: **Next.js**
Profesyonel, modern, TradingView benzeri UI.

---

## TradingView Widget Entegrasyonu

Her üç seçenekte de TradingView chart widget'ını ekleyebilirsiniz:

```html
<!-- TradingView Widget -->
<div class="tradingview-widget-container">
  <div id="tradingview_widget"></div>
</div>

<script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
<script type="text/javascript">
new TradingView.widget({
  "width": "100%",
  "height": 400,
  "symbol": "BIST:THYAO",
  "interval": "D",
  "timezone": "Europe/Istanbul",
  "theme": "light",
  "style": "1",
  "locale": "tr",
  "toolbar_bg": "#f1f3f6",
  "enable_publishing": false,
  "allow_symbol_change": true,
  "container_id": "tradingview_widget"
});
</script>
```

---

## Sonraki Adımlar

1. **Bir seçenek belirle** (Next.js öneriyorum)
2. **Kurulumu yap** (yukarıdaki adımları takip et)
3. **API'yi çalıştır** (`python3.11 api.py`)
4. **Dashboard'u çalıştır**
5. **Özelleştir** (TradingView benzeri tasarım)

---

## Yardım

Herhangi bir seçenekle devam etmek isterseniz, detaylı kurulum ve geliştirme için yardımcı olabilirim!

