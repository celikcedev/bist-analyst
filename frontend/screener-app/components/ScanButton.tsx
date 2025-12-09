'use client';

import { Scan, Loader2 } from 'lucide-react';

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
      className="relative flex items-center gap-3 px-10 py-3.5 bg-gradient-primary hover:shadow-glow-lg disabled:opacity-60 disabled:cursor-not-allowed text-white font-bold rounded-xl transition-all shadow-lg disabled:shadow-none overflow-hidden group"
    >
      <span className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent translate-x-[-200%] group-hover:translate-x-[200%] transition-transform duration-1000"></span>
      
      {loading ? (
        <>
          <Loader2 className="w-5 h-5 animate-spin relative z-10" />
          <span className="relative z-10">Piyasa Taranıyor...</span>
        </>
      ) : (
        <>
          <Scan className="w-5 h-5 relative z-10" />
          <span className="relative z-10">Taramayı Başlat</span>
        </>
      )}
    </button>
  );
}
