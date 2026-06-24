"use client";

import React, { useState } from 'react';
import { Sidebar } from '@/components/Sidebar';
import { SettingsTab } from '@/components/views/SettingsTab';
import { PWATab } from '@/components/views/PWATab';
import { ImportTab } from '@/components/views/ImportTab';
import { ReviewTab } from '@/components/views/ReviewTab';
import { ExecutionTab } from '@/components/views/ExecutionTab';

export type TabState = 'settings' | 'pwa' | 'import' | 'review' | 'execution';

export default function AxeaneApp() {
  const [currentTab, setCurrentTab] = useState<TabState>('settings');
  const [sessionId, setSessionId] = useState<string | null>(null);

  return (
    // "flex" ensures the sidebar and content sit side-by-side
    <div className="flex h-screen w-full overflow-hidden bg-background">
      
      <Sidebar currentTab={currentTab} onChangeTab={setCurrentTab} />
      
      {/* 
         This container holds the views. 
         "flex-1" makes it take up the rest of the width.
      */}
      <div className="flex-1 h-full overflow-hidden relative">
        {currentTab === 'settings' && <SettingsTab />}
        {currentTab === 'pwa' && <PWATab />}
        {currentTab === 'import' && (
          <ImportTab 
            sessionId={sessionId} 
            setSessionId={setSessionId} 
            onChangeTab={setCurrentTab} 
          />
        )}
        {currentTab === 'review' && (
          <ReviewTab 
            sessionId={sessionId} 
            onChangeTab={setCurrentTab} 
          />
        )}
        {currentTab === 'execution' && (
          <ExecutionTab 
            sessionId={sessionId} 
            onChangeTab={setCurrentTab} 
          />
        )}
      </div>
    </div>
  );
}
