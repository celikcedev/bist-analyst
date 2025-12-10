'use client';

import { useEffect, useState } from 'react';
import { api, type Strategy, type StrategyParameters } from '@/lib/api';

export default function StrategiesPage() {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [selectedStrategy, setSelectedStrategy] = useState<string | null>(null);
  const [parameters, setParameters] = useState<StrategyParameters>({});
  const [originalParameters, setOriginalParameters] = useState<StrategyParameters>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Fetch strategies on mount
  useEffect(() => {
    fetchStrategies();
  }, []);

  // Fetch parameters when strategy changes
  useEffect(() => {
    if (selectedStrategy) {
      fetchParameters(selectedStrategy);
    }
  }, [selectedStrategy]);

  const fetchStrategies = async () => {
    try {
      setLoading(true);
      const data = await api.getStrategies();
      setStrategies(data.strategies);
      if (data.strategies.length > 0 && !selectedStrategy) {
        setSelectedStrategy(data.strategies[0].name);
      }
    } catch (error: any) {
      showMessage('error', 'Failed to load strategies: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchParameters = async (strategyName: string) => {
    try {
      const data = await api.getStrategyParameters(strategyName);
      setParameters(data);
      setOriginalParameters(JSON.parse(JSON.stringify(data))); // Deep copy
    } catch (error: any) {
      showMessage('error', 'Failed to load parameters: ' + error.message);
    }
  };

  const handleSave = async () => {
    if (!selectedStrategy) return;

    try {
      setSaving(true);
      await api.updateStrategyParameters(selectedStrategy, parameters);
      setOriginalParameters(JSON.parse(JSON.stringify(parameters)));
      showMessage('success', 'Parameters saved successfully!');
    } catch (error: any) {
      showMessage('error', 'Failed to save parameters: ' + error.message);
    } finally {
      setSaving(false);
    }
  };

  const handleReset = () => {
    setParameters(JSON.parse(JSON.stringify(originalParameters)));
    showMessage('success', 'Parameters reset to saved values');
  };

  const showMessage = (type: 'success' | 'error', text: string) => {
    setMessage({ type, text });
    setTimeout(() => setMessage(null), 5000);
  };

  const handleParameterChange = (key: string, value: any) => {
    setParameters(prev => ({ ...prev, [key]: value }));
  };

  const hasChanges = JSON.stringify(parameters) !== JSON.stringify(originalParameters);

  const renderParameterInput = (key: string, value: any) => {
    const type = typeof value;

    if (type === 'boolean') {
      return (
        <label className="flex items-center gap-3 cursor-pointer">
          <input
            type="checkbox"
            checked={value}
            onChange={(e) => handleParameterChange(key, e.target.checked)}
            className="w-5 h-5 rounded border-gray-600 bg-gray-700 text-blue-600 focus:ring-2 focus:ring-blue-500"
          />
          <span className="text-gray-300">{value ? 'Enabled' : 'Disabled'}</span>
        </label>
      );
    }

    if (type === 'number') {
      return (
        <input
          type="number"
          value={value}
          onChange={(e) => handleParameterChange(key, parseFloat(e.target.value) || 0)}
          className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          step={value % 1 === 0 ? 1 : 0.1}
        />
      );
    }

    return (
      <input
        type="text"
        value={String(value)}
        onChange={(e) => handleParameterChange(key, e.target.value)}
        className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-300">Loading strategies...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700 shadow-lg">
        <div className="container mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white">Strategy Management</h1>
              <p className="text-gray-400 mt-1">Configure trading strategy parameters</p>
            </div>
            <a
              href="/"
              className="px-6 py-3 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition-colors font-medium"
            >
              ← Back to Screener
            </a>
          </div>
        </div>
      </header>

      {/* Message Banner */}
      {message && (
        <div className={`py-3 px-6 ${message.type === 'success' ? 'bg-green-600' : 'bg-red-600'}`}>
          <div className="container mx-auto">
            <p className="text-white font-medium">{message.text}</p>
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Strategy Selector Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
              <h2 className="text-xl font-bold text-white mb-4">Strategies</h2>
              <div className="space-y-2">
                {strategies.map((strategy) => (
                  <button
                    key={strategy.id}
                    onClick={() => setSelectedStrategy(strategy.name)}
                    className={`w-full text-left px-4 py-3 rounded-lg transition-colors ${
                      selectedStrategy === strategy.name
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                    }`}
                  >
                    <div className="font-semibold">{strategy.display_name}</div>
                    <div className="text-xs mt-1 opacity-75">{strategy.description}</div>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Parameters Panel */}
          <div className="lg:col-span-3">
            <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-white">Parameters</h2>
                <div className="flex gap-3">
                  <button
                    onClick={handleReset}
                    disabled={!hasChanges || saving}
                    className="px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Reset
                  </button>
                  <button
                    onClick={handleSave}
                    disabled={!hasChanges || saving}
                    className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium flex items-center gap-2"
                  >
                    {saving ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        <span>Saving...</span>
                      </>
                    ) : (
                      'Save Changes'
                    )}
                  </button>
                </div>
              </div>

              {Object.keys(parameters).length === 0 ? (
                <div className="text-center py-12">
                  <p className="text-gray-400">No parameters available for this strategy</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {Object.entries(parameters).map(([key, value]) => (
                    <div key={key} className="space-y-2">
                      <label className="block text-sm font-medium text-gray-300">
                        {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </label>
                      {renderParameterInput(key, value)}
                      <p className="text-xs text-gray-500">
                        Type: {typeof value} | Current: {String(value)}
                      </p>
                    </div>
                  ))}
                </div>
              )}

              {hasChanges && (
                <div className="mt-6 p-4 bg-yellow-900/20 border border-yellow-700 rounded-lg">
                  <p className="text-yellow-400 text-sm">
                    ⚠️ You have unsaved changes. Click "Save Changes" to apply them.
                  </p>
                </div>
              )}
            </div>

            {/* Strategy Info */}
            {selectedStrategy && (
              <div className="mt-6 bg-gray-800 rounded-lg border border-gray-700 p-6">
                <h3 className="text-lg font-bold text-white mb-3">About This Strategy</h3>
                <div className="space-y-2 text-gray-300">
                  <p>
                    <span className="font-semibold">Name:</span>{' '}
                    {strategies.find(s => s.name === selectedStrategy)?.display_name}
                  </p>
                  <p>
                    <span className="font-semibold">Description:</span>{' '}
                    {strategies.find(s => s.name === selectedStrategy)?.description}
                  </p>
                  <p>
                    <span className="font-semibold">Status:</span>{' '}
                    <span className="text-green-400">Active</span>
                  </p>
                  <p className="text-sm text-gray-400 mt-4">
                    💡 <strong>Tip:</strong> Changes will take effect on the next scan. Make sure to test your
                    parameters before running a full scan.
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
