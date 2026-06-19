// modules/useRulesModule.ts
import { useState } from 'react';
import { AxeaneConfig } from '../types/axeane';

export function useRulesModule() {
  // Mimics Vente_Formats.json
  const [profiles, setProfiles] = useState([
    { id: '1', match: 'PASSAGER', compte_client: '411000', use_timbre: true, use_cash: true, compte_caisse: '541100', type: 'specific' },
    { id: '2', match: 'TUNISIE AUTOMOTIVE', compte_client: '411032', use_timbre: true, use_cash: false, type: 'specific' },
    { id: '3', match: 'DEFAULT', compte_client: '411000', use_timbre: true, use_cash: false, type: 'default' },
  ]);

  const [selectedProfileId, setSelectedProfileId] = useState('1');
  const [isTesting, setIsTesting] = useState(false);

  const selectedProfile = profiles.find(p => p.id === selectedProfileId);

  const updateProfile = (id: string, updates: any) => {
    setProfiles(prev => prev.map(p => p.id === id ? { ...p, ...updates } : p));
  };

  const addProfile = () => {
    const newId = Math.random().toString(36).substr(2, 9);
    setProfiles([...profiles, { 
      id: newId, match: 'NEW CLIENT', compte_client: '411000', 
      use_timbre: true, use_cash: false, type: 'specific' 
    }]);
    setSelectedProfileId(newId);
  };

  return {
    profiles,
    selectedProfile,
    setSelectedProfileId,
    updateProfile,
    addProfile,
    isTesting,
    setIsTesting
  };
}
