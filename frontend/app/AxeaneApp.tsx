"use client";

import React, { useState } from 'react';
import { Sidebar } from '../components/Sidebar';
import { SettingsTab } from '../components/views/SettingsTab';
import { PWATab } from '../components/views/PWATab';
import { ImportTab } from '../components/views/ImportTab';
import { ReviewTab } from '../components/views/ReviewTab';
import { ExecutionTab } from '../components/views/ExecutionTab';
import { TabState } from '../types/navigation';

export default function AxeaneApp() {
  const [currentTab, setCurrentTab] = useState<TabState>('settings');

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar currentTab={currentTab} onChangeTab={setCurrentTab} />
      
      <div className="flex-1 overflow-hidden">
        {currentTab === 'settings' && <SettingsTab />}
        {currentTab === 'pwa' && <PWATab />}
        {currentTab === 'import' && <ImportTab />}
        {currentTab === 'review' && <ReviewTab />}
        {currentTab === 'execution' && <ExecutionTab />}
      </div>
    </div>
  );
}
