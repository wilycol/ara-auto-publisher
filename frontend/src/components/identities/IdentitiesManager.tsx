import React, { useEffect, useState } from 'react';
import { identitiesApi } from '../../api/identities';
import type { Identity } from '../../api/identities';
import { IdentityCreator } from './IdentityCreator';
import { Plus, User, Trash2, Edit, X, Loader2 } from 'lucide-react';

interface IdentitiesManagerProps {
  onClose: () => void;
}

export const IdentitiesManager: React.FC<IdentitiesManagerProps> = ({ onClose }) => {
  const [identities, setIdentities] = useState<Identity[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreator, setShowCreator] = useState(false);
  const [selectedIdentity, setSelectedIdentity] = useState<Identity | null>(null);
  const [editingIdentity, setEditingIdentity] = useState<Identity | null>(null);
  const [actionLoadingId, setActionLoadingId] = useState<string | null>(null);

  const loadIdentities = async () => {
    setLoading(true);
    try {
      const data = await identitiesApi.getAll();
      setIdentities(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadIdentities();
  }, []);

  const handleArchive = async (identity: Identity) => {
    try {
      setActionLoadingId(identity.id);
      await identitiesApi.update(identity.id, { status: 'archived' });
      await loadIdentities();
    } catch (err) {
      console.error(err);
    } finally {
      setActionLoadingId(null);
    }
  };

  if (showCreator) {
    return (
      <IdentityCreator 
        mode={editingIdentity ? 'edit' : 'create'}
        identity={editingIdentity ?? undefined}
        onClose={() => {
          setShowCreator(false);
          setEditingIdentity(null);
        }}
        onCreated={() => {
          setShowCreator(false);
          setEditingIdentity(null);
          loadIdentities();
        }}
        onUpdated={async () => {
          setShowCreator(false);
          setEditingIdentity(null);
          await loadIdentities();
        }}
      />
    );
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <div className="bg-slate-900 w-full max-w-4xl h-[80vh] rounded-xl shadow-2xl flex flex-col border border-slate-800 animate-in fade-in zoom-in duration-200">
        
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-slate-800 bg-slate-900/50">
          <div className="flex items-center gap-3">
             <div className="p-2 bg-indigo-500/10 rounded-lg">
               <User className="w-6 h-6 text-indigo-400" />
             </div>
             <div>
               <h2 className="text-lg font-bold text-slate-100">Gestor de Identidades</h2>
               <p className="text-xs text-slate-400">Administra las personalidades de Ara</p>
             </div>
          </div>
          <button 
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
           <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {/* Create New Card */}
              <button 
                onClick={() => {
                  setEditingIdentity(null);
                  setShowCreator(true);
                }}
                className="flex flex-col items-center justify-center h-48 rounded-xl border-2 border-dashed border-slate-700 hover:border-indigo-500/50 hover:bg-slate-800/50 transition-all group"
              >
                <div className="p-3 rounded-full bg-slate-800 group-hover:bg-indigo-500/20 text-slate-400 group-hover:text-indigo-400 transition-colors mb-3">
                  <Plus size={24} />
                </div>
                <span className="text-sm font-medium text-slate-400 group-hover:text-slate-200">Nueva Identidad</span>
              </button>

              {/* Identity Cards */}
              {loading ? (
                <div className="col-span-full flex justify-center py-12">
                  <Loader2 className="w-8 h-8 text-indigo-500 animate-spin" />
                </div>
              ) : identities.map(identity => (
                <div key={identity.id} className="bg-slate-800/50 border border-slate-700 rounded-xl p-4 hover:border-indigo-500/30 transition-colors relative group">
                  <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity flex gap-1">
                    <button
                      onClick={() => setSelectedIdentity(identity)}
                      className="p-1 rounded-md bg-slate-800/80 hover:bg-slate-700 text-slate-300 text-xs"
                    >
                      Ver
                    </button>
                    <button
                      onClick={() => {
                        setEditingIdentity(identity);
                        setShowCreator(true);
                      }}
                      className="p-1 rounded-md bg-indigo-500/20 hover:bg-indigo-500/30 text-indigo-200 text-xs flex items-center gap-1"
                    >
                      <Edit size={12} />
                      Editar
                    </button>
                    <button
                      onClick={() => handleArchive(identity)}
                      disabled={actionLoadingId === identity.id}
                      className="p-1 rounded-md bg-red-500/10 hover:bg-red-500/20 text-red-400 text-xs disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1"
                    >
                      <Trash2 size={12} />
                      Archivar
                    </button>
                  </div>

                  <div className="flex items-center gap-3 mb-3">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold text-lg">
                      {identity.name.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <h3 className="font-semibold text-slate-200">{identity.name}</h3>
                      <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 capitalize">
                        {identity.status}
                      </span>
                    </div>
                  </div>
                  
                  <div className="space-y-2 text-sm text-slate-400">
                    <p className="line-clamp-2" title={identity.purpose}>{identity.purpose || "Sin propósito definido"}</p>
                    <div className="flex items-center gap-2 text-xs">
                       <span className="text-slate-500">Tono:</span>
                       <span className="text-slate-300">{identity.tone || "N/A"}</span>
                    </div>
                  </div>
                </div>
              ))}
           </div>
        </div>
        {selectedIdentity && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70">
            <div className="bg-slate-900 w-full max-w-md rounded-xl border border-slate-800 shadow-2xl p-6 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold text-lg">
                    {selectedIdentity.name.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <h3 className="text-base font-semibold text-slate-100">{selectedIdentity.name}</h3>
                    <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] bg-slate-800 text-slate-300 border border-slate-700">
                      Estado: {selectedIdentity.status}
                    </span>
                  </div>
                </div>
                <button
                  onClick={() => setSelectedIdentity(null)}
                  className="p-1.5 rounded-lg bg-slate-800 text-slate-400 hover:text-white hover:bg-slate-700"
                >
                  <X size={16} />
                </button>
              </div>

              <div className="space-y-3 text-sm text-slate-300">
                <div>
                  <div className="text-xs uppercase tracking-wide text-slate-500 mb-1">Propósito</div>
                  <div className="bg-slate-950/60 border border-slate-800 rounded-lg p-3 text-slate-200 min-h-[52px]">
                    {selectedIdentity.purpose || 'Sin propósito definido'}
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <div className="text-xs uppercase tracking-wide text-slate-500 mb-1">Tono</div>
                    <div className="bg-slate-950/60 border border-slate-800 rounded-lg px-3 py-2 text-slate-200">
                      {selectedIdentity.tone || 'N/A'}
                    </div>
                  </div>
                  <div>
                    <div className="text-xs uppercase tracking-wide text-slate-500 mb-1">Estilo</div>
                    <div className="bg-slate-950/60 border border-slate-800 rounded-lg px-3 py-2 text-slate-200">
                      {selectedIdentity.communication_style || 'N/A'}
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-1 gap-3">
                  <div>
                     <div className="text-xs uppercase tracking-wide text-slate-500 mb-1">Límites (Lo que NO hace)</div>
                     <div className="bg-slate-950/60 border border-slate-800 rounded-lg p-3 text-slate-200 text-sm whitespace-pre-wrap">
                       {selectedIdentity.content_limits || 'Sin límites definidos'}
                     </div>
                  </div>
                </div>

                <div>
                    <div className="text-xs uppercase tracking-wide text-slate-500 mb-1">Plataformas</div>
                    <div className="bg-slate-950/60 border border-slate-800 rounded-lg px-3 py-2 text-slate-200 text-xs">
                      {Array.isArray(selectedIdentity.preferred_platforms)
                        ? selectedIdentity.preferred_platforms.join(', ')
                        : (selectedIdentity.preferred_platforms || 'No definido')}
                    </div>
                </div>
                
                {selectedIdentity.created_at && (
                  <div className="text-xs text-slate-500">
                    Creada el {new Date(selectedIdentity.created_at).toLocaleString()}
                  </div>
                )}
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  onClick={() => setSelectedIdentity(null)}
                  className="px-3 py-1.5 text-xs rounded-lg border border-slate-700 text-slate-300 hover:bg-slate-800"
                >
                  Cerrar
                </button>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
};
