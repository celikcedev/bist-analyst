'use client';

import { X } from 'lucide-react';
import { useState, useEffect } from 'react';
import { StrategyParameter, getStrategyParameters, updateStrategyParameters } from '@/lib/api';

interface ParameterModalProps {
  isOpen: boolean;
  onClose: () => void;
  strategyName: string;
  strategyDisplayName: string;
}

export default function ParameterModal({
  isOpen,
  onClose,
  strategyName,
  strategyDisplayName,
}: ParameterModalProps) {
  const [parameters, setParameters] = useState<StrategyParameter[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [localValues, setLocalValues] = useState<Record<string, any>>({});

  useEffect(() => {
    if (isOpen && strategyName) {
      loadParameters();
    }
  }, [isOpen, strategyName]);

  const loadParameters = async () => {
    setLoading(true);
    try {
      const data = await getStrategyParameters(strategyName);
      setParameters(data);
      
      // Initialize local values
      const values: Record<string, any> = {};
      data.forEach(param => {
        values[param.parameter_name] = param.parameter_value;
      });
      setLocalValues(values);
    } catch (error) {
      console.error('Failed to load parameters:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await updateStrategyParameters(strategyName, localValues);
      onClose();
    } catch (error) {
      console.error('Failed to save parameters:', error);
      alert('Parametreler kaydedilemedi. Lütfen tekrar deneyin.');
    } finally {
      setSaving(false);
    }
  };

  const handleChange = (name: string, value: any, type: string) => {
    let parsedValue = value;
    
    if (type === 'int') {
      parsedValue = parseInt(value) || 0;
    } else if (type === 'float') {
      parsedValue = parseFloat(value) || 0;
    } else if (type === 'bool') {
      parsedValue = value === 'true' || value === true;
    }
    
    setLocalValues(prev => ({ ...prev, [name]: parsedValue }));
  };

  // Group parameters by display_group
  const groupedParams: Record<string, StrategyParameter[]> = {};
  parameters.forEach(param => {
    const group = param.display_group || 'GENEL AYARLAR';
    if (!groupedParams[group]) {
      groupedParams[group] = [];
    }
    groupedParams[group].push(param);
  });

  // Sort parameters within each group by display_order
  Object.keys(groupedParams).forEach(group => {
    groupedParams[group].sort((a, b) => a.display_order - b.display_order);
  });

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div className="bg-tv-dark-surface rounded-lg w-full max-w-2xl max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-tv-dark-border">
          <h2 className="text-lg font-semibold text-tv-dark-text">
            {strategyDisplayName}
          </h2>
          <button
            onClick={onClose}
            className="p-1 hover:bg-tv-dark-border rounded transition-colors"
          >
            <X className="w-5 h-5 text-tv-dark-textMuted" />
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto p-4 space-y-6">
          {loading ? (
            <div className="text-center py-8 text-tv-dark-textMuted">
              Parametreler yükleniyor...
            </div>
          ) : (
            Object.keys(groupedParams).map(group => (
              <div key={group}>
                <h3 className="text-xs font-semibold text-tv-dark-textMuted uppercase tracking-wider mb-3">
                  {group}
                </h3>
                <div className="space-y-3">
                  {groupedParams[group].map(param => (
                    <div key={param.id} className="flex items-center justify-between">
                      <label className="text-sm text-tv-dark-text flex-1">
                        {param.display_name}
                      </label>
                      <div className="w-32">
                        {param.parameter_type === 'bool' ? (
                          <label className="flex items-center justify-end gap-2 cursor-pointer">
                            <input
                              type="checkbox"
                              checked={localValues[param.parameter_name] === true}
                              onChange={(e) =>
                                handleChange(param.parameter_name, e.target.checked, param.parameter_type)
                              }
                              className="w-4 h-4 rounded border-tv-dark-border bg-tv-dark-bg accent-tv-dark-primary"
                            />
                          </label>
                        ) : (
                          <input
                            type="number"
                            step={param.parameter_type === 'float' ? '0.01' : '1'}
                            value={localValues[param.parameter_name] ?? ''}
                            onChange={(e) =>
                              handleChange(param.parameter_name, e.target.value, param.parameter_type)
                            }
                            className="w-full px-3 py-1.5 bg-tv-dark-bg border border-tv-dark-border rounded text-sm text-tv-dark-text focus:outline-none focus:border-tv-dark-primary"
                          />
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 p-4 border-t border-tv-dark-border">
          <button
            onClick={onClose}
            disabled={saving}
            className="px-4 py-2 text-sm font-medium text-tv-dark-textMuted hover:text-tv-dark-text transition-colors"
          >
            İptal
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-4 py-2 text-sm font-medium bg-tv-dark-primary text-white rounded hover:bg-blue-700 transition-colors disabled:opacity-50"
          >
            {saving ? 'Kaydediliyor...' : 'Uygula'}
          </button>
        </div>
      </div>
    </div>
  );
}
