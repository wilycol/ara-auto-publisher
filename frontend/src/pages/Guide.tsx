import React, { useState, useEffect } from 'react';
import { GuideChat } from '../components/guide/GuideChat';
import type { Message } from '../components/guide/GuideChat';
import { campaignsApi } from '../api/campaigns';
import { guideApi } from '../api/guide';
import type { GuideState, GuideMode } from '../api/guide';
import { useNavigate } from 'react-router-dom';
import { Bot, FileEdit, Sparkles, Zap } from 'lucide-react';

// ------------------------------------------------------------------
// 🧠 FASE 3.2 — Estado Conversacional (OBLIGATORIO)
// ------------------------------------------------------------------
// GuideState now imported from API to ensure consistency

type ViewMode = GuideMode | 'manual_form';

export const Guide: React.FC = () => {
  const navigate = useNavigate();
  const [isProcessing, setIsProcessing] = useState(false);
  const [isBlocked, setIsBlocked] = useState(false);
  const [mode, setMode] = useState<ViewMode>('guided');
  
  // Ref to track current mode for async operations
  const modeRef = React.useRef(mode);
  useEffect(() => {
    modeRef.current = mode;
  }, [mode]);
  
  // 🧠 FASE 4.2 — Observabilidad: Session ID
  const [sessionId] = useState(() => {
    if (typeof crypto !== 'undefined' && crypto.randomUUID) {
      return crypto.randomUUID();
    }
    return 'session-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
  });

  // Estado del negocio (La verdad)
  const [guideState, setGuideState] = useState<GuideState>({
    step: 1
  });

  // Estado de UX (Lo que ve el usuario)
  const [messages, setMessages] = useState<Message[]>([]);

  // Inicializar mensaje según modo
  useEffect(() => {
    const initMsg = getInitialMessage(mode);
    setMessages([{
      id: Date.now().toString(),
      role: 'ai',
      content: initMsg
    }]);
    setGuideState({ step: 1, conversation_summary: "" });
    setIsProcessing(false); // Reset processing state on mode switch
    setIsBlocked(false); // Reset blocked state on mode switch
  }, [mode]);

  const getInitialMessage = (m: ViewMode): string => {
    switch (m) {
      case 'collaborator': return 'Soy ARA Post Manager, tu copiloto para convertir ideas desordenadas en campañas claras y accionables. Vamos al grano. ¿Qué objetivo tienes con tu campaña?';
      case 'expert': return '¿Objetivo de la campaña?';
      case 'guided': default: return 'Cuéntame qué quieres lograr con tu contenido.\nNo pienses en redes todavía, piensa en el objetivo.';
    }
  };

  const [manualFormData, setManualFormData] = useState({
    topic: '',
    platform: 'linkedin',
    tone: 'professional',
    extraInfo: ''
  });

  const handleManualSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const state: GuideState = {
      step: 6,
      topics: [manualFormData.topic],
      platform: manualFormData.platform as GuideState['platform'],
      tone: manualFormData.tone,
      extra_context: manualFormData.extraInfo
    };
    await executeCampaignCreation(state);
  };

  const addMessage = (role: 'ai' | 'user', content: string, options?: { label: string; value: string }[]) => {
    setMessages(prev => [...prev, {
      id: Date.now().toString(),
      role,
      content,
      options
    }]);
  };

  const resetGuide = () => {
    setGuideState({ step: 1, conversation_summary: "" });
    setMessages([{
      id: Date.now().toString(),
      role: 'ai',
      content: getInitialMessage(mode)
    }]);
  };

  const handleUserResponse = async (text: string, value?: string) => {
    if (isProcessing) return; // 🛡️ FASE 4.3 - Prevent double submit

    // 1. Mostrar mensaje del usuario
    addMessage('user', text);
    setIsProcessing(true);

    // 2. Procesar siguiente paso con pequeño delay para "sentir" la IA
    setTimeout(() => {
      processStep(text, value);
    }, 600);
  };

  // ------------------------------------------------------------------
  // 🗣️ FASE 3.3 — Guion Conversacional CANÓNICO
  // ------------------------------------------------------------------
  const processStep = async (userText: string, userValue?: string) => {
    const currentStep = guideState.step;

    // ------------------------------------------------------------------
    // 🧠 FASE 4.1 — Backend: Guide Orchestrator
    // ------------------------------------------------------------------
    
    // Casos especiales frontend (Confirmación final y Restart)
    if (currentStep === 6 && mode !== 'collaborator') { // En colaborador el step 6 puede ser dinámico
        if (userValue === 'create') {
            await executeCampaignCreation(guideState);
            return;
        } else if (userValue === 'restart') {
            resetGuide();
            setIsProcessing(false);
            return;
        }
    }
    
    // En Collaborator mode, si recibimos 'create' o 'restart' desde las opciones sugeridas
    if (mode === 'collaborator') {
        if (userValue === 'create') {
             await executeCampaignCreation(guideState);
             return;
        }
        if (userValue === 'restart') {
            resetGuide();
            setIsProcessing(false);
            return;
        }
        // Manejo de botones de bloqueo
        if (userValue === 'switch_guide') {
            setMode('guided');
            return;
        }
        if (userValue === 'switch_expert') {
            setMode('expert');
            return;
        }
    }

    try {
        // Llamada al orquestador IA en backend
        // Capture mode at the start of request
        const requestMode = mode as GuideMode;
        
        console.log(`🧠 [Guide.tsx] Sending request. Mode: ${requestMode}, Step: ${currentStep}, Input: "${userText}"`);

        const response = await guideApi.nextStep({
            current_step: currentStep,
            mode: requestMode, 
            state: guideState,
            user_input: userText,
            user_value: userValue,
            guide_session_id: sessionId // 🧠 FASE 4.2
        });

        console.log(`✅ [Guide.tsx] Received response. Next Step: ${response.next_step}, Message: "${response.assistant_message?.substring(0, 50)}..."`);


        // 🛡️ RACE CONDITION CHECK
        // If the mode has changed while we were waiting, discard the result.
        if (modeRef.current !== mode) {
            console.log("Mode changed during request, ignoring response.");
            return;
        }

        // Actualizar estado con el patch del backend
        setGuideState(prev => ({
            ...prev,
            ...response.state_patch,
            step: response.next_step
        }));

        // Mostrar respuesta de IA
        // 🛡️ FASE 4.3 - UX Contención
        const safeMessage = response.assistant_message || "Sigamos adelante, te propongo una opción segura 👇";
        addMessage('ai', safeMessage, response.options);

        // 🛡️ CHECK BLOCKED STATUS
        if (response.status === 'blocked') {
            setIsBlocked(true);
        }

    } catch (error) {
        console.error('Error in guide orchestration', error);
        addMessage('ai', 'Lo siento, tuve un problema de conexión. ¿Podemos intentar de nuevo?', [
            { label: 'Reintentar', value: 'retry' }
        ]);
    } finally {
        setIsProcessing(false);
    }
  };

  // ------------------------------------------------------------------
  // 🚀 FASE 3.4 — Acción Final (SIN MAGIA)
  // ------------------------------------------------------------------
  const executeCampaignCreation = async (finalState: GuideState) => {
    try {
      setIsProcessing(true);
      
      // Mapear GuideState -> Payload Real
      const campaignName = `Campaña ${finalState.platform} - ${finalState.topics?.[0] || 'General'}`;
      const startDate = new Date().toISOString().split('T')[0];

      // Nota: En un futuro aquí enviaríamos todo el contexto a la IA para generar posts
      // Por ahora, creamos el contenedor de la campaña
      await campaignsApi.create({
        project_id: 1, // Hardcoded for MVP
        name: campaignName,
        objective: finalState.objective || finalState.extra_context || 'Generar engagement y posicionamiento',
        tone: finalState.tone || 'professional',
        topics: finalState.topics ? finalState.topics.join(',') : 'General',
        start_date: startDate,
        status: 'draft' // lowercase to match enum
      });

      // Toast simulado en chat
      addMessage('ai', '✅ Campaña creada. Ahora generemos contenido.');
      
      // Redirect
      setTimeout(() => {
        // En futuro: navigate(`/campaigns/${newCampaign.id}`);
        navigate('/campaigns'); 
      }, 1500);

    } catch (error) {
      console.error('Error creating campaign', error);
      addMessage('ai', '❌ Hubo un error al guardar la campaña. Inténtalo de nuevo.');
      setIsProcessing(false);
    }
  };

  return (
    <div className="h-full flex flex-col bg-slate-950 overflow-hidden rounded-2xl border border-slate-800 shadow-2xl">
      {/* Header with Mode Selector */}
      <header className="bg-slate-900/80 backdrop-blur-md border-b border-slate-800 px-4 py-3 md:px-6 md:py-4 flex flex-col md:flex-row justify-between items-start md:items-center gap-4 shrink-0">
        <div>
          <h1 className="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-amber-400 to-amber-600">
            AraPost Manager
          </h1>
          <p className="text-sm text-slate-400 hidden sm:block">
            Tu asistente IA para crear contenido de alto impacto
          </p>
        </div>

        {/* Mode Selector */}
        <div className="flex flex-wrap items-center gap-1 bg-slate-950/50 p-1 rounded-lg border border-slate-800 w-full md:w-auto overflow-x-auto">
          <button
            onClick={() => setMode('guided')}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-sm font-medium transition-all ${
              mode === 'guided'
                ? 'bg-amber-500/10 text-amber-400 shadow-[0_0_10px_rgba(245,158,11,0.1)] border border-amber-500/20'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Bot size={16} />
            Guía
          </button>
          
          <button
            onClick={() => setMode('collaborator')}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-sm font-medium transition-all ${
              mode === 'collaborator'
                ? 'bg-emerald-500/10 text-emerald-400 shadow-[0_0_10px_rgba(16,185,129,0.1)] border border-emerald-500/20'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Sparkles size={16} />
            Colaborador
          </button>

          <button
            onClick={() => setMode('expert')}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-sm font-medium transition-all ${
              mode === 'expert'
                ? 'bg-rose-500/10 text-rose-400 shadow-[0_0_10px_rgba(244,63,94,0.1)] border border-rose-500/20'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Zap size={16} />
            Experto
          </button>

          <div className="w-px h-6 bg-slate-800 mx-1"></div>

          <button
            onClick={() => setMode('manual_form')}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-sm font-medium transition-all ${
              mode === 'manual_form'
                ? 'bg-indigo-500/10 text-indigo-400 shadow-[0_0_10px_rgba(99,102,241,0.1)] border border-indigo-500/20'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <FileEdit size={16} />
            Formulario
          </button>
        </div>
      </header>
      
      <div className="flex-1 overflow-hidden relative">
        {mode !== 'manual_form' ? (
          <GuideChat 
            messages={messages} 
            onSendMessage={(text) => handleUserResponse(text)}
            onSelectOption={(value, label) => handleUserResponse(label, value)}
            isProcessing={isProcessing}
            inputDisabled={isBlocked}
          />
        ) : (
          <div className="h-full overflow-y-auto p-4 sm:p-8 scrollbar-thin scrollbar-thumb-slate-800 scrollbar-track-transparent">
            <div className="max-w-2xl mx-auto bg-slate-900/50 backdrop-blur-sm p-8 rounded-2xl border border-slate-800 shadow-xl">
              <div className="mb-8">
                <h2 className="text-2xl font-bold text-slate-200 mb-2 flex items-center gap-2">
                  <FileEdit className="text-indigo-400" />
                  Configuración Manual de Campaña
                </h2>
                <p className="text-slate-400">
                  Define los parámetros exactos para tu campaña sin pasar por el asistente conversacional.
                </p>
              </div>

              <form onSubmit={handleManualSubmit} className="space-y-6">
                {/* Topic */}
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Tema Principal
                  </label>
                  <input
                    type="text"
                    required
                    value={manualFormData.topic}
                    onChange={(e) => setManualFormData(prev => ({ ...prev, topic: e.target.value }))}
                    placeholder="Ej: Lanzamiento de nuevo producto de IA"
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg px-4 py-3 text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500/50 transition-all"
                  />
                </div>

                {/* Platform & Tone Row */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Plataforma Destino
                    </label>
                    <select
                      value={manualFormData.platform}
                      onChange={(e) => setManualFormData(prev => ({ ...prev, platform: e.target.value }))}
                      className="w-full bg-slate-950 border border-slate-700 rounded-lg px-4 py-3 text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500/50 transition-all appearance-none"
                    >
                      <option value="linkedin">LinkedIn</option>
                      <option value="twitter">Twitter / X</option>
                      <option value="instagram">Instagram</option>
                      <option value="facebook">Facebook</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Tono de Comunicación
                    </label>
                    <select
                      value={manualFormData.tone}
                      onChange={(e) => setManualFormData(prev => ({ ...prev, tone: e.target.value }))}
                      className="w-full bg-slate-950 border border-slate-700 rounded-lg px-4 py-3 text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500/50 transition-all appearance-none"
                    >
                      <option value="professional">Profesional / Corporativo</option>
                      <option value="casual">Casual / Amigable</option>
                      <option value="enthusiastic">Entusiasta / Enérgico</option>
                      <option value="informative">Informativo / Educativo</option>
                      <option value="controversial">Disruptivo / Polémico</option>
                    </select>
                  </div>
                </div>

                {/* Extra Context */}
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Instrucciones Adicionales (Opcional)
                  </label>
                  <textarea
                    rows={4}
                    value={manualFormData.extraInfo}
                    onChange={(e) => setManualFormData(prev => ({ ...prev, extraInfo: e.target.value }))}
                    placeholder="Menciona que el descuento termina el viernes. Usa emojis moderadamente."
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg px-4 py-3 text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500/50 transition-all resize-none"
                  />
                </div>

                {/* Submit Button */}
                <div className="pt-4">
                  <button
                    type="submit"
                    disabled={isProcessing}
                    className={`w-full py-4 rounded-xl font-bold text-white shadow-lg shadow-indigo-500/20 transition-all flex items-center justify-center gap-2 ${
                      isProcessing 
                        ? 'bg-slate-700 cursor-not-allowed opacity-70' 
                        : 'bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400 transform hover:-translate-y-0.5'
                    }`}
                  >
                    {isProcessing ? (
                      <>
                        <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        Procesando...
                      </>
                    ) : (
                      <>
                        <Bot size={20} />
                        Generar Campaña con IA
                      </>
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
