// components/views/ProcessView.tsx
"use client";

import React from 'react';
import { Play, Square, RefreshCw, Terminal, Cpu, CheckCircle2, AlertTriangle, Boxes } from 'lucide-react';
import { useProcessModule } from '@/modules/useProcessModule';
import { CARD_THEMES, LOG_COLORS } from '@/metadata/processSettings';

export function ProcessView() {
  const { 
    cards, handleGenerateTemplates, 
    isExecuting, handleStartAutomation, handleStop,
    logs, progress, scrollRef 
  } = useProcessModule();

  return (
    <main className="ml-[var(--spacing-sidebar-width)] flex-1 flex flex-col h-full bg-background overflow-hidden">
      <header className="bg-surface flex justify-between items-center px-6 h-16 border-b border-outline-variant shrink-0">
        <div className="flex items-center gap-4">
          <h2 className="text-xl font-bold">2. Rule Engine & Execution</h2>
          {cards.length > 0 && (
            <div className="flex items-center gap-2 px-3 py-1 bg-primary/10 rounded-full">
              <Boxes size={14} className="text-primary" />
              <span className="text-[10px] font-black text-primary uppercase">{cards.length} Profiles Generated</span>
            </div>
          )}
        </div>
        
        <div className="flex items-center gap-3">
          {cards.length === 0 ? (
            <button onClick={handleGenerateTemplates} className="bg-primary text-white text-xs font-bold px-6 py-2 rounded-lg hover:opacity-90 transition-all shadow-md flex items-center gap-2">
              <Cpu size={16} /> Generate Formula Cards
            </button>
          ) : (
            <div className="flex gap-2">
              <button 
                disabled={isExecuting}
                onClick={handleStartAutomation}
                className="bg-green-600 text-white text-xs font-bold px-6 py-2 rounded-lg flex items-center gap-2 hover:bg-green-700 disabled:opacity-50 shadow-md"
              >
                <Play size={16} /> Start Automation
              </button>
              <button 
                disabled={!isExecuting}
                onClick={handleStop}
                className="bg-error text-white text-xs font-bold px-6 py-2 rounded-lg flex items-center gap-2 hover:opacity-90 disabled:opacity-50 shadow-md"
              >
                <Square size={16} /> Stop
              </button>
            </div>
          )}
        </div>
      </header>

      <div className="flex-1 overflow-hidden flex flex-col p-6 gap-6 bg-surface-container-low">
        
        {/* Progress & Stats (Only visible when executing) */}
        {isExecuting && (
          <div className="bg-surface border border-outline-variant rounded-2xl p-5 flex flex-col gap-3 shadow-sm shrink-0 animate-in fade-in slide-in-from-top-2">
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-3">
                <RefreshCw className="animate-spin text-primary" size={20} />
                <span className="text-sm font-bold text-on-surface">Processing Invoices: {progress.current} / {progress.total}</span>
              </div>
              <span className="font-mono text-xs font-black text-primary">{progress.percent}%</span>
            </div>
            <div className="w-full h-3 bg-surface-container-highest rounded-full overflow-hidden border border-outline-variant/20">
              <div className="h-full bg-primary transition-all duration-500 ease-out" style={{ width: `${progress.percent}%` }}></div>
            </div>
          </div>
        )}

        {/* Formula Cards Grid (The Python review_and_rules equivalent) */}
        <div className="flex-1 overflow-y-auto grid grid-cols-1 lg:grid-cols-2 gap-4 pb-4">
          {cards.map((card, idx) => {
            const theme = CARD_THEMES[card.match_type as keyof typeof CARD_THEMES] || CARD_THEMES.default;
            return (
              <div key={idx} className={`rounded-2xl border border-outline-variant/50 overflow-hidden shadow-sm flex flex-col ${theme.body}`}>
                <div className={`${theme.header} p-4 flex justify-between items-center text-white`}>
                  <div className="flex items-center gap-3">
                    <span className="text-[10px] font-black bg-white/20 px-2 py-0.5 rounded uppercase tracking-widest">{card.match_type}</span>
                    <h3 className="font-bold text-md">{card.match_key}</h3>
                  </div>
                  <span className={`${theme.badge} px-3 py-1 rounded-lg text-xs font-bold border border-white/20`}>
                    {card.invoice_count} Invoices
                  </span>
                </div>
                
                <div className="p-4 space-y-4 flex-1">
                  <div className="flex items-center gap-6">
                    <div>
                      <p className="text-[9px] font-bold uppercase opacity-60">Total TTC</p>
                      <p className="text-sm font-black font-mono">{card.total_ttc.toFixed(3)} TND</p>
                    </div>
                    <div className="h-8 w-px bg-outline-variant/30" />
                    <div className="flex gap-2">
                      {card.use_cash && <span className="bg-green-200 text-green-800 text-[9px] font-bold px-2 py-0.5 rounded">CASH</span>}
                      {card.use_timbre && <span className="bg-blue-200 text-blue-800 text-[9px] font-bold px-2 py-0.5 rounded">TIMBRE</span>}
                    </div>
                  </div>

                  <div className="bg-white/50 rounded-xl border border-outline-variant/30 overflow-hidden">
                    <table className="w-full text-[10px] font-mono">
                      <thead className="bg-black/5 border-b border-outline-variant/20">
                        <tr>
                          <th className="p-2 text-left">Account</th>
                          <th className="p-2 text-left">Label</th>
                          <th className="p-2 text-right">Debit</th>
                          <th className="p-2 text-right">Credit</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-outline-variant/10">
                        {card.formula_lines.map((line: any, lIdx: number) => (
                          <tr key={lIdx}>
                            <td className="p-2 font-bold">{line.account}</td>
                            <td className="p-2 truncate max-w-[100px]">{line.label}</td>
                            <td className="p-2 text-right text-error">{line.debit > 0 ? line.debit.toFixed(3) : ''}</td>
                            <td className="p-2 text-right text-primary">{line.credit > 0 ? line.credit.toFixed(3) : ''}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Live Execution Terminal (The Python Execution_Tab equivalent) */}
        <div className="h-64 bg-[#121212] rounded-2xl border border-outline-variant shadow-2xl overflow-hidden flex flex-col shrink-0">
          <div className="bg-[#1e1e1e] px-5 py-2.5 border-b border-[#333] flex justify-between items-center">
            <div className="flex items-center gap-3 text-[#aaa] text-xs font-bold uppercase tracking-widest">
              <Terminal size={16} className="text-primary" /> 
              Execution Console
            </div>
          </div>
          <div 
            ref={scrollRef}
            className="p-4 overflow-y-auto font-mono text-[11px] leading-relaxed flex flex-col gap-1.5"
          >
            {logs.length === 0 ? (
              <div className="text-gray-600 italic">Waiting for process initiation...</div>
            ) : (
              logs.map((log, i) => (
                <div key={i} className="flex gap-3">
                  <span className="text-gray-500 shrink-0 select-none">[{i+1}]</span>
                  <span className={LOG_COLORS[log.level as keyof typeof LOG_COLORS] || LOG_COLORS.DEFAULT}>
                    {log.msg}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </main>
  );
}
