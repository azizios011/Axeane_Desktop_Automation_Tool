"use client";

import React from 'react';
import { 
  Settings, Monitor, Upload, Workflow, PlayCircle, Droplet, HelpCircle 
} from 'lucide-react';
import { TabState } from '@/app/page';

interface SidebarProps {
  currentTab: TabState;
  onChangeTab: (tab: TabState) => void;
}

export function Sidebar({ currentTab, onChangeTab }: SidebarProps) {
  const navItems = [
    { id: 'settings', label: '⚙️ Settings', icon: Settings },
    { id: 'pwa', label: '🚀 Browser / CDP', icon: Monitor },
    { id: 'import', label: '📥 Import Data', icon: Upload },
    { id: 'review', label: '🔧 Preview & Rules', icon: Workflow },
    { id: 'execution', label: '🏁 Execution & Logs', icon: PlayCircle },
  ];

  const getNavClass = (id: TabState) => {
    const isActive = currentTab === id;
    return `flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 cursor-pointer text-sm font-bold ${
      isActive 
        ? "text-white bg-primary shadow-lg shadow-primary/20" 
        : "text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high"
    }`;
  };

  return (
    /* 
      REMOVED: fixed, left-0, top-0 
      ADDED: shrink-0 (prevents the sidebar from collapsing)
    */
    <aside className="h-full shrink-0 border-r border-outline-variant bg-surface flex flex-col py-4 px-2 z-40">
      
      {/* Branding */}
      <div className="mb-8 px-2 flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center text-on-primary shadow-inner">
          <Droplet size={20} />
        </div>
        <div>
          <h1 className="text-lg font-black text-on-surface leading-tight uppercase tracking-tighter">Axeane</h1>
          <p className="text-[10px] font-mono text-on-surface-variant">ENGINE v1.0.0</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 overflow-y-auto px-1">
        {navItems.map((item) => (
          <div 
            key={item.id} 
            onClick={() => onChangeTab(item.id as TabState)} 
            className={getNavClass(item.id as TabState)}
          >
            <item.icon size={18} strokeWidth={isActive(item.id) ? 2.5 : 2} /> 
            {item.label}
          </div>
        ))}
      </nav>

      {/* Footer User Profile */}
      <div className="mt-auto pt-4 border-t border-outline-variant space-y-1">
        <div className="flex items-center gap-3 px-3 py-2 rounded-lg text-on-surface-variant hover:bg-surface-container-high cursor-pointer text-xs font-bold transition-colors">
          <HelpCircle size={18} /> Support Center
        </div>
        <div className="flex items-center gap-3 px-3 py-3 mt-2 bg-surface-container-low rounded-2xl border border-outline-variant/50">
          <div className="w-8 h-8 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center text-primary font-bold text-xs">
            AJ
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-bold text-on-surface truncate">Admin User</p>
            <p className="font-mono text-[9px] text-on-surface-variant uppercase tracking-widest">Controller</p>
          </div>
        </div>
      </div>
    </aside>
  );

  // Helper to check if item is active for icon styling
  function isActive(id: string) {
    return currentTab === id;
  }
}
