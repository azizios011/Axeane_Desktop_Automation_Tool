"use client";

import React from 'react';
import { 
  Play, Square, Terminal, Trash2, 
  CheckCircle2, AlertCircle, Loader2, Gauge 
} from 'lucide-react';
import { useExecutionModule } from '@/modules/useExecutionModule';
import { LOG_LEVEL_COLORS } from '@/metadata/executionSettings';
import { TabState } from '@/app/page';

interface ExecutionTabProps {
  sessionId: string | null;
  onChangeTab: (tab: TabState) => void;
}

export function ExecutionTab({ sessionId, onChangeTab }: ExecutionTabProps) {
  const { 
    isRunning, progress, logs, terminalRef, 
    startAutomation, stopAutomation, clearLogs 
  } = useExecutionModule(sessionId);

  const [execMode, setExecMode] = React.useState<'dry_run' | 'live'>('dry_run');
  const [browserMode, setBrowserMode] = React.useState<'headless' | 'visible'>('visible');

  if (!sessionId) {
    return (
      <main className="flex-1 flex flex-col h-full bg-background overflow-hidden">
        <header className="h-16 border-b border-outline-variant bg-surface px-6 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-3">
            <Play size={20} className="text-primary" />
            <h1 className="text-xl font-bold text-on-surface">Execution & Logs</h1>
          </div>
        </header>
        <div className="flex-1 flex flex-col items-center justify-center bg-surface-container-low p-8">
          <div className="max-w-md w-full bg-surface border border-outline-variant rounded-2xl p-8 text-center shadow-md space-y-6">
            <div className="w-16 h-16 bg-primary/10 border border-primary/20 rounded-full flex items-center justify-center mx-auto text-primary">
              <Play size={32} />
            </div>
            <div className="space-y-2">
              <h2 className="text-lg font-bold text-on-surface">No Active Session</h2>
              <p className="text-xs text-on-surface-variant leading-relaxed">
                You must import and parse a CSV file first before running automation.
              </p>
            </div>
            <button
              onClick={() => onChangeTab('import')}
              className="w-full py-3 bg-primary text-white rounded-xl font-bold text-xs hover:opacity-90 transition-all shadow-md shadow-primary/20 cursor-pointer"
            >
              Go to Import Data
            </button>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="flex-1 flex flex-col h-full bg-background overflow-hidden">
      {/* Header / Top Control Bar */}
      <header className="h-20 border-b border-outline-variant bg-surface px-6 flex items-center justify-between shrink-0 shadow-sm z-10">
        <div className="flex items-center gap-6">
          <div className="flex gap-2">
            <button 
              disabled={isRunning}
              onClick={() => startAutomation(execMode, browserMode)}
              className="bg-green-600 text-white text-xs font-black px-6 py-3 rounded-xl flex items-center gap-2 hover:bg-green-700 disabled:opacity-50 shadow-lg shadow-green-900/20 transition-all cursor-pointer"
            >
              <Play size={18} /> START AUTOMATION
            </button>
            <button 
              disabled={!isRunning}
              onClick={stopAutomation}
              className="bg-error text-white text-xs font-black px-6 py-3 rounded-xl flex items-center gap-2 hover:opacity-90 disabled:opacity-50 shadow-lg shadow-red-900/20 transition-all cursor-pointer"
            >
              <Square size={18} /> STOP
            </button>
          </div>

          <div className="h-10 w-px bg-outline-variant" />

          {/* Config Selectors */}
          <div className="flex items-center gap-4">
            <div className="flex flex-col">
              <label className="text-[9px] font-black text-on-surface-variant uppercase tracking-wider mb-1">Execution Mode</label>
              <select
                disabled={isRunning}
                value={execMode}
                onChange={(e) => setExecMode(e.target.value as any)}
                className="bg-surface-container border border-outline-variant rounded-lg px-3 py-1.5 text-xs font-bold outline-none focus:border-primary cursor-pointer disabled:opacity-50"
              >
                <option value="dry_run">Dry Run (Simulate)</option>
                <option value="live">Live (Fill Forms)</option>
              </select>
            </div>
            
            <div className="flex flex-col">
              <label className="text-[9px] font-black text-on-surface-variant uppercase tracking-wider mb-1">Browser Visibility</label>
              <select
                disabled={isRunning}
                value={browserMode}
                onChange={(e) => setBrowserMode(e.target.value as any)}
                className="bg-surface-container border border-outline-variant rounded-lg px-3 py-1.5 text-xs font-bold outline-none focus:border-primary cursor-pointer disabled:opacity-50"
              >
                <option value="headless">Headless (Background)</option>
                <option value="visible">Visible (Open Browser)</option>
              </select>
            </div>
          </div>

          <div className="h-10 w-px bg-outline-variant" />

          {/* Statistics Display */}
          <div className="flex items-center gap-8">
            <div className="flex flex-col">
              <span className="text-[10px] font-black text-on-surface-variant uppercase tracking-widest">Progress</span>
              <span className="text-md font-black font-mono text-primary">{progress.current} / {progress.total}</span>
            </div>
            <div className="flex flex-col">
              <span className="text-[10px] font-black text-on-surface-variant uppercase tracking-widest text-green-600">Success</span>
              <span className="text-md font-black font-mono text-green-600">{progress.success}</span>
            </div>
            <div className="flex flex-col">
              <span className="text-[10px] font-black text-on-surface-variant uppercase tracking-widest text-error">Failed</span>
              <span className="text-md font-black font-mono text-error">{progress.failed}</span>
            </div>
          </div>
        </div>

        {/* Big Percentage Display */}
        <div className="flex flex-col items-end">
          <span className="text-[10px] font-black text-on-surface-variant uppercase">Automation Load</span>
          <span className="text-2xl font-black text-primary font-mono">{progress.percent}%</span>
        </div>
      </header>

      <div className="flex-1 flex flex-col p-6 gap-6 bg-surface-container-low overflow-hidden">
        
        {/* Modern Progress Bar (Determinate) */}
        <div className="bg-surface border border-outline-variant rounded-2xl p-2 shadow-sm shrink-0">
          <div className="w-full h-4 bg-surface-container-highest rounded-xl overflow-hidden relative border border-outline-variant/30">
            <div 
              className="h-full bg-primary transition-all duration-500 ease-out flex items-center justify-center relative overflow-hidden" 
              style={{ width: `${progress.percent}%` }}
            >
              <div className="absolute inset-0 bg-gradient-to-r from-white/20 to-transparent animate-pulse" />
            </div>
          </div>
        </div>

        {/* Live Terminal (Python ScrolledText Equivalent) */}
        <div className="flex-1 bg-[#1e1e1e] rounded-2xl border-4 border-surface shadow-2xl flex flex-col overflow-hidden">
          <div className="bg-[#2d2d2d] px-5 py-3 border-b border-[#404040] flex justify-between items-center shrink-0">
            <div className="flex items-center gap-3">
              <Terminal size={18} className="text-primary" />
              <span className="text-xs font-black text-[#d4d4d4] uppercase tracking-widest">Execution Logs & Network Debug</span>
            </div>
            <button 
              onClick={clearLogs}
              className="p-1.5 hover:bg-white/10 rounded-lg text-[#888] hover:text-white transition-all"
            >
              <Trash2 size={16} />
            </button>
          </div>

          <div 
            ref={terminalRef}
            className="flex-1 p-5 overflow-y-auto font-mono text-xs leading-relaxed selection:bg-primary/30"
          >
            {logs.length === 0 ? (
              <div className="text-[#666] flex flex-col items-center justify-center h-full gap-4 opacity-50">
                <Gauge size={48} strokeWidth={1} />
                <p className="font-bold uppercase tracking-[0.2em]">Ready for initialization</p>
              </div>
            ) : (
              <div className="space-y-1">
                {logs.map((log) => (
                  <div key={log.id} className="flex gap-4 group">
                    <span className="text-[#666] shrink-0 font-bold w-16">[{log.timestamp}]</span>
                    <span className={`font-bold shrink-0 w-20 ${LOG_LEVEL_COLORS[log.level]}`}>
                      [{log.level}]
                    </span>
                    <span className="text-[#d4d4d4]">{log.message}</span>
                  </div>
                ))}
                {isRunning && (
                  <div className="flex items-center gap-2 text-primary mt-2">
                    <Loader2 size={12} className="animate-spin" />
                    <span className="animate-pulse">_</span>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Summary Footer */}
        <div className="bg-surface border border-outline-variant rounded-xl p-4 flex items-center justify-between text-[11px] font-bold text-on-surface-variant uppercase tracking-widest shadow-sm">
          <div className="flex gap-6">
            <span className="flex items-center gap-2"><CheckCircle2 size={14} className="text-green-600"/> Thread Safe Engine</span>
            <span className="flex items-center gap-2"><AlertCircle size={14} className="text-blue-600"/> Playwright Async Context</span>
          </div>
          <span>Active Session: {isRunning ? 'Processing...' : 'Idle'}</span>
        </div>
      </div>
    </main>
  );
}
