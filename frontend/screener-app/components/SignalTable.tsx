'use client';

import { Signal } from '@/lib/api';
import { ArrowUpDown } from 'lucide-react';

interface SignalTableProps {
  signals: Signal[];
  loading: boolean;
}

export default function SignalTable({ signals, loading }: SignalTableProps) {
  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="text-tv-dark-textMuted">Taranıyor...</div>
      </div>
    );
  }

  if (signals.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <div className="text-tv-dark-text text-lg mb-2">Henüz sinyal bulunamadı</div>
        <div className="text-tv-dark-textMuted text-sm">
          Tarama çalıştırarak sinyal oluşturabilirsiniz
        </div>
      </div>
    );
  }

  // Generate simple logo placeholder based on first letter
  const getLogoColor = (symbol: string) => {
    const colors = [
      'bg-red-500',
      'bg-blue-500',
      'bg-green-500',
      'bg-yellow-500',
      'bg-purple-500',
      'bg-pink-500',
      'bg-indigo-500',
    ];
    const index = symbol.charCodeAt(0) % colors.length;
    return colors[index];
  };

  return (
    <div className="bg-tv-dark-surface rounded-lg border border-tv-dark-border overflow-hidden">
      {/* Header */}
      <div className="flex items-center px-4 py-3 border-b border-tv-dark-border">
        <button className="flex items-center gap-2 text-sm font-medium text-tv-dark-textMuted hover:text-tv-dark-text transition-colors">
          <span>Symbol</span>
          <ArrowUpDown className="w-4 h-4" />
        </button>
        <div className="ml-auto text-sm text-tv-dark-textMuted">
          {signals.length}
        </div>
      </div>

      {/* Signals List */}
      <div className="divide-y divide-tv-dark-border">
        {signals.map((signal, index) => (
          <div
            key={`${signal.symbol}-${signal.signal_type}-${index}`}
            className="flex items-center gap-3 px-4 py-3 hover:bg-tv-dark-border transition-colors cursor-pointer"
          >
            {/* Logo */}
            <div
              className={`w-8 h-8 rounded-full ${getLogoColor(
                signal.symbol
              )} flex items-center justify-center text-white text-xs font-bold`}
            >
              {signal.symbol.charAt(0)}
            </div>

            {/* Symbol & Name */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-tv-dark-text">
                  {signal.symbol}
                </span>
                <span className="text-xs px-1.5 py-0.5 rounded bg-tv-dark-primary/20 text-tv-dark-primary">
                  {signal.signal_type}
                </span>
              </div>
              <div className="text-xs text-tv-dark-textMuted mt-0.5 flex items-center gap-3">
                <span>₺{signal.price.toFixed(2)}</span>
                {signal.rsi && <span>RSI: {signal.rsi.toFixed(1)}</span>}
                {signal.adx && <span>ADX: {signal.adx.toFixed(1)}</span>}
                <span>{new Date(signal.signal_date).toLocaleDateString('tr-TR')}</span>
              </div>
            </div>

            {/* Badge (G for Günlük) */}
            <div className="w-5 h-5 rounded bg-tv-dark-border flex items-center justify-center">
              <span className="text-xs text-tv-dark-textMuted font-medium">G</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
