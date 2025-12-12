/**
 * API client for BIST Analyst Screener
 * Extended version with strategy parameter management
 */
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001';

// Create axios instance
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// ============================================================================
// TYPES
// ============================================================================

export interface Signal {
  id: number;
  symbol: string;
  signal_type: string;
  signal_date: string;
  price: number;
  rsi: number | null;
  adx: number | null;
  metadata: Record<string, any>;
  created_at: string;
}

export interface Strategy {
  id: number;
  name: string;
  display_name: string;
  description: string;
  is_active: boolean;
  parameters?: StrategyParameters;
}

export interface StrategyParameters {
  [key: string]: any;
}

export interface Stats {
  tickers_count: number;
  active_tickers: number;
  latest_data_date: string;
  data_points: number;
}

export interface Ticker {
  symbol: string;
  name: string;
  type: string;
  is_active: boolean;
}

export interface OHLCVData {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface ScanResult {
  strategy_name: string;
  total_tickers_scanned: number;
  signals_found: number;
  execution_time: number;
  signals: Signal[];
  saved_to_db: boolean;
}

// Performance Types
export interface PerformanceData {
  price_1d: number | null;
  price_3d: number | null;
  price_7d: number | null;
  gain_1d: number | null;
  gain_3d: number | null;
  gain_7d: number | null;
  updated_at: string | null;
}

export interface PeriodPerformance {
  tracked: number;
  avg_gain: number | null;
  win_rate: number | null;
  wins: number;
  best: number | null;
  worst: number | null;
}

export interface SignalTypePerformance {
  signal_type: string;
  total_signals: number;
  performance: {
    '1d': PeriodPerformance;
    '3d': PeriodPerformance;
    '7d': PeriodPerformance;
  };
}

export interface PerformanceSummary {
  period_days: number;
  generated_at: string;
  summary: {
    total_signals: number;
    tracked_signals: number;
    overall_win_rate_7d: number | null;
    overall_avg_gain_7d: number | null;
  };
  by_signal_type: SignalTypePerformance[];
}

export interface TopPerformer {
  id: number;
  symbol: string;
  signal_type: string;
  signal_date: string;
  price_at_signal: number | null;
  price_later: number | null;
  gain: number | null;
}

export interface SymbolPerformance {
  symbol: string;
  total_signals: number;
  signal_types: string[];
  avg_gain_7d: number | null;
  win_rate_7d: number | null;
  tracked_7d: number;
  best_gain: number | null;
  worst_gain: number | null;
}

// ============================================================================
// API FUNCTIONS
// ============================================================================

export const api = {
  // Health check
  health: async () => {
    const response = await apiClient.get('/api/health');
    return response.data;
  },

  // ========================================================================
  // MARKET DATA
  // ========================================================================
  
  getStats: async (): Promise<Stats> => {
    const response = await apiClient.get('/api/market-data/stats');
    return response.data;
  },

  getTickers: async (params?: { 
    active_only?: boolean; 
    limit?: number; 
    offset?: number;
  }): Promise<{ tickers: Ticker[]; total: number; limit: number; offset: number }> => {
    const response = await apiClient.get('/api/market-data/tickers', { params });
    return response.data;
  },

  getTickerData: async (symbol: string, days: number = 30): Promise<{ data: any[] }> => {
    const response = await apiClient.get(`/api/market-data/tickers/${symbol}/data`, {
      params: { days },
    });
    return response.data;
  },

  /**
   * Get OHLCV data for charting
   * @param symbol - Ticker symbol
   * @param days - Number of days (default: 90)
   * @returns Array of OHLCV candles
   */
  getOHLCV: async (symbol: string, days: number = 90): Promise<{ data: OHLCVData[] }> => {
    const response = await apiClient.get(`/api/market-data/${symbol}/ohlcv`, {
      params: { days },
    });
    return response.data;
  },

  // ========================================================================
  // SCREENER & STRATEGIES
  // ========================================================================

  getStrategies: async (): Promise<{ strategies: Strategy[] }> => {
    const response = await apiClient.get('/api/screener/strategies');
    return response.data;
  },

  getStrategy: async (strategyName: string): Promise<Strategy> => {
    const response = await apiClient.get(`/api/screener/strategies/${strategyName}`);
    return response.data;
  },

  getStrategyParameters: async (strategyName: string, userId: number = 1): Promise<StrategyParameters> => {
    const response = await apiClient.get(`/api/screener/strategies/${strategyName}/parameters`, {
      params: { user_id: userId },
    });
    return response.data;
  },

  updateStrategyParameters: async (
    strategyName: string, 
    parameters: StrategyParameters,
    userId: number = 1
  ): Promise<{ message: string; parameters: StrategyParameters }> => {
    const response = await apiClient.post(
      `/api/screener/strategies/${strategyName}/parameters`,
      { user_id: userId, parameters }
    );
    return response.data;
  },

  // ========================================================================
  // SIGNALS
  // ========================================================================

  getSignals: async (params?: {
    user_id?: number;
    strategy_id?: number;
    signal_type?: string;
    date_from?: string;
    date_to?: string;
    limit?: number;
    offset?: number;
  }): Promise<{ signals: Signal[]; total: number; limit: number; offset: number }> => {
    const response = await apiClient.get('/api/screener/signals', { params });
    return response.data;
  },

  runScan: async (data: {
    strategy_name: string;
    user_id?: number;
    save_to_db?: boolean;
    symbols?: string[];
    signal_types?: string[];
  }): Promise<ScanResult> => {
    const response = await apiClient.post('/api/screener/scan', data);
    return response.data;
  },

  // ========================================================================
  // PERFORMANCE TRACKING
  // ========================================================================

  /**
   * Get performance summary for all signal types
   * @param days - Number of days to look back (default: 30)
   * @param userId - User ID (default: 1)
   */
  getPerformanceSummary: async (days: number = 30, userId: number = 1): Promise<PerformanceSummary> => {
    const response = await apiClient.get('/api/screener/performance/summary', {
      params: { days, user_id: userId },
    });
    return response.data;
  },

  /**
   * Get top and worst performing signals
   * @param period - 1d, 3d, or 7d (default: 7d)
   * @param days - Days to look back (default: 30)
   * @param limit - Number of results (default: 10)
   */
  getTopPerformers: async (
    period: '1d' | '3d' | '7d' = '7d',
    days: number = 30,
    limit: number = 10,
    userId: number = 1
  ): Promise<{ period: string; days_back: number; top_gainers: TopPerformer[]; top_losers: TopPerformer[] }> => {
    const response = await apiClient.get('/api/screener/performance/top-performers', {
      params: { period, days, limit, user_id: userId },
    });
    return response.data;
  },

  /**
   * Get performance for a specific signal
   * @param signalId - Signal ID
   */
  getSignalPerformance: async (signalId: number): Promise<{ signal: Signal; performance: PerformanceData | null }> => {
    const response = await apiClient.get(`/api/screener/signals/${signalId}/performance`);
    return response.data;
  },

  /**
   * Get performance grouped by symbol
   * @param days - Days to look back (default: 30)
   * @param minSignals - Minimum signals to include (default: 1)
   * @param limit - Max results (default: 50)
   */
  getPerformanceBySymbol: async (
    days: number = 30,
    minSignals: number = 1,
    limit: number = 50,
    userId: number = 1
  ): Promise<{ period_days: number; symbols: SymbolPerformance[] }> => {
    const response = await apiClient.get('/api/screener/performance/by-symbol', {
      params: { days, min_signals: minSignals, limit, user_id: userId },
    });
    return response.data;
  },
};

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Export signals to CSV
 */
export const exportSignalsToCSV = (signals: Signal[], filename: string = 'signals.csv') => {
  if (signals.length === 0) {
    alert('No signals to export');
    return;
  }

  // Create CSV header
  const headers = ['Symbol', 'Signal Type', 'Date', 'Price', 'RSI', 'ADX', 'Metadata'];
  
  // Create CSV rows
  const rows = signals.map(signal => [
    signal.symbol,
    signal.signal_type,
    signal.signal_date,
    signal.price.toFixed(2),
    signal.rsi?.toFixed(2) || '-',
    signal.adx?.toFixed(2) || '-',
    JSON.stringify(signal.metadata)
  ]);

  // Combine headers and rows
  const csvContent = [
    headers.join(','),
    ...rows.map(row => row.join(','))
  ].join('\n');

  // Create download link
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  
  link.setAttribute('href', url);
  link.setAttribute('download', filename);
  link.style.visibility = 'hidden';
  
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

/**
 * Format date for display
 */
export const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleDateString('tr-TR', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
};

/**
 * Get signal type color
 */
export const getSignalTypeColor = (signalType: string): string => {
  const colors: Record<string, string> = {
    'ALTIN KIRILIM': 'yellow',
    'ZİRVE KIRILIMI': 'orange',
    'TREND BAŞLANGIÇ': 'purple',
    'PULLBACK AL': 'blue',
    'DİRENÇ REDDİ': 'red',
    'KURUMSAL DİP': 'gray',
    'DİP AL': 'cyan',
  };
  return colors[signalType] || 'blue';
};
