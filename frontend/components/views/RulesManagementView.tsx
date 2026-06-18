"use client";

import React from 'react';
import { Router, Key, ListChecks, Plus, Code, Trash2, Save, Play } from 'lucide-react';

export function RulesManagementView() {
  return (
    <main className="ml-[var(--spacing-sidebar-width)] flex-1 flex flex-col h-full bg-background overflow-hidden">
      <header className="h-16 border-b border-outline-variant flex items-center justify-between px-6 bg-surface shrink-0">
        <h2 className="text-xl font-bold">Validation Rules</h2>
        <div className="flex items-center gap-3">
          <button className="px-4 py-1.5 border border-outline-variant text-xs font-bold rounded-lg hover:bg-surface-container flex items-center gap-2 transition-colors">
            <Play size={16} /> Test Logic
          </button>
          <button className="px-4 py-1.5 bg-primary text-white text-xs font-bold rounded-lg hover:opacity-90 flex items-center gap-2 shadow-sm">
            <Save size={16} /> Save Changes
          </button>
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden">
        {/* Left: Rule List */}
        <div className="w-80 border-r border-outline-variant bg-surface flex flex-col shrink-0">
          <div className="p-4 border-b border-outline-variant flex items-center justify-between bg-surface-container-low">
            <span className="text-xs font-bold uppercase tracking-widest text-on-surface-variant">Active Rules</span>
            <Plus className="text-primary cursor-pointer hover:scale-110 transition-transform" size={18} />
          </div>
          
          <div className="p-3 overflow-y-auto flex-1 space-y-3">
            <div className="border-2 border-primary bg-primary/5 rounded-xl p-4 cursor-pointer">
              <div className="flex justify-between items-start mb-2">
                <div className="flex items-center gap-2">
                  <Router className="text-primary" size={16} />
                  <h3 className="text-xs font-bold">Telecom (Vente)</h3>
                </div>
              </div>
              <div className="space-y-1">
                <div className="flex items-center gap-1.5 text-[10px] font-mono text-on-surface-variant">
                  <Key size={12} /> ^OOREDOO|^TT
                </div>
                <div className="flex items-center gap-1.5 text-[10px] text-on-surface-variant">
                  <ListChecks size={12} /> 3 GL Rows
                </div>
              </div>
            </div>

            <div className="border border-outline-variant bg-surface rounded-xl p-4 cursor-pointer hover:border-primary/50 transition-colors">
              <h3 className="text-xs font-bold">Bank Fees (BQ)</h3>
              <p className="text-[10px] text-on-surface-variant mt-1 font-mono">MATCH: COM &amp; TVA</p>
            </div>
          </div>
        </div>

        {/* Right: Rule Editor */}
        <div className="flex-1 bg-surface-container-low overflow-y-auto p-8">
          <div className="max-w-2xl mx-auto space-y-6">
            <div className="bg-surface rounded-xl border border-outline-variant shadow-sm p-6 space-y-6">
              <div>
                <label className="block text-xs font-bold uppercase tracking-widest text-on-surface-variant mb-3">Identity Matching (Regex)</label>
                <div className="relative">
                  <Code className="absolute left-3 top-2.5 text-on-surface-variant" size={18} />
                  <input type="text" defaultValue="^OOREDOO|^TT|^ORANGE" className="w-full pl-10 pr-3 py-2 border border-outline-variant rounded-lg font-mono text-sm bg-surface-container-lowest outline-none focus:border-primary" />
                </div>
              </div>

              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold">Ledger Mapping Matrix</h3>
                  <button className="text-primary text-xs font-bold hover:underline flex items-center gap-1">
                    <Plus size={14} /> Add Row
                  </button>
                </div>
                
                <div className="border border-outline-variant rounded-lg overflow-hidden">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-surface-container-low border-b border-outline-variant">
                      <tr>
                        <th className="p-3 font-bold uppercase tracking-wider text-[10px]">GL Account</th>
                        <th className="p-3 font-bold uppercase tracking-wider text-[10px]">Side</th>
                        <th className="p-3 font-bold uppercase tracking-wider text-[10px]">Source</th>
                        <th className="p-3 w-10"></th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-outline-variant/50">
                      <tr>
                        <td className="p-3 font-mono">626100</td>
                        <td className="p-3"><span className="text-blue-600 font-bold">DEBIT</span></td>
                        <td className="p-3 text-on-surface-variant">row.ht_19</td>
                        <td className="p-3 text-right"><Trash2 className="text-on-surface-variant hover:text-error cursor-pointer" size={14} /></td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
