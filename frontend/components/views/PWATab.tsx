"use client";

import React from 'react';
import { 
  Monitor, Globe, Folder, Cpu, Network, 
  Activity, Save, Settings2, ShieldCheck, HardDrive 
} from 'lucide-react';
import { usePwaModule } from '@/modules/usePwaModule';
import { BROWSER_TYPES, LAUNCH_MODES } from '@/metadata/cdpDefaults';

export function PWATab() {
  const { 
    cdpSettings, updateBrowserType, updateField, handleSave 
  } = usePwaModule();

  return (
    <main className="flex-1 flex flex-col h-full bg-background overflow-hidden">
      <header className="h-16 border-b border-outline-variant bg-surface px-6 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-3">
          <Monitor className="text-primary" size={20} />
          <h1 className="text-xl font-bold text-on-surface">Browser Engine & CDP Configuration</h1>
        </div>
        <button 
          onClick={handleSave}
          className="bg-primary text-white text-xs font-bold px-6 py-2.5 rounded-xl hover:opacity-90 flex items-center gap-2 shadow-lg shadow-primary/20 transition-all"
        >
          <Save size={16}/> Save Browser Config
        </button>
      </header>

      <div className="flex-1 overflow-y-auto p-8 bg-surface-container-low space-y-6">
        <div className="max-w-4xl mx-auto space-y-6">
          
          {/* Section 1: Browser Engine (Matches Python Engine Selection) */}
          <section className="bg-surface border border-outline-variant rounded-2xl p-6 shadow-sm space-y-6">
            <h3 className="text-sm font-black uppercase tracking-widest text-primary flex items-center gap-2">
              <Cpu size={18} /> 1. Browser Engine & Executable
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-1.5">
                <label className="text-[10px] font-bold text-on-surface-variant uppercase">Browser Type</label>
                <select 
                  value={cdpSettings.browser_type}
                  onChange={(e) => updateBrowserType(e.target.value)}
                  className="w-full bg-surface-container-low border border-outline-variant rounded-xl px-4 py-2.5 text-sm outline-none appearance-none"
                >
                  {BROWSER_TYPES.map(type => <option key={type} value={type}>{type}</option>)}
                </select>
              </div>

              <div className="space-y-1.5">
                <label className="text-[10px] font-bold text-on-surface-variant uppercase">Executable Path</label>
                <div className="flex gap-2">
                  <input 
                    type="text" 
                    value={cdpSettings.executable_path}
                    onChange={(e) => updateField('executable_path', e.target.value)}
                    className="flex-1 bg-surface-container-low border border-outline-variant rounded-xl px-4 py-2.5 text-xs font-mono outline-none focus:border-primary" 
                  />
                  <button className="px-4 py-2 bg-surface-container-high border border-outline-variant rounded-xl text-xs font-bold hover:bg-surface-variant transition-colors shrink-0">
                    Browse
                  </button>
                </div>
              </div>
            </div>
          </section>

          {/* Section 2: Launch Mode (Matches Python Radio Buttons) */}
          <section className="bg-surface border border-outline-variant rounded-2xl p-6 shadow-sm space-y-4">
            <h3 className="text-sm font-black uppercase tracking-widest text-secondary flex items-center gap-2">
              <Network size={18} /> 2. Launch Mode
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {LAUNCH_MODES.map((mode) => (
                <label 
                  key={mode.id}
                  className={`flex items-center gap-3 p-4 rounded-xl border-2 transition-all cursor-pointer ${
                    cdpSettings.mode === mode.id 
                      ? 'border-primary bg-primary/5 ring-1 ring-primary' 
                      : 'border-outline-variant bg-surface hover:bg-surface-container-low'
                  }`}
                >
                  <input 
                    type="radio" 
                    name="launch_mode" 
                    checked={cdpSettings.mode === mode.id}
                    onChange={() => updateField('mode', mode.id)}
                    className="w-4 h-4 accent-primary" 
                  />
                  <span className="text-xs font-bold text-on-surface">{mode.label}</span>
                </label>
              ))}
            </div>
          </section>

          {/* Section 3: Mode Specific Settings (Matches Python Section 3) */}
          <section className="bg-surface border border-outline-variant rounded-2xl p-6 shadow-sm space-y-6">
            <h3 className="text-sm font-black uppercase tracking-widest text-on-surface-variant flex items-center gap-2">
              <Settings2 size={18} /> 3. Mode Specific Settings
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-1.5">
                <label className="text-[10px] font-bold text-on-surface-variant uppercase flex items-center gap-2">
                   <Activity size={14} /> CDP Port
                </label>
                <input 
                  type="number" 
                  value={cdpSettings.cdp_port}
                  onChange={(e) => updateField('cdp_port', parseInt(e.target.value))}
                  className="w-full bg-surface-container-low border border-outline-variant rounded-xl px-4 py-2.5 text-sm font-mono outline-none" 
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-[10px] font-bold text-on-surface-variant uppercase flex items-center gap-2">
                  <Folder size={14} /> Profile Directory
                </label>
                <input 
                  type="text" 
                  value={cdpSettings.profile_dir}
                  onChange={(e) => updateField('profile_dir', e.target.value)}
                  className="w-full bg-surface-container-low border border-outline-variant rounded-xl px-4 py-2.5 text-sm outline-none" 
                />
              </div>

              <div className="col-span-1 md:col-span-2 space-y-1.5">
                <label className="text-[10px] font-bold text-on-surface-variant uppercase flex items-center gap-2">
                  <Globe size={14} /> PWA / Entry URL
                </label>
                <input 
                  type="text" 
                  value={cdpSettings.pwa_url}
                  onChange={(e) => updateField('pwa_url', e.target.value)}
                  className="w-full bg-surface-container-low border border-outline-variant rounded-xl px-4 py-2.5 text-sm outline-none" 
                />
              </div>

              <div className="col-span-1 md:col-span-2 flex items-center justify-between p-4 bg-primary/5 rounded-2xl border border-primary/10">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-primary/10 text-primary rounded-lg">
                    <ShieldCheck size={18} />
                  </div>
                  <div>
                    <span className="block text-sm font-bold text-on-surface">Run in Background (Headless)</span>
                    <span className="text-[10px] text-on-surface-variant uppercase font-bold">Standard automation performance</span>
                  </div>
                </div>
                <input 
                  type="checkbox" 
                  checked={cdpSettings.headless}
                  onChange={(e) => updateField('headless', e.target.checked)}
                  className="w-6 h-6 rounded-lg accent-primary cursor-pointer" 
                />
              </div>
            </div>

            <button className="w-full bg-secondary-container text-on-secondary-container hover:bg-secondary-container/80 rounded-xl py-3 px-4 flex items-center justify-center gap-2 text-sm font-black transition-all border border-outline-variant/30">
              <HardDrive size={18} /> Validate Connection to CDP
            </button>
          </section>

        </div>
      </div>
    </main>
  );
}
