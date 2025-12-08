'use client';

import { Search } from 'lucide-react';

interface ScanButtonProps {
  onClick: () => void;
  loading: boolean;
  disabled?: boolean;
}

export default function ScanButton({ onClick, loading, disabled }: ScanButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={loading || disabled}
      className="flex items-center gap-2 px-6 py-2 bg-white text-tv-dark-bg rounded-lg font-medium hover:bg-gray-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
    >
      <Search className="w-4 h-4" />
      <span>{loading ? 'Taranıyor...' : 'Scan'}</span>
    </button>
  );
}
