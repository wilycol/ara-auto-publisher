import React from 'react';
import { Bot, User } from 'lucide-react';
import clsx from 'clsx';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface GuideMessageProps {
  role: 'ai' | 'user';
  content: string;
}

export const GuideMessage: React.FC<GuideMessageProps> = ({ role, content }) => {
  const isAi = role === 'ai';

  return (
    <div className={clsx(
      "flex gap-4 max-w-3xl",
      isAi ? "self-start" : "self-end flex-row-reverse"
    )}>
      <div className={clsx(
        "w-8 h-8 rounded-full flex items-center justify-center shrink-0 border",
        isAi 
          ? "bg-slate-900 text-amber-400 border-slate-800 shadow-[0_0_10px_rgba(245,158,11,0.1)]" 
          : "bg-slate-800 text-slate-400 border-slate-700"
      )}>
        {isAi ? <Bot size={18} /> : <User size={18} />}
      </div>
      
      <div className={clsx(
        "px-6 py-4 rounded-2xl text-sm leading-relaxed shadow-sm backdrop-blur-sm overflow-hidden",
        isAi 
          ? "bg-slate-900/80 text-slate-200 rounded-tl-none border border-slate-800" 
          : "bg-gradient-to-r from-amber-500 to-orange-600 text-white rounded-tr-none shadow-lg shadow-amber-500/20"
      )}>
        {isAi ? (
          <div className="prose prose-invert prose-sm max-w-none 
              prose-headings:text-amber-50 prose-headings:font-semibold prose-headings:mb-2 prose-headings:mt-4 first:prose-headings:mt-0
              prose-p:text-slate-300 prose-p:my-2
              prose-strong:text-amber-400 prose-strong:font-bold
              prose-ul:my-2 prose-ul:list-disc prose-ul:pl-4
              prose-ol:my-2 prose-ol:list-decimal prose-ol:pl-4
              prose-li:text-slate-300 prose-li:my-0.5
              prose-blockquote:border-l-4 prose-blockquote:border-amber-500/50 prose-blockquote:bg-slate-800/50 prose-blockquote:px-4 prose-blockquote:py-1 prose-blockquote:rounded-r prose-blockquote:not-italic prose-blockquote:text-slate-300
              prose-code:text-amber-300 prose-code:bg-slate-800 prose-code:px-1 prose-code:py-0.5 prose-code:rounded prose-code:before:content-none prose-code:after:content-none
              prose-hr:border-slate-700 prose-hr:my-4">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {content}
            </ReactMarkdown>
          </div>
        ) : (
          <div className="whitespace-pre-wrap">{content}</div>
        )}
      </div>
    </div>
  );
};
