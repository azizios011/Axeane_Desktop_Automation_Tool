"use client";

import React from 'react';
import { 
  Workflow, Cpu, Trash2, CheckCircle2, 
  Coins, Receipt, Info, Layers, BarChart3 
} from 'lucide-react';
import { useReviewModule } from '@/modules/useReviewModule';
import { CARD_THEMES } from '@/metadata/processSettings';

export function ReviewTab() {
  const { 
    templateCards, isGenerating, summary, 
    handleGenerateTemplates, handleClear 
  } = useReviewModule();

  return (
    <main className="flex-1 flex flex-col h-full bg-background overflow-hidden">
      <header className="h-16 border-b border-outline-variant bg-surface px-6 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-3">
          <Workflow className="text-primary" size={20} />
          <h1 className="text-xl font-bold text-on-surface">Template Formulas by Client Profile</h1>
        </div>
        <div className="flex items-center gap-3">
          <button 
            onClick={handleClear}
            className="px-4 py-2 text-xs font-bold text-on-surface-variant hover:text-error flex items-center gap-2 transition-colors"
          >
            <Trash2 size={16} /> Clear Templates
          </button>
          <button 
            onClick={handleGenerateTemplates}
            disabled={isGenerating}
            className="bg-primary text-white text-xs font-bold px-6 py-2.5 rounded-xl hover:opacity-90 flex items-center gap-2 shadow-lg shadow-primary/20 transition-all disabled:opacity-50"
          >
            <Cpu size={16}/> {isGenerating ? 'Generating...' : 'Generate Template Cards'}
          </button>
        </div>
      </header>

      <div className="flex-1 overflow-y-auto p-8 bg-surface-container-low space-y-6">
        <div className="max-w-5xl mx-auto space-y-8">
          
          {/* Summary Banner (Python Summary Panel) */}
          {summary && (
            <div className="bg-surface border border-outline-variant rounded-2xl p-6 shadow-sm flex items-center justify-between">
              <div className="flex items-center gap-6">
                <div className="flex flex-col">
                  <span className="text-[10px] font-black text-on-surface-variant uppercase tracking-widest">Profiles Detected</span>
                  <span className="text-xl font-black text-primary">{summary.total_profiles} Profiles</span>
                </div>
                <div className="w-px h-10 bg-outline-variant" />
                <div className="flex flex-col">
                  <span className="text-[10px] font-black text-on-surface-variant uppercase tracking-widest">Invoices Covered</span>
                  <span className="text-xl font-black text-on-surface">{summary.total_invoices} Items</span>
                </div>
                <div className="w-px h-10 bg-outline-variant" />
                <div className="flex flex-col">
                  <span className="text-[10px] font-black text-on-surface-variant uppercase tracking-widest">Total Batch TTC</span>
                  <span className="text-xl font-black text-on-surface font-mono">{summary.total_ttc.toFixed(3)} TND</span>
                </div>
              </div>
              <CheckCircle2 className="text-green-500" size={32} />
            </div>
          )}

          {/* Card Grid (Python cards_container) */}
          <div className="grid grid-cols-1 gap-6">
            {templateCards.length > 0 ? (
              templateCards.map((card, idx) => {
                const theme = CARD_THEMES[card.match_type as keyof typeof CARD_THEMES] || CARD_THEMES.default;
                return (
                  <div key={idx} className={`rounded-2xl border-2 overflow-hidden shadow-md flex flex-col ${theme.body} ${theme.border}`}>
                    {/* Card Header */}
                    <div className={`${theme.header} p-5 flex justify-between items-center text-white`}>
                      <div className="flex items-center gap-4">
                        <div className="w-3 h-3 rounded-full bg-white animate-pulse" />
                        <div>
                          <span className="text-[10px] font-black uppercase tracking-widest opacity-80 block mb-0.5">{card.match_type} match</span>
                          <h3 className="text-lg font-black">{card.match_key}</h3>
                        </div>
                      </div>
                      <div className={`${theme.badge} border border-white/20 px-4 py-2 rounded-xl text-xs font-black shadow-inner`}>
                        {card.invoice_count} INVOICES
                      </div>
                    </div>

                    <div className="p-6 space-y-6">
                      {/* Stats & Flags */}
                      <div className="flex items-center gap-8">
                        <div className="flex flex-col">
                          <span className="text-[10px] font-black text-on-surface-variant uppercase">Aggregated TTC</span>
                          <span className="text-md font-mono font-black">{card.total_ttc.toFixed(3)} TND</span>
                        </div>
                        <div className="flex flex-col">
                          <span className="text-[10px] font-black text-on-surface-variant uppercase">VAT Rates</span>
                          <span className="text-md font-mono font-black">{card.tva_rates.join('% + ')}%</span>
                        </div>
                        <div className="flex gap-2 ml-auto">
                          {card.use_cash && (
                            <div className="flex items-center gap-1.5 bg-green-600 text-white px-3 py-1 rounded-lg text-[10px] font-black uppercase">
                              <Coins size={12} /> Cash
                            </div>
                          )}
                          {card.use_timbre && (
                            <div className="flex items-center gap-1.5 bg-blue-600 text-white px-3 py-1 rounded-lg text-[10px] font-black uppercase">
                              <Receipt size={12} /> Timbre
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Formula Table (Python Formula lines section) */}
                      <div className="bg-white border border-outline-variant rounded-xl overflow-hidden shadow-sm">
                        <table className="w-full text-left border-collapse text-[11px] font-mono">
                          <thead className="bg-surface-container-high text-on-surface-variant">
                            <tr>
                              <th className="p-3 border-b border-outline-variant font-black uppercase">Step</th>
                              <th className="p-3 border-b border-outline-variant font-black uppercase">Account</th>
                              <th className="p-3 border-b border-outline-variant font-black uppercase">Label</th>
                              <th className="p-3 border-b border-outline-variant font-black uppercase text-right">Debit</th>
                              <th className="p-3 border-b border-outline-variant font-black uppercase text-right">Credit</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-outline-variant/30 text-on-surface">
                            {card.formula_lines.map((line: any, lIdx: number) => (
                              <tr key={lIdx} className="hover:bg-primary/5">
                                <td className="p-3 text-primary font-bold">{line.step}</td>
                                <td className="p-3 font-black">{line.account}</td>
                                <td className="p-3">{line.label}</td>
                                <td className="p-3 text-right text-error font-bold">
                                  {line.debit > 0 ? line.debit.toFixed(3) : ''}
                                </td>
                                <td className="p-3 text-right text-green-700 font-bold">
                                  {line.credit > 0 ? line.credit.toFixed(3) : ''}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </div>
                );
              })
            ) : (
              <div className="h-64 flex flex-col items-center justify-center border-2 border-dashed border-outline-variant rounded-3xl opacity-30">
                <Layers size={48} strokeWidth={1} />
                <p className="mt-4 font-black uppercase tracking-widest text-xs">Waiting for formula generation</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}
