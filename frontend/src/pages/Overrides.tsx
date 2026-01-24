import React, { useState } from 'react';
import { controlApi } from '../api/control';
import { AlertOctagon, Lock, ShieldAlert } from 'lucide-react';

export const Overrides: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const handleEmergencyStop = async () => {
    if (!confirm("⛔ ¿ESTÁS SEGURO? Esto detendrá TODAS las campañas activas inmediatamente.")) return;
    
    const doubleCheck = prompt("Escribe 'PARAR' para confirmar:");
    if (doubleCheck !== "PARAR") return;

    try {
      setLoading(true);
      const res = await controlApi.emergencyStop();
      setSuccessMsg(`🛑 PARADA DE EMERGENCIA EJECUTADA: ${res.stopped_campaigns} campañas detenidas.`);
    } catch (err) {
      alert("Error al ejecutar parada de emergencia");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <div className="bg-red-500/10 border-l-4 border-red-500 p-6 rounded-r-xl backdrop-blur-sm">
        <div className="flex items-start gap-4">
          <ShieldAlert className="text-red-500 mt-1 drop-shadow-[0_0_8px_rgba(239,68,68,0.5)]" size={32} />
          <div>
            <h2 className="text-2xl font-bold text-red-400">Control de Emergencia</h2>
            <p className="text-red-300/80 mt-1">
              Si algo no se ve bien, tienes el control total para detener el sistema aquí.
              Todas las acciones quedarán registradas para auditoría.
            </p>
          </div>
        </div>
      </div>

      {successMsg && (
        <div className="bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 p-4 rounded-lg flex items-center gap-2 shadow-[0_0_15px_rgba(16,185,129,0.2)]">
          <AlertOctagon size={20} />
          {successMsg}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Global Controls */}
        <div className="bg-slate-900/50 p-8 rounded-xl border border-red-500/30 shadow-lg backdrop-blur-sm hover:border-red-500/50 transition-colors">
          <h3 className="text-lg font-bold text-slate-200 mb-6 flex items-center gap-2">
            <AlertOctagon className="text-red-500 drop-shadow-[0_0_5px_rgba(239,68,68,0.5)]" />
            Control Global
          </h3>
          
          <div className="space-y-4">
            <button
              onClick={handleEmergencyStop}
              disabled={loading}
              className="w-full py-6 bg-red-600/90 hover:bg-red-500 text-white rounded-xl font-bold text-xl shadow-[0_0_20px_rgba(220,38,38,0.4)] hover:shadow-[0_0_30px_rgba(220,38,38,0.6)] transition-all flex items-center justify-center gap-3 active:scale-95 border border-red-400/20"
            >
              {loading ? "DETENIENDO..." : "⛔ DETENER TODO EL SISTEMA"}
            </button>
            <p className="text-sm text-slate-500 text-center px-4">
              Esto pausará todas las campañas y bloqueará la autonomía. Nada se publicará hasta que tú lo reactives manualmente.
            </p>
          </div>
        </div>

        {/* Per-Campaign Override Hint */}
        <div className="bg-slate-900/50 p-8 rounded-xl border border-slate-800 backdrop-blur-sm">
           <h3 className="text-lg font-bold text-slate-200 mb-4 flex items-center gap-2">
            <Lock className="text-slate-500" />
            Controles por Campaña
          </h3>
          <p className="text-slate-400 mb-6">
            Si solo quieres detener o modificar una campaña específica (sin apagar todo), ve al listado de campañas.
          </p>
          <a href="/campaigns" className="block w-full text-center py-3 bg-slate-800 border border-slate-700 rounded-lg text-amber-400 font-bold hover:bg-slate-700 hover:text-amber-300 transition-all hover:shadow-[0_0_10px_rgba(251,191,36,0.2)]">
            Ir a Mis Campañas &rarr;
          </a>
        </div>
      </div>
    </div>
  );
};
