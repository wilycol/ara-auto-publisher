import React, { useState, useEffect } from 'react';
import { GuideChat } from '../guide/GuideChat';
import type { Message } from '../guide/GuideChat';
import { guideApi } from '../../api/guide';
import type { GuideState } from '../../api/guide';
import type { Identity } from '../../api/identities';
import { Bot, X } from 'lucide-react';

interface IdentityCreatorProps {
  onClose: () => void;
  onCreated?: () => void;
  onUpdated?: () => void;
  mode?: 'create' | 'edit';
  identity?: Identity;
}

export const IdentityCreator: React.FC<IdentityCreatorProps> = ({ onClose, onCreated, onUpdated, mode = 'create', identity }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentStep, setCurrentStep] = useState(1);
  const [guideState, setGuideState] = useState<GuideState>(() => {
    if (mode === 'edit' && identity) {
      const platforms = Array.isArray(identity.preferred_platforms)
        ? identity.preferred_platforms
        : identity.preferred_platforms
          ? String(identity.preferred_platforms).split(',').map(p => p.trim()).filter(Boolean)
          : [];

      return {
        step: 1,
        identity_id: identity.id,
        identity_draft: {
          name: identity.name,
          purpose: identity.purpose,
          tone: identity.tone,
          communication_style: identity.communication_style,
          content_limits: identity.content_limits,
          platforms,
        },
      } as GuideState;
    }
    return { step: 1 } as GuideState;
  });
  
  const [sessionId] = useState(() => {
    if (typeof crypto !== 'undefined' && crypto.randomUUID) {
      return crypto.randomUUID();
    }
    return 'session-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
  });

  const processStep = async (userInput?: string, userValue?: string) => {
    setIsProcessing(true);

    if (userInput) {
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        role: 'user',
        content: userInput
      }]);
    }

    try {
      const response = await guideApi.nextStep({
        current_step: currentStep,
        mode: 'identity_creation',
        state: guideState,
        user_input: userInput,
        user_value: userValue,
        guide_session_id: sessionId
      });

      // Handle closing/completion
      if (response.options.find(o => o.value === 'close_wizard')) {
         if (mode === 'edit') {
           if (onUpdated) onUpdated();
         } else {
           if (onCreated) onCreated();
         }
         onClose();
         return;
      }

      setMessages(prev => [...prev, {
        id: Date.now().toString() + '-ai',
        role: 'ai',
        content: response.assistant_message,
        options: response.options
      }]);

      setCurrentStep(response.next_step);
      setGuideState(prev => ({ ...prev, ...response.state_patch }));

    } catch (error) {
      console.error("Error in identity creation:", error);
      setMessages(prev => [...prev, {
        id: Date.now().toString() + '-err',
        role: 'ai',
        content: "Lo siento, hubo un error al procesar tu solicitud. Por favor intenta de nuevo.",
        options: [{ label: "Reintentar", value: "retry" }]
      }]);
    } finally {
      setIsProcessing(false);
    }
  };

  const initialized = React.useRef(false);

  // Initial step trigger
  useEffect(() => {
    // Only trigger if we haven't initialized yet to avoid duplication on re-renders
    if (!initialized.current) {
      initialized.current = true;
      if (messages.length === 0) {
        processStep();
      }
    }
  }, []); // Run once on mount

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <div className="bg-slate-900 w-full max-w-4xl h-[80vh] rounded-xl shadow-2xl flex flex-col border border-slate-800 animate-in fade-in zoom-in duration-200">
        
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-slate-800 bg-slate-900/50">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-amber-500/10 rounded-lg">
              <Bot className="w-6 h-6 text-amber-400" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-slate-100">{mode === 'edit' ? 'Editar Identidad Funcional' : 'Crear Identidad Funcional'}</h2>
              <p className="text-xs text-slate-400">{mode === 'edit' && identity ? `Ajusta la identidad "${identity.name}"` : "Define una nueva 'máscara' para Ara"}</p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        {/* Chat Area */}
        <div className="flex-1 min-h-0">
          <GuideChat 
            messages={messages}
            onSendMessage={(text) => processStep(text)}
            onSelectOption={(val, label) => processStep(label, val)}
            isProcessing={isProcessing}
          />
        </div>
      </div>
    </div>
  );
};
