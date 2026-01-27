import React, { useState, useRef, useEffect } from 'react';
import { Send, Paperclip, Mic, X, Check } from 'lucide-react';

interface GuideFooterProps {
  onSend: (message: string) => void;
  placeholder?: string;
  disabled?: boolean;
}

export const GuideFooter: React.FC<GuideFooterProps> = ({ onSend, placeholder = "Escribe tu respuesta...", disabled }) => {
  const [input, setInput] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [preRecordingInput, setPreRecordingInput] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const recognitionRef = useRef<any>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`; // Max height approx 5 rows
    }
  }, [input]);

  // Ensure focus stays on textarea during and after recording for keyboard control
  useEffect(() => {
    if (isListening && textareaRef.current) {
      textareaRef.current.focus();
    }
  }, [isListening]);

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (input.trim() && !disabled) {
      onSend(input.trim());
      setInput('');
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (isListening) {
        stopRecording(true);
      } else {
        handleSubmit();
      }
    }
  };

  const handleAttachment = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validación de tamaño (Aumentado a 5MB para PDFs)
    if (file.size > 5 * 1024 * 1024) { 
        alert("El archivo es demasiado grande (Máximo 5MB).");
        return;
    }

    try {
        const formData = new FormData();
        formData.append('file', file);

        // Usamos el backend para extraer texto (soporta PDF)
        const response = await fetch('http://localhost:8000/api/v1/utils/extract-text', {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            throw new Error('Error procesando el archivo');
        }

        const data = await response.json();
        const text = data.text;
        
        if (text) {
            const attachmentBlock = `\n\n[ARCHIVO ADJUNTO: ${file.name}]\n${text}\n[FIN ADJUNTO]\n`;
            setInput((prev) => prev + attachmentBlock);
        } else {
            alert("No se pudo extraer texto del archivo.");
        }

    } catch (error) {
        console.error("Error uploading file:", error);
        alert("Error al procesar el archivo. Asegúrate de que el backend esté corriendo.");
    }
    
    // Reset value so we can select same file again if needed
    e.target.value = ''; 
  };

  const startRecording = () => {
    if (!('webkitSpeechRecognition' in window)) {
      alert("Tu navegador no soporta dictado por voz. Intenta usar Chrome o Edge.");
      return;
    }

    setPreRecordingInput(input);
    
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const SpeechRecognition = (window as any).webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.lang = 'es-ES';
    recognition.interimResults = true; // Show results as we speak
    recognition.continuous = true; // Don't stop on silence
    recognition.maxAlternatives = 1;

    recognition.onstart = () => setIsListening(true);

    recognition.onresult = (event: any) => {
      let finalTranscript = '';
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          finalTranscript += event.results[i][0].transcript;
        }
      }
      
      if (finalTranscript) {
          setInput((prev) => {
              const separator = prev && !prev.endsWith(' ') ? ' ' : '';
              return prev + separator + finalTranscript;
          });
      }
    };

    recognition.onerror = (event: any) => {
      console.error("Speech recognition error", event.error);
      if (event.error === 'network') {
        alert("Error de red: El dictado por voz requiere conexión a internet.");
        stopRecording(false); // Stop but keep text? Or just stop.
      } else if (event.error === 'not-allowed') {
        alert("Permiso denegado: Por favor permite el acceso al micrófono.");
        stopRecording(false);
      }
    };
    
    // Prevent auto-stop logic from clearing state if we want manual control
    // recognition.onend = () => setIsListening(false); 
    // We handle onend manually via buttons

    recognitionRef.current = recognition;
    recognition.start();
  };

  const stopRecording = (save: boolean) => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      recognitionRef.current = null;
    }
    setIsListening(false);
    
    if (!save) {
      setInput(preRecordingInput);
    }
    
    // Return focus to textarea so user can press Enter again to send
    setTimeout(() => {
        textareaRef.current?.focus();
    }, 0);
  };

  return (
    <div className="border-t border-slate-800 bg-slate-900/80 backdrop-blur-md p-2 md:p-4 pb-safe">
      <input 
        type="file" 
        ref={fileInputRef} 
        onChange={handleFileChange} 
        className="hidden" 
        accept=".txt,.md,.csv,.json,.log,.pdf" 
      />
      <form onSubmit={handleSubmit} className="w-full max-w-3xl mx-auto relative flex gap-2 items-end">
        {/* Attachment Button */}
        <button
          type="button"
          onClick={handleAttachment}
          disabled={disabled || isListening}
          className="p-3 mb-1 text-slate-400 hover:text-white hover:bg-slate-800 rounded-xl transition-colors disabled:opacity-50 shrink-0"
          title="Adjuntar archivo"
        >
          <Paperclip size={20} />
        </button>

        {/* Input Field */}
        <div className="relative flex-1 min-w-0">
            <textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={isListening ? "Escuchando... (Habla ahora)" : placeholder}
                disabled={disabled}
                rows={1}
                className="w-full px-3 py-3 md:px-4 bg-slate-950/50 border border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-amber-500/50 focus:border-amber-500/50 focus:bg-slate-900 transition-all text-sm text-slate-200 placeholder-slate-500 pr-20 md:pr-24 resize-none min-h-[46px] max-h-[120px] scrollbar-thin scrollbar-thumb-slate-700"
                style={{ lineHeight: '1.5' }}
            />
            
            {/* Voice Controls */}
            <div className="absolute right-1.5 bottom-1.5 md:right-2 md:bottom-2 flex gap-1">
                {isListening ? (
                    <>
                        <button
                            type="button"
                            onClick={() => stopRecording(false)}
                            className="p-1.5 text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded-lg transition-colors"
                            title="Descartar grabación"
                        >
                            <X size={18} />
                        </button>
                        <button
                            type="button"
                            onClick={() => stopRecording(true)}
                            className="p-1.5 text-green-400 hover:text-green-300 hover:bg-green-500/10 rounded-lg transition-colors"
                            title="Aprobar grabación"
                        >
                            <Check size={18} />
                        </button>
                    </>
                ) : (
                    <button
                        type="button"
                        onClick={startRecording}
                        disabled={disabled}
                        className="p-1.5 text-slate-400 hover:text-amber-500 transition-colors disabled:opacity-50"
                        title="Dictado por voz"
                    >
                        <Mic size={18} />
                    </button>
                )}
            </div>
        </div>

        {/* Send Button */}
        <button
          type="submit"
          disabled={!input.trim() || disabled || isListening}
          className="p-3 mb-1 bg-gradient-to-r from-amber-500 to-orange-600 text-white rounded-xl font-medium shadow-lg shadow-amber-500/20 hover:shadow-amber-500/30 hover:scale-105 active:scale-95 transition-all disabled:opacity-50 disabled:shadow-none disabled:hover:scale-100 disabled:cursor-not-allowed"
        >
          <Send size={20} />
        </button>
      </form>
    </div>
  );
};
