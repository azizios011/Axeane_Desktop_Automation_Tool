// components/views/RulesManagementView.tsx
"use client";

import React from 'react';
import { 
  Router, Key, ListChecks, Plus, Code, Trash2, 
  Save, Play, Hash, Landmark, Receipt, Coins, 
  ChevronRight, Sparkles 
} from 'lucide-react';
import { useRulesModule } from '@/modules/useRulesModule';
import { ENTRY_STEPS, DEFAULT_TVA_RATES } from '@/metadata/rulesDefinitions';

export function SettingsTab() {
  const { 
    profiles, selectedProfile, setSelectedProfileId, 
    updateProfile, addProfile, isTesting, setIsTesting 
  } = useRulesModule();

  return (
    <main className="ml-[var(--spacing-sidebar-width)] flex-1 flex flex-col h-full bg-background overflow-hidden">
      <header className="h-16 border-b border-outline-variant flex items-center justify-between px-6 bg-surface shrink-0">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-primary/10 text-primary rounded-lg">
            <Router size={20} />
          </div>
          <h2 className="text-xl font-bold">Accounting Logic & Rules</h2>
        </div>
        <div className="flex items-center gap-3">
          <button 
            onClick={() => setIsTesting(!isTesting)}
            className={`px-4 py-2 border rounded-xl text-xs font-bold flex items-center gap-2 transition-all ${isTesting ? 'bg-primary text-white border-primary' : 'border-outline-variant hover:bg-surface-container'}`}
          >
            <Play size={16} /> {isTesting ? 'Logic Test Active' : 'Test Logic'}
          </button>
          <button className="px-6 py-2 bg-primary text-white text-xs font-bold rounded-xl hover:opacity-90 flex items-center gap-2 shadow-lg shadow-primary/20">
            <Save size={16} /> Deploy Rules
          </button>
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden bg-surface-container-low">
        {/* Left: Client Profile List (AccountManager Logic) */}
        <div className="w-80 border-r border-outline-variant bg-surface flex flex-col shrink-0 shadow-sm">
          <div className="p-4 border-b border-outline-variant flex items-center justify-between bg-surface-container-low">
            <span className="text-[10px] font-black uppercase tracking-widest text-on-surface-variant">Client Profiles</span>
            <button onClick={addProfile} className="p-1 hover:bg-primary/10 rounded-full text-primary transition-colors">
              <Plus size={20} />
            </button>
          </div>
          
          <div className="p-3 overflow-y-auto flex-1 space-y-2">
            {profiles.map((profile) => (
              <div 
                key={profile.id}
                onClick={() => setSelectedProfileId(profile.id)}
                className={`group p-4 rounded-2xl cursor-pointer transition-all border-2 ${
                  selectedProfile?.id === profile.id 
                    ? 'border-primary bg-primary/5 shadow-sm' 
                    : 'border-transparent hover:border-outline-variant bg-surface'
                }`}
              >
                <div className="flex justify-between items-start mb-2">
                  <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${profile.type === 'specific' ? 'bg-green-500' : 'bg-orange-500'}`} />
                    <h3 className="text-xs font-bold truncate max-w-[140px]">{profile.match}</h3>
                  </div>
                  <ChevronRight size={14} className={`transition-transform ${selectedProfile?.id === profile.id ? 'translate-x-1 text-primary' : 'text-on-surface-variant'}`} />
                </div>
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-1 text-[10px] font-mono text-on-surface-variant bg-surface-container-high px-1.5 py-0.5 rounded">
                    <Hash size={10} /> {profile.compte_client}
                  </div>
                  <div className="flex gap-1">
                    {profile.use_cash && <Coins size={12} className="text-green-600" />}
                    {profile.use_timbre && <Receipt size={12} className="text-blue-600" />}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right: Rule Editor (RulesEngine Logic) */}
        <div className="flex-1 overflow-y-auto p-8">
          {selectedProfile ? (
            <div className="max-w-3xl mx-auto space-y-6">
              {/* Part 1: Matching String */}
              <div className="bg-surface rounded-2xl border border-outline-variant shadow-sm p-6 space-y-4">
                <div className="flex items-center gap-2 text-primary font-bold text-sm">
                  <Key size={18} /> Profile Identification
                </div>
                <div className="space-y-2">
                  <label className="text-[10px] font-bold uppercase text-on-surface-variant">Substring Match Key (Case Insensitive)</label>
                  <div className="relative">
                    <Code className="absolute left-4 top-3 text-on-surface-variant" size={18} />
                    <input 
                      type="text" 
                      value={selectedProfile.match}
                      onChange={(e) => updateProfile(selectedProfile.id, { match: e.target.value })}
                      className="w-full pl-12 pr-4 py-3 border border-outline-variant rounded-xl font-mono text-sm bg-surface-container-lowest outline-none focus:border-primary transition-all" 
                    />
                  </div>
                  <p className="text-[10px] text-on-surface-variant italic">Matches if this text appears in the CSV &quot;Client&quot; column.</p>
                </div>
              </div>

              {/* Part 2: Journal Settings */}
              <div className="grid grid-cols-2 gap-6">
                <div className="bg-surface rounded-2xl border border-outline-variant shadow-sm p-6 space-y-4">
                  <div className="flex items-center gap-2 text-secondary font-bold text-sm">
                    <Landmark size={18} /> Main Account
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-[10px] font-bold text-on-surface-variant">CLIENT LEDGER</label>
                    <input 
                      type="text" 
                      value={selectedProfile.compte_client}
                      onChange={(e) => updateProfile(selectedProfile.id, { compte_client: e.target.value })}
                      className="w-full bg-surface-container-low border border-outline-variant rounded-xl px-4 py-2.5 text-sm font-mono" 
                    />
                  </div>
                </div>

                <div className="bg-surface rounded-2xl border border-outline-variant shadow-sm p-6 space-y-4">
                  <div className="flex items-center gap-2 text-secondary font-bold text-sm">
                    <Sparkles size={18} /> Automated Flags
                  </div>
                  <div className="space-y-3">
                    <label className="flex items-center justify-between cursor-pointer group">
                      <span className="text-xs font-medium group-hover:text-primary transition-colors">Apply Timbre Fiscal</span>
                      <input 
                        type="checkbox" 
                        checked={selectedProfile.use_timbre}
                        onChange={(e) => updateProfile(selectedProfile.id, { use_timbre: e.target.checked })}
                        className="w-5 h-5 accent-primary" 
                      />
                    </label>
                    <label className="flex items-center justify-between cursor-pointer group">
                      <span className="text-xs font-medium group-hover:text-primary transition-colors">Reroute to Caisse (Cash)</span>
                      <input 
                        type="checkbox" 
                        checked={selectedProfile.use_cash}
                        onChange={(e) => updateProfile(selectedProfile.id, { use_cash: e.target.checked })}
                        className="w-5 h-5 accent-primary" 
                      />
                    </label>
                  </div>
                </div>
              </div>

              {/* Part 3: Step Visualizer (Mimics entry_sequence) */}
              <div className="bg-surface rounded-2xl border border-outline-variant shadow-sm p-6 space-y-4">
                <h3 className="text-sm font-bold flex items-center gap-2">
                  <ListChecks size={18} className="text-primary" /> Generated Entry Sequence
                </h3>
                <div className="space-y-2">
                  {ENTRY_STEPS.map((step, idx) => {
                    // Logic check to gray out steps that aren't active
                    const isActive = step.id === 'cash_reroute' ? selectedProfile.use_cash : 
                                   step.id === 'timbre' ? selectedProfile.use_timbre : true;
                    
                    return (
                      <div key={step.id} className={`flex items-center gap-4 p-3 rounded-xl border ${isActive ? 'bg-surface border-outline-variant' : 'bg-surface-container-low opacity-40 grayscale'}`}>
                        <div className="w-6 h-6 rounded-full bg-surface-container-highest flex items-center justify-center text-[10px] font-bold">
                          {idx + 1}
                        </div>
                        <div className="flex-1">
                          <p className="text-xs font-bold">{step.label}</p>
                          <p className="text-[10px] text-on-surface-variant">{step.description}</p>
                        </div>
                        {isActive && <div className="text-[10px] font-mono font-bold text-primary">AUTO</div>}
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-on-surface-variant opacity-40">
              <Router size={64} strokeWidth={1} />
              <p className="mt-4 font-medium">Select a profile to edit rules</p>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
