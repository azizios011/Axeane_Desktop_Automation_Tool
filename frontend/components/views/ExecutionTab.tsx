"use client";

import React from 'react';
import { 
  Play, Square, Terminal, Trash2, 
  CheckCircle2, AlertCircle, Loader2, Gauge 
} from 'lucide-react';
import { useExecutionModule } from '@/modules/useExecutionModule';
import { LOG_LEVEL_COLORS } from '@/metadata/executionSettings';

export function ExecutionTab() {
  const { 
    isRunning, progress, logs, terminalRef, 
    startAutomation, stopAutomation, clearLogs 
  } = useExecutionModule();

  return (
    <main className="flex-1 flex flex-col h-full bg-background overflow-hidden">
      {/* Header / Top Control Bar */}
      <header className="h-20 border-b border-outline-variant bg-surface px-6 flex items-center justify-between shrink-0 shadow-sm z-10">
        <div className="flex items-center gap-6">
          <div className="flex gap-2">
            <button 
              disabled={isRunning}
              onClick={startAutomation}
              className="bg-green-600 text-white text-xs font-black px-6 py-3 rounded-xl flex items-center gap-2 hover:bg-green-700 disabled:opacity-50 shadow-lg shadow-green-900/20 transition-all"
            >
              <Play size={18} /> START AUTOMATION
            </button>
            <button 
              disabled={!isRunning}
              onClick={stopAutomation}
              className="bg-error text-white text-xs font-black px-6 py-3 rounded-xl flex items-center gap-2 hover:opacity-90 disabled:opacity-50 shadow-lg shadow-red-900/20 transition-all"
            >
              <Square size={18} /> STOP
            </button>
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
