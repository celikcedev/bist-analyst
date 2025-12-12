'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { api, PerformanceSummary, TopPerformer, SymbolPerformance } from '@/lib/api';

type Period = '1d' | '3d' | '7d';

export default function PerformancePage() {
  const [summary, setSummary] = useState<PerformanceSummary | null>(null);
  const [topPerformers, setTopPerformers] = useState<{ top_gainers: TopPerformer[]; top_losers: TopPerformer[] } | null>(null);
  const [symbolPerformance, setSymbolPerformance] = useState<SymbolPerformance[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [days, setDays] = useState(30);
  const [period, setPeriod] = useState<Period>('7d');
  const [activeTab, setActiveTab] = useState<'summary' | 'top' | 'symbols'>('summary');

  useEffect(() => {
    loadData();
  }, [days, period]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [summaryData, topData, symbolData] = await Promise.all([
        api.getPerformanceSummary(days),
        api.getTopPerformers(period, days, 10),
        api.getPerformanceBySymbol(days, 1, 50),
      ]);
      
      setSummary(summaryData);
      setTopPerformers(topData);
      setSymbolPerformance(symbolData.symbols);
    } catch (err: any) {
      console.error('Error loading performance data:', err);
      setError(err.message || 'Performans verileri yüklenirken hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  const formatGain = (gain: number | null) => {
    if (gain === null) return '-';
    const color = gain > 0 ? 'text-green-400' : gain < 0 ? 'text-red-400' : 'text-gray-400';
    return <span className={color}>{gain > 0 ? '+' : ''}{gain.toFixed(2)}%</span>;
  };

  const formatWinRate = (rate: number | null) => {
    if (rate === null) return '-';
    const color = rate >= 60 ? 'text-green-400' : rate >= 50 ? 'text-yellow-400' : 'text-red-400';
    return <span className={color}>{rate.toFixed(1)}%</span>;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-blue-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-blue-300">Performans verileri yükleniyor...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-blue-900 flex items-center justify-center">
        <div className="text-center bg-red-900/20 border border-red-500/30 rounded-lg p-8">
          <p className="text-red-400 mb-4">{error}</p>
          <button 
            onClick={loadData}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
          >
            Tekrar Dene
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-blue-900">
      {/* Header */}
      <header className="bg-slate-900/50 backdrop-blur-xl border-b border-blue-500/20 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              <Link href="/" className="text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                BIST Analyst
              </Link>
              <span className="text-slate-500">/</span>
              <span className="text-white font-medium">📊 Performans</span>
            </div>
            <nav className="flex items-center gap-4">
              <Link href="/" className="text-blue-300 hover:text-white transition-colors">
                Tarayıcı
              </Link>
              <Link href="/strategies" className="text-blue-300 hover:text-white transition-colors">
                Stratejiler
              </Link>
            </nav>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Controls */}
        <div className="flex flex-wrap items-center justify-between gap-4 mb-8">
          <div className="flex items-center gap-4">
            <h1 className="text-2xl font-bold text-white">Sinyal Performansı</h1>
            <span className="text-sm text-blue-300 bg-blue-500/10 px-3 py-1 rounded-full">
              Son {days} Gün
            </span>
          </div>
          
          <div className="flex items-center gap-4">
            {/* Days Selector */}
            <select
              value={days}
              onChange={(e) => setDays(Number(e.target.value))}
              className="bg-slate-800 border border-slate-600 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value={7}>Son 7 Gün</option>
              <option value={14}>Son 14 Gün</option>
              <option value={30}>Son 30 Gün</option>
              <option value={60}>Son 60 Gün</option>
              <option value={90}>Son 90 Gün</option>
            </select>

            {/* Period Selector */}
            <div className="flex bg-slate-800 rounded-lg p-1">
              {(['1d', '3d', '7d'] as Period[]).map((p) => (
                <button
                  key={p}
                  onClick={() => setPeriod(p)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                    period === p
                      ? 'bg-blue-600 text-white'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  +{p.replace('d', ' Gün')}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Summary Cards */}
        {summary && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6">
              <p className="text-slate-400 text-sm mb-1">Toplam Sinyal</p>
              <p className="text-3xl font-bold text-white">{summary.summary.total_signals}</p>
            </div>
            <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6">
              <p className="text-slate-400 text-sm mb-1">Takip Edilen</p>
              <p className="text-3xl font-bold text-blue-400">{summary.summary.tracked_signals}</p>
            </div>
            <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6">
              <p className="text-slate-400 text-sm mb-1">Kazanma Oranı (+7G)</p>
              <p className="text-3xl font-bold">
                {formatWinRate(summary.summary.overall_win_rate_7d)}
              </p>
            </div>
            <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6">
              <p className="text-slate-400 text-sm mb-1">Ortalama Kazanç (+7G)</p>
              <p className="text-3xl font-bold">
                {formatGain(summary.summary.overall_avg_gain_7d)}
              </p>
            </div>
          </div>
        )}

        {/* Tabs */}
        <div className="flex border-b border-slate-700 mb-6">
          {[
            { id: 'summary', label: 'Sinyal Türüne Göre' },
            { id: 'top', label: 'En İyi/Kötü Performans' },
            { id: 'symbols', label: 'Hisseye Göre' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`px-6 py-3 font-medium transition-all border-b-2 -mb-px ${
                activeTab === tab.id
                  ? 'text-blue-400 border-blue-400'
                  : 'text-slate-400 border-transparent hover:text-white'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl overflow-hidden">
          {/* Summary Tab */}
          {activeTab === 'summary' && summary && (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-slate-900/50">
                  <tr>
                    <th className="text-left px-6 py-4 text-slate-400 font-medium">Sinyal Türü</th>
                    <th className="text-center px-4 py-4 text-slate-400 font-medium">Toplam</th>
                    <th className="text-center px-4 py-4 text-slate-400 font-medium">+1 Gün</th>
                    <th className="text-center px-4 py-4 text-slate-400 font-medium">+3 Gün</th>
                    <th className="text-center px-4 py-4 text-slate-400 font-medium">+7 Gün</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-700">
                  {summary.by_signal_type.map((item) => (
                    <tr key={item.signal_type} className="hover:bg-slate-700/30 transition-colors">
                      <td className="px-6 py-4">
                        <span className="font-medium text-white">{item.signal_type}</span>
                      </td>
                      <td className="text-center px-4 py-4 text-slate-300">
                        {item.total_signals}
                      </td>
                      <td className="text-center px-4 py-4">
                        <div className="flex flex-col items-center">
                          {formatGain(item.performance['1d'].avg_gain)}
                          <span className="text-xs text-slate-500">
                            WR: {formatWinRate(item.performance['1d'].win_rate)}
                          </span>
                        </div>
                      </td>
                      <td className="text-center px-4 py-4">
                        <div className="flex flex-col items-center">
                          {formatGain(item.performance['3d'].avg_gain)}
                          <span className="text-xs text-slate-500">
                            WR: {formatWinRate(item.performance['3d'].win_rate)}
                          </span>
                        </div>
                      </td>
                      <td className="text-center px-4 py-4">
                        <div className="flex flex-col items-center">
                          {formatGain(item.performance['7d'].avg_gain)}
                          <span className="text-xs text-slate-500">
                            WR: {formatWinRate(item.performance['7d'].win_rate)}
                          </span>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              
              {summary.by_signal_type.length === 0 && (
                <div className="text-center py-12 text-slate-400">
                  <p>Bu dönemde sinyal bulunamadı.</p>
                  <p className="text-sm mt-2">Tarama yaparak sinyal oluşturun.</p>
                </div>
              )}
            </div>
          )}

          {/* Top Performers Tab */}
          {activeTab === 'top' && topPerformers && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 p-6">
              {/* Top Gainers */}
              <div>
                <h3 className="text-lg font-semibold text-green-400 mb-4 flex items-center gap-2">
                  🚀 En Çok Kazandıranlar (+{period.replace('d', ' Gün')})
                </h3>
                <div className="space-y-2">
                  {topPerformers.top_gainers.map((item, index) => (
                    <div
                      key={item.id}
                      className="flex items-center justify-between bg-slate-900/50 rounded-lg px-4 py-3"
                    >
                      <div className="flex items-center gap-3">
                        <span className="text-slate-500 font-mono w-6">{index + 1}.</span>
                        <div>
                          <span className="font-medium text-white">{item.symbol}</span>
                          <span className="text-xs text-slate-500 ml-2">{item.signal_type}</span>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-green-400 font-bold">
                          +{item.gain?.toFixed(2)}%
                        </div>
                        <div className="text-xs text-slate-500">
                          {item.signal_date}
                        </div>
                      </div>
                    </div>
                  ))}
                  {topPerformers.top_gainers.length === 0 && (
                    <p className="text-slate-400 text-center py-4">Veri bulunamadı</p>
                  )}
                </div>
              </div>

              {/* Top Losers */}
              <div>
                <h3 className="text-lg font-semibold text-red-400 mb-4 flex items-center gap-2">
                  📉 En Çok Kaybedenler (+{period.replace('d', ' Gün')})
                </h3>
                <div className="space-y-2">
                  {topPerformers.top_losers.map((item, index) => (
                    <div
                      key={item.id}
                      className="flex items-center justify-between bg-slate-900/50 rounded-lg px-4 py-3"
                    >
                      <div className="flex items-center gap-3">
                        <span className="text-slate-500 font-mono w-6">{index + 1}.</span>
                        <div>
                          <span className="font-medium text-white">{item.symbol}</span>
                          <span className="text-xs text-slate-500 ml-2">{item.signal_type}</span>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-red-400 font-bold">
                          {item.gain?.toFixed(2)}%
                        </div>
                        <div className="text-xs text-slate-500">
                          {item.signal_date}
                        </div>
                      </div>
                    </div>
                  ))}
                  {topPerformers.top_losers.length === 0 && (
                    <p className="text-slate-400 text-center py-4">Veri bulunamadı</p>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Symbols Tab */}
          {activeTab === 'symbols' && (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-slate-900/50">
                  <tr>
                    <th className="text-left px-6 py-4 text-slate-400 font-medium">Hisse</th>
                    <th className="text-center px-4 py-4 text-slate-400 font-medium">Sinyal Sayısı</th>
                    <th className="text-left px-4 py-4 text-slate-400 font-medium">Sinyal Türleri</th>
                    <th className="text-center px-4 py-4 text-slate-400 font-medium">Ort. Kazanç (+7G)</th>
                    <th className="text-center px-4 py-4 text-slate-400 font-medium">Kazanma Oranı</th>
                    <th className="text-center px-4 py-4 text-slate-400 font-medium">En İyi</th>
                    <th className="text-center px-4 py-4 text-slate-400 font-medium">En Kötü</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-700">
                  {symbolPerformance.map((item) => (
                    <tr key={item.symbol} className="hover:bg-slate-700/30 transition-colors">
                      <td className="px-6 py-4">
                        <span className="font-medium text-white">{item.symbol}</span>
                      </td>
                      <td className="text-center px-4 py-4 text-slate-300">
                        {item.total_signals}
                      </td>
                      <td className="px-4 py-4">
                        <div className="flex flex-wrap gap-1">
                          {item.signal_types.slice(0, 3).map((type) => (
                            <span
                              key={type}
                              className="text-xs bg-slate-700 text-slate-300 px-2 py-1 rounded"
                            >
                              {type}
                            </span>
                          ))}
                          {item.signal_types.length > 3 && (
                            <span className="text-xs text-slate-500">
                              +{item.signal_types.length - 3}
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="text-center px-4 py-4">
                        {formatGain(item.avg_gain_7d)}
                      </td>
                      <td className="text-center px-4 py-4">
                        {formatWinRate(item.win_rate_7d)}
                      </td>
                      <td className="text-center px-4 py-4">
                        {formatGain(item.best_gain)}
                      </td>
                      <td className="text-center px-4 py-4">
                        {formatGain(item.worst_gain)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              
              {symbolPerformance.length === 0 && (
                <div className="text-center py-12 text-slate-400">
                  <p>Bu dönemde sinyal bulunamadı.</p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Info Note */}
        <div className="mt-8 bg-blue-900/20 border border-blue-500/30 rounded-xl p-6">
          <h3 className="text-blue-400 font-medium mb-2">📌 Performans Takibi Hakkında</h3>
          <ul className="text-slate-400 text-sm space-y-1">
            <li>• <strong>+1G, +3G, +7G:</strong> Sinyalden 1, 3 ve 7 gün sonraki fiyat değişimi</li>
            <li>• <strong>WR (Win Rate):</strong> Kazanan sinyallerin oranı (fiyat artışı = kazanç)</li>
            <li>• <strong>Ortalama Kazanç:</strong> Tüm sinyallerin ortalama getirisi</li>
            <li>• Performans verileri günlük olarak güncellenir (19:00 sonrası)</li>
            <li>• Yeni sinyallerin performansı 1-7 gün sonra görünür hale gelir</li>
          </ul>
        </div>
      </main>
    </div>
  );
}

