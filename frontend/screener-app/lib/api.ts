import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface Signal {
  id: number;
  symbol: string;
  signal_type: string;
  signal_date: string;
  price: number;
  rsi?: number;
  adx?: number;
  signal_metadata?: Record<string, any>;
}

export interface Strategy {
  id: number;
  name: string;
  display_name: string;
  description: string;
  is_active: boolean;
}

export interface StrategyParameter {
  id: number;
  strategy_id: number;
  parameter_name: string;
  parameter_value: string | number | boolean;
  parameter_type: string;
  display_name: string;
  display_group?: string;
  display_order: number;
}

export interface Ticker {
  id: number;
  symbol: string;
  name: string;
  exchange: string;
  is_active: boolean;
}

export interface ScanRequest {
  strategy_name: string;
  signal_types?: string[];
  parameters?: Record<string, any>;
}

export interface ScanResponse {
  strategy: string;
  total_symbols_scanned: number;
  signals_found: number;
  scan_date: string;
  signals: Signal[];
}

// API Functions
export const getStrategies = async (): Promise<Strategy[]> => {
  const response = await apiClient.get('/api/screener/strategies');
  return response.data.strategies;
};

export const getStrategyParameters = async (strategyName: string): Promise<StrategyParameter[]> => {
  const response = await apiClient.get(`/api/screener/strategies/${strategyName}/parameters`);
  return response.data.parameters;
};

export const updateStrategyParameters = async (
  strategyName: string,
  parameters: Record<string, any>
): Promise<void> => {
  await apiClient.put(`/api/screener/strategies/${strategyName}/parameters`, { parameters });
};

export const runScan = async (request: ScanRequest): Promise<ScanResponse> => {
  const response = await apiClient.post('/api/screener/scan', request);
  return response.data;
};

export const getTickers = async (): Promise<Ticker[]> => {
  const response = await apiClient.get('/api/market-data/tickers?limit=1000');
  return response.data.tickers;
};

export const getSignalHistory = async (params?: {
  strategy_name?: string;
  signal_type?: string;
  limit?: number;
}): Promise<Signal[]> => {
  const response = await apiClient.get('/api/screener/signals', { params });
  return response.data.signals;
};

export default apiClient;
