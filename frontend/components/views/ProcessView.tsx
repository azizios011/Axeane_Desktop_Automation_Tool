"use client";

import React from 'react';
import { Play, Square, Bell, RefreshCw, Filter, Download, Terminal, Trash } from 'lucide-react';

export function ProcessView() {
  return (
    <main className="ml-[var(--spacing-sidebar-width)] flex-1 flex flex-col h-full bg-background">
      <header className="bg-surface flex justify-between items-center px-6 h-16 border-b border-outline-variant sticky top-0 z-30 shrink-0">
        <div className="flex items-center gap-4">
          <h2 className="text-lg font-black text-primary">Process Workflows</h2>
          <span className="px-2 py-1 bg-surface-container rounded text-on-surface-variant font-mono text-[11px]">Batch ID: B-7829</span>
        </div>
        
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <button className="bg-green-600 text-white text-xs font-bold px-4 py-1.5 rounded flex items-center gap-1 hover:bg-green-700 transition-colors shadow-sm">
              <Play size={14} /> Start Automation
            </button>
            <button className="bg-error text-white text-xs font-bold px-4 py-1.5 rounded flex items-center gap-1 hover:opacity-90 transition-colors shadow-sm">
              <Square size={14} /> Stop
            </button>
          </div>
          <div className="w-px h-6 bg-outline-variant" />
          <Bell className="text-on-surface-variant cursor-pointer" size={20} />
          <div className="w-8 h-8 rounded-full bg-secondary-container border border-outline-variant shrink-0" />
        </div>
      </header>

      <div className="flex-1 overflow-hidden flex flex-col p-6 gap-6">
        {/* Progress Card */}
        <div className="bg-surface border border-outline-variant rounded-lg p-4 flex flex-col gap-2 shadow-sm shrink-0">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-2 text-primary text-sm font-bold">
              <RefreshCw className="animate-spin" size={16} />
              AI Extraction: OpenRouter Active
            </div>
            <span className="font-mono text-xs text-on-surface-variant">65% Complete</span>
          </div>
          <div className="w-full h-2 bg-surface-container-high rounded-full overflow-hidden">
            <div className="h-full bg-primary transition-all duration-500" style={{ width: '65%' }}></div>
          </div>
          <p className="text-[11px] text-on-surface-variant italic">Processing row 14 of 21... Detecting TVA codes</p>
        </div>

        {/* Data Table */}
        <div className="flex-1 bg-surface border border-outline-variant rounded-lg overflow-hidden flex flex-col shadow-sm min-h-0">
          <div className="flex justify-between items-center p-4 border-b border-outline-variant bg-surface-container-low">
            <h3 className="text-sm font-bold">Extracted Accounting Data</h3>
            <div className="flex gap-2">
              <button className="px-3 py-1 border border-outline-variant rounded text-xs hover:bg-surface-container flex items-center gap-1"><Filter size={14} /> Filter</button>
              <button className="px-3 py-1 border border-outline-variant rounded text-xs hover:bg-surface-container flex items-center gap-1"><Download size={14} /> Export</button>
            </div>
          </div>
          
          <div className="flex-1 overflow-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead className="sticky top-0 bg-surface-container-low border-b border-outline-variant z-10">
                <tr>
                  <th className="p-3 uppercase tracking-wider text-on-surface-variant font-bold">Ref</th>
                  <th className="p-3 uppercase tracking-wider text-on-surface-variant font-bold">Entity</th>
                  <th className="p-3 uppercase tracking-wider text-on-surface-variant font-bold">Date</th>
                  <th className="p-3 uppercase tracking-wider text-on-surface-variant font-bold text-right">Amount (TND)</th>
                  <th className="p-3 uppercase tracking-wider text-on-surface-variant font-bold text-center">Confidence</th>
                  <th className="p-3 uppercase tracking-wider text-on-surface-variant font-bold">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-outline-variant/50">
                <tr className="hover:bg-primary/5 transition-colors">
                  <td className="p-3 font-mono text-primary">INV-8821</td>
                  <td className="p-3 font-bold">SMG ARIANA</td>
                  <td className="p-3 font-mono">2023-11-01</td>
                  <td className="p-3 font-mono text-right">4,500.000</td>
                  <td className="p-3">
                    <div className="flex items-center gap-2 justify-center">
                      <div className="w-12 h-1 bg-surface-container rounded-full"><div className="h-full bg-green-500 rounded-full" style={{ width: '98%' }}></div></div>
                      <span className="font-mono text-[10px]">98%</span>
                    </div>
                  </td>
                  <td className="p-3"><span className="px-2 py-0.5 bg-green-100 text-green-700 rounded text-[9px] font-bold uppercase tracking-wide">Processed</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* Console */}
        <div className="h-40 bg-[#1e1e1e] rounded-lg border border-outline-variant overflow-hidden flex flex-col shrink-0 shadow-lg">
          <div className="bg-[#2d2d2d] px-4 py-1.5 border-b border-[#404040] flex justify-between items-center text-[#cccccc] text-[11px] font-bold">
            <div className="flex items-center gap-2"><Terminal size={14} /> Automation Logs</div>
            <Trash className="hover:text-white cursor-pointer" size={14} />
          </div>
          <div className="p-3 overflow-y-auto font-mono text-[#d4d4d4] flex flex-col gap-1 text-[11px] leading-relaxed">
            <div className="text-green-400">[14:32:01] INFO: Initializing extraction pipeline...</div>
            <div className="text-blue-300">[14:32:02] API: Connected to OpenRouter (Claude-3.5).</div>
            <div>[14:32:05] Row 01: Matched &quot;SMG ARIANA&quot; to Account 108000.</div>
            <div className="animate-pulse">_</div>
          </div>
        </div>
      </div>
    </main>
  );
}
