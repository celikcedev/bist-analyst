'use client';

import { useEffect, useState } from 'react';
import { api, type Signal, type Stats } from '@/lib/api';
import { formatDistanceToNow } from 'date-fns';
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
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Yükleniyor...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md">
          <h3 className="text-red-800 font-semibold mb-2">Hata</h3>
          <p className="text-red-600">{error}</p>
          <p className="text-sm text-red-500 mt-2">Backend API'nin çalıştığından emin olun (port 5000)</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">🚀 BIST Analyst</h1>
              <p className="text-gray-600 mt-1">Otonom Trading Sinyal Tarayıcı</p>
            </div>
            <div className="flex gap-4">
              <a
                href="http://localhost:3001"
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
              >
                Screener →
              </a>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-gray-600 text-sm mb-1">Toplam Hisse</p>
            <p className="text-3xl font-bold text-gray-900">{stats?.tickers_count || 0}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-gray-600 text-sm mb-1">Aktif Hisse</p>
            <p className="text-3xl font-bold text-green-600">{stats?.active_tickers || 0}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-gray-600 text-sm mb-1">Veri Noktası</p>
            <p className="text-3xl font-bold text-blue-600">
              {stats?.data_points ? (stats.data_points / 1000).toFixed(0) + 'K' : '0'}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-gray-600 text-sm mb-1">Son Güncelleme</p>
            <p className="text-xl font-semibold text-gray-900">
              {stats?.latest_data_date || 'N/A'}
            </p>
          </div>
        </div>

        {/* Recent Signals */}
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-2xl font-bold text-gray-900">Son Sinyaller</h2>
            <p className="text-gray-600 mt-1">En son tespit edilen alım sinyalleri</p>
          </div>

          {signals.length === 0 ? (
            <div className="p-12 text-center text-gray-500">
              <p className="text-lg">Henüz sinyal bulunamadı</p>
              <p className="text-sm mt-2">Tarama çalıştırarak sinyal oluşturabilirsiniz</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Hisse
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Sinyal Türü
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Fiyat
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      RSI
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      ADX
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Tarih
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {signals.map((signal) => (
                    <tr key={signal.id} className="hover:bg-gray-50 transition">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="font-bold text-gray-900">{signal.symbol}</span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                          {signal.signal_type}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-gray-900">
                        {signal.price.toFixed(2)} TL
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-gray-600">
                        {signal.rsi?.toFixed(1) || '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-gray-600">
                        {signal.adx?.toFixed(1) || '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {signal.signal_date}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          <div className="p-4 border-t border-gray-200 bg-gray-50">
            <a
              href="http://localhost:3001"
              className="text-blue-600 hover:text-blue-800 font-medium"
            >
              Tüm sinyalleri görüntüle →
            </a>
          </div>
        </div>

        {/* Features */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-3xl mb-4">📊</div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">6 Sinyal Türü</h3>
            <p className="text-gray-600 text-sm">
              KURUMSAL DİP, TREND BAŞLANGIÇ, PULLBACK AL, DİP AL, ALTIN KIRILIM, ZİRVE KIRILIMI
            </p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-3xl mb-4">🎯</div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">%100 Uyumlu</h3>
            <p className="text-gray-600 text-sm">
              TradingView Pine Script XTUMY V27 stratejisi ile matematiksel olarak eşdeğer
            </p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-3xl mb-4">⚡</div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Otomatik Tarama</h3>
            <p className="text-gray-600 text-sm">
              Günde 2 kez otomatik tarama (13:10 ve 18:40) ve Telegram bildirimleri
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-16 border-t border-gray-200 bg-white">
        <div className="container mx-auto px-4 py-6">
          <div className="text-center text-gray-600 text-sm">
            <p>BIST Analyst v1.0 - Modular Architecture</p>
            <p className="mt-1">Backend: Flask + SQLAlchemy + Pydantic | Frontend: Next.js 14 + TypeScript</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
