'use client';

import { useState, useEffect } from 'react';
import { Settings, Plus } from 'lucide-react';
import WatchlistSelector from '@/components/WatchlistSelector';
import StrategySelector from '@/components/StrategySelector';
import SignalTypeChips from '@/components/SignalTypeChips';
import ParameterModal from '@/components/ParameterModal';
import SignalTable from '@/components/SignalTable';
import ScanButton from '@/components/ScanButton';
import { Signal, runScan, Strategy, getStrategies } from '@/lib/api';

export default function ScreenerPage() {
  const [watchlist, setWatchlist] = useState('BIST TUM');
  const [strategy, setStrategy] = useState('XTUMYV27Strategy');
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  
  // All available signal types for XTUMY V27
  const allSignalTypes = [
    'TREND_BAŞLANGIÇ',
    'PULLBACK_AL',
    'DIP_AL',
    'ALTIN_KIRILIM',
    'ZİRVE_KIRILIMI',
    'DİRENÇ_REDDİ',
    'KURUMSAL_DIP',
  ];
  
  const [visibleSignalTypes, setVisibleSignalTypes] = useState<string[]>(allSignalTypes.slice(0, 4));
  const [activeSignalTypes, setActiveSignalTypes] = useState<string[]>([]);
  const [signals, setSignals] = useState<Signal[]>([]);
  const [loading, setLoading] = useState(false);
  const [paramModalOpen, setParamModalOpen] = useState(false);

  useEffect(() => {
    loadStrategies();
  }, []);

  const loadStrategies = async () => {
    try {
      const data = await getStrategies();
      setStrategies(data.filter(s => s.is_active));
    } catch (error) {
      console.error('Failed to load strategies:', error);
    }
  };

  const handleScan = async () => {
    setLoading(true);
    try {
      const result = await runScan({
        strategy_name: strategy,
        signal_types: activeSignalTypes.length > 0 ? activeSignalTypes : undefined,
      });
      setSignals(result.signals);
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
      <header className="bg-tv-dark-surface border-b border-tv-dark-border px-6 py-4">
        <div className="flex items-center justify-between max-w-[1920px] mx-auto">
          <div className="flex items-center gap-4">
            <h1 className="text-2xl font-bold text-tv-dark-text flex items-center gap-2">
              Pine Screener
              <span className="text-xs px-2 py-0.5 bg-tv-dark-border text-tv-dark-textMuted rounded">
                BETA
              </span>
            </h1>
          </div>
          
          <a
            href="http://localhost:3000"
            className="text-sm text-tv-dark-textMuted hover:text-tv-dark-text transition-colors"
          >
            ← Ana Sayfa
          </a>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-[1920px] mx-auto px-6 py-6">
        {/* Filter Bar */}
        <div className="bg-tv-dark-surface border border-tv-dark-border rounded-lg p-4 mb-6">
          <div className="flex flex-wrap items-center gap-3 mb-4">
            <WatchlistSelector value={watchlist} onChange={setWatchlist} />
            <StrategySelector value={strategy} onChange={setStrategy} />
            
            <button
              onClick={() => setParamModalOpen(true)}
              className="p-2 bg-tv-dark-border hover:bg-tv-dark-text/10 rounded-lg transition-colors"
              title="Parametre Ayarları"
            >
              <Settings className="w-5 h-5 text-tv-dark-text" />
            </button>

            <div className="ml-auto">
              <ScanButton onClick={handleScan} loading={loading} />
            </div>
          </div>

          {/* Signal Type Chips */}
          <div className="flex items-center gap-2">
            <SignalTypeChips
              signalTypes={visibleSignalTypes}
              activeTypes={activeSignalTypes}
              onToggle={handleToggleSignalType}
              onRemove={handleRemoveSignalType}
            />
            
            {visibleSignalTypes.length < allSignalTypes.length && (
              <button
                onClick={handleAddSignalType}
                className="p-1.5 bg-tv-dark-border hover:bg-tv-dark-text/10 rounded-lg transition-colors"
                title="Filtre Ekle"
              >
                <Plus className="w-4 h-4 text-tv-dark-text" />
              </button>
            )}
          </div>
        </div>

        {/* Results */}
        <SignalTable signals={signals} loading={loading} />
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
