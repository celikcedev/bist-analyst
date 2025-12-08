'use client';

import { X, ChevronDown } from 'lucide-react';
import { useState } from 'react';

interface SignalTypeChipsProps {
  signalTypes: string[];
  activeTypes: string[];
  onToggle: (type: string) => void;
  onRemove: (type: string) => void;
}

const SIGNAL_TYPE_LABELS: Record<string, string> = {
  'TREND_BAŞLANGIÇ': 'TREND BAŞLANGIÇ',
  'PULLBACK_AL': 'PULLBACK AL',
  'DIP_AL': 'DIP AL',
  'ALTIN_KIRILIM': 'ALTIN KIRILIM',
  'ZİRVE_KIRILIMI': 'ZİRVE KIRILIMI',
  'DİRENÇ_REDDİ': 'DİRENÇ REDDİ',
  'KURUMSAL_DIP': 'KURUMSAL DIP',
};

export default function SignalTypeChips({
  signalTypes,
  activeTypes,
  onToggle,
  onRemove,
}: SignalTypeChipsProps) {
  const [openMenu, setOpenMenu] = useState<string | null>(null);

  return (
    <div className="flex items-center gap-2 flex-wrap">
      {signalTypes.map((type) => {
        const isActive = activeTypes.includes(type);
        const label = SIGNAL_TYPE_LABELS[type] || type;

        return (
          <div key={type} className="relative">
            <button
              className={`
                flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors
                ${
                  isActive
                    ? 'bg-tv-dark-primary text-white'
                    : 'bg-tv-dark-surface text-tv-dark-textMuted border border-tv-dark-border hover:border-tv-dark-text'
                }
              `}
              onClick={() => setOpenMenu(openMenu === type ? null : type)}
            >
              <span>XTUMY V27: {label}</span>
              {isActive && <span className="text-xs opacity-80">True</span>}
              <ChevronDown className="w-3 h-3" />
            </button>

            {openMenu === type && (
              <div className="absolute top-full left-0 mt-1 bg-tv-dark-surface border border-tv-dark-border rounded-lg shadow-xl z-50 overflow-hidden min-w-[120px]">
                <button
                  className="w-full px-3 py-2 text-left text-sm text-tv-dark-text hover:bg-tv-dark-border transition-colors"
                  onClick={() => {
                    onToggle(type);
                    setOpenMenu(null);
                  }}
                >
                  {isActive ? 'False' : 'True'}
                </button>
                <button
                  className="w-full px-3 py-2 text-left text-sm text-tv-dark-danger hover:bg-tv-dark-border transition-colors flex items-center gap-2"
                  onClick={() => {
                    onRemove(type);
                    setOpenMenu(null);
                  }}
                >
                  <X className="w-3 h-3" />
                  Remove
                </button>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
