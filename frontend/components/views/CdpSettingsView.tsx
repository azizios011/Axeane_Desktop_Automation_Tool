"use client";

import React from 'react';
import { UserRoundCog, EyeOff, ChevronDown, Network, Activity, Save } from 'lucide-react';

export function CdpSettingsView() {
  return (
    <main className="ml-[var(--spacing-sidebar-width)] flex-1 flex flex-col h-full bg-background overflow-hidden">
      <header className="h-16 border-b border-outline-variant bg-surface px-6 flex items-center justify-between shrink-0">
        <h1 className="text-xl font-bold text-on-surface">CDP Settings</h1>
        <button className="bg-primary text-white text-xs font-bold px-6 py-2 rounded-lg hover:opacity-90 flex items-center gap-2 shadow-sm">
          <Save size={16}/> Save Configuration
        </button>
      </header>

      <div className="flex-1 overflow-y-auto p-8">
        <div className="max-w-4xl mx-auto space-y-8">
          <p className="text-sm text-on-surface-variant">
            Configure the Chrome DevTools Protocol (CDP) and Axeane credentials for automated headless navigation.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Left Column: Credentials */}
            <div className="bg-surface border border-outline-variant rounded-xl p-6 shadow-sm space-y-4">
              <h3 className="text-md font-bold flex items-center gap-2 border-b border-outline-variant pb-3">
                <UserRoundCog className="text-primary" size={18} /> Axeane Credentials
              </h3>
              
              <div className="space-y-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-on-surface">Username</label>
                  <input type="text" defaultValue="admin@axeane.com" className="w-full bg-surface-container-low border border-outline-variant rounded-lg px-3 py-2 text-sm outline-none focus:border-primary" />
                </div>
                
                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-on-surface">Password</label>
                  <div className="relative">
                    <input type="password" defaultValue="••••••••" className="w-full bg-surface-container-low border border-outline-variant rounded-lg px-3 py-2 text-sm outline-none focus:border-primary" />
                    <button className="absolute right-3 top-2.5 text-on-surface-variant"><EyeOff size={16} /></button>
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                   <div className="space-y-1.5">
                    <label className="text-xs font-bold text-on-surface">Enterprise ID</label>
                    <input type="text" defaultValue="AX-9942" className="w-full bg-surface-container-low border border-outline-variant rounded-lg px-3 py-2 text-sm font-mono" />
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-xs font-bold text-on-surface">Exercice</label>
                    <div className="relative">
                      <select className="w-full bg-surface-container-low border border-outline-variant rounded-lg px-3 py-2 text-sm appearance-none outline-none">
                        <option>2026</option>
                        <option>2025</option>
                      </select>
                      <ChevronDown className="absolute right-3 top-2.5 text-on-surface-variant pointer-events-none" size={16} />
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Right Column: Connection */}
            <div className="bg-surface border border-outline-variant rounded-xl p-6 shadow-sm space-y-4">
              <h3 className="text-md font-bold flex items-center gap-2 border-b border-outline-variant pb-3">
                <Network className="text-secondary" size={18} /> CDP Connection
              </h3>
              
              <div className="space-y-6">
                <div className="flex items-center justify-between p-3 bg-primary/5 rounded-lg border border-primary/20">
                  <div>
                    <span className="block text-sm font-bold text-primary">Headless Mode</span>
                    <span className="text-[10px] text-on-surface-variant uppercase font-bold">Recommended for Speed</span>
                  </div>
                  <input type="checkbox" defaultChecked className="w-5 h-5 accent-primary" />
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1.5">
                    <label className="text-xs font-bold text-on-surface">CDP Port</label>
                    <input type="number" defaultValue="9222" className="w-full bg-surface-container-low border border-outline-variant rounded-lg px-3 py-2 text-sm font-mono" />
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-xs font-bold text-on-surface">Timeout (ms)</label>
                    <input type="number" defaultValue="30000" className="w-full bg-surface-container-low border border-outline-variant rounded-lg px-3 py-2 text-sm font-mono" />
                  </div>
                </div>
                
                <button className="w-full bg-secondary-container text-on-secondary-container hover:opacity-90 rounded-lg py-2.5 px-4 flex items-center justify-center gap-2 text-sm font-bold transition-all border border-outline-variant/30">
                  <Activity size={18} /> Test CDP Connection
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
