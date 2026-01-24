import React, { useState } from 'react';
import { Send, Paperclip, Mic } from 'lucide-react';

interface GuideFooterProps {
  onSend: (message: string) => void;
  placeholder?: string;
  disabled?: boolean;
}

export const GuideFooter: React.FC<GuideFooterProps> = ({ onSend, placeholder = "Escribe tu respuesta...", disabled }) => {
  const [input, setInput] = useState('');
  const [isListening, setIsListening] = useState(false);
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !disabled) {
      onSend(input.trim());
      setInput('');
    }
  };

  const handleAttachment = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validación simple
    if (file.size > 100000) { // 100KB limit for text injection
        alert("El archivo es demasiado grande para procesar en texto directo. Por favor usa archivos pequeños de texto/CV.");
        return;
    }

    const reader = new FileReader();
    reader.onload = (event) => {
        const text = event.target?.result as string;
        if (text) {
            const attachmentBlock = `\n\n[ARCHIVO ADJUNTO: ${file.name}]\n${text}\n[FIN ADJUNTO]\n`;
            setInput((prev) => prev + attachmentBlock);
        }
    };
    reader.onerror = () => alert("Error al leer el archivo.");
    reader.readAsText(file);
    
    // Reset value so we can select same file again if needed
    e.target.value = ''; 
  };

  const handleVoiceInput = () => {
    if (!('webkitSpeechRecognition' in window)) {
      alert("Tu navegador no soporta dictado por voz. Intenta usar Chrome o Edge.");
      return;
    }

    if (isListening) {
      // Stop logic if needed, but usually we just let it finish or wait for onend
      return;
    }

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const SpeechRecognition = (window as any).webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.lang = 'es-ES';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => setIsListening(true);

    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      setInput((prev) => prev + (prev ? ' ' : '') + transcript);
    };

    recognition.onerror = (event: any) => {
      console.error("Speech recognition error", event.error);
      setIsListening(false);
    };

    recognition.onend = () => setIsListening(false);

    recognition.start();
  };

  return (
    <div className="border-t border-slate-800 bg-slate-900/80 backdrop-blur-md p-4">
      <input 
        type="file" 
        ref={fileInputRef} 
        onChange={handleFileChange} 
        className="hidden" 
        accept=".txt,.md,.csv,.json,.log" // Restrict to text-ish files for now
      />
      <form onSubmit={handleSubmit} className="max-w-3xl mx-auto relative flex gap-2 items-center">
        {/* Attachment Button */}
        <button
          type="button"
          onClick={handleAttachment}
          disabled={disabled}
          className="p-3 text-slate-400 hover:text-white hover:bg-slate-800 rounded-xl transition-colors disabled:opacity-50"
          title="Adjuntar archivo"
        >
          <Paperclip size={20} />
        </button>

        {/* Input Field */}
        <div className="relative flex-1">
            <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={isListening ? "Escuchando..." : placeholder}
            disabled={disabled}
            className="w-full px-4 py-3 bg-slate-950/50 border border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-amber-500/50 focus:border-amber-500/50 focus:bg-slate-900 transition-all text-sm text-slate-200 placeholder-slate-500 pr-10"
            />
            {/* Voice Button inside Input (Right side) */}
             <button
            type="button"
            onClick={handleVoiceInput}
            disabled={disabled}
            className={`absolute right-2 top-1/2 -translate-y-1/2 p-1.5 transition-all disabled:opacity-50 ${
                isListening 
                ? 'text-red-500 animate-pulse' 
                : 'text-slate-400 hover:text-amber-500'
            }`}
            title="Dictado por voz"
            >
            <Mic size={18} />
            </button>
        </div>

        {/* Send Button */}
        <button
          type="submit"
          disabled={!input.trim() || disabled}
          className="p-3 bg-gradient-to-r from-amber-500 to-orange-600 text-white rounded-xl hover:from-amber-400 hover:to-orange-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-amber-500/20"
        >
          <Send size={20} />
        </button>
      </form>
    </div>
  );
};
