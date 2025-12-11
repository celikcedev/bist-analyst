'use client';

import { Signal, exportSignalsToCSV } from '@/lib/api';
import { ArrowUpDown, ArrowUp, ArrowDown, TrendingUp, Activity, Download, BarChart3 } from 'lucide-react';
import { useState } from 'react';
import ChartModal from './ChartModal';

interface SignalTableProps {
  signals: Signal[];
  loading: boolean;
}

type SortField = 'symbol' | 'price' | 'rsi' | 'adx' | 'signal_date';
type SortDirection = 'asc' | 'desc';

export default function SignalTable({ signals, loading }: SignalTableProps) {
  const [sortField, setSortField] = useState<SortField>('signal_date');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');
  const [chartModalOpen, setChartModalOpen] = useState(false);
  const [selectedSymbol, setSelectedSymbol] = useState<string>('');

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-[9999]">
        <div className="flex flex-col items-center gap-6 bg-tv-dark-card p-12 rounded-3xl border-2 border-tv-dark-border shadow-2xl shadow-tv-dark-primary/30">
          <div className="relative w-24 h-24">
            {/* Outer ring */}
            <div className="absolute inset-0 border-4 border-tv-dark-border rounded-full"></div>
            
            {/* Spinning gradient ring */}
            <div className="absolute inset-0 rounded-full animate-spin" style={{
              background: 'conic-gradient(from 0deg, transparent 0deg, #3B82F6 90deg, #8B5CF6 180deg, #EC4899 270deg, transparent 360deg)',
              WebkitMaskImage: 'radial-gradient(circle, transparent 36px, black 36px)',
              maskImage: 'radial-gradient(circle, transparent 36px, black 36px)'
            }}></div>
            
            {/* Inner pulsing dot */}
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-8 h-8 rounded-full bg-gradient-to-r from-tv-dark-primary via-tv-dark-secondary to-tv-dark-danger animate-pulse"></div>
            </div>
          </div>
          
          <div className="text-center">
            <div className="text-tv-dark-text font-bold text-2xl mb-2">Piyasa Taranıyor</div>
            <div className="text-tv-dark-textMuted text-base">Sinyaller analiz ediliyor...</div>
          </div>
        </div>
      </div>
    );
  }

  if (signals.length === 0) {
    return (
      <div className="relative flex flex-col items-center justify-center py-32 bg-tv-dark-surface rounded-lg border border-tv-dark-border z-0">
        <div className="w-16 h-16 rounded-full bg-tv-dark-border flex items-center justify-center mb-4">
          <TrendingUp className="w-8 h-8 text-tv-dark-textMuted" />
        </div>
        <div className="text-tv-dark-text text-lg font-semibold mb-2">Sinyal Bulunamadı</div>
        <div className="text-tv-dark-textMuted text-sm text-center max-w-md">
          Seçili filtrelere göre sinyal tespit edilemedi. Filtre ayarlarını değiştirip tekrar deneyin.
        </div>
      </div>
    );
  }

  // Sorting logic
  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  const sortedSignals = [...signals].sort((a, b) => {
    let aVal: any = a[sortField];
    let bVal: any = b[sortField];
    
    if (sortField === 'signal_date') {
      aVal = new Date(aVal).getTime();
      bVal = new Date(bVal).getTime();
    }
    
    if (aVal < bVal) return sortDirection === 'asc' ? -1 : 1;
    if (aVal > bVal) return sortDirection === 'asc' ? 1 : -1;
    return 0;
  });

  // Signal type color mapping
  const getSignalColor = (signalType: string) => {
    const colorMap: Record<string, string> = {
      'TREND BAŞLANGIÇ': 'bg-blue-500/20 text-blue-400 border-blue-500/30',
      'PULLBACK AL': 'bg-green-500/20 text-green-400 border-green-500/30',
      'DİP AL': 'bg-purple-500/20 text-purple-400 border-purple-500/30',
      'ALTIN KIRILIM': 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
      'ZİRVE KIRILIMI': 'bg-pink-500/20 text-pink-400 border-pink-500/30',
      'KURUMSAL DİP': 'bg-indigo-500/20 text-indigo-400 border-indigo-500/30',
    };
    return colorMap[signalType] || 'bg-gray-500/20 text-gray-400 border-gray-500/30';
  };

  // RSI strength indicator
  const getRSIStrength = (rsi: number | null) => {
    if (!rsi) return { label: '-', color: 'text-tv-dark-textMuted' };
    if (rsi < 30) return { label: 'Güçlü', color: 'text-green-400' };
    if (rsi < 50) return { label: 'İyi', color: 'text-green-400' };
    if (rsi < 70) return { label: 'Normal', color: 'text-yellow-400' };
    return { label: 'Yüksek', color: 'text-red-400' };
  };

  // ADX trend strength
  const getADXStrength = (adx: number | null) => {
    if (!adx) return { label: '-', color: 'text-tv-dark-textMuted' };
    if (adx < 20) return { label: 'Zayıf', color: 'text-red-400' };
    if (adx < 40) return { label: 'Güçlü', color: 'text-yellow-400' };
    return { label: 'Çok Güçlü', color: 'text-green-400' };
  };

  const SortButton = ({ field, children }: { field: SortField; children: React.ReactNode }) => (
    <button
      onClick={() => handleSort(field)}
      className="flex items-center gap-1.5 text-xs font-semibold text-tv-dark-textMuted hover:text-tv-dark-text transition-colors uppercase tracking-wider"
    >
      {children}
      {sortField === field ? (
        sortDirection === 'asc' ? (
          <ArrowUp className="w-3.5 h-3.5" />
        ) : (
          <ArrowDown className="w-3.5 h-3.5" />
        )
      ) : (
        <ArrowUpDown className="w-3.5 h-3.5 opacity-30" />
      )}
    </button>
  );

  const handleExportCSV = () => {
    const filename = `bist-signals-${new Date().toISOString().split('T')[0]}.csv`;
    exportSignalsToCSV(signals, filename);
  };

  return (
    <div className="bg-tv-dark-card rounded-2xl border border-tv-dark-border/50 overflow-hidden shadow-xl">
      {/* Actions Bar */}
      <div className="px-6 py-3 border-b border-tv-dark-border/50 bg-gradient-card/30 flex items-center justify-between">
        <div className="text-tv-dark-text font-semibold">
          {signals.length} Sinyal
        </div>
        <button
          onClick={handleExportCSV}
          className="flex items-center gap-2 px-3 py-1.5 bg-tv-dark-primary hover:bg-tv-dark-primary/80 text-white rounded-lg transition-colors text-sm font-medium"
        >
          <Download className="w-4 h-4" />
          <span>CSV İndir</span>
        </button>
      </div>
      
      {/* Table Header */}
      <div className="grid grid-cols-12 gap-4 px-6 py-4 border-b border-tv-dark-border/50 bg-gradient-card/30">
        <div className="col-span-3">
          <SortButton field="symbol">Sembol</SortButton>
        </div>
        <div className="col-span-2">
          <span className="text-xs font-semibold text-tv-dark-textMuted uppercase tracking-wider">Sinyal Türü</span>
        </div>
        <div className="col-span-2 text-right">
          <SortButton field="price">Fiyat</SortButton>
        </div>
        <div className="col-span-2 text-center">
          <SortButton field="rsi">RSI</SortButton>
        </div>
        <div className="col-span-2 text-center">
          <SortButton field="adx">ADX</SortButton>
        </div>
        <div className="col-span-1 text-right">
          <SortButton field="signal_date">Tarih</SortButton>
        </div>
      </div>

      {/* Table Body */}
      <div className="divide-y divide-tv-dark-border max-h-[600px] overflow-y-auto">
        {sortedSignals.map((signal, index) => {
          const rsiStrength = getRSIStrength(signal.rsi);
          const adxStrength = getADXStrength(signal.adx);
          
          return (
            <div
              key={`${signal.symbol}-${signal.signal_type}-${index}`}
              className="grid grid-cols-12 gap-4 px-6 py-4 hover:bg-tv-dark-border/50 transition-all cursor-pointer group"
            >
              {/* Symbol */}
              <div className="col-span-3 flex items-center gap-3">
                <div className="relative w-11 h-11 rounded-xl bg-gradient-primary flex items-center justify-center shadow-md group-hover:shadow-glow-sm transition-all">
                  <span className="text-sm font-bold text-white">{signal.symbol.charAt(0)}</span>
                  <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-gradient-success rounded-full border-2 border-tv-dark-bg"></div>
                </div>
                <div className="flex-1">
                  <div className="text-sm font-bold text-tv-dark-text group-hover:text-tv-dark-primary transition-colors">
                    {signal.symbol}
                  </div>
                  <div className="text-xs text-tv-dark-textMuted font-medium">BIST</div>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setSelectedSymbol(signal.symbol);
                    setChartModalOpen(true);
                  }}
                  className="opacity-0 group-hover:opacity-100 p-2 hover:bg-tv-dark-primary/20 rounded-lg transition-all"
                  title="Grafiği Görüntüle"
                >
                  <BarChart3 className="w-4 h-4 text-tv-dark-primary" />
                </button>
              </div>

              {/* Signal Type */}
              <div className="col-span-2 flex items-center">
                <span className={`text-xs font-medium px-2.5 py-1 rounded-md border ${getSignalColor(signal.signal_type)}`}>
                  {signal.signal_type}
                </span>
              </div>

              {/* Price */}
              <div className="col-span-2 flex items-center justify-end">
                <div className="text-right">
                  <div className="text-sm font-semibold text-tv-dark-text">₺{signal.price.toFixed(2)}</div>
                  <div className="text-xs text-tv-dark-textMuted">TRY</div>
                </div>
              </div>

              {/* RSI */}
              <div className="col-span-2 flex items-center justify-center">
                {signal.rsi ? (
                  <div className="text-center">
                    <div className="text-sm font-semibold text-tv-dark-text">{signal.rsi.toFixed(1)}</div>
                    <div className={`text-xs ${rsiStrength.color}`}>{rsiStrength.label}</div>
                  </div>
                ) : (
                  <span className="text-sm text-tv-dark-textMuted">-</span>
                )}
              </div>

              {/* ADX */}
              <div className="col-span-2 flex items-center justify-center">
                {signal.adx ? (
                  <div className="text-center">
                    <div className="text-sm font-semibold text-tv-dark-text">{signal.adx.toFixed(1)}</div>
                    <div className={`text-xs ${adxStrength.color}`}>{adxStrength.label}</div>
                  </div>
                ) : (
                  <span className="text-sm text-tv-dark-textMuted">-</span>
                )}
              </div>

              {/* Date */}
              <div className="col-span-1 flex items-center justify-end">
                <div className="text-xs text-tv-dark-textMuted text-right">
                  {new Date(signal.signal_date).toLocaleDateString('tr-TR', { 
                    day: '2-digit', 
                    month: '2-digit' 
                  })}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Footer */}
      <div className="px-6 py-4 border-t border-tv-dark-border/50 bg-gradient-card/20">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-tv-dark-primary/10 rounded-lg">
              <Activity className="w-4 h-4 text-tv-dark-primary" />
            </div>
            <div>
              <div className="text-sm font-bold text-tv-dark-text">{signals.length} Sinyal Tespit Edildi</div>
              <div className="text-xs text-tv-dark-textMuted">Son tarama: {new Date().toLocaleTimeString('tr-TR')}</div>
            </div>
          </div>
          <div className="text-right">
            <div className="text-xs text-tv-dark-textMuted">Son Güncelleme</div>
            <div className="text-sm font-semibold text-tv-dark-text">
              {new Date().toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' })}
            </div>
          </div>
        </div>
      </div>

      {/* Chart Modal */}
      <ChartModal
        isOpen={chartModalOpen}
        onClose={() => setChartModalOpen(false)}
        symbol={selectedSymbol}
      />
    </div>
  );
}
