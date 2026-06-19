// components/views/CdpSettingsView.tsx
"use client";

import React from 'react';
import { 
  UserRoundCog, EyeOff, Eye, ChevronDown, Network, 
  Activity, Save, Globe, Folder, Monitor, Cpu 
} from 'lucide-react';
import { useCdpModule } from '@/modules/useCdpModule';
import { BROWSER_TYPES, LAUNCH_MODES, ENTERPRISE_OPTIONS, EXERCICE_OPTIONS } from '@/metadata/cdpDefaults';

export function CdpSettingsView() {
  const { 
    config, updateField, updateBrowserType, 
    showPassword, setShowPassword, handleSave 
  } = useCdpModule();

  return (
    <main className="ml-[var(--spacing-sidebar-width)] flex-1 flex flex-col h-full bg-background overflow-hidden">
      <header className="h-16 border-b border-outline-variant bg-surface px-6 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-secondary-container flex items-center justify-center text-on-secondary-container">
            <Cpu size={18} />
          </div>
          <h1 className="text-xl font-bold">System Configuration</h1>
        </div>
        <button 
          onClick={handleSave}
          className="bg-primary text-white text-xs font-bold px-6 py-2.5 rounded-xl hover:opacity-90 flex items-center gap-2 shadow-lg shadow-primary/20 transition-all"
        >
          <Save size={16}/> Save Settings
        </button>
      </header>

      <div className="flex-1 overflow-y-auto p-8 bg-surface-container-low">
        <div className="max-w-5xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* Left Column: Authentication & Context (4 Cols) */}
          <div className="lg:col-span-5 space-y-6">
            <section className="bg-surface border border-outline-variant rounded-2xl p-6 shadow-sm">
              <h3 className="text-sm font-black uppercase tracking-widest text-primary mb-6 flex items-center gap-2">
                <UserRoundCog size={18} /> Axeane Credentials
              </h3>
              
              <div className="space-y-4">
                <div className="space-y-1.5">
                  <label className="text-[10px] font-bold text-on-surface-variant uppercase">Username</label>
                  <input 
                    type="text" 
                    value={config.auth.username}
                    onChange={(e) => updateField('auth', 'username', e.target.value)}
                    className="w-full bg-surface-container-low border border-outline-variant rounded-xl px-4 py-2.5 text-sm outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all" 
                  />
                </div>
                
                <div className="space-y-1.5">
                  <label className="text-[10px] font-bold text-on-surface-variant uppercase">Password</label>
                  <div className="relative">
                    <input 
                      type={showPassword ? "text" : "password"} 
                      value={config.auth.password}
                      onChange={(e) => updateField('auth', 'password', e.target.value)}
                      className="w-full bg-surface-container-low border border-outline-variant rounded-xl px-4 py-2.5 text-sm outline-none focus:border-primary" 
                    />
                    <button 
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-2.5 text-on-surface-variant hover:text-primary"
                    >
                      {showPassword ? <Eye size={18} /> : <EyeOff size={18} />}
                    </button>
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-4 pt-2">
                   <div className="space-y-1.5">
                    <label className="text-[10px] font-bold text-on-surface-variant uppercase">Enterprise</label>
                    <select 
                      value={config.auth.enterprise}
                      onChange={(e) => updateField('auth', 'enterprise', e.target.value)}
                      className="w-full bg-surface-container-low border border-outline-variant rounded-xl px-3 py-2.5 text-sm outline-none appearance-none"
                    >
                      {ENTERPRISE_OPTIONS.map(opt => <option key={opt}>{opt}</option>)}
                    </select>
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-[10px] font-bold text-on-surface-variant uppercase">Exercice</label>
                    <select 
                      value={config.auth.exercice}
                      onChange={(e) => updateField('auth', 'exercice', e.target.value)}
                      className="w-full bg-surface-container-low border border-outline-variant rounded-xl px-3 py-2.5 text-sm outline-none appearance-none"
                    >
                      {EXERCICE_OPTIONS.map(opt => <option key={opt}>{opt}</option>)}
                    </select>
                  </div>
                </div>
              </div>
            </section>
          </div>

          {/* Right Column: Browser & CDP (7 Cols) */}
          <div className="lg:col-span-7 space-y-6">
            <section className="bg-surface border border-outline-variant rounded-2xl p-6 shadow-sm">
              <h3 className="text-sm font-black uppercase tracking-widest text-secondary mb-6 flex items-center gap-2">
                <Network size={18} /> Browser Engine & CDP
              </h3>
              
              <div className="grid grid-cols-2 gap-6">
                <div className="space-y-1.5">
                  <label className="text-[10px] font-bold text-on-surface-variant uppercase">Browser Type</label>
                  <select 
                    value={config.browser.type}
                    onChange={(e) => updateBrowserType(e.target.value)}
                    className="w-full bg-surface-container-low border border-outline-variant rounded-xl px-3 py-2.5 text-sm outline-none appearance-none"
                  >
                    {BROWSER_TYPES.map(opt => <option key={opt}>{opt}</option>)}
                  </select>
                </div>

                <div className="space-y-1.5">
                  <label className="text-[10px] font-bold text-on-surface-variant uppercase">Launch Mode</label>
                  <select 
                    value={config.browser.mode}
                    onChange={(e) => updateField('browser', 'mode', e.target.value)}
                    className="w-full bg-surface-container-low border border-outline-variant rounded-xl px-3 py-2.5 text-sm outline-none appearance-none"
                  >
                    {LAUNCH_MODES.map(opt => <option key={opt.id} value={opt.id}>{opt.label}</option>)}
                  </select>
                </div>

                <div className="col-span-2 space-y-1.5">
                  <label className="text-[10px] font-bold text-on-surface-variant uppercase">Executable Path</label>
                  <div className="flex gap-2">
                    <input 
                      type="text" 
                      value={config.browser.executable_path}
                      onChange={(e) => updateField('browser', 'executable_path', e.target.value)}
                      className="flex-1 bg-surface-container-low border border-outline-variant rounded-xl px-4 py-2.5 text-xs font-mono outline-none" 
                    />
                    <button className="px-4 py-2 bg-surface-container-high border border-outline-variant rounded-xl text-xs font-bold hover:bg-surface-variant transition-colors">
                      Browse
                    </button>
                  </div>
                </div>

                <div className="space-y-1.5">
                  <label className="text-[10px] font-bold text-on-surface-variant uppercase">CDP Port</label>
                  <input 
                    type="number" 
                    value={config.browser.cdp_port}
                    onChange={(e) => updateField('browser', 'cdp_port', parseInt(e.target.value))}
                    className="w-full bg-surface-container-low border border-outline-variant rounded-xl px-4 py-2.5 text-sm font-mono outline-none" 
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="text-[10px] font-bold text-on-surface-variant uppercase">PWA URL</label>
                  <input 
                    type="text" 
                    value={config.browser.pwa_url}
                    onChange={(e) => updateField('browser', 'pwa_url', e.target.value)}
                    className="w-full bg-surface-container-low border border-outline-variant rounded-xl px-4 py-2.5 text-sm outline-none" 
                  />
                </div>

                <div className="col-span-2 flex items-center justify-between p-4 bg-primary/5 rounded-2xl border border-primary/10">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-primary/10 text-primary rounded-lg">
                      <Monitor size={18} />
                    </div>
                    <div>
                      <span className="block text-sm font-bold text-on-surface">Headless Execution</span>
                      <span className="text-[10px] text-on-surface-variant uppercase font-bold">Run without visible window</span>
                    </div>
                  </div>
                  <input 
                    type="checkbox" 
                    checked={config.browser.headless}
                    onChange={(e) => updateField('browser', 'headless', e.target.checked)}
                    className="w-6 h-6 rounded-lg accent-primary cursor-pointer" 
                  />
                </div>
              </div>

              <div className="pt-4">
                <button className="w-full bg-secondary-container text-on-secondary-container hover:bg-secondary-container/80 rounded-xl py-3 px-4 flex items-center justify-center gap-2 text-sm font-bold transition-all border border-outline-variant/30">
                  <Activity size={18} /> Test CDP Connectivity
                </button>
              </div>
            </section>
          </div>

        </div>
      </div>
    </main>
  );
}
