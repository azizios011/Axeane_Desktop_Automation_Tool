"use client";

import React from 'react';
import {
  Droplet, Plus, Upload, Workflow, CheckSquare,
  Settings2, HelpCircle, Settings, Ruler
} from 'lucide-react';

type ViewState = 'import' | 'process' | 'validation' | 'cdp' | 'rules';

interface SidebarProps {
  currentView: ViewState;
  onChangeView: (view: ViewState) => void;
}

export function Sidebar({ currentView, onChangeView }: SidebarProps) {
  const getNavClass = (view: ViewState) => {
    const isActive = currentView === view;
    return `flex items-center gap-3 px-3 py-2 rounded-lg transition-all duration-200 cursor-pointer focus-ring ${
      isActive 
        ? "text-primary font-bold border-l-2 border-primary bg-secondary-container/30" 
        : "text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high"
    }`;
  };

  return (
    <aside className="fixed left-0 top-0 h-full w-[var(--spacing-sidebar-width)] border-r border-outline-variant bg-surface flex flex-col py-4 px-2 z-40">
      <div className="mb-8 px-2 flex items-center gap-3">
        <div className="w-8 h-8 rounded bg-primary flex items-center justify-center text-on-primary">
          <Droplet size={20} />
        </div>
        <div>
          <h1 className="text-lg font-bold text-on-surface leading-tight">Axeane Flow</h1>
          <p className="text-xs text-on-surface-variant">Enterprise Finance</p>
        </div>
      </div>

      <button className="mb-6 w-full flex items-center justify-center gap-2 bg-primary text-on-primary py-2 px-4 rounded-lg hover:bg-primary/90 transition-colors focus-ring font-medium">
        <Plus size={18} />
        New Workflow
      </button>

      <nav className="flex-1 space-y-1 overflow-y-auto">
        <div onClick={() => onChangeView('import')} className={getNavClass('import')}>
          <Upload size={20} /> Import
        </div>
        <div onClick={() => onChangeView('process')} className={getNavClass('process')}>
          <Workflow size={20} /> Process
        </div>
        <div onClick={() => onChangeView('validation')} className={getNavClass('validation')}>
          <CheckSquare size={20} /> Validation
        </div>
        <div onClick={() => onChangeView('cdp')} className={getNavClass('cdp')}>
          <Settings2 size={20} /> CDP Settings
        </div>
        <div onClick={() => onChangeView('rules')} className={getNavClass('rules')}>
          <Ruler size={20} /> Rules
        </div>
      </nav>

      <div className="mt-auto pt-4 border-t border-outline-variant space-y-1">
        <div className="flex items-center gap-3 px-3 py-2 rounded-lg text-on-surface-variant hover:bg-surface-container-high cursor-pointer">
          <HelpCircle size={20} /> Support
        </div>
        <div className="flex items-center gap-3 px-3 py-2 mb-4">
          <div className="w-8 h-8 rounded-full bg-secondary-container border border-outline-variant" />
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-on-surface truncate">Sarah Jenkins</p>
            <p className="font-mono text-[10px] text-on-surface-variant">Controller</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
