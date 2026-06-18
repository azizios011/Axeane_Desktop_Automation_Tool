"use client";

import React, { useState } from 'react';
import { Sidebar } from '../components/Sidebar';
import { ImportView } from '../components/views/ImportView';
import { ProcessView } from '../components/views/ProcessView';
import { ValidationView } from '../components/views/ValidationView';
import { CdpSettingsView } from '../components/views/CdpSettingsView';
import { RulesManagementView } from '../components/views/RulesManagementView';

export type ViewState = 'import' | 'process' | 'validation' | 'cdp' | 'rules';

export default function AxeaneApp() {
  const [currentView, setCurrentView] = useState<ViewState>('import');

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar currentView={currentView} onChangeView={setCurrentView} />
      
      <div className="flex-1 overflow-hidden">
        {currentView === 'import' && <ImportView />}
        {currentView === 'process' && <ProcessView />}
        {currentView === 'validation' && <ValidationView />}
        {currentView === 'cdp' && <CdpSettingsView />}
        {currentView === 'rules' && <RulesManagementView />}
      </div>
    </div>
  );
}