'use client';

import { ChevronDown } from 'lucide-react';
import { useState, useEffect } from 'react';
import { Strategy, getStrategies } from '@/lib/api';

interface StrategySelectorProps {
  value: string;
  onChange: (value: string) => void;
}

export default function StrategySelector({ value, onChange }: StrategySelectorProps) {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStrategies();
  }, []);

  const loadStrategies = async () => {
    try {
      const data = await getStrategies();
      setStrategies(data.filter(s => s.is_active));
      setLoading(false);
    } catch (error) {
      console.error('Failed to load strategies:', error);
      setLoading(false);
    }
  };

  const selectedStrategy = strategies.find(s => s.name === value);

  return (
    <div className="relative">
      <button
        className="flex items-center gap-3 px-4 py-2.5 bg-tv-dark-card border-2 border-tv-dark-border hover:border-tv-dark-primary rounded-xl text-tv-dark-text transition-all min-w-[280px] group shadow-md hover:shadow-glow-sm"
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className="w-9 h-9 rounded-xl bg-gradient-secondary flex items-center justify-center shadow-md">
          <span className="text-xs font-bold text-white">X27</span>
        </div>
        <span className="text-sm font-medium flex-1 text-left truncate">
          {loading ? 'Yükleniyor...' : (selectedStrategy?.display_name || value)}
        </span>
        <ChevronDown className={`w-4 h-4 text-tv-dark-textMuted group-hover:text-tv-dark-primary transition-all ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && strategies.length > 0 && (
        <div className="absolute top-full left-0 mt-2 w-full bg-tv-dark-surface border border-tv-dark-border rounded-lg shadow-2xl z-[9998] overflow-hidden animate-in fade-in slide-in-from-top-2 duration-200">
          {strategies.map((strategy) => (
            <button
              key={strategy.id}
              className="w-full px-4 py-3 text-left hover:bg-tv-dark-border transition-colors group/item"
              onClick={() => {
                onChange(strategy.name);
                setIsOpen(false);
              }}
            >
              <div className="text-sm font-semibold text-tv-dark-text group-hover/item:text-tv-dark-primary transition-colors">
                {strategy.display_name}
              </div>
              <div className="text-xs text-tv-dark-textMuted mt-1 line-clamp-2">
                {strategy.description}
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
