
import React, { useState } from 'react';
import { X, ArrowRight, Check, Shield, Zap, Lock } from 'lucide-react';
import { campaignsApi } from '../../../api/campaigns';
import { controlApi } from '../../../api/control';
import type { CreateCampaignRequest } from '../../../types';

interface UnifiedWizardProps {
  onClose: () => void;
  onSuccess: () => void;
}

type Step = 'DETAILS' | 'STRATEGY' | 'AUTOMATION' | 'REVIEW';

export const UnifiedWizard: React.FC<UnifiedWizardProps> = ({ onClose, onSuccess }) => {
  const [step, setStep] = useState<Step>('DETAILS');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form State
  const [formData, setFormData] = useState<CreateCampaignRequest>({
    name: '',
    project_id: 1, // Default project for now
    objective: '',
    tone: 'Professional',
    topics: '',
    posts_per_day: 1,
    schedule_strategy: 'interval',
    start_date: new Date().toISOString().split('T')[0] // Default to today
  });

  const [automationConfig, setAutomationConfig] = useState({
    autonomy_status: 'autonomous_active',
    style_locked: false
  });

  const handleNext = () => {
    if (step === 'DETAILS') {
      if (!formData.name || !formData.objective) {
        setError("Nombre y Objetivo son requeridos.");
        return;
      }
      setStep('STRATEGY');
    } else if (step === 'STRATEGY') {
        if (!formData.topics) {
            setError("Define al menos un tema (Topic).");
            return;
        }
      setStep('AUTOMATION');
    } else if (step === 'AUTOMATION') {
      setStep('REVIEW');
    }
    setError(null);
  };

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);
    try {
      // 1. Create Campaign
      console.log("Creating campaign...", formData);
      const campaign = await campaignsApi.create(formData);
      
      // 2. Setup Automation (using project_id from campaign or formData)
      console.log("Setting up automation...", campaign.project_id);
      await controlApi.setupAutomation({
        project_id: campaign.project_id,
        name: campaign.name,
        status: 'active',
        autonomy_status: automationConfig.autonomy_status,
        style_locked: automationConfig.style_locked
      });

      onSuccess();
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.detail || "Error al crear la campaña y automatización.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-gray-900/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-100 flex justify-between items-center bg-gray-50">
          <div>
            <h2 className="text-lg font-bold text-gray-900">Nueva Campaña Autónoma</h2>
            <div className="flex gap-1 mt-1">
              <div className={`h-1 w-8 rounded-full ${step === 'DETAILS' || step === 'STRATEGY' || step === 'AUTOMATION' || step === 'REVIEW' ? 'bg-indigo-600' : 'bg-gray-200'}`} />
              <div className={`h-1 w-8 rounded-full ${step === 'STRATEGY' || step === 'AUTOMATION' || step === 'REVIEW' ? 'bg-indigo-600' : 'bg-gray-200'}`} />
              <div className={`h-1 w-8 rounded-full ${step === 'AUTOMATION' || step === 'REVIEW' ? 'bg-indigo-600' : 'bg-gray-200'}`} />
              <div className={`h-1 w-8 rounded-full ${step === 'REVIEW' ? 'bg-indigo-600' : 'bg-gray-200'}`} />
            </div>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 p-2">
            <X size={20} />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto flex-1">
          {error && (
            <div className="mb-4 p-3 bg-red-50 text-red-700 text-sm rounded-lg border border-red-100">
              {error}
            </div>
          )}

          {step === 'DETAILS' && (
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-gray-800">1. Detalles Básicos</h3>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Nombre de la Campaña</label>
                <input 
                  type="text" 
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder="Ej: Lanzamiento Q1 2026"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Objetivo Principal</label>
                <textarea 
                  value={formData.objective}
                  onChange={(e) => setFormData({...formData, objective: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  rows={3}
                  placeholder="Ej: Aumentar la visibilidad de la marca en el sector tecnológico..."
                />
              </div>
            </div>
          )}

          {step === 'STRATEGY' && (
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-gray-800">2. Estrategia de Contenido</h3>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Tono de Voz</label>
                <select 
                  value={formData.tone}
                  onChange={(e) => setFormData({...formData, tone: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                >
                  <option value="Professional">Profesional</option>
                  <option value="Casual">Casual</option>
                  <option value="Inspirational">Inspiracional</option>
                  <option value="Educational">Educativo</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Temas Clave (separados por comas)</label>
                <input 
                  type="text" 
                  value={formData.topics}
                  onChange={(e) => setFormData({...formData, topics: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder="Ej: AI, Marketing, Innovation"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Posts por día</label>
                <div className="flex items-center gap-4">
                    <input 
                    type="range" 
                    min="1" 
                    max="5" 
                    value={formData.posts_per_day}
                    onChange={(e) => setFormData({...formData, posts_per_day: parseInt(e.target.value)})}
                    className="flex-1"
                    />
                    <span className="font-bold text-indigo-600">{formData.posts_per_day}</span>
                </div>
              </div>
            </div>
          )}

          {step === 'AUTOMATION' && (
            <div className="space-y-6">
              <h3 className="text-xl font-semibold text-gray-800">3. Configuración de Autonomía</h3>
              
              <div 
                className={`p-4 rounded-xl border-2 cursor-pointer transition-all ${automationConfig.autonomy_status === 'autonomous_active' ? 'border-indigo-600 bg-indigo-50' : 'border-gray-200 hover:border-indigo-300'}`}
                onClick={() => setAutomationConfig({...automationConfig, autonomy_status: 'autonomous_active'})}
              >
                <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg ${automationConfig.autonomy_status === 'autonomous_active' ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-500'}`}>
                        <Zap size={24} />
                    </div>
                    <div>
                        <h4 className="font-bold text-gray-900">Modo Autónomo Total</h4>
                        <p className="text-sm text-gray-600">La IA genera y propone. Tú apruebas o dejas que el timer decida.</p>
                    </div>
                </div>
              </div>

              <div 
                className={`p-4 rounded-xl border-2 cursor-pointer transition-all ${automationConfig.autonomy_status === 'autonomous_paused' ? 'border-amber-500 bg-amber-50' : 'border-gray-200 hover:border-amber-300'}`}
                onClick={() => setAutomationConfig({...automationConfig, autonomy_status: 'autonomous_paused'})}
              >
                <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg ${automationConfig.autonomy_status === 'autonomous_paused' ? 'bg-amber-500 text-white' : 'bg-gray-100 text-gray-500'}`}>
                        <Lock size={24} />
                    </div>
                    <div>
                        <h4 className="font-bold text-gray-900">Modo Supervisado (Pausado)</h4>
                        <p className="text-sm text-gray-600">La IA genera borradores pero NO publica sin tu clic explícito.</p>
                    </div>
                </div>
              </div>

              <div className="flex items-center gap-2 mt-4 pt-4 border-t border-gray-100">
                <input 
                    type="checkbox" 
                    id="styleLock"
                    checked={automationConfig.style_locked}
                    onChange={(e) => setAutomationConfig({...automationConfig, style_locked: e.target.checked})}
                    className="w-5 h-5 text-indigo-600 rounded focus:ring-indigo-500"
                />
                <label htmlFor="styleLock" className="text-gray-700 font-medium cursor-pointer">
                    Bloquear Estilo (Style Lock)
                    <p className="text-xs text-gray-500 font-normal">Impide que la IA modifique el tono o los temas automáticamente.</p>
                </label>
              </div>
            </div>
          )}

          {step === 'REVIEW' && (
            <div className="space-y-6">
                <div className="text-center">
                    <div className="w-16 h-16 bg-green-100 text-green-600 rounded-full flex items-center justify-center mx-auto mb-4">
                        <Check size={32} />
                    </div>
                    <h3 className="text-2xl font-bold text-gray-900">¡Todo listo!</h3>
                    <p className="text-gray-500 mt-2">Revisa tu configuración antes de lanzar.</p>
                </div>

                <div className="bg-gray-50 rounded-xl p-4 space-y-3 text-sm">
                    <div className="flex justify-between">
                        <span className="text-gray-500">Campaña:</span>
                        <span className="font-medium text-gray-900">{formData.name}</span>
                    </div>
                    <div className="flex justify-between">
                        <span className="text-gray-500">Estrategia:</span>
                        <span className="font-medium text-gray-900">{formData.posts_per_day} posts/día ({formData.tone})</span>
                    </div>
                    <div className="flex justify-between">
                        <span className="text-gray-500">Modo:</span>
                        <span className={`font-bold ${automationConfig.autonomy_status === 'autonomous_active' ? 'text-indigo-600' : 'text-amber-600'}`}>
                            {automationConfig.autonomy_status === 'autonomous_active' ? 'AUTÓNOMO' : 'SUPERVISADO'}
                        </span>
                    </div>
                </div>

                <div className="bg-blue-50 p-4 rounded-xl flex gap-3 items-start">
                    <Shield className="text-blue-600 shrink-0 mt-0.5" size={20} />
                    <p className="text-sm text-blue-800">
                        Recuerda: Siempre puedes usar el <strong>Botón de Emergencia</strong> o pausar la campaña desde el Dashboard.
                    </p>
                </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-gray-100 bg-gray-50 flex justify-between">
          {step !== 'DETAILS' ? (
            <button 
                onClick={() => {
                    if (step === 'REVIEW') setStep('AUTOMATION');
                    else if (step === 'AUTOMATION') setStep('STRATEGY');
                    else if (step === 'STRATEGY') setStep('DETAILS');
                }}
                className="text-gray-600 hover:text-gray-900 font-medium px-4 py-2"
            >
                Atrás
            </button>
          ) : (
            <div /> // Spacer
          )}

          {step === 'REVIEW' ? (
            <button 
                onClick={handleSubmit}
                disabled={loading}
                className="bg-indigo-600 text-white px-8 py-3 rounded-xl hover:bg-indigo-700 transition-all font-bold shadow-lg shadow-indigo-200 flex items-center gap-2"
            >
                {loading ? 'Creando...' : 'Lanzar Sistema 🚀'}
            </button>
          ) : (
            <button 
                onClick={handleNext}
                className="bg-gray-900 text-white px-6 py-2 rounded-lg hover:bg-gray-800 transition-colors flex items-center gap-2"
            >
                Siguiente <ArrowRight size={18} />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
