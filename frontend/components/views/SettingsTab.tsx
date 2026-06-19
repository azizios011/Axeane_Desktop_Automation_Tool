"use client";

import React from 'react';
import { 
  UserRoundCog, EyeOff, Eye, ChevronRight, Plus, 
  Hash, Landmark, Receipt, Coins, Save, Settings, Key
} from 'lucide-react';
import { useSettingsModule } from '@/modules/useSettingsModule';
import { ENTERPRISE_OPTIONS, EXERCICE_OPTIONS } from '@/metadata/cdpDefaults';

export function SettingsTab() {
  const { 
    config, updateField, showPassword, setShowPassword,
    profiles, selectedProfile, setSelectedProfileId, updateProfile, addProfile,
    handleSave 
  } = useSettingsModule();

  return (
    <main className="flex-1 flex flex-col h-full bg-background overflow-hidden">
      <header className="h-16 border-b border-outline-variant bg-surface px-6 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-3">
          <Settings className="text-primary" size={20} />
          <h1 className="text-xl font-bold text-on-surface">Settings & Profiles</h1>
        </div>
        <button 
          onClick={handleSave}
          className="bg-primary text-white text-xs font-bold px-6 py-2.5 rounded-xl hover:opacity-90 flex items-center gap-2 shadow-lg shadow-primary/20 transition-all"
        >
          <Save size={16}/> Save Configuration
        </button>
      </header>

      <div className="flex-1 flex overflow-hidden">
        <div className="w-80 border-r border-outline-variant bg-surface flex flex-col shrink-0 shadow-sm">
          <div className="p-4 border-b border-outline-variant flex items-center justify-between bg-surface-container-low">
            <span className="text-[10px] font-black uppercase tracking-widest text-on-surface-variant">Client Profiles</span>
            <button onClick={addProfile} className="p-1 hover:bg-primary/10 rounded-full text-primary transition-colors">
              <Plus size={20} />
            </button>
          </div>
          
          <div className="p-3 overflow-y-auto flex-1 space-y-2">
            {profiles.map((profile: any) => (
              <div 
                key={profile.id}
                onClick={() => setSelectedProfileId(profile.id)}
                className={`group p-4 rounded-2xl cursor-pointer transition-all border-2 ${
                  selectedProfile?.id === profile.id 
                    ? 'border-primary bg-primary/5 shadow-sm' 
                    : 'border-transparent hover:border-outline-variant bg-surface'
                }`}
              >
                <div className="flex justify-between items-start mb-1">
                  <h3 className="text-xs font-bold truncate max-w-[140px]">{profile.match}</h3>
                  <ChevronRight size={14} className={selectedProfile?.id === profile.id ? 'text-primary' : 'text-on-surface-variant'} />
                </div>
                <div className="flex items-center gap-2 text-[10px] font-mono text-on-surface-variant">
                  <Hash size={10} /> {profile.compte_client}
                  <div className="flex gap-1 ml-auto">
                    {profile.use_cash && <Coins size={12} className="text-green-600" />}
                    {profile.use_timbre && <Receipt size={12} className="text-blue-600" />}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-8 bg-surface-container-low space-y-8">
          <section className="max-w-3xl mx-auto space-y-6">
            <div className="bg-surface rounded-2xl border border-outline-variant p-6 shadow-sm">
              <h3 className="text-sm font-black uppercase tracking-widest text-primary mb-6 flex items-center gap-2">
                <UserRoundCog size={18} /> Axeane Authentication
              </h3>
              
              <div className="grid grid-cols-2 gap-6">
                <div className="space-y-1.5">
                  <label className="text-[10px] font-bold text-on-surface-variant uppercase">Username</label>
                  <input 
                    type="text" 
                    value={config.auth.username}
                    onChange={(e) => updateField('auth', 'username', e.target.value)}
                    className="w-full bg-surface-container-low border border-outline-variant rounded-xl px-4 py-2 text-sm outline-none focus:border-primary" 
                  />
                </div>
                
                <div className="space-y-1.5">
                  <label className="text-[10px] font-bold text-on-surface-variant uppercase">Password</label>
                  <div className="relative">
                    <input 
                      type={showPassword ? "text" : "password"} 
                      value={config.auth.password}
                      onChange={(e) => updateField('auth', 'password', e.target.value)}
                      className="w-full bg-surface-container-low border border-outline-variant rounded-xl px-4 py-2 text-sm outline-none focus:border-primary" 
                    />
                    <button 
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-2 text-on-surface-variant hover:text-primary"
                    >
                      {showPassword ? <Eye size={16} /> : <EyeOff size={16} />}
                    </button>
                  </div>
                </div>

                <div className="space-y-1.5">
                  <label className="text-[10px] font-bold text-on-surface-variant uppercase">Enterprise</label>
                  <select 
                    value={config.auth.enterprise}
                    onChange={(e) => updateField('auth', 'enterprise', e.target.value)}
                    className="w-full bg-surface-container-low border border-outline-variant rounded-xl px-3 py-2 text-sm outline-none appearance-none"
                  >
                    {ENTERPRISE_OPTIONS.map(opt => <option key={opt}>{opt}</option>)}
                  </select>
                </div>

                <div className="space-y-1.5">
                  <label className="text-[10px] font-bold text-on-surface-variant uppercase">Exercice</label>
                  <select 
                    value={config.auth.exercice}
                    onChange={(e) => updateField('auth', 'exercice', e.target.value)}
                    className="w-full bg-surface-container-low border border-outline-variant rounded-xl px-3 py-2 text-sm outline-none appearance-none"
                  >
                    {EXERCICE_OPTIONS.map(opt => <option key={opt}>{opt}</option>)}
                  </select>
                </div>
              </div>
            </div>

            {selectedProfile && (
              <div className="bg-surface rounded-2xl border border-outline-variant p-6 shadow-sm space-y-6">
                <h3 className="text-sm font-black uppercase tracking-widest text-secondary flex items-center gap-2">
                  <Key size={18} /> Profile Logic: {selectedProfile.match}
                </h3>

                <div className="grid grid-cols-2 gap-6">
                  <div className="space-y-1.5">
                    <label className="text-[10px] font-bold text-on-surface-variant uppercase">Match Substring</label>
                    <input 
                      type="text" 
                      value={selectedProfile.match}
                      onChange={(e) => updateProfile(selectedProfile.id, { match: e.target.value })}
                      className="w-full bg-surface-container-low border border-outline-variant rounded-xl px-4 py-2 text-sm font-mono" 
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-[10px] font-bold text-on-surface-variant uppercase">Ledger Account</label>
                    <input 
                      type="text" 
                      value={selectedProfile.compte_client}
                      onChange={(e) => updateProfile(selectedProfile.id, { compte_client: e.target.value })}
                      className="w-full bg-surface-container-low border border-outline-variant rounded-xl px-4 py-2 text-sm font-mono" 
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <label className="flex items-center justify-between p-3 rounded-xl border border-outline-variant bg-surface-container-low cursor-pointer hover:bg-surface-container">
                    <div className="flex items-center gap-2">
                      <Receipt size={16} className="text-primary" />
                      <span className="text-xs font-bold">Use Timbre Fiscal</span>
                    </div>
                    <input 
                      type="checkbox" 
                      checked={selectedProfile.use_timbre}
                      onChange={(e) => updateProfile(selectedProfile.id, { use_timbre: e.target.checked })}
                      className="w-5 h-5 accent-primary" 
                    />
                  </label>

                  <label className="flex items-center justify-between p-3 rounded-xl border border-outline-variant bg-surface-container-low cursor-pointer hover:bg-surface-container">
                    <div className="flex items-center gap-2">
                      <Coins size={16} className="text-green-600" />
                      <span className="text-xs font-bold">Reroute to Cash</span>
                    </div>
                    <input 
                      type="checkbox" 
                      checked={selectedProfile.use_cash}
                      onChange={(e) => updateProfile(selectedProfile.id, { use_cash: e.target.checked })}
                      className="w-5 h-5 accent-primary" 
                    />
                  </label>
                </div>
              </div>
            )}
          </section>
        </div>
      </div>
    </main>
  );
}
