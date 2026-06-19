// modules/useSettingsModule.ts
import { useState } from 'react';
import { DEFAULT_PATHS } from '../metadata/cdpDefaults';

export function useSettingsModule() {
  // 1. Axeane Auth & Context State
  const [config, setConfig] = useState({
    auth: {
      username: "RIHAB1",
      password: "",
      enterprise: "CPR",
      exercice: "2026"
    }
  });

  const [showPassword, setShowPassword] = useState(false);

  // 2. Client Profiles State (Logic/accounts.py)
  const [profiles, setProfiles] = useState([
    { id: '1', match: 'PASSAGER', compte_client: '411000', use_timbre: true, use_cash: true, compte_caisse: '541100', type: 'specific' },
    { id: '2', match: 'TUNISIE AUTOMOTIVE', compte_client: '411032', use_timbre: true, use_cash: false, type: 'specific' },
    { id: '3', match: 'DEFAULT', compte_client: '411000', use_timbre: true, use_cash: false, type: 'default' },
  ]);

  const [selectedProfileId, setSelectedProfileId] = useState('1');
  const selectedProfile = profiles.find(p => p.id === selectedProfileId);

  // 3. Handlers
  const updateField = (section: 'auth', field: string, value: string) => {
    setConfig(prev => ({
      ...prev,
      [section]: { ...prev[section], [field]: value }
    }));
  };

  const updateProfile = (id: string, updates: any) => {
    setProfiles(prev => prev.map(p => p.id === id ? { ...p, ...updates } : p));
  };

  const addProfile = () => {
    const newId = Math.random().toString(36).substr(2, 9);
    const newProfile = { 
      id: newId, match: 'NEW CLIENT', compte_client: '411000', 
      use_timbre: true, use_cash: false, type: 'specific' 
    };
    setProfiles([...profiles, newProfile]);
    setSelectedProfileId(newId);
  };

  const handleSave = async () => {
    console.log("Saving all settings to Python backend via API...", { config, profiles });
    // This will call AxeaneAPI in the future
  };

  return {
    config,
    updateField,
    showPassword,
    setShowPassword,
    profiles,
    selectedProfile,
    setSelectedProfileId,
    updateProfile,
    addProfile,
    handleSave
  };
}
