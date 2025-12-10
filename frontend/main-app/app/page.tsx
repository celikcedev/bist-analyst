'use client';

import { useEffect, useState } from 'react';
import { api, type Signal, type Stats } from '@/lib/api';
import { formatDistanceToNow, format } from 'date-fns';
import { tr } from 'date-fns/locale';

export default function Home() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [signals, setSignals] = useState<Signal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const [statsData, signalsData] = await Promise.all([
          api.getStats(),
          api.getSignals({ limit: 10 }),
        ]);
        setStats(statsData);
        setSignals(signalsData.signals);
      } catch (err: any) {
        setError(err.message || 'Veri yüklenirken hata oluştu');
        console.error('Error fetching data:', err);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
    
    // Auto-refresh every 5 minutes
    const interval = setInterval(fetchData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
        <div className="text-center">
          <div className="relative w-24 h-24 mx-auto mb-6">
            <div className="absolute inset-0 rounded-full animate-spin" style={{
              background: 'conic-gradient(from 0deg, transparent 0deg, #3B82F6 90deg, #8B5CF6 180deg, #EC4899 270deg, transparent 360deg)',
              WebkitMaskImage: 'radial-gradient(circle, transparent 42px, black 42px)',
              maskImage: 'radial-gradient(circle, transparent 42px, black 42px)'
            }}></div>
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-10 h-10 rounded-full bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 animate-pulse"></div>
            </div>
          </div>
          <p className="text-white text-xl font-semibold">Yükleniyor...</p>
          <p className="text-blue-300 text-sm mt-2">Piyasa verileri hazırlanıyor</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
        <div className="bg-red-900/20 border-2 border-red-500/50 rounded-2xl p-8 max-w-md backdrop-blur-sm">
          <div className="text-center">
            <div className="text-6xl mb-4">⚠️</div>
            <h3 className="text-red-400 font-bold text-xl mb-3">Bağlantı Hatası</h3>
            <p className="text-red-300">{error}</p>
            <p className="text-sm text-red-400 mt-4">Backend API'nin çalıştığından emin olun</p>
            <p className="text-xs text-gray-400 mt-2 font-mono">http://localhost:5001</p>
            <button 
              onClick={() => window.location.reload()} 
              className="mt-6 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl font-semibold hover:shadow-lg transition-all"
            >
              Tekrar Dene
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      {/* Header */}
      <header className="border-b border-blue-500/20 backdrop-blur-xl bg-slate-900/50 shadow-2xl sticky top-0 z-50">
        <div className="container mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="relative w-14 h-14 rounded-2xl bg-gradient-to-br from-blue-600 via-purple-600 to-pink-600 flex items-center justify-center shadow-2xl">
                <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M3 17l3-3 4 4 6-6 5 5" stroke="white" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M21 7v5h-5" stroke="white" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
                <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-500 rounded-full border-2 border-slate-900 animate-pulse shadow-lg shadow-green-500/50"></div>
              </div>
              <div>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                  BIST Analyst
                </h1>
                <p className="text-blue-300 text-sm font-medium">Modular Architecture Platform</p>
              </div>
            </div>
            <div className="flex gap-4">
              <a
                href="http://localhost:3001"
                className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl hover:shadow-2xl hover:shadow-blue-500/50 transition-all font-bold flex items-center gap-2"
              >
                <span>Screener'ı Aç</span>
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M5 12h14"></path>
                  <path d="m12 5 7 7-7 7"></path>
                </svg>
              </a>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600/10 via-purple-600/10 to-pink-600/10"></div>
        <div className="container mx-auto px-6 py-16 relative">
          <div className="text-center max-w-4xl mx-auto">
            <h2 className="text-5xl md:text-6xl font-bold mb-6">
              <span className="bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                Python-Powered
              </span>
              <br />
              <span className="text-white">Trading Signal Platform</span>
            </h2>
            <p className="text-xl text-blue-200 mb-8 leading-relaxed">
              TradingView Pine Script XTUMY V27 stratejisinin %100 uyumlu Python implementasyonu. 
              7 farklı sinyal türü ile BIST hisselerini otomatik olarak tarayan modüler platform.
            </p>
            <div className="flex gap-4 justify-center">
              <a
                href="http://localhost:3001"
                className="px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-2xl hover:shadow-2xl hover:shadow-blue-500/50 transition-all font-bold text-lg"
              >
                Taramayı Başlat →
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-12">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
          <div className="bg-slate-800/50 backdrop-blur-sm border border-blue-500/20 rounded-2xl p-6 hover:border-blue-500/40 transition-all shadow-xl">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
                  <path d="M3 3v18h18"></path>
                  <path d="m19 9-5 5-4-4-3 3"></path>
                </svg>
              </div>
              <p className="text-blue-300 text-sm font-medium">Toplam Hisse</p>
            </div>
            <p className="text-4xl font-bold text-white">{stats?.tickers_count || 0}</p>
            <p className="text-green-400 text-xs mt-2">BIST TÜM</p>
          </div>
          
          <div className="bg-slate-800/50 backdrop-blur-sm border border-green-500/20 rounded-2xl p-6 hover:border-green-500/40 transition-all shadow-xl">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-green-500 to-green-600 flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
                  <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
                </svg>
              </div>
              <p className="text-green-300 text-sm font-medium">Aktif Hisse</p>
            </div>
            <p className="text-4xl font-bold text-white">{stats?.active_tickers || 0}</p>
            <p className="text-green-400 text-xs mt-2">Güncel veri ile</p>
          </div>
          
          <div className="bg-slate-800/50 backdrop-blur-sm border border-purple-500/20 rounded-2xl p-6 hover:border-purple-500/40 transition-all shadow-xl">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-purple-600 flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
                  <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
                  <polyline points="7.5 4.21 12 6.81 16.5 4.21"></polyline>
                  <polyline points="7.5 19.79 7.5 14.6 3 12"></polyline>
                  <polyline points="21 12 16.5 14.6 16.5 19.79"></polyline>
                  <polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
                  <line x1="12" y1="22.08" x2="12" y2="12"></line>
                </svg>
              </div>
              <p className="text-purple-300 text-sm font-medium">Veri Noktası</p>
            </div>
            <p className="text-4xl font-bold text-white">
              {stats?.data_points ? (stats.data_points / 1000).toFixed(0) + 'K' : '0'}
            </p>
            <p className="text-purple-400 text-xs mt-2">OHLCV bars</p>
          </div>
          
          <div className="bg-slate-800/50 backdrop-blur-sm border border-pink-500/20 rounded-2xl p-6 hover:border-pink-500/40 transition-all shadow-xl">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-pink-500 to-pink-600 flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
                  <circle cx="12" cy="12" r="10"></circle>
                  <polyline points="12 6 12 12 16 14"></polyline>
                </svg>
              </div>
              <p className="text-pink-300 text-sm font-medium">Son Güncelleme</p>
            </div>
            <p className="text-2xl font-bold text-white">
              {stats?.latest_data_date ? format(new Date(stats.latest_data_date), 'dd MMM', { locale: tr }) : 'N/A'}
            </p>
            <p className="text-pink-400 text-xs mt-2">Market data</p>
          </div>
        </div>

        {/* Recent Signals */}
        <div className="bg-slate-800/50 backdrop-blur-sm border border-blue-500/20 rounded-2xl shadow-2xl overflow-hidden">
          <div className="p-6 border-b border-blue-500/20 bg-gradient-to-r from-blue-900/30 to-purple-900/30">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-white flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
                      <path d="M22 12h-4l-3 9L9 3l-3 9H2"></path>
                    </svg>
                  </div>
                  Son Sinyaller
                </h2>
                <p className="text-blue-300 mt-1">En son tespit edilen alım sinyalleri</p>
              </div>
              <div className="text-right">
                <p className="text-3xl font-bold text-white">{signals.length}</p>
                <p className="text-xs text-blue-300">Aktif sinyal</p>
              </div>
            </div>
          </div>

          {signals.length === 0 ? (
            <div className="p-16 text-center">
              <div className="text-6xl mb-4">📊</div>
              <p className="text-xl text-gray-300">Henüz sinyal bulunamadı</p>
              <p className="text-sm text-gray-400 mt-2">Screener'da tarama çalıştırarak sinyal oluşturabilirsiniz</p>
              <a
                href="http://localhost:3001"
                className="inline-block mt-6 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl font-semibold hover:shadow-lg transition-all"
              >
                Screener'a Git →
              </a>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-slate-900/50 border-b border-blue-500/10">
                  <tr>
                    <th className="px-6 py-4 text-left text-xs font-bold text-blue-300 uppercase tracking-wider">
                      Hisse
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-bold text-blue-300 uppercase tracking-wider">
                      Sinyal Türü
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-bold text-blue-300 uppercase tracking-wider">
                      Fiyat
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-bold text-blue-300 uppercase tracking-wider">
                      RSI
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-bold text-blue-300 uppercase tracking-wider">
                      ADX
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-bold text-blue-300 uppercase tracking-wider">
                      Tarih
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-700/50">
                  {signals.map((signal, idx) => (
                    <tr key={signal.id} className="hover:bg-slate-700/30 transition-all group">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="font-bold text-white text-lg group-hover:text-blue-400 transition-colors">
                          {signal.symbol}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-3 py-1.5 inline-flex text-xs font-bold rounded-lg ${
                          signal.signal_type === 'ALTIN KIRILIM' ? 'bg-yellow-500/20 text-yellow-300 border border-yellow-500/30' :
                          signal.signal_type === 'ZİRVE KIRILIMI' ? 'bg-orange-500/20 text-orange-300 border border-orange-500/30' :
                          signal.signal_type === 'TREND BAŞLANGIÇ' ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30' :
                          signal.signal_type === 'PULLBACK AL' ? 'bg-blue-500/20 text-blue-300 border border-blue-500/30' :
                          signal.signal_type === 'DİRENÇ REDDİ' ? 'bg-red-500/20 text-red-300 border border-red-500/30' :
                          signal.signal_type === 'KURUMSAL DİP' ? 'bg-gray-500/20 text-gray-300 border border-gray-500/30' :
                          'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
                        }`}>
                          {signal.signal_type}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-white font-semibold">₺{signal.price.toFixed(2)}</span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`font-medium ${
                          (signal.rsi || 0) > 70 ? 'text-red-400' :
                          (signal.rsi || 0) > 50 ? 'text-green-400' :
                          'text-yellow-400'
                        }`}>
                          {signal.rsi?.toFixed(1) || '-'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`font-medium ${
                          (signal.adx || 0) > 25 ? 'text-green-400' :
                          (signal.adx || 0) > 20 ? 'text-yellow-400' :
                          'text-red-400'
                        }`}>
                          {signal.adx?.toFixed(1) || '-'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                        {signal.signal_date}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          <div className="p-6 border-t border-blue-500/10 bg-slate-900/50">
            <a
              href="http://localhost:3001"
              className="text-blue-400 hover:text-blue-300 font-bold flex items-center gap-2 group"
            >
              <span>Tüm sinyalleri görüntüle</span>
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="group-hover:translate-x-1 transition-transform">
                <path d="M5 12h14"></path>
                <path d="m12 5 7 7-7 7"></path>
              </svg>
            </a>
          </div>
        </div>

        {/* Features */}
        <div className="mt-16">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-white mb-4">Platform Özellikleri</h2>
            <p className="text-blue-300 text-lg">Modüler mimari ile gelişmiş trading analizi</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-slate-800/50 backdrop-blur-sm border border-blue-500/20 rounded-2xl p-8 hover:border-blue-500/40 transition-all shadow-xl group">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-yellow-500 to-orange-500 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform shadow-lg shadow-yellow-500/30">
                <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
                  <path d="M22 12h-4l-3 9L9 3l-3 9H2"></path>
                </svg>
              </div>
              <h3 className="text-xl font-bold text-white mb-3">7 Sinyal Türü</h3>
              <p className="text-blue-200 text-sm leading-relaxed mb-4">
                KURUMSAL DİP, TREND BAŞLANGIÇ, PULLBACK AL, DİP AL, ALTIN KIRILIM, ZİRVE KIRILIMI, DİRENÇ REDDİ
              </p>
              <div className="flex items-center gap-2 text-xs text-yellow-400 font-semibold">
                <span className="w-2 h-2 rounded-full bg-yellow-400 animate-pulse"></span>
                <span>Multi-signal detection</span>
              </div>
            </div>
            
            <div className="bg-slate-800/50 backdrop-blur-sm border border-purple-500/20 rounded-2xl p-8 hover:border-purple-500/40 transition-all shadow-xl group">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform shadow-lg shadow-purple-500/30">
                <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
                  <polyline points="22 7 13.5 15.5 8.5 10.5 2 17"></polyline>
                  <polyline points="16 7 22 7 22 13"></polyline>
                </svg>
              </div>
              <h3 className="text-xl font-bold text-white mb-3">%100 Pine Script Uyumlu</h3>
              <p className="text-blue-200 text-sm leading-relaxed mb-4">
                TradingView Pine Script XTUMY V27 stratejisi ile matematiksel olarak tam uyumlu. Her sinyal tipi bire bir eşleşir.
              </p>
              <div className="flex items-center gap-2 text-xs text-purple-400 font-semibold">
                <span className="w-2 h-2 rounded-full bg-purple-400 animate-pulse"></span>
                <span>Verified accuracy</span>
              </div>
            </div>
            
            <div className="bg-slate-800/50 backdrop-blur-sm border border-green-500/20 rounded-2xl p-8 hover:border-green-500/40 transition-all shadow-xl group">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-green-500 to-emerald-500 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform shadow-lg shadow-green-500/30">
                <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
                  <path d="M12 2v20"></path>
                  <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
                </svg>
              </div>
              <h3 className="text-xl font-bold text-white mb-3">Modüler Mimari</h3>
              <p className="text-blue-200 text-sm leading-relaxed mb-4">
                Pydantic base classes, Strategy Registry, SQLAlchemy ORM. Yeni strateji eklemek sadece 1-2 saat.
              </p>
              <div className="flex items-center gap-2 text-xs text-green-400 font-semibold">
                <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></span>
                <span>Scalable architecture</span>
              </div>
            </div>
          </div>
        </div>

        {/* Tech Stack */}
        <div className="mt-16 bg-slate-800/30 backdrop-blur-sm border border-blue-500/10 rounded-2xl p-8">
          <h3 className="text-2xl font-bold text-white mb-6 text-center">Technology Stack</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
            <div>
              <div className="text-3xl mb-2">🐍</div>
              <p className="text-white font-bold">Python</p>
              <p className="text-xs text-gray-400">Backend Logic</p>
            </div>
            <div>
              <div className="text-3xl mb-2">⚡</div>
              <p className="text-white font-bold">Flask</p>
              <p className="text-xs text-gray-400">REST API</p>
            </div>
            <div>
              <div className="text-3xl mb-2">⚛️</div>
              <p className="text-white font-bold">Next.js</p>
              <p className="text-xs text-gray-400">Frontend</p>
            </div>
            <div>
              <div className="text-3xl mb-2">🗄️</div>
              <p className="text-white font-bold">PostgreSQL</p>
              <p className="text-xs text-gray-400">Database</p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-20 border-t border-blue-500/20 bg-slate-900/50 backdrop-blur-sm">
        <div className="container mx-auto px-6 py-8">
          <div className="text-center">
            <p className="text-white font-bold text-lg mb-2">BIST Analyst Platform</p>
            <p className="text-blue-300 text-sm mb-4">
              v1.0.0 - Modular Architecture | Sprint 0-3 Completed
            </p>
            <div className="flex items-center justify-center gap-4 text-xs text-gray-400">
              <span>Flask + SQLAlchemy + Pydantic</span>
              <span>•</span>
              <span>Next.js 16 + TypeScript</span>
              <span>•</span>
              <span>PostgreSQL</span>
            </div>
            <div className="mt-4 text-xs text-gray-500">
              <p>© 2024 BIST Analyst - %100 Pine Script Compatible</p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
