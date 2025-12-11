'use client';

import { useState } from 'react';
import { Filter, X, ChevronDown, ChevronUp } from 'lucide-react';

interface AdvancedFiltersProps {
  onFilterChange: (filters: FilterValues) => void;
}

export interface FilterValues {
  rsiMin: number;
  rsiMax: number;
  adxMin: number;
  priceMin: number;
  priceMax: number;
  volumeMin: number;
}

const DEFAULT_FILTERS: FilterValues = {
  rsiMin: 0,
  rsiMax: 100,
  adxMin: 0,
  priceMin: 0,
  priceMax: 10000,
  volumeMin: 0,
};

export default function AdvancedFilters({ onFilterChange }: AdvancedFiltersProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [filters, setFilters] = useState<FilterValues>(DEFAULT_FILTERS);

  const handleFilterChange = (key: keyof FilterValues, value: number) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    onFilterChange(newFilters);
  };

  const resetFilters = () => {
    setFilters(DEFAULT_FILTERS);
    onFilterChange(DEFAULT_FILTERS);
  };

  const hasActiveFilters = () => {
    return (
      filters.rsiMin !== DEFAULT_FILTERS.rsiMin ||
      filters.rsiMax !== DEFAULT_FILTERS.rsiMax ||
      filters.adxMin !== DEFAULT_FILTERS.adxMin ||
      filters.priceMin !== DEFAULT_FILTERS.priceMin ||
      filters.priceMax !== DEFAULT_FILTERS.priceMax ||
      filters.volumeMin !== DEFAULT_FILTERS.volumeMin
    );
  };

  return (
    <div className="bg-tv-dark-card rounded-2xl border border-tv-dark-border/50 overflow-hidden shadow-lg">
      {/* Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-6 py-4 flex items-center justify-between hover:bg-tv-dark-border/30 transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
            <Filter className="w-5 h-5 text-white" />
          </div>
          <div className="text-left">
            <h3 className="text-lg font-bold text-tv-dark-text">Gelişmiş Filtreler</h3>
            <p className="text-xs text-tv-dark-textMuted">
              {hasActiveFilters() ? 'Aktif filtreler var' : 'Sinyalleri detaylı filtrele'}
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          {hasActiveFilters() && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                resetFilters();
              }}
              className="px-3 py-1.5 bg-red-500/20 text-red-400 rounded-lg text-sm font-medium hover:bg-red-500/30 transition-colors"
            >
              Sıfırla
            </button>
          )}
          {isExpanded ? (
            <ChevronUp className="w-5 h-5 text-tv-dark-textMuted" />
          ) : (
            <ChevronDown className="w-5 h-5 text-tv-dark-textMuted" />
          )}
        </div>
      </button>

      {/* Filter Content */}
      {isExpanded && (
        <div className="px-6 py-6 border-t border-tv-dark-border/50 bg-gradient-card/30">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* RSI Range */}
            <div className="space-y-3">
              <label className="block text-sm font-semibold text-tv-dark-text">
                RSI Aralığı
              </label>
              <div className="flex items-center gap-3">
                <div className="flex-1">
                  <input
                    type="number"
                    min="0"
                    max="100"
                    value={filters.rsiMin}
                    onChange={(e) => handleFilterChange('rsiMin', Number(e.target.value))}
                    className="w-full px-3 py-2 bg-tv-dark-surface border border-tv-dark-border rounded-lg text-tv-dark-text text-sm focus:outline-none focus:ring-2 focus:ring-tv-dark-primary"
                    placeholder="Min"
                  />
                  <p className="text-xs text-tv-dark-textMuted mt-1">Minimum</p>
                </div>
                <span className="text-tv-dark-textMuted">-</span>
                <div className="flex-1">
                  <input
                    type="number"
                    min="0"
                    max="100"
                    value={filters.rsiMax}
                    onChange={(e) => handleFilterChange('rsiMax', Number(e.target.value))}
                    className="w-full px-3 py-2 bg-tv-dark-surface border border-tv-dark-border rounded-lg text-tv-dark-text text-sm focus:outline-none focus:ring-2 focus:ring-tv-dark-primary"
                    placeholder="Max"
                  />
                  <p className="text-xs text-tv-dark-textMuted mt-1">Maksimum</p>
                </div>
              </div>
              <div className="flex items-center gap-2 text-xs text-tv-dark-textMuted">
                <div className="w-2 h-2 rounded-full bg-yellow-500"></div>
                <span>Şu an: {filters.rsiMin} - {filters.rsiMax}</span>
              </div>
            </div>

            {/* ADX Minimum */}
            <div className="space-y-3">
              <label className="block text-sm font-semibold text-tv-dark-text">
                ADX Minimum
              </label>
              <input
                type="number"
                min="0"
                max="100"
                value={filters.adxMin}
                onChange={(e) => handleFilterChange('adxMin', Number(e.target.value))}
                className="w-full px-3 py-2 bg-tv-dark-surface border border-tv-dark-border rounded-lg text-tv-dark-text text-sm focus:outline-none focus:ring-2 focus:ring-tv-dark-primary"
                placeholder="Minimum ADX"
              />
              <p className="text-xs text-tv-dark-textMuted">
                Trend gücü: {filters.adxMin > 25 ? 'Güçlü' : filters.adxMin > 20 ? 'Orta' : 'Zayıf'}
              </p>
            </div>

            {/* Price Range */}
            <div className="space-y-3">
              <label className="block text-sm font-semibold text-tv-dark-text">
                Fiyat Aralığı (TL)
              </label>
              <div className="flex items-center gap-3">
                <div className="flex-1">
                  <input
                    type="number"
                    min="0"
                    value={filters.priceMin}
                    onChange={(e) => handleFilterChange('priceMin', Number(e.target.value))}
                    className="w-full px-3 py-2 bg-tv-dark-surface border border-tv-dark-border rounded-lg text-tv-dark-text text-sm focus:outline-none focus:ring-2 focus:ring-tv-dark-primary"
                    placeholder="Min"
                  />
                  <p className="text-xs text-tv-dark-textMuted mt-1">Minimum</p>
                </div>
                <span className="text-tv-dark-textMuted">-</span>
                <div className="flex-1">
                  <input
                    type="number"
                    min="0"
                    value={filters.priceMax}
                    onChange={(e) => handleFilterChange('priceMax', Number(e.target.value))}
                    className="w-full px-3 py-2 bg-tv-dark-surface border border-tv-dark-border rounded-lg text-tv-dark-text text-sm focus:outline-none focus:ring-2 focus:ring-tv-dark-primary"
                    placeholder="Max"
                  />
                  <p className="text-xs text-tv-dark-textMuted mt-1">Maksimum</p>
                </div>
              </div>
            </div>

            {/* Volume Minimum */}
            <div className="space-y-3">
              <label className="block text-sm font-semibold text-tv-dark-text">
                Minimum Hacim
              </label>
              <input
                type="number"
                min="0"
                value={filters.volumeMin}
                onChange={(e) => handleFilterChange('volumeMin', Number(e.target.value))}
                className="w-full px-3 py-2 bg-tv-dark-surface border border-tv-dark-border rounded-lg text-tv-dark-text text-sm focus:outline-none focus:ring-2 focus:ring-tv-dark-primary"
                placeholder="Minimum hacim"
              />
              <p className="text-xs text-tv-dark-textMuted">
                {filters.volumeMin > 0 ? `${(filters.volumeMin / 1000000).toFixed(1)}M+` : 'Filtre yok'}
              </p>
            </div>
          </div>

          {/* Info */}
          <div className="mt-6 p-4 bg-blue-900/20 border border-blue-500/30 rounded-lg">
            <p className="text-sm text-blue-300">
              💡 <strong>İpucu:</strong> Filtreler gerçek zamanlı olarak uygulanır. Daha dar aralıklar seçerek sonuçları daraltabilirsiniz.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
