'use client';

import { X } from 'lucide-react';
import { useState, useEffect } from 'react';
// Deprecated: Use Strategy Management page instead (/strategies)
// import { api, type StrategyParameters } from '@/lib/api';

interface StrategyParameter {
  parameter_name: string;
  parameter_value: any;
  parameter_type: string;
}

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
      // Deprecated: Redirect to /strategies page
      console.warn('ParameterModal is deprecated. Use /strategies page instead.');
      setParameters([]);
      setLocalValues({});
    } catch (error) {
      console.error('Failed to load parameters:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      // Deprecated: Use /strategies page
      console.warn('ParameterModal save is deprecated. Use /strategies page instead.');
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
    <div 
      className="fixed inset-0 bg-black/80 backdrop-blur-sm z-[9999] p-4 animate-in fade-in duration-200"
      onClick={onClose}
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}
    >
      <div 
        className="bg-tv-dark-card rounded-2xl w-full max-w-2xl max-h-[90vh] flex flex-col shadow-2xl shadow-tv-dark-primary/20 border-2 border-tv-dark-border/50 animate-in slide-in-from-bottom-4 duration-300"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header with gradient */}
        <div className="relative overflow-hidden p-6 border-b border-tv-dark-border/50">
          <div className="absolute inset-0 bg-gradient-card opacity-50"></div>
          <div className="relative flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold text-tv-dark-text flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-primary flex items-center justify-center">
                  <span className="text-white font-bold text-sm">X27</span>
                </div>
                {strategyDisplayName}
              </h2>
              <p className="text-sm text-tv-dark-textMuted mt-1">Strateji parametrelerini özelleştirin</p>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-tv-dark-surface rounded-xl transition-all hover:rotate-90 duration-300"
            >
              <X className="w-6 h-6 text-tv-dark-textMuted hover:text-tv-dark-text transition-colors" />
            </button>
          </div>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar">
          {loading ? (
            <div className="text-center py-16">
              <div className="inline-flex flex-col items-center gap-4">
                <div className="relative">
                  <div className="w-16 h-16 border-4 border-tv-dark-border rounded-full"></div>
                  <div className="absolute top-0 left-0 w-16 h-16 border-4 border-tv-dark-primary border-t-transparent rounded-full animate-spin"></div>
                </div>
                <p className="text-tv-dark-textMuted font-medium">Parametreler yükleniyor...</p>
              </div>
            </div>
          ) : (
            Object.keys(groupedParams).map((group, groupIndex) => (
              <div key={group} className="bg-tv-dark-surface rounded-xl p-5 border border-tv-dark-border/50 hover:border-tv-dark-border transition-all">
                <div className="flex items-center gap-3 mb-4">
                  <div className={`w-1 h-6 rounded-full ${groupIndex % 3 === 0 ? 'bg-gradient-primary' : groupIndex % 3 === 1 ? 'bg-gradient-success' : 'bg-gradient-secondary'}`}></div>
                  <h3 className="text-sm font-bold text-tv-dark-text uppercase tracking-wide">
                    {group}
                  </h3>
                </div>
                <div className="space-y-4">
                  {groupedParams[group].map(param => (
                    <div key={param.id} className="flex items-center justify-between py-2">
                      <label className="text-sm text-tv-dark-text font-medium flex-1">
                        {param.display_name}
                      </label>
                      <div className="w-36">
                        {param.parameter_type === 'bool' ? (
                          <label className="flex items-center justify-end gap-2 cursor-pointer group">
                            <input
                              type="checkbox"
                              checked={localValues[param.parameter_name] === true}
                              onChange={(e) =>
                                handleChange(param.parameter_name, e.target.checked, param.parameter_type)
                              }
                              className="w-5 h-5 rounded-md border-2 border-tv-dark-border bg-tv-dark-bg checked:bg-gradient-primary checked:border-tv-dark-primary transition-all cursor-pointer"
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
                            className="w-full px-4 py-2 bg-tv-dark-bg border-2 border-tv-dark-border rounded-lg text-sm text-tv-dark-text font-medium focus:outline-none focus:border-tv-dark-primary focus:ring-2 focus:ring-tv-dark-primary/20 transition-all"
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
        <div className="flex items-center justify-end gap-3 p-6 border-t border-tv-dark-border/50 bg-tv-dark-surface/50">
          <button
            onClick={onClose}
            disabled={saving}
            className="px-6 py-2.5 text-sm font-semibold text-tv-dark-textMuted hover:text-tv-dark-text hover:bg-tv-dark-surface rounded-xl transition-all disabled:opacity-50"
          >
            İptal
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="relative px-8 py-2.5 text-sm font-bold bg-gradient-primary text-white rounded-xl hover:shadow-glow-md transition-all disabled:opacity-50 overflow-hidden group"
          >
            <span className="relative z-10">{saving ? 'Kaydediliyor...' : 'Kaydet ve Uygula'}</span>
            <div className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700"></div>
          </button>
        </div>
      </div>
    </div>
  );
}
