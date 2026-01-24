import React, { useEffect, useState } from 'react';
import { getTrackingReport, downloadReport } from '../api/tracking';
import type { TrackingEntry } from '../api/tracking';

export const Tracking: React.FC = () => {
  const [data, setData] = useState<TrackingEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [projectId, setProjectId] = useState<number | undefined>(undefined);

  const loadData = async () => {
    setLoading(true);
    try {
      const res = await getTrackingReport(projectId);
      setData(res.data);
    } catch (e) {
      console.error("Failed to load tracking", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [projectId]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col xl:flex-row justify-between items-start xl:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-amber-400 to-amber-600">
            Registro de Producción
          </h1>
          <p className="text-slate-400 mt-1">Historial detallado de todas las acciones del sistema</p>
        </div>
        <div className="flex flex-wrap gap-2 w-full xl:w-auto">
          <button 
            onClick={() => downloadReport('csv', projectId)} 
            className="flex-1 xl:flex-none px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg border border-slate-700 transition-colors text-sm font-medium"
          >
            Export CSV
          </button>
          <button 
            onClick={() => downloadReport('xlsx', projectId)} 
            className="flex-1 xl:flex-none px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg border border-slate-700 transition-colors text-sm font-medium"
          >
            Export Excel
          </button>
          <button 
            onClick={() => downloadReport('json', projectId)} 
            className="flex-1 xl:flex-none px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg border border-slate-700 transition-colors text-sm font-medium"
          >
            Export JSON
          </button>
        </div>
      </div>

      <div className="bg-slate-900/50 backdrop-blur-sm p-4 rounded-xl border border-slate-800 flex items-center gap-4">
        <label className="text-slate-400 text-sm font-medium">Filtrar Proyecto ID:</label>
        <input 
          type="number" 
          value={projectId || ''} 
          onChange={(e) => setProjectId(e.target.value ? parseInt(e.target.value) : undefined)}
          className="bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-amber-500/50 focus:border-amber-500/50 w-32 placeholder-slate-600"
          placeholder="Todos"
        />
      </div>

      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-amber-500 mx-auto"></div>
        </div>
      ) : (
        <div className="bg-slate-900/50 backdrop-blur-sm rounded-xl shadow-lg border border-slate-800 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-800">
              <thead className="bg-slate-800/50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">ID</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Fecha</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Proyecto</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Plataforma</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Tipo</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Estado</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Objetivo</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">URL</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {data.map((row) => (
                  <tr key={row.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500 font-mono">#{row.id}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-400">{new Date(row.created_at).toLocaleString()}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-200 font-medium">{row.project_name || '-'}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-xs font-bold px-2 py-1 rounded bg-slate-800 text-slate-300 border border-slate-700 uppercase">
                        {row.platform}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-300">{row.type}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 rounded-md text-xs font-medium border ${
                        row.status === 'published' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 
                        row.status === 'generated' ? 'bg-blue-500/10 text-blue-400 border-blue-500/20' : 
                        'bg-slate-800 text-slate-400 border-slate-700'
                      }`}>
                        {row.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-400 max-w-xs truncate" title={row.objective}>{row.objective}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {row.url ? (
                        <a href={row.url} target="_blank" rel="noreferrer" className="text-amber-400 hover:text-amber-300 hover:underline flex items-center gap-1">
                          Ver Link ↗
                        </a>
                      ) : (
                        <span className="text-slate-600">-</span>
                      )}
                    </td>
                  </tr>
                ))}
                {data.length === 0 && (
                  <tr>
                    <td colSpan={8} className="px-6 py-12 text-center text-slate-500">
                      No se encontraron registros de tracking
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
