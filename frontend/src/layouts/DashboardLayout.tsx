import React, { useState } from 'react';
import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { LayoutDashboard, Megaphone, LogOut, Compass, LineChart, ShieldAlert, BrainCircuit, Menu, X, User, HelpCircle, Share2, ArrowLeft, Users } from 'lucide-react';
import { AIStatusBadge } from '../components/common/AIStatusBadge';
import { IdentitiesManager } from '../components/identities/IdentitiesManager';

export const DashboardLayout: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isIdentityModalOpen, setIsIdentityModalOpen] = useState(false);

  // Updated order based on user request (Logical Flow):
  // 1. Dashboard (Overview)
  // 2. Ara Post Manager (Creation/Strategy)
  // 3. Control Humano (Approval/Safety)
  // 4. Campañas (Execution/Management) -> Moved up
  // 5. Tracking (Analytics/Results) -> Moved down
  // 6. Zona Roja (Emergency)
  // 7. Conexiones (Configuration)
  // 8. Ayuda & Soporte (Help)
  const navItems = [
    { icon: LayoutDashboard, label: 'Dashboard', path: '/' },
    { icon: Compass, label: 'Ara Post Manager', path: '/guide' },
    { icon: Users, label: 'Identidades funcionales', action: () => setIsIdentityModalOpen(true) },
    { icon: BrainCircuit, label: 'Control Humano', path: '/control' },
    { icon: Megaphone, label: 'Campañas', path: '/campaigns' },
    { icon: LineChart, label: 'Tracking', path: '/tracking' },
    { icon: ShieldAlert, label: 'Zona Roja (Override)', path: '/overrides' },
    { icon: Share2, label: 'Conexiones', path: '/connections' },
    { icon: HelpCircle, label: 'Ayuda & Soporte', path: '/support' },
  ];

  return (
    <div className="flex h-screen bg-slate-950 text-slate-200 overflow-hidden">
      {/* Mobile Overlay */}
      {isMobileMenuOpen && (
        <div 
          className="fixed inset-0 bg-black/60 z-40 lg:hidden backdrop-blur-sm"
          onClick={() => setIsMobileMenuOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={`
        fixed inset-y-0 left-0 z-50 w-64 bg-slate-900/95 backdrop-blur-xl border-r border-slate-800 
        transform transition-transform duration-300 ease-in-out
        lg:relative lg:translate-x-0 
        ${isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <div className="p-6 flex justify-between items-center">
          <h1 className="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-amber-400 to-amber-600">
            Ara Neuro Post
          </h1>
          <button 
            onClick={() => setIsMobileMenuOpen(false)}
            className="lg:hidden text-slate-400 hover:text-white"
          >
            <X size={24} />
          </button>
        </div>
        
        <nav className="mt-4 px-4 space-y-2">
          {navItems.map((item, index) => {
            const Icon = item.icon;
            
            if (item.action) {
              return (
                <button
                  key={index}
                  onClick={() => {
                    item.action();
                    setIsMobileMenuOpen(false);
                  }}
                  className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium text-slate-400 hover:bg-slate-800 hover:text-slate-200 transition-all duration-200"
                >
                  <Icon size={20} />
                  {item.label}
                </button>
              );
            }

            const isActive = location.pathname === item.path;
            
            return (
              <Link
                key={item.path}
                to={item.path!}
                onClick={() => setIsMobileMenuOpen(false)}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${
                  isActive 
                    ? 'bg-amber-500/10 text-amber-400 border-l-2 border-amber-400' 
                    : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'
                }`}
              >
                <Icon size={20} className={isActive ? 'drop-shadow-[0_0_8px_rgba(251,191,36,0.5)]' : ''} />
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="absolute bottom-0 w-64 p-4 border-t border-slate-800 bg-slate-900/50">
          <button className="flex items-center gap-3 px-4 py-3 w-full text-sm font-medium text-red-400 hover:bg-red-500/10 rounded-lg transition-colors">
            <LogOut size={20} />
            Cerrar Sesión
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col h-full overflow-hidden bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-slate-900 via-slate-950 to-slate-950">
        <header className="h-16 bg-slate-900/50 backdrop-blur-md border-b border-slate-800 px-4 lg:px-8 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-4">
            <button 
              onClick={() => setIsMobileMenuOpen(true)}
              className="lg:hidden text-slate-400 hover:text-white p-1"
            >
              <Menu size={24} />
            </button>
            
            {/* Back Button (visible if not on Dashboard) */}
            {location.pathname !== '/' && (
              <button 
                onClick={() => navigate(-1)}
                className="p-1 text-slate-400 hover:text-amber-400 transition-colors mr-2"
                title="Volver atrás"
              >
                <ArrowLeft size={20} />
              </button>
            )}

            <h2 className="text-lg font-semibold text-slate-200 truncate max-w-[150px] sm:max-w-none">
              {navItems.find(i => i.path === location.pathname)?.label || 'Dashboard'}
            </h2>
          </div>
          <div className="flex items-center gap-4">
            <AIStatusBadge />
            <span className="hidden sm:inline text-sm text-slate-500 font-mono">v0.1.0 (MVP)</span>
            <div className="w-8 h-8 bg-amber-500/20 rounded-full flex items-center justify-center text-amber-400 font-bold border border-amber-500/30 shadow-[0_0_10px_rgba(245,158,11,0.2)]">
              <User size={18} />
            </div>
          </div>
        </header>
        
        <div className="flex-1 overflow-auto p-4 lg:p-8">
          <Outlet />
        </div>
      </main>

      {/* Identity Manager Modal */}
      {isIdentityModalOpen && (
        <IdentitiesManager 
          onClose={() => setIsIdentityModalOpen(false)} 
        />
      )}
    </div>
  );
};
