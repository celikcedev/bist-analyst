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
