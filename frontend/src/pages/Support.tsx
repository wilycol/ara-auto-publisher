import React, { useState } from 'react';
import { Mail, PlayCircle, BookOpen, MessageSquare, Shield, AlertTriangle, Activity, LayoutDashboard, HelpCircle } from 'lucide-react';
import clsx from 'clsx';

export const Support: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'faq' | 'videos' | 'guide'>('faq');

  const modules = [
    {
      icon: LayoutDashboard,
      title: "Dashboard",
      description: "Tu centro de comando. Visualiza el estado general del sistema, métricas clave y accesos directos. Es puramente informativo y de navegación rápida."
    },
    {
      icon: Activity,
      title: "Control Humano",
      description: "La capa de seguridad. Aquí supervisas las decisiones de la IA antes de que se ejecuten. Tú siempre tienes la última palabra."
    },
    {
      icon: Shield,
      title: "Zona Roja (Override)",
      description: "Intervención manual directa. Úsalo para detener campañas de emergencia o forzar publicaciones ignorando las restricciones habituales."
    },
    {
      icon: MessageSquare,
      title: "Guía IA (Tu Copiloto)",
      highlight: true,
      description: "Mucho más que un chatbot. Es un estratega conversacional que entiende tu intención, contexto y objetivos. No solo responde, sino que sugiere soluciones proactivas y te ayuda a planificar campañas complejas como si hablaras con un experto en marketing."
    },
    {
      icon: BookOpen,
      title: "Campañas",
      description: "Gestión integral de tus publicaciones. Crea, edita, pausa y revisa el historial de todas tus estrategias de contenido."
    },
    {
      icon: Activity,
      title: "Tracking",
      description: "Analítica en tiempo real. Mide el impacto de tus publicaciones y ajusta tu estrategia basándote en datos reales."
    }
  ];

  const videos = [
    { title: "Tour General en 3 minutos", duration: "3:15", thumbnail: "bg-slate-800" },
    { title: "Cómo crear tu primera campaña", duration: "2:45", thumbnail: "bg-indigo-900/50" },
    { title: "Dominando la Guía IA", duration: "4:20", thumbnail: "bg-amber-900/30" },
  ];

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 bg-slate-900/50 backdrop-blur-sm p-8 rounded-2xl border border-slate-800">
        <div>
          <h1 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-amber-400 to-amber-600 mb-2">
            Centro de Soporte & Ayuda
          </h1>
          <p className="text-slate-400 max-w-2xl">
            Resuelve tus dudas, aprende a usar la plataforma y contacta directamente con el desarrollador.
          </p>
        </div>
        <div className="flex items-center gap-4 bg-slate-950/50 p-4 rounded-xl border border-slate-800/50 shadow-inner">
          <div className="p-3 bg-indigo-500/10 rounded-full text-indigo-400">
            <Mail size={24} />
          </div>
          <div>
            <p className="text-xs text-slate-500 uppercase tracking-wider font-semibold">Soporte Directo</p>
            <a href="mailto:wilycol1492@gmail.com" className="text-slate-200 hover:text-amber-400 transition-colors font-mono">
              wilycol1492@gmail.com
            </a>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex gap-4 border-b border-slate-800 pb-1 overflow-x-auto">
        <button 
          onClick={() => setActiveTab('faq')}
          className={clsx(
            "px-6 py-3 text-sm font-medium rounded-t-lg transition-all flex items-center gap-2",
            activeTab === 'faq' 
              ? "bg-slate-800 text-amber-400 border-b-2 border-amber-400" 
              : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
          )}
        >
          <HelpCircle size={18} />
          Documentación de Módulos
        </button>
        <button 
          onClick={() => setActiveTab('videos')}
          className={clsx(
            "px-6 py-3 text-sm font-medium rounded-t-lg transition-all flex items-center gap-2",
            activeTab === 'videos' 
              ? "bg-slate-800 text-amber-400 border-b-2 border-amber-400" 
              : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
          )}
        >
          <PlayCircle size={18} />
          Video Tutoriales
        </button>
        <button 
          onClick={() => setActiveTab('guide')}
          className={clsx(
            "px-6 py-3 text-sm font-medium rounded-t-lg transition-all flex items-center gap-2",
            activeTab === 'guide' 
              ? "bg-slate-800 text-amber-400 border-b-2 border-amber-400" 
              : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
          )}
        >
          <BookOpen size={18} />
          Guía de Inicio Rápido
        </button>
      </div>

      {/* Content Area */}
      <div className="min-h-[400px]">
        {/* FAQ / Modules Section */}
        {activeTab === 'faq' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {modules.map((module, idx) => (
              <div 
                key={idx}
                className={clsx(
                  "p-6 rounded-xl border transition-all duration-300 group",
                  module.highlight 
                    ? "bg-gradient-to-br from-indigo-900/20 to-slate-900/50 border-indigo-500/30 hover:border-indigo-400/50 shadow-[0_0_15px_rgba(99,102,241,0.1)]" 
                    : "bg-slate-900/50 border-slate-800 hover:border-slate-700 hover:bg-slate-800/50"
                )}
              >
                <div className="flex items-start gap-4">
                  <div className={clsx(
                    "p-3 rounded-lg",
                    module.highlight ? "bg-indigo-500/20 text-indigo-400" : "bg-slate-800 text-slate-400 group-hover:text-amber-400 group-hover:bg-amber-400/10 transition-colors"
                  )}>
                    <module.icon size={24} />
                  </div>
                  <div>
                    <h3 className={clsx(
                      "text-lg font-semibold mb-2 flex items-center gap-2",
                      module.highlight ? "text-indigo-300" : "text-slate-200"
                    )}>
                      {module.title}
                      {module.highlight && (
                        <span className="px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 text-xs border border-indigo-500/30">
                          Recomendado
                        </span>
                      )}
                    </h3>
                    <p className="text-slate-400 text-sm leading-relaxed">
                      {module.description}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Videos Section */}
        {activeTab === 'videos' && (
          <div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {videos.map((video, idx) => (
                <div key={idx} className="group cursor-pointer">
                  <div className={clsx(
                    "aspect-video rounded-xl border border-slate-800 relative overflow-hidden mb-3 transition-all group-hover:border-amber-500/50",
                    video.thumbnail
                  )}>
                    <div className="absolute inset-0 flex items-center justify-center bg-black/20 group-hover:bg-black/40 transition-colors">
                      <div className="w-12 h-12 rounded-full bg-amber-500/90 flex items-center justify-center text-slate-900 shadow-lg group-hover:scale-110 transition-transform">
                        <PlayCircle size={24} fill="currentColor" />
                      </div>
                    </div>
                    <span className="absolute bottom-2 right-2 px-2 py-1 bg-black/80 text-white text-xs rounded font-mono">
                      {video.duration}
                    </span>
                  </div>
                  <h3 className="text-slate-200 font-medium group-hover:text-amber-400 transition-colors">
                    {video.title}
                  </h3>
                  <p className="text-slate-500 text-sm mt-1">Video Tutorial</p>
                </div>
              ))}
              
              {/* Placeholder for more */}
              <div className="aspect-video rounded-xl border-2 border-dashed border-slate-800 flex flex-col items-center justify-center text-slate-600 bg-slate-900/20">
                <PlayCircle size={32} className="mb-2 opacity-50" />
                <span className="text-sm font-medium">Más videos próximamente...</span>
              </div>
            </div>
            
            <div className="mt-8 p-4 bg-amber-500/5 border border-amber-500/10 rounded-lg flex items-center gap-3 text-amber-200/80 text-sm">
              <AlertTriangle size={18} />
              <p>Estamos grabando nuevos tutoriales. Si necesitas una explicación específica, contáctanos directamente.</p>
            </div>
          </div>
        )}

        {/* Quick Guide Section */}
        {activeTab === 'guide' && (
          <div className="bg-slate-900/50 rounded-2xl border border-slate-800 p-8">
            <div className="max-w-3xl mx-auto space-y-12">
              <div className="relative border-l-2 border-slate-800 pl-8 space-y-12">
                <div className="relative">
                  <span className="absolute -left-[41px] top-0 w-6 h-6 rounded-full bg-slate-800 border-2 border-slate-700 flex items-center justify-center text-xs font-bold text-slate-400">1</span>
                  <h3 className="text-xl font-bold text-slate-200 mb-3">Conecta tu cuenta</h3>
                  <p className="text-slate-400">
                    Al iniciar, el sistema verificará tus credenciales. Asegúrate de tener los permisos necesarios en la plataforma de destino.
                  </p>
                </div>
                
                <div className="relative">
                  <span className="absolute -left-[41px] top-0 w-6 h-6 rounded-full bg-amber-500/20 border-2 border-amber-500 text-amber-500 flex items-center justify-center text-xs font-bold">2</span>
                  <h3 className="text-xl font-bold text-amber-400 mb-3">Consulta a la Guía IA</h3>
                  <p className="text-slate-300">
                    No empieces desde cero. Ve a la pestaña <span className="text-amber-400 font-medium">Guía IA</span> y cuéntale tu objetivo: 
                    <em className="block mt-2 p-3 bg-slate-950 rounded border border-slate-800 text-slate-400 not-italic">
                      "Quiero crear una campaña para promocionar zapatos deportivos este fin de semana."
                    </em>
                    La IA estructurará el plan por ti.
                  </p>
                </div>

                <div className="relative">
                  <span className="absolute -left-[41px] top-0 w-6 h-6 rounded-full bg-slate-800 border-2 border-slate-700 flex items-center justify-center text-xs font-bold text-slate-400">3</span>
                  <h3 className="text-xl font-bold text-slate-200 mb-3">Revisa en Control Humano</h3>
                  <p className="text-slate-400">
                    Antes de publicar, todo pasa por <span className="text-slate-200 font-medium">Control Humano</span>. Aprueba o rechaza las sugerencias. Nada sale sin tu "OK".
                  </p>
                </div>
                
                <div className="relative">
                  <span className="absolute -left-[41px] top-0 w-6 h-6 rounded-full bg-slate-800 border-2 border-slate-700 flex items-center justify-center text-xs font-bold text-slate-400">4</span>
                  <h3 className="text-xl font-bold text-slate-200 mb-3">Monitorea el Tracking</h3>
                  <p className="text-slate-400">
                    Una vez activa, sigue el rendimiento en tiempo real desde la pestaña de Tracking.
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
