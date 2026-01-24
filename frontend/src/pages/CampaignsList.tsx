import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { campaignsApi } from '../api/campaigns';
import type { Campaign } from '../types';
import { Plus, Calendar, Activity } from 'lucide-react';
import { UnifiedWizard } from '../components/campaigns/Wizard/UnifiedWizard';

export const CampaignsList: React.FC = () => {
  const navigate = useNavigate();
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [loading, setLoading] = useState(true);
  const [showWizard, setShowWizard] = useState(false);

  useEffect(() => {
    loadCampaigns();
  }, []);

  const loadCampaigns = async () => {
    try {
      const data = await campaignsApi.getAll();
      setCampaigns(data);
    } catch (error) {
      console.error('Error loading campaigns', error);
    } finally {
      setLoading(false);
    }
  };

  const handleWizardSuccess = () => {
    setShowWizard(false);
    loadCampaigns(); // Reload list
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ACTIVE': return 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20';
      case 'DRAFT': return 'bg-slate-800 text-slate-400 border border-slate-700';
      case 'PAUSED': return 'bg-amber-500/10 text-amber-400 border border-amber-500/20';
      case 'COMPLETED': return 'bg-blue-500/10 text-blue-400 border border-blue-500/20';
      default: return 'bg-slate-800 text-slate-400 border border-slate-700';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h3 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-amber-400 to-amber-600">Mis Campañas</h3>
          <p className="text-slate-400 mt-1">Gestiona y monitorea tus estrategias de contenido</p>
        </div>
        <button 
          onClick={() => setShowWizard(true)}
          className="w-full sm:w-auto flex items-center justify-center gap-2 bg-gradient-to-r from-amber-500 to-orange-600 text-white px-4 py-2 rounded-lg hover:from-amber-400 hover:to-orange-500 transition-all shadow-lg shadow-amber-500/20"
        >
          <Plus size={20} />
          Nueva Campaña
        </button>
      </div>

      {showWizard && (
        <UnifiedWizard 
            onClose={() => setShowWizard(false)} 
            onSuccess={handleWizardSuccess} 
        />
      )}

      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-amber-500 mx-auto"></div>
        </div>
      ) : campaigns.length === 0 ? (
        <div className="bg-slate-900/50 backdrop-blur-sm rounded-xl p-12 text-center border border-dashed border-slate-800">
          <div className="w-16 h-16 bg-slate-800/50 rounded-full flex items-center justify-center mx-auto mb-4">
            <Activity className="text-slate-500" size={32} />
          </div>
          <h3 className="text-lg font-medium text-slate-200">No hay campañas activas</h3>
          <p className="text-slate-500 mt-2 mb-6">Comienza creando tu primera estrategia de contenido.</p>
          <button 
            onClick={() => setShowWizard(true)}
            className="text-amber-400 font-medium hover:text-amber-300 transition-colors"
          >
            Crear primera campaña &rarr;
          </button>
        </div>
      ) : (
        <div className="bg-slate-900/50 backdrop-blur-sm rounded-xl shadow-lg border border-slate-800 overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-800">
            <thead className="bg-slate-800/50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Nombre</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Estado</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Fechas</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Posts</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-slate-400 uppercase tracking-wider">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {campaigns.map((campaign) => (
                <tr key={campaign.id} className="hover:bg-slate-800/30 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-slate-200">{campaign.name}</div>
                    <div className="text-xs text-slate-500">ID: {campaign.id}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(campaign.status)}`}>
                      {campaign.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-400">
                    <div className="flex items-center gap-1">
                      <Calendar size={14} />
                      {new Date(campaign.start_date).toLocaleDateString()}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-400">
                    {campaign.posts?.length || 0} posts
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button 
                      onClick={(e) => {
                        e.stopPropagation();
                        navigate(`/campaigns/${campaign.id}`);
                      }}
                      className="text-amber-500 hover:text-amber-400 mr-4"
                    >
                      Ver detalles
                    </button>
                    <button className="text-slate-500 hover:text-red-400">
                      Eliminar
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
