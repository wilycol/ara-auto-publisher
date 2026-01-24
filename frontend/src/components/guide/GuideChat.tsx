import React, { useRef, useEffect } from 'react';
import { GuideMessage } from './GuideMessage';
import { GuideOption } from './GuideOption';
import { GuideFooter } from './GuideFooter';

export interface Message {
  id: string;
  role: 'ai' | 'user';
  content: string;
  options?: { label: string; value: string }[];
}

interface GuideChatProps {
  messages: Message[];
  onSendMessage: (text: string) => void;
  onSelectOption: (value: string, label: string) => void;
  isProcessing?: boolean;
  inputDisabled?: boolean;
}

export const GuideChat: React.FC<GuideChatProps> = ({ 
  messages, 
  onSendMessage, 
  onSelectOption,
  isProcessing = false,
  inputDisabled = false
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="flex flex-col h-full bg-slate-950">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin scrollbar-thumb-slate-800 scrollbar-track-transparent">
        <div className="max-w-3xl mx-auto space-y-6">
          {messages.map((msg) => (
            <div key={msg.id} className="space-y-4">
              <GuideMessage role={msg.role} content={msg.content} />
              
              {/* Options (only for AI messages) */}
              {msg.role === 'ai' && msg.options && msg.options.length > 0 && (
                <div className="flex flex-wrap gap-2 ml-12 animate-in fade-in slide-in-from-top-2 duration-300">
                  {msg.options.map((opt, index) => (
                    <GuideOption
                      key={`${opt.value}-${index}`}
                      label={opt.label}
                      onClick={() => onSelectOption(opt.value, opt.label)}
                      disabled={isProcessing}
                    />
                  ))}
                </div>
              )}
            </div>
          ))}
          
          {isProcessing && (
            <div className="flex gap-4 ml-2 animate-pulse">
              <div className="w-8 h-8 bg-slate-800 rounded-full border border-slate-700"></div>
              <div className="h-10 w-32 bg-slate-800 rounded-xl border border-slate-700"></div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <GuideFooter 
        onSend={onSendMessage} 
        disabled={isProcessing || inputDisabled} 
      />
    </div>
  );
};
