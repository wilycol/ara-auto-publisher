import React, { useEffect, useState } from 'react';
import { controlApi } from '../api/control';
import type { Recommendation } from '../api/control';
import { CheckCircle, XCircle, Clock } from 'lucide-react';

export const HumanControl: React.FC = () => {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchRecommendations = async () => {
    try {
      setLoading(true);
      const data = await controlApi.getRecommendations('PENDING');
      setRecommendations(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const handleAction = async (id: number, action: 'APPROVE' | 'REJECT') => {
    if (!confirm(`Are you sure you want to ${action} this recommendation?`)) return;
    
    try {
      await controlApi.actOnRecommendation(id, action);
      // Remove from list immediately
      setRecommendations(prev => prev.filter(r => r.id !== id));
    } catch (err) {
      alert('Error processing action');
      console.error(err);
    }
  };

  if (loading && recommendations.length === 0) return <div className="p-8 text-slate-400 animate-pulse">Cargando recomendaciones...</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-slate-200">Panel de Recomendaciones</h2>
        <button 
          onClick={fetchRecommendations}
          className="px-4 py-2 bg-slate-800 border border-slate-700 text-slate-300 rounded-lg text-sm font-medium hover:bg-slate-700 hover:text-white transition-colors"
        >
          Refrescar
        </button>
      </div>

      {recommendations.length === 0 ? (
        <div className="bg-slate-900/50 backdrop-blur-sm p-12 rounded-xl border border-slate-800 text-center">
           <div className="w-16 h-16 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded-full flex items-center justify-center mx-auto mb-4 shadow-[0_0_15px_rgba(16,185,129,0.2)]">
             <CheckCircle size={32} />
           </div>
           <h3 className="text-lg font-medium text-slate-200">Todo limpio</h3>
           <p className="text-slate-500 mt-2">No hay recomendaciones pendientes de revisión humana.</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {recommendations.map((rec) => (
            <div key={rec.id} className="bg-slate-900/50 backdrop-blur-sm p-6 rounded-xl border border-slate-800 shadow-lg hover:border-slate-700 transition-colors">
              <div className="flex flex-col md:flex-row justify-between items-start gap-4">
                <div className="space-y-2 w-full">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className={`px-2 py-1 rounded-md text-xs font-bold uppercase tracking-wide border
                      ${rec.type.includes('BLOCK') || rec.type.includes('ROLLBACK') 
                        ? 'bg-red-500/10 text-red-400 border-red-500/20' 
                        : 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20'}
                    `}>
                      {rec.type.replace('_', ' ')}
                    </span>
                    <span className="text-sm text-slate-500 flex items-center gap-1 font-mono">
                      <Clock size={14} /> {new Date(rec.created_at).toLocaleString()}
                    </span>
                  </div>
                  
                  <h3 className="text-lg font-semibold text-slate-200">
                    Campaña: {rec.automation_name}
                  </h3>
                  
                  <p className="text-slate-400">
                    {rec.reasoning}
                  </p>
                  
                  {rec.suggested_value && (
                    <div className="bg-slate-950 p-3 rounded-lg text-sm font-mono text-slate-300 mt-2 block w-full border border-slate-800 overflow-x-auto">
                      Suggested Change: {JSON.stringify(rec.suggested_value, null, 2)}
                    </div>
                  )}
                </div>

                <div className="flex flex-row md:flex-col gap-2 w-full md:w-auto shrink-0">
                  <button
                    onClick={() => handleAction(rec.id, 'APPROVE')}
                    className="flex-1 md:flex-none flex items-center justify-center gap-2 px-4 py-2 bg-emerald-600/20 text-emerald-400 border border-emerald-600/50 rounded-lg hover:bg-emerald-600/30 font-medium text-sm transition-all duration-200 hover:shadow-[0_0_10px_rgba(16,185,129,0.2)]"
                  >
                    <CheckCircle size={16} />
                    Aprobar
                  </button>
                  <button
                    onClick={() => handleAction(rec.id, 'REJECT')}
                    className="flex-1 md:flex-none flex items-center justify-center gap-2 px-4 py-2 bg-red-600/20 text-red-400 border border-red-600/50 rounded-lg hover:bg-red-600/30 font-medium text-sm transition-all duration-200 hover:shadow-[0_0_10px_rgba(239,68,68,0.2)]"
                  >
                    <XCircle size={16} />
                    Rechazar
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
