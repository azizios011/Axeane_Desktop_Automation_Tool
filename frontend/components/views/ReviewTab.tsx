"use client";

import React from 'react';
import { 
  Workflow, Cpu, Trash2, CheckCircle2, 
  Coins, Receipt, Info, Layers, BarChart3 
} from 'lucide-react';
import { useReviewModule } from '@/modules/useReviewModule';
import { CARD_THEMES } from '@/metadata/processSettings';
import { TabState } from '@/app/page';

interface ReviewTabProps {
  sessionId: string | null;
  onChangeTab: (tab: TabState) => void;
}

export function ReviewTab({ sessionId, onChangeTab }: ReviewTabProps) {
  const { 
    templateCards, isGenerating, summary, 
    handleGenerateTemplates, handleClear 
  } = useReviewModule(sessionId);

  const [searchTerm, setSearchTerm] = React.useState('');
  const [statusFilter, setStatusFilter] = React.useState<'all' | 'balanced' | 'unbalanced'>('all');

  if (!sessionId) {
    return (
      <main className="flex-1 flex flex-col h-full bg-background overflow-hidden">
        <header className="h-16 border-b border-outline-variant bg-surface px-6 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-3">
            <Workflow className="text-primary" size={20} />
            <h1 className="text-xl font-bold text-on-surface">Preview & Rules</h1>
          </div>
        </header>
        <div className="flex-1 flex flex-col items-center justify-center bg-surface-container-low p-8">
          <div className="max-w-md w-full bg-surface border border-outline-variant rounded-2xl p-8 text-center shadow-md space-y-6">
            <div className="w-16 h-16 bg-primary/10 border border-primary/20 rounded-full flex items-center justify-center mx-auto text-primary">
              <Workflow size={32} />
            </div>
            <div className="space-y-2">
              <h2 className="text-lg font-bold text-on-surface">No Active Session</h2>
              <p className="text-xs text-on-surface-variant leading-relaxed">
                You must import and parse a CSV file first before reviewing accounting entries.
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

  const filteredCards = templateCards.filter(card => {
    // Filter by search term (check ref, sample_client, or match_key)
    const matchesSearch = 
      (card.ref || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (card.sample_client || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (card.match_key || '').toLowerCase().includes(searchTerm.toLowerCase());
      
    // Filter by status
    if (statusFilter === 'balanced') {
      return matchesSearch && card.is_balanced;
    } else if (statusFilter === 'unbalanced') {
      return matchesSearch && !card.is_balanced;
    }
    return matchesSearch;
  });

  return (
    <main className="flex-1 flex flex-col h-full bg-background overflow-hidden">
      <header className="h-16 border-b border-outline-variant bg-surface px-6 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-3">
          <Workflow className="text-primary" size={20} />
          <h1 className="text-xl font-bold text-on-surface">Audit Accounting Journal Entries</h1>
        </div>
        <div className="flex items-center gap-3">
          <button 
            onClick={handleClear}
            className="px-4 py-2 text-xs font-bold text-on-surface-variant hover:text-error flex items-center gap-2 transition-colors cursor-pointer"
          >
            <Trash2 size={16} /> Clear Entries
          </button>
          <button 
            onClick={handleGenerateTemplates}
            disabled={isGenerating}
            className="bg-primary text-white text-xs font-bold px-6 py-2.5 rounded-xl hover:opacity-90 flex items-center gap-2 shadow-lg shadow-primary/20 transition-all disabled:opacity-50 cursor-pointer"
          >
            <Cpu size={16}/> {isGenerating ? 'Reloading...' : 'Reload Entries'}
          </button>
        </div>
      </header>

      {/* Search & Filter Toolbar */}
      <div className="h-14 border-b border-outline-variant bg-surface-container-low px-6 flex items-center justify-between shrink-0 gap-4">
        <div className="flex items-center gap-3 flex-1 max-w-md">
          <input 
            type="text"
            placeholder="Search reference, client, or match key..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-surface border border-outline-variant rounded-xl px-4 py-1.5 text-xs outline-none focus:border-primary"
          />
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <span className="text-[10px] font-black uppercase text-on-surface-variant mr-2">Filter Status:</span>
          {(['all', 'balanced', 'unbalanced'] as const).map((status) => (
            <button
              key={status}
              onClick={() => setStatusFilter(status)}
              className={`px-3 py-1 rounded-lg text-[10px] font-black uppercase border transition-all cursor-pointer ${
                statusFilter === status
                  ? 'bg-primary text-white border-primary shadow-sm shadow-primary/10'
                  : 'bg-surface border-outline-variant text-on-surface-variant hover:bg-surface-container-high'
              }`}
            >
              {status}
            </button>
          ))}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-8 bg-surface-container-low space-y-6">
        <div className="max-w-5xl mx-auto space-y-8">
          
          {/* Summary Banner (Python Summary Panel) */}
          {summary && (
            <div className="bg-surface border border-outline-variant rounded-2xl p-6 shadow-sm flex items-center justify-between">
              <div className="flex items-center gap-6">
                <div className="flex flex-col">
                  <span className="text-[10px] font-black text-on-surface-variant uppercase tracking-widest">Invoices Grouped</span>
                  <span className="text-xl font-black text-primary">{summary.total_profiles} References</span>
                </div>
                <div className="w-px h-10 bg-outline-variant" />
                <div className="flex flex-col">
                  <span className="text-[10px] font-black text-on-surface-variant uppercase tracking-widest">Raw Rows Parsed</span>
                  <span className="text-xl font-black text-on-surface">{summary.total_invoices} Rows</span>
                </div>
                <div className="w-px h-10 bg-outline-variant" />
                <div className="flex flex-col">
                  <span className="text-[10px] font-black text-on-surface-variant uppercase tracking-widest">Total Batch TTC</span>
                  <span className="text-xl font-black text-on-surface font-mono">{summary.total_ttc.toFixed(3)} TND</span>
                </div>
                <div className="w-px h-10 bg-outline-variant" />
                <div className="flex flex-col">
                  <span className="text-[10px] font-black text-on-surface-variant uppercase tracking-widest text-green-600">Balanced</span>
                  <span className="text-xl font-black text-green-600">{summary.balanced_cards}</span>
                </div>
                <div className="w-px h-10 bg-outline-variant" />
                <div className="flex flex-col">
                  <span className="text-[10px] font-black text-on-surface-variant uppercase tracking-widest text-error">Unbalanced</span>
                  <span className="text-xl font-black text-error">{summary.unbalanced_cards}</span>
                </div>
              </div>
              <CheckCircle2 className={summary.unbalanced_cards === 0 ? "text-green-500" : "text-error"} size={32} />
            </div>
          )}

          {/* Card Grid (Python cards_container) */}
          <div className="grid grid-cols-1 gap-6">
            {filteredCards.length > 0 ? (
              filteredCards.map((card, idx) => {
                const theme = CARD_THEMES[card.match_type as keyof typeof CARD_THEMES] || CARD_THEMES.default;
                const hasTimbre = card.formula_lines.some((l: any) => l.step && l.step.includes('timbre'));
                const hasCash = card.formula_lines.some((l: any) => l.step && l.step.includes('cash_reroute'));

                return (
                  <div key={idx} className={`rounded-2xl border-2 overflow-hidden shadow-md flex flex-col ${theme.body} ${theme.border}`}>
                    {/* Card Header */}
                    <div className={`${theme.header} p-5 flex justify-between items-center text-white`}>
                      <div className="flex items-center gap-4">
                        <div className={`w-3 h-3 rounded-full ${card.is_balanced ? 'bg-green-400' : 'bg-red-400'} animate-pulse`} />
                        <div>
                          <span className="text-[10px] font-black uppercase tracking-widest opacity-80 block mb-0.5">
                            Ref: {card.ref} | {card.match_type} match ({card.match_key})
                          </span>
                          <h3 className="text-lg font-black">{card.sample_client || card.match_key}</h3>
                        </div>
                      </div>
                      <div className={`${theme.badge} border border-white/20 px-4 py-2 rounded-xl text-xs font-black shadow-inner`}>
                        {card.row_count} {card.row_count === 1 ? 'ROW' : 'ROWS'}
                      </div>
                    </div>

                    <div className="p-6 space-y-6">
                      {/* Stats & Flags */}
                      <div className="flex items-center gap-8">
                        <div className="flex flex-col">
                          <span className="text-[10px] font-black text-on-surface-variant uppercase">Invoice TTC</span>
                          <span className="text-md font-mono font-black">{card.total_ttc.toFixed(3)} TND</span>
                        </div>
                        <div className="flex flex-col">
                          <span className="text-[10px] font-black text-on-surface-variant uppercase">VAT Rates</span>
                          <span className="text-md font-mono font-black">{card.tva_rates.join('% + ')}%</span>
                        </div>
                        <div className="flex gap-2 ml-auto">
                          {hasCash && (
                            <div className="flex items-center gap-1.5 bg-green-600 text-white px-3 py-1 rounded-lg text-[10px] font-black uppercase">
                              <Coins size={12} /> Cash
                            </div>
                          )}
                          {hasTimbre && (
                            <div className="flex items-center gap-1.5 bg-blue-600 text-white px-3 py-1 rounded-lg text-[10px] font-black uppercase">
                              <Receipt size={12} /> Timbre
                            </div>
                          )}
                          <div className={`flex items-center gap-1.5 px-3 py-1 rounded-lg text-[10px] font-black uppercase text-white ${
                            card.is_balanced ? 'bg-green-600' : 'bg-error'
                          }`}>
                            {card.is_balanced ? 'Balanced' : 'Out of Balance'}
                          </div>
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
                                <td className="p-3 text-right text-error font-bold font-mono">
                                  {line.debit > 0 ? line.debit.toFixed(3) : ''}
                                </td>
                                <td className="p-3 text-right text-green-700 font-bold font-mono">
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
              <div className="h-64 flex flex-col items-center justify-center border-2 border-dashed border-outline-variant rounded-3xl opacity-30 bg-surface">
                <Layers size={48} strokeWidth={1} />
                <p className="mt-4 font-black uppercase tracking-widest text-xs">No matching entries found</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}
