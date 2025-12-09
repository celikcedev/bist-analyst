'use client';

import { X, ChevronDown, CheckCircle2, Circle } from 'lucide-react';
import { useState, useRef, useEffect } from 'react';

interface SignalTypeChipsProps {
  signalTypes: string[];
  activeTypes: string[];
  onToggle: (type: string) => void;
  onRemove: (type: string) => void;
}

const SIGNAL_TYPE_LABELS: Record<string, string> = {
  'KURUMSAL DİP': 'KURUMSAL DİP',
  'TREND BAŞLANGIÇ': 'TREND BAŞLANGIÇ',
  'PULLBACK AL': 'PULLBACK AL',
  'DİP AL': 'DİP AL',
  'ALTIN KIRILIM': 'ALTIN KIRILIM',
  'ZİRVE KIRILIMI': 'ZİRVE KIRILIMI',
  'DİRENÇ REDDİ': 'DİRENÇ REDDİ',
};

const SIGNAL_TYPE_COLORS: Record<string, string> = {
  'KURUMSAL DİP': 'bg-gray-500/10 border-gray-500/30 text-gray-400 hover:bg-gray-500/20',
  'TREND BAŞLANGIÇ': 'bg-purple-500/10 border-purple-500/30 text-purple-400 hover:bg-purple-500/20',
  'PULLBACK AL': 'bg-blue-500/10 border-blue-500/30 text-blue-400 hover:bg-blue-500/20',
  'DİP AL': 'bg-cyan-500/10 border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/20',
  'ALTIN KIRILIM': 'bg-yellow-500/10 border-yellow-500/30 text-yellow-400 hover:bg-yellow-500/20',
  'ZİRVE KIRILIMI': 'bg-orange-500/10 border-orange-500/30 text-orange-400 hover:bg-orange-500/20',
  'DİRENÇ REDDİ': 'bg-red-500/10 border-red-500/30 text-red-400 hover:bg-red-500/20',
};

export default function SignalTypeChips({
  signalTypes,
  activeTypes,
  onToggle,
  onRemove,
}: SignalTypeChipsProps) {
  const [openMenu, setOpenMenu] = useState<string | null>(null);
  const menuRef = useRef<HTMLDivElement>(null);

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setOpenMenu(null);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className="flex items-center gap-2.5 flex-wrap">
      {signalTypes.map((type) => {
        const isActive = activeTypes.includes(type);
        const label = SIGNAL_TYPE_LABELS[type] || type;
        const colorClass = SIGNAL_TYPE_COLORS[type] || 'bg-gray-500/10 border-gray-500/30 text-gray-400 hover:bg-gray-500/20';

        return (
          <div key={type} className="relative" ref={openMenu === type ? menuRef : null}>
            <button
              className={`
                flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-medium transition-all border
                ${isActive 
                  ? colorClass
                  : 'bg-tv-dark-surface/50 text-tv-dark-textMuted border-tv-dark-border hover:border-tv-dark-text hover:bg-tv-dark-surface'
                }
              `}
              onClick={() => setOpenMenu(openMenu === type ? null : type)}
            >
              {isActive ? (
                <CheckCircle2 className="w-3.5 h-3.5" />
              ) : (
                <Circle className="w-3.5 h-3.5 opacity-50" />
              )}
              <span className="font-semibold">{label}</span>
              <ChevronDown className={`w-3.5 h-3.5 transition-transform ${openMenu === type ? 'rotate-180' : ''}`} />
            </button>

            {openMenu === type && (
              <div className="absolute top-full left-0 mt-2 bg-tv-dark-card border-2 border-tv-dark-border rounded-xl shadow-2xl z-[9998] overflow-hidden min-w-[180px] animate-in fade-in slide-in-from-top-2 duration-200">
                <div className="p-2">
                  <button
                    className="w-full px-4 py-3 text-left text-sm font-medium text-tv-dark-text hover:bg-tv-dark-surface rounded-lg transition-colors flex items-center justify-between"
                    onClick={() => {
                      onToggle(type);
                      setOpenMenu(null);
                    }}
                  >
                    <span className="font-semibold">{isActive ? 'Deaktif Et' : 'Aktif Et'}</span>
                    {isActive ? (
                      <CheckCircle2 className="w-5 h-5 text-tv-dark-success" />
                    ) : (
                      <Circle className="w-5 h-5 text-tv-dark-textMuted" />
                    )}
                  </button>
                  <div className="h-px bg-tv-dark-border my-2"></div>
                  <button
                    className="w-full px-4 py-3 text-left text-sm font-semibold text-tv-dark-danger hover:bg-tv-dark-danger/10 rounded-lg transition-colors flex items-center gap-2"
                    onClick={() => {
                      onRemove(type);
                      setOpenMenu(null);
                    }}
                  >
                    <X className="w-5 h-5" />
                    <span>Kaldır</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
