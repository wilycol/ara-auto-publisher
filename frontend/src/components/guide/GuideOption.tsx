import React from 'react';

interface GuideOptionProps {
  label: string;
  onClick: () => void;
  disabled?: boolean;
}

export const GuideOption: React.FC<GuideOptionProps> = ({ label, onClick, disabled }) => {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className="px-4 py-2 bg-slate-900/80 border border-amber-500/20 text-amber-400 rounded-full text-sm font-medium hover:bg-amber-500/10 hover:border-amber-500/40 hover:shadow-[0_0_10px_rgba(245,158,11,0.1)] transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-sm backdrop-blur-sm"
    >
      {label}
    </button>
  );
};
