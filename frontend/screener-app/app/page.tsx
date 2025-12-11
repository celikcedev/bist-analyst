'use client';

import { useState, useEffect } from 'react';
import { Settings, Plus } from 'lucide-react';
import WatchlistSelector from '@/components/WatchlistSelector';
import StrategySelector from '@/components/StrategySelector';
import SignalTypeChips from '@/components/SignalTypeChips';
import ParameterModal from '@/components/ParameterModal';
import SignalTable from '@/components/SignalTable';
import ScanButton from '@/components/ScanButton';
import AdvancedFilters, { type FilterValues } from '@/components/AdvancedFilters';
import { api, type Signal, type Strategy } from '@/lib/api';

export default function ScreenerPage() {
  const [watchlist, setWatchlist] = useState('BIST TUM');
  const [strategy, setStrategy] = useState('XTUMYV27Strategy');
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  
  // All available signal types for XTUMY V27
  const allSignalTypes = [
    'KURUMSAL DİP',
    'TREND BAŞLANGIÇ',
    'PULLBACK AL',
    'DİP AL',
    'ALTIN KIRILIM',
    'ZİRVE KIRILIMI',
    'DİRENÇ REDDİ',
  ];
  
  const [visibleSignalTypes, setVisibleSignalTypes] = useState<string[]>(allSignalTypes.slice(0, 4));
  const [activeSignalTypes, setActiveSignalTypes] = useState<string[]>([]);
  const [signals, setSignals] = useState<Signal[]>([]);
  const [filteredSignals, setFilteredSignals] = useState<Signal[]>([]);
  const [loading, setLoading] = useState(false);
  const [paramModalOpen, setParamModalOpen] = useState(false);
  const [advancedFilters, setAdvancedFilters] = useState<FilterValues>({
    rsiMin: 0,
    rsiMax: 100,
    adxMin: 0,
    priceMin: 0,
    priceMax: 10000,
    volumeMin: 0,
  });

  useEffect(() => {
    loadStrategies();
  }, []);

  const loadStrategies = async () => {
    try {
      const data = await api.getStrategies();
      setStrategies(data.strategies.filter(s => s.is_active));
    } catch (error) {
      console.error('Failed to load strategies:', error);
    }
  };

  const applyFilters = (signalsToFilter: Signal[], filters: FilterValues) => {
    const filtered = signalsToFilter.filter(signal => {
      const rsi = signal.rsi || 0;
      const adx = signal.adx || 0;
      const price = signal.price || 0;
      
      return (
        rsi >= filters.rsiMin &&
        rsi <= filters.rsiMax &&
        adx >= filters.adxMin &&
        price >= filters.priceMin &&
        price <= filters.priceMax
      );
    });
    
    setFilteredSignals(filtered);
  };

  const handleFilterChange = (filters: FilterValues) => {
    setAdvancedFilters(filters);
    applyFilters(signals, filters);
  };

  const handleScan = async () => {
    setLoading(true);
    try {
      const result = await api.runScan({
        strategy_name: strategy,
        user_id: 1,
        save_to_db: false,
        signal_types: activeSignalTypes.length > 0 ? activeSignalTypes : undefined,
      });
      const resultSignals = result.signals || [];
      setSignals(resultSignals);
      applyFilters(resultSignals, advancedFilters);
    } catch (error) {
      console.error('Scan failed:', error);
      alert('Tarama başarısız oldu. Lütfen tekrar deneyin.');
    } finally {
      setLoading(false);
    }
  };

  const handleToggleSignalType = (type: string) => {
    setActiveSignalTypes(prev => {
      if (prev.includes(type)) {
        return prev.filter(t => t !== type);
      } else {
        return [...prev, type];
      }
    });
  };

  const handleRemoveSignalType = (type: string) => {
    setVisibleSignalTypes(prev => prev.filter(t => t !== type));
    setActiveSignalTypes(prev => prev.filter(t => t !== type));
  };

  const handleAddSignalType = () => {
    const remaining = allSignalTypes.filter(t => !visibleSignalTypes.includes(t));
    if (remaining.length > 0) {
      setVisibleSignalTypes(prev => [...prev, remaining[0]]);
    }
  };

  const selectedStrategy = strategies.find(s => s.name === strategy);

  return (
    <div className="min-h-screen bg-tv-dark-bg">
      {/* Header */}
      <header className="bg-tv-dark-surface border-b border-tv-dark-border px-6 py-4 sticky top-0 z-50 backdrop-blur-xl bg-tv-dark-surface/90 shadow-lg">
        <div className="flex items-center justify-between max-w-[1920px] mx-auto">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-3">
              <div className="relative w-12 h-12 rounded-2xl bg-gradient-primary flex items-center justify-center shadow-glow-md">
                <svg className="w-7 h-7" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M3 17l3-3 4 4 6-6 5 5" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M21 7v5h-5" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
                <div className="absolute -top-1 -right-1 w-3 h-3 bg-gradient-success rounded-full border-2 border-tv-dark-surface animate-pulse"></div>
              </div>
              <div>
                <h1 className="text-xl font-bold text-tv-dark-text flex items-center gap-2">
                  Python Screener
                  <span className="text-xs px-2.5 py-0.5 bg-gradient-secondary text-white rounded-lg font-bold shadow-md">
                    BETA
                  </span>
                </h1>
                <p className="text-xs text-tv-dark-textMuted font-medium">Python-powered Signal Detection</p>
              </div>
            </div>
          </div>
          
          <a
            href="http://localhost:3000"
            className="text-sm text-tv-dark-textMuted hover:text-tv-dark-primary transition-all font-semibold flex items-center gap-2 px-4 py-2 rounded-xl hover:bg-tv-dark-card"
          >
            <span>←</span>
            <span>Ana Sayfa</span>
          </a>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-[1920px] mx-auto px-6 py-6">
        {/* Filter Bar */}
        <div className="relative bg-tv-dark-card border border-tv-dark-border/50 rounded-2xl p-6 mb-6 shadow-2xl overflow-visible z-10">
          {/* Subtle background gradient */}
          <div className="absolute inset-0 bg-gradient-card opacity-30 rounded-2xl"></div>
          
          <div className="relative flex flex-col gap-6 z-20">
            {/* Top Row: Selectors and Action */}
            <div className="flex flex-wrap items-center gap-3">
              <WatchlistSelector value={watchlist} onChange={setWatchlist} />
              <StrategySelector value={strategy} onChange={setStrategy} />
              
              <button
                onClick={() => setParamModalOpen(true)}
                className="relative p-3 bg-tv-dark-surface hover:bg-tv-dark-surface/80 border-2 border-tv-dark-border hover:border-tv-dark-primary rounded-xl transition-all group shadow-md hover:shadow-glow-sm"
                title="Parametre Ayarları"
              >
                <Settings className="w-5 h-5 text-tv-dark-textMuted group-hover:text-tv-dark-primary transition-all group-hover:rotate-90 duration-300" />
              </button>

              <div className="ml-auto">
                <ScanButton onClick={handleScan} loading={loading} />
              </div>
            </div>

            {/* Bottom Row: Signal Type Filters */}
            <div className="border-t border-tv-dark-border/30 pt-5">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-1 h-5 rounded-full bg-gradient-primary"></div>
                  <h3 className="text-sm font-bold text-tv-dark-text uppercase tracking-wide">Sinyal Türü Filtreleri</h3>
                </div>
                {activeSignalTypes.length > 0 && (
                  <div className="flex items-center gap-2 px-3 py-1 bg-gradient-primary/10 border border-tv-dark-primary/30 rounded-lg">
                    <div className="w-2 h-2 rounded-full bg-tv-dark-primary animate-pulse"></div>
                    <span className="text-xs text-tv-dark-primary font-bold">
                      {activeSignalTypes.length} Aktif Filtre
                    </span>
                  </div>
                )}
              </div>
              
              <div className="flex items-center gap-2.5 flex-wrap">
                <SignalTypeChips
                  signalTypes={visibleSignalTypes}
                  activeTypes={activeSignalTypes}
                  onToggle={handleToggleSignalType}
                  onRemove={handleRemoveSignalType}
                />
                
                {visibleSignalTypes.length < allSignalTypes.length && (
                  <button
                    onClick={handleAddSignalType}
                    className="p-2.5 bg-tv-dark-surface hover:bg-gradient-primary/10 border-2 border-dashed border-tv-dark-border hover:border-tv-dark-primary rounded-xl transition-all group"
                    title="Yeni Filtre Ekle"
                  >
                    <Plus className="w-4 h-4 text-tv-dark-textMuted group-hover:text-tv-dark-primary transition-all group-hover:rotate-90 duration-300" />
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Results */}
        {/* Advanced Filters */}
        {signals.length > 0 && (
          <div className="mb-6">
            <AdvancedFilters onFilterChange={handleFilterChange} />
          </div>
        )}

        <SignalTable signals={filteredSignals.length > 0 ? filteredSignals : signals} loading={loading} />
      </main>

      {/* Parameter Modal */}
      <ParameterModal
        isOpen={paramModalOpen}
        onClose={() => setParamModalOpen(false)}
        strategyName={strategy}
        strategyDisplayName={selectedStrategy?.display_name || 'XTUMY V27'}
      />
    </div>
  );
}
