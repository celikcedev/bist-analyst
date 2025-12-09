'use client';

import { ChevronDown } from 'lucide-react';

interface WatchlistSelectorProps {
  value: string;
  onChange: (value: string) => void;
}

export default function WatchlistSelector({ value, onChange }: WatchlistSelectorProps) {
  // For now, only BIST TUM - later can add custom watchlists
  const watchlists = [
    { id: 'BIST_TUM', name: 'BIST TUM', count: 593 },
  ];

  return (
    <div className="relative">
      <button
        className="flex items-center gap-3 px-4 py-2.5 bg-tv-dark-card border-2 border-tv-dark-border hover:border-tv-dark-success rounded-xl text-tv-dark-text transition-all min-w-[200px] group shadow-md hover:shadow-glow-sm"
        onClick={() => {
          // Placeholder - single option for now
        }}
      >
        <div className="w-2.5 h-2.5 rounded-full bg-gradient-success shadow-glow-sm animate-pulse"></div>
        <div className="flex-1 text-left">
          <div className="text-xs text-tv-dark-textMuted">Watchlist</div>
          <div className="text-sm font-semibold">{value}</div>
        </div>
        <div className="px-2 py-0.5 bg-tv-dark-border rounded text-xs text-tv-dark-textMuted font-medium">
          593
        </div>
        <ChevronDown className="w-4 h-4 text-tv-dark-textMuted group-hover:text-tv-dark-primary transition-colors" />
      </button>
    </div>
  );
}
