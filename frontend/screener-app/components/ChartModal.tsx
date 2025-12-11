'use client';

import { useEffect, useRef, useState } from 'react';
import { X, TrendingUp, Activity, BarChart3 } from 'lucide-react';
import { createChart, ColorType, IChartApi, ISeriesApi } from 'lightweight-charts';
import { api, type OHLCVData } from '@/lib/api';

interface ChartModalProps {
  isOpen: boolean;
  onClose: () => void;
  symbol: string;
  symbolName?: string;
}

export default function ChartModal({ isOpen, onClose, symbol, symbolName }: ChartModalProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [days, setDays] = useState(90);

  useEffect(() => {
    if (!isOpen || !symbol) return;

    loadChartData();

    return () => {
      if (chartRef.current) {
        chartRef.current.remove();
        chartRef.current = null;
      }
    };
  }, [isOpen, symbol, days]);

  const loadChartData = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await api.getOHLCV(symbol, days);
      
      if (!response.data || response.data.length === 0) {
        setError('No chart data available');
        setLoading(false);
        return;
      }

      renderChart(response.data);
      setLoading(false);
    } catch (err: any) {
      console.error('Failed to load chart data:', err);
      setError(err.message || 'Failed to load chart data');
      setLoading(false);
    }
  };

  const renderChart = (data: OHLCVData[]) => {
    if (!chartContainerRef.current) return;

    // Remove existing chart
    if (chartRef.current) {
      chartRef.current.remove();
    }

    // Create chart
    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: 500,
      layout: {
        background: { type: ColorType.Solid, color: '#1a1a2e' },
        textColor: '#d1d5db',
      },
      grid: {
        vertLines: { color: '#2d2d44' },
        horzLines: { color: '#2d2d44' },
      },
      crosshair: {
        mode: 1,
      },
      rightPriceScale: {
        borderColor: '#2d2d44',
      },
      timeScale: {
        borderColor: '#2d2d44',
        timeVisible: true,
      },
    });

    chartRef.current = chart;

    // Add candlestick series
    const candlestickSeries = chart.addCandlestickSeries({
      upColor: '#22c55e',
      downColor: '#ef4444',
      borderUpColor: '#22c55e',
      borderDownColor: '#ef4444',
      wickUpColor: '#22c55e',
      wickDownColor: '#ef4444',
    });

    // Convert data to lightweight-charts format
    const candleData = data.map(d => ({
      time: d.date,
      open: d.open,
      high: d.high,
      low: d.low,
      close: d.close,
    }));

    candlestickSeries.setData(candleData);

    // Add volume series
    const volumeSeries = chart.addHistogramSeries({
      color: '#3b82f6',
      priceFormat: {
        type: 'volume',
      },
      priceScaleId: '',
      scaleMargins: {
        top: 0.8,
        bottom: 0,
      },
    });

    const volumeData = data.map(d => ({
      time: d.date,
      value: d.volume,
      color: d.close >= d.open ? '#22c55e50' : '#ef444450',
    }));

    volumeSeries.setData(volumeData);

    // Auto-fit content
    chart.timeScale().fitContent();

    // Handle window resize
    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({
          width: chartContainerRef.current.clientWidth,
        });
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
    };
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-[10000] p-4">
      <div className="bg-tv-dark-card rounded-2xl border border-tv-dark-border shadow-2xl w-full max-w-6xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-tv-dark-border bg-gradient-card/30">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center">
              <BarChart3 className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-tv-dark-text">{symbol}</h2>
              {symbolName && <p className="text-sm text-tv-dark-textMuted">{symbolName}</p>}
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            {/* Time Range Selector */}
            <select
              value={days}
              onChange={(e) => setDays(Number(e.target.value))}
              className="px-3 py-2 bg-tv-dark-surface border border-tv-dark-border rounded-lg text-tv-dark-text text-sm focus:outline-none focus:ring-2 focus:ring-tv-dark-primary"
            >
              <option value={30}>30 Gün</option>
              <option value={90}>90 Gün</option>
              <option value={180}>180 Gün</option>
              <option value={365}>1 Yıl</option>
            </select>
            
            <button
              onClick={onClose}
              className="p-2 hover:bg-tv-dark-border rounded-lg transition-colors"
            >
              <X className="w-5 h-5 text-tv-dark-textMuted" />
            </button>
          </div>
        </div>

        {/* Chart Content */}
        <div className="p-6">
          {loading && (
            <div className="flex items-center justify-center h-[500px]">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-tv-dark-primary mx-auto mb-4"></div>
                <p className="text-tv-dark-textMuted">Grafik yükleniyor...</p>
              </div>
            </div>
          )}

          {error && (
            <div className="flex items-center justify-center h-[500px]">
              <div className="text-center">
                <div className="text-5xl mb-4">📊</div>
                <p className="text-tv-dark-text font-semibold mb-2">Grafik Yüklenemedi</p>
                <p className="text-tv-dark-textMuted text-sm">{error}</p>
              </div>
            </div>
          )}

          {!loading && !error && (
            <div>
              {/* Chart Container */}
              <div ref={chartContainerRef} className="rounded-lg overflow-hidden border border-tv-dark-border" />
              
              {/* Chart Legend */}
              <div className="mt-4 flex items-center justify-center gap-6 text-sm">
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-green-500 rounded"></div>
                  <span className="text-tv-dark-textMuted">Yükseliş</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-red-500 rounded"></div>
                  <span className="text-tv-dark-textMuted">Düşüş</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-blue-500 rounded opacity-50"></div>
                  <span className="text-tv-dark-textMuted">Hacim</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-tv-dark-border bg-gradient-card/30">
          <p className="text-xs text-tv-dark-textMuted text-center">
            💡 Grafik üzerinde fare ile sürükleyerek yakınlaştırma yapabilirsiniz
          </p>
        </div>
      </div>
    </div>
  );
}
