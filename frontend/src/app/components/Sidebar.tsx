import {
  LayoutDashboard,
  PlusCircle,
  History,
  BarChart3,
  Settings,
  Shield,
  Bell,
  ChevronRight,
  Car,
  HelpCircle,
  LogOut,
} from 'lucide-react';
import { motion } from 'motion/react';
import type { ViewType } from '../types';

interface SidebarProps {
  currentView: ViewType;
  onNavigate: (view: ViewType) => void;
}

const mainNav = [
  { icon: LayoutDashboard, label: 'Dashboard', view: 'dashboard' as ViewType },
  { icon: PlusCircle, label: 'New Claim', view: 'new-claim' as ViewType },
  { icon: History, label: 'Claim History', view: 'history' as ViewType },
  { icon: BarChart3, label: 'Analytics', view: 'dashboard' as ViewType },
];

const bottomNav = [
  { icon: Bell, label: 'Notifications', badge: 3, view: 'dashboard' as ViewType },
  { icon: Settings, label: 'Settings', view: 'dashboard' as ViewType },
  { icon: HelpCircle, label: 'Help & Support', view: 'dashboard' as ViewType },
];

export function Sidebar({ currentView, onNavigate }: SidebarProps) {
  return (
    <div
      className="flex flex-col h-full w-64 shrink-0"
      style={{ background: '#0D1B3E', fontFamily: "'Roboto', sans-serif" }}
    >
      {/* Logo */}
      <div className="px-6 py-5 border-b border-white/10">
        <div className="flex items-center gap-3">
          <div
            className="w-9 h-9 rounded-xl flex items-center justify-center"
            style={{ background: 'linear-gradient(135deg, #1976D2, #42A5F5)' }}
          >
            <Shield className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="text-white font-semibold text-base leading-tight">ClaimSense</div>
            <div className="text-xs leading-tight" style={{ color: '#42A5F5' }}>
              AI Platform
            </div>
          </div>
        </div>
      </div>

      {/* New Claim CTA */}
      <div className="px-4 py-4">
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => onNavigate('new-claim')}
          className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl text-sm font-medium text-white"
          style={{
            background: 'linear-gradient(135deg, #1565C0, #1976D2)',
            boxShadow: '0 4px 14px rgba(25, 118, 210, 0.4)',
          }}
        >
          <PlusCircle className="w-4 h-4" />
          New Claim
        </motion.button>
      </div>

      {/* Main Navigation */}
      <nav className="flex-1 px-3 py-2 space-y-0.5">
        <div className="text-xs font-medium px-3 py-2" style={{ color: 'rgba(255,255,255,0.3)' }}>
          MAIN MENU
        </div>
        {mainNav.map((item) => {
          const isActive =
            currentView === item.view ||
            (item.view === 'dashboard' && item.label === 'Dashboard' && currentView === 'dashboard');
          const isActuallyActive =
            item.label === 'Dashboard'
              ? currentView === 'dashboard'
              : item.label === 'New Claim'
              ? currentView === 'new-claim'
              : item.label === 'Claim History'
              ? currentView === 'history'
              : false;

          return (
            <motion.button
              key={item.label}
              whileHover={{ x: 2 }}
              onClick={() => onNavigate(item.view)}
              className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm transition-all"
              style={{
                color: isActuallyActive ? '#fff' : 'rgba(255,255,255,0.6)',
                background: isActuallyActive ? 'rgba(25, 118, 210, 0.35)' : 'transparent',
              }}
            >
              <item.icon className="shrink-0" style={{ width: 18, height: 18 }} />
              <span>{item.label}</span>
              {isActuallyActive && (
                <ChevronRight className="w-3 h-3 ml-auto" style={{ color: '#42A5F5' }} />
              )}
            </motion.button>
          );
        })}

        <div
          className="text-xs font-medium px-3 py-2 mt-4"
          style={{ color: 'rgba(255,255,255,0.3)' }}
        >
          SYSTEM
        </div>
        {bottomNav.map((item) => (
          <motion.button
            key={item.label}
            whileHover={{ x: 2 }}
            onClick={() => onNavigate(item.view)}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm"
            style={{ color: 'rgba(255,255,255,0.5)' }}
          >
            <item.icon className="shrink-0" style={{ width: 18, height: 18 }} />
            <span>{item.label}</span>
            {'badge' in item && item.badge && (
              <span
                className="ml-auto text-xs px-1.5 py-0.5 rounded-full"
                style={{ background: '#EF4444', color: '#fff', fontSize: 10 }}
              >
                {item.badge}
              </span>
            )}
          </motion.button>
        ))}
      </nav>

      {/* User Profile */}
      <div className="px-4 py-4 border-t border-white/10">
        <div className="flex items-center gap-3">
          <div
            className="w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold text-white shrink-0"
            style={{ background: 'linear-gradient(135deg, #1976D2, #42A5F5)' }}
          >
            JD
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-sm font-medium text-white truncate">Jane Doe</div>
            <div className="text-xs truncate" style={{ color: 'rgba(255,255,255,0.4)' }}>
              Claims Adjuster
            </div>
          </div>
          <button style={{ color: 'rgba(255,255,255,0.4)' }}>
            <LogOut style={{ width: 16, height: 16 }} />
          </button>
        </div>
      </div>
    </div>
  );
}
