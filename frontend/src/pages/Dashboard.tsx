import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { controlApi } from '../api/control';
import type { DashboardStats } from '../api/control';
import { Activity, AlertTriangle, ShieldCheck, Zap } from 'lucide-react';

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchStats = async () => {
    try {
      const data = await controlApi.getDashboardStats();
      setStats(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 5000); // Poll every 5s
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div className="p-8 text-slate-400 animate-pulse">Cargando cabina de mando...</div>;
  if (!stats) return <div className="p-8 text-red-400 bg-red-900/10 border border-red-900/50 rounded-lg">Error al cargar estado del sistema. Verifique conexión.</div>;

  const getSystemStatus = () => {
    if (stats.autonomy_states.errors > 0) return { label: 'AI ERROR - ATENCIÓN REQUERIDA', color: 'bg-red-950/50 text-red-400 border-red-900 animate-pulse shadow-[0_0_15px_rgba(239,68,68,0.5)]' };
    if (stats.autonomy_states.manually_overridden > 0) return { label: 'INTERVENCIÓN MANUAL ACTIVA', color: 'bg-amber-950/50 text-amber-400 border-amber-900 shadow-[0_0_15px_rgba(245,158,11,0.3)]' };
    if (!stats.global_autonomy_enabled) return { label: 'SISTEMA DETENIDO (KILL SWITCH)', color: 'bg-slate-900 text-slate-400 border-slate-700' };
    if (stats.autonomy_states.active > 0) return { label: 'AUTONOMÍA ACTIVA', color: 'bg-emerald-950/50 text-emerald-400 border-emerald-900 shadow-[0_0_15px_rgba(16,185,129,0.3)]' };
    return { label: 'EN ESPERA', color: 'bg-slate-900/50 text-slate-400 border-slate-800' };
  };

  const status = getSystemStatus();

  return (
    <div className="space-y-6">
      {/* System Status Banner */}
      <div className={`p-4 rounded-xl border flex flex-col sm:flex-row items-center justify-between transition-all duration-300 ${status.color}`}>
        <div className="flex items-center gap-3 mb-2 sm:mb-0">
          {stats.autonomy_states.errors > 0 ? <AlertTriangle size={32} /> : <ShieldCheck size={32} />}
          <div>
            <h2 className="text-xl font-bold tracking-tight">ESTADO DEL SISTEMA</h2>
            <p className="text-sm font-mono font-semibold opacity-80">{status.label}</p>
          </div>
        </div>
        <div className="text-right">
           <span className="text-xs uppercase font-bold tracking-wider opacity-60">Actualizado: {new Date().toLocaleTimeString()}</span>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div 
          onClick={() => navigate('/campaigns')}
          className="bg-slate-900/50 backdrop-blur-sm p-6 rounded-xl border border-slate-800 shadow-lg hover:border-indigo-500/50 hover:bg-slate-800/50 transition-all cursor-pointer group"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-slate-400 font-medium text-sm uppercase tracking-wider group-hover:text-indigo-400 transition-colors">Campañas Totales</h3>
            <Activity className="text-indigo-400 drop-shadow-[0_0_5px_rgba(129,140,248,0.5)] group-hover:scale-110 transition-transform" size={24} />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold text-slate-200 group-hover:text-white transition-colors">{stats.campaigns.total}</span>
            <span className="text-sm text-slate-500">definidas</span>
          </div>
          <div className="mt-4 flex gap-2 text-sm">
             <span className="px-2 py-1 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded-md font-medium">
               {stats.campaigns.active_status} Activas
             </span>
             <span className="px-2 py-1 bg-slate-800 text-slate-400 border border-slate-700 rounded-md font-medium">
               {stats.campaigns.paused_status} Pausadas
             </span>
          </div>
        </div>

        <div 
          onClick={() => navigate('/control')}
          className="bg-slate-900/50 backdrop-blur-sm p-6 rounded-xl border border-slate-800 shadow-lg hover:border-amber-500/50 hover:bg-slate-800/50 transition-all cursor-pointer group"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-slate-400 font-medium text-sm uppercase tracking-wider group-hover:text-amber-400 transition-colors">Estado Autonomía</h3>
            <Zap className="text-amber-400 drop-shadow-[0_0_5px_rgba(251,191,36,0.5)] group-hover:scale-110 transition-transform" size={24} />
          </div>
           <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold text-slate-200 group-hover:text-white transition-colors">{stats.autonomy_states.active}</span>
            <span className="text-sm text-slate-500">auto-pilotando</span>
          </div>
          <div className="mt-4 flex gap-2 text-sm flex-wrap">
             <span className="px-2 py-1 bg-amber-500/10 text-amber-400 border border-amber-500/20 rounded-md font-medium">
               {stats.autonomy_states.paused} Auto-Pausadas
             </span>
             {stats.autonomy_states.errors > 0 && (
                 <span className="px-2 py-1 bg-red-500/10 text-red-400 border border-red-500/20 rounded-md font-bold flex items-center gap-1 animate-pulse">
                   <AlertTriangle size={12} /> {stats.autonomy_states.errors} Errores
                 </span>
             )}
          </div>
        </div>

        <div 
          onClick={() => navigate('/overrides')}
          className="bg-slate-900/50 backdrop-blur-sm p-6 rounded-xl border border-slate-800 shadow-lg hover:border-red-500/50 hover:bg-slate-800/50 transition-all cursor-pointer group"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-slate-400 font-medium text-sm uppercase tracking-wider group-hover:text-red-400 transition-colors">Intervenciones Manuales</h3>
            <AlertTriangle className="text-red-500 drop-shadow-[0_0_5px_rgba(239,68,68,0.5)] group-hover:scale-110 transition-transform" size={24} />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold text-slate-200 group-hover:text-white transition-colors">{stats.autonomy_states.manually_overridden}</span>
            <span className="text-sm text-slate-500">override activos</span>
          </div>
          <p className="mt-4 text-xs text-slate-500 group-hover:text-slate-400 transition-colors">
             Campañas donde el humano ha tomado el control total.
          </p>
        </div>
      </div>
      
      {/* Recent Alerts Mockup (Placeholder for future Alert API) */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-slate-900/50 backdrop-blur-sm rounded-xl border border-slate-800 shadow-lg overflow-hidden hover:border-slate-700 transition-colors">
            <div className="px-6 py-4 border-b border-slate-800 bg-slate-900/80 flex justify-between items-center">
                <h3 className="font-semibold text-slate-200">Alertas Recientes & Logs</h3>
                <span className="text-xs text-slate-500 font-mono">Live Feed</span>
            </div>
            <div className="p-6 text-center text-slate-500 py-12 font-mono text-sm">
                <p>Sistema operando nominalmente. No hay alertas críticas recientes.</p>
                {/* Future: Map through logs/alerts here */}
            </div>
          </div>

          <div className="bg-slate-900/50 backdrop-blur-sm rounded-xl border border-slate-800 shadow-lg overflow-hidden hover:border-slate-700 transition-colors">
            <div className="px-6 py-4 border-b border-slate-800 bg-slate-900/80 flex justify-between items-center">
                <h3 className="font-semibold text-slate-200">Última Acción Humana</h3>
                <span className="text-xs text-slate-500 font-mono">Audit Log</span>
            </div>
            <div className="p-6">
                {stats.last_human_action ? (
                    <div className="flex items-start gap-4">
                        <div className="p-3 bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 rounded-full shadow-[0_0_10px_rgba(129,140,248,0.2)]">
                            <ShieldCheck size={24} />
                        </div>
                        <div>
                            <h4 className="font-bold text-slate-200">{stats.last_human_action.decision}</h4>
                            <p className="text-slate-400 text-sm mt-1">{stats.last_human_action.reason}</p>
                            <p className="text-xs text-slate-600 mt-2 font-mono">
                                {new Date(stats.last_human_action.created_at).toLocaleString()}
                            </p>
                        </div>
                    </div>
                ) : (
                    <div className="text-center text-slate-500 py-8 font-mono text-sm">
                        <p>No se han registrado intervenciones manuales recientes.</p>
                    </div>
                )}
            </div>
          </div>
      </div>
    </div>
  );
};
