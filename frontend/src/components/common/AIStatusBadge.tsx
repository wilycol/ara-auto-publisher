import React, { useEffect, useState } from 'react';
import { BrainCircuit, Wifi, WifiOff, RefreshCw } from 'lucide-react';
import apiClient from '../../api/client';

interface AIHealth {
  status: 'connected' | 'disconnected';
  provider: string;
  is_real_ai: boolean;
}

export const AIStatusBadge: React.FC = () => {
  const [health, setHealth] = useState<AIHealth | null>(null);
  const [loading, setLoading] = useState(true);

  const checkHealth = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get('/health/ai');
      setHealth(response.data);
    } catch (error) {
      setHealth({ status: 'disconnected', provider: 'none', is_real_ai: false });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkHealth();
    // Poll every 2 minutes to be polite
    const interval = setInterval(checkHealth, 120000);
    return () => clearInterval(interval);
  }, []);

  if (!health && loading) return (
    <div className="animate-pulse flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-800/50 border border-slate-700 w-24 h-8"></div>
  );

  const isConnected = health?.status === 'connected';
  const isReal = health?.is_real_ai;

  return (
    <button 
        onClick={checkHealth}
        className={`flex items-center gap-2 px-3 py-1.5 rounded-full border text-xs font-medium transition-all hover:opacity-80 ${
        isConnected 
            ? isReal 
            ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20 hover:bg-emerald-500/20'
            : 'bg-amber-500/10 text-amber-400 border-amber-500/20 hover:bg-amber-500/20'
            : 'bg-red-500/10 text-red-400 border-red-500/20 hover:bg-red-500/20'
        }`}
        title={isConnected ? `Proveedor: ${health?.provider}` : 'Error de conexión con IA'}
    >
      <BrainCircuit size={14} />
      <span className="hidden sm:inline">
        {loading ? 'Verificando...' : (isConnected ? (isReal ? `Cerebro Activo (${health?.provider})` : 'Modo Local') : 'IA Desconectada')}
      </span>
      <span className="sm:hidden">
        {loading ? '...' : (isConnected ? 'IA' : 'Offline')}
      </span>
      {loading ? <RefreshCw size={12} className="animate-spin" /> : (isConnected ? <Wifi size={12} /> : <WifiOff size={12} />)}
    </button>
  );
};
