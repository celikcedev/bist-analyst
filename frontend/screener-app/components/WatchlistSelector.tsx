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
        className="flex items-center gap-2 px-4 py-2 bg-tv-dark-surface border border-tv-dark-border rounded-lg text-tv-dark-text hover:border-tv-dark-text transition-colors min-w-[180px]"
        onClick={() => {
          // Placeholder - single option for now
        }}
      >
        <span className="text-sm font-medium">İzleme Listesi</span>
        <span className="text-tv-dark-textMuted text-sm font-bold">{value}</span>
        <ChevronDown className="w-4 h-4 ml-auto text-tv-dark-textMuted" />
      </button>
    </div>
  );
}
