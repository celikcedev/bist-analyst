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
        className="flex items-center gap-2 px-4 py-2 bg-tv-dark-surface border border-tv-dark-border rounded-lg text-tv-dark-text hover:border-tv-dark-text transition-colors min-w-[280px]"
        onClick={() => setIsOpen(!isOpen)}
      >
        <span className="text-sm flex-1 text-left truncate">
          {loading ? 'Yükleniyor...' : (selectedStrategy?.display_name || value)}
        </span>
        <ChevronDown className="w-4 h-4 text-tv-dark-textMuted" />
      </button>

      {isOpen && strategies.length > 0 && (
        <div className="absolute top-full left-0 mt-2 w-full bg-tv-dark-surface border border-tv-dark-border rounded-lg shadow-xl z-50 overflow-hidden">
          {strategies.map((strategy) => (
            <button
              key={strategy.id}
              className="w-full px-4 py-3 text-left hover:bg-tv-dark-border transition-colors"
              onClick={() => {
                onChange(strategy.name);
                setIsOpen(false);
              }}
            >
              <div className="text-sm font-medium text-tv-dark-text">
                {strategy.display_name}
              </div>
              <div className="text-xs text-tv-dark-textMuted mt-1">
                {strategy.description}
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
