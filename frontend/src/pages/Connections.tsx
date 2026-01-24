import React, { useState, useEffect } from 'react';
import { Facebook, Linkedin, Instagram, Globe, Link as LinkIcon, Plus, Trash2, CheckCircle, AlertCircle, RefreshCw, Loader2 } from 'lucide-react';
import clsx from 'clsx';
import { authApi } from '../api/auth';
import type { ConnectedAccount } from '../api/auth';
import { useSearchParams } from 'react-router-dom';

export const Connections: React.FC = () => {
  const [searchParams] = useSearchParams();
  const [loading, setLoading] = useState(true);
  const [accounts, setAccounts] = useState<ConnectedAccount[]>([]);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  // Definición de plataformas soportadas
  const SUPPORTED_PLATFORMS = [
    { 
      id: 'linkedin', 
      name: 'LinkedIn', 
      icon: Linkedin, 
      color: 'text-blue-400', 
      bg: 'bg-blue-500/10',
      border: 'border-blue-500/20'
    },
    { 
      id: 'facebook', 
      name: 'Facebook', 
      icon: Facebook, 
      color: 'text-blue-500', 
      bg: 'bg-blue-600/10',
      border: 'border-blue-600/20'
    },
    { 
      id: 'instagram', 
      name: 'Instagram', 
      icon: Instagram, 
      color: 'text-pink-500', 
      bg: 'bg-pink-500/10',
      border: 'border-pink-500/20'
    }
  ];

  const [customWebhooks] = useState([
    { id: 1, name: 'Foro Tech Latam', url: 'https://foro-tech.example/api/v1/post', status: 'active' }
  ]);

  useEffect(() => {
    loadAccounts();
  }, [searchParams]);

  const loadAccounts = async () => {
    try {
      setLoading(true);
      const data = await authApi.getAccounts();
      setAccounts(data);
    } catch (err) {
      console.error('Error loading accounts', err);
    } finally {
      setLoading(false);
    }
  };

  const handleConnect = async (platformId: string) => {
    if (platformId !== 'linkedin') {
        alert('Próximamente: Integración con ' + platformId);
        return;
    }

    try {
        setActionLoading(platformId);
        const url = await authApi.getLinkedInAuthUrl();
        window.location.href = url;
    } catch (err: any) {
        console.error('Error initiating auth', err);
        const msg = err.response?.data?.detail || 'Error al conectar con LinkedIn. Verifica que el servidor tenga las credenciales configuradas.';
        alert(msg);
        setActionLoading(null);
    }
  };

  const handleDisconnect = async (accountId: number, platformId: string) => {
    if (!confirm('¿Seguro que quieres desconectar esta cuenta?')) return;
    
    try {
        setActionLoading(platformId);
        await authApi.disconnectAccount(accountId);
        await loadAccounts();
    } catch (err) {
        console.error('Error disconnecting', err);
        alert('Error al desconectar cuenta');
    } finally {
        setActionLoading(null);
    }
  };

  return (
    <div className="space-y-8 max-w-6xl mx-auto pb-12">
      {/* Header */}
      <div className="bg-slate-900/50 backdrop-blur-sm p-4 md:p-8 rounded-2xl border border-slate-800 overflow-hidden">
        <h1 className="text-xl md:text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-amber-400 to-amber-600 mb-2 break-words">
          Conexiones & Integraciones
        </h1>
        <p className="text-slate-400 text-sm md:text-base max-w-2xl">
          Gestiona dónde publica Ara Auto Publisher. Conecta redes sociales oficiales y configura webhooks.
        </p>
      </div>

      {/* Social Networks Section */}
      <div>
        <h2 className="text-xl font-semibold text-slate-200 mb-4 flex items-center gap-2">
          <Globe size={20} className="text-indigo-400" />
          Redes Sociales Principales
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {SUPPORTED_PLATFORMS.map((platform) => {
            const account = accounts.find(a => a.provider === platform.id && a.active);
            const isConnected = !!account;
            const accountName = account?.provider_name || 'Sin cuenta vinculada';
            const isActionLoading = actionLoading === platform.id;

            return (
            <div 
              key={platform.id}
              className={clsx(
                "p-6 rounded-xl border transition-all duration-300 relative overflow-hidden",
                isConnected 
                  ? `bg-slate-900/80 ${platform.border} shadow-[0_0_15px_rgba(0,0,0,0.2)]` 
                  : "bg-slate-900/30 border-slate-800 border-dashed"
              )}
            >
              <div className="flex justify-between items-start mb-4">
                <div className={clsx("p-3 rounded-lg", platform.bg, platform.color)}>
                  <platform.icon size={28} />
                </div>
                <div className={clsx(
                  "px-2 py-1 rounded text-xs font-medium border flex items-center gap-1",
                  isConnected 
                    ? "bg-green-500/10 text-green-400 border-green-500/20" 
                    : "bg-slate-800 text-slate-400 border-slate-700"
                )}>
                  {isConnected ? (
                    <><CheckCircle size={12} /> Conectado</>
                  ) : (
                    <><AlertCircle size={12} /> Desconectado</>
                  )}
                </div>
              </div>
              
              <h3 className="text-lg font-bold text-slate-200">{platform.name}</h3>
              <p className="text-sm text-slate-500 mb-6 h-5 truncate">
                {accountName}
              </p>

              <button 
                onClick={() => isConnected ? handleDisconnect(account!.id, platform.id) : handleConnect(platform.id)}
                disabled={isActionLoading || loading}
                className={clsx(
                  "w-full py-2 rounded-lg text-sm font-medium transition-colors border flex items-center justify-center gap-2",
                  isConnected
                    ? "bg-red-500/5 text-red-400 border-red-500/20 hover:bg-red-500/10"
                    : "bg-slate-800 text-slate-200 border-slate-700 hover:bg-slate-700 hover:border-slate-600",
                  (isActionLoading || loading) && "opacity-50 cursor-not-allowed"
                )}
              >
                {isActionLoading ? <Loader2 className="animate-spin" size={16} /> : null}
                {isConnected ? 'Desconectar' : 'Conectar Cuenta'}
              </button>
            </div>
          );
          })}
        </div>
      </div>

      {/* Custom Integrations / Forums Section */}
      <div className="pt-8 border-t border-slate-800">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-end mb-6 gap-4">
          <div>
            <h2 className="text-lg sm:text-xl font-semibold text-slate-200 mb-1 flex items-center gap-2">
              <LinkIcon size={20} className="text-amber-400" />
              Foros & Webhooks
            </h2>
            <p className="text-slate-400 text-sm">
              Conecta con plataformas vía API/Webhooks.
            </p>
          </div>
          <button className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-medium transition-colors shadow-lg shadow-indigo-500/20 w-full sm:w-auto justify-center">
            <Plus size={18} />
            Nueva Integración
          </button>
        </div>

        <div className="bg-slate-900/50 rounded-xl border border-slate-800 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-400">
              <thead className="bg-slate-950/50 text-slate-200 font-medium border-b border-slate-800">
                <tr>
                  <th className="px-6 py-4">Nombre del Destino</th>
                  <th className="px-6 py-4">Endpoint / URL</th>
                  <th className="px-6 py-4">Estado</th>
                  <th className="px-6 py-4">Última Actividad</th>
                  <th className="px-6 py-4 text-right">Acciones</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {customWebhooks.map((webhook) => (
                  <tr key={webhook.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="px-6 py-4 font-medium text-slate-300">
                      {webhook.name}
                    </td>
                    <td className="px-6 py-4 font-mono text-xs text-slate-500 truncate max-w-[200px]">
                      {webhook.url}
                    </td>
                    <td className="px-6 py-4">
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-500/10 text-green-400 border border-green-500/20">
                        <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse"></span>
                        Activo
                      </span>
                    </td>
                    <td className="px-6 py-4 text-slate-500">
                      Hace 2 horas
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button className="p-2 hover:bg-slate-800 rounded-lg text-slate-400 hover:text-indigo-400 transition-colors" title="Probar conexión">
                          <RefreshCw size={16} />
                        </button>
                        <button className="p-2 hover:bg-slate-800 rounded-lg text-slate-400 hover:text-red-400 transition-colors" title="Eliminar">
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
                {/* Empty State for demo */}
                {customWebhooks.length === 0 && (
                  <tr>
                    <td colSpan={5} className="px-6 py-12 text-center text-slate-500">
                      No hay integraciones personalizadas configuradas.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
