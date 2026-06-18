"use client";

import React, { useState } from 'react';
import { 
  History, HelpCircle, Bell, Filter, MoreVertical, Lock, 
  ZoomOut, ZoomIn, FileText, CheckCircle2, XCircle, 
  AlertTriangle, ShieldCheck, Upload, FileUp 
} from 'lucide-react';

export function ValidationView() {
  const [isImportMenuOpen, setIsImportMenuOpen] = useState(false);

  return (
    <main className="ml-[var(--spacing-sidebar-width)] flex-1 flex flex-col h-full bg-background overflow-hidden">
      {/* View Header */}
      <header className="flex justify-between items-center px-6 h-16 bg-surface border-b border-outline-variant sticky top-0 z-30 shrink-0">
        <div className="flex items-center gap-4">
          <span className="text-xl font-black text-primary uppercase tracking-tighter">Axeane Flow</span>
          <div className="h-4 w-px bg-outline-variant mx-2" />
          <span className="text-on-surface-variant text-sm font-medium">Reconciliation Engine</span>
        </div>
        
        <div className="flex items-center gap-4">
          <button className="text-on-surface-variant hover:text-primary transition-colors">
            <History size={20} />
          </button>
          <div className="relative">
            <Bell className="text-on-surface-variant cursor-pointer" size={20} />
            <span className="absolute -top-1 -right-1 w-2 h-2 bg-error rounded-full border-2 border-surface"></span>
          </div>
          <div className="h-6 w-px bg-outline-variant mx-2" />
          <button className="bg-surface border border-outline-variant text-on-surface hover:bg-surface-container-low text-xs font-bold py-1.5 px-4 rounded transition-all shadow-sm">
            Sync Axeane GL
          </button>
        </div>
      </header>

      <div className="flex-1 flex flex-col p-6 gap-4 overflow-hidden">
        {/* Toolbar Controls */}
        <div className="bg-surface border border-outline-variant rounded-lg p-3 px-4 flex items-center justify-between shrink-0 shadow-sm">
          <div className="flex items-center gap-8">
            <div className="flex items-center gap-3">
              <label className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">Target Account</label>
              <div className="relative">
                <input 
                  type="text" 
                  value="707019" 
                  readOnly 
                  className="w-28 bg-surface-container-low border border-outline-variant text-on-surface font-mono text-sm py-1 px-3 rounded outline-none" 
                />
                <Lock className="absolute right-2 top-1.5 text-on-surface-variant" size={14} />
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              <label className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">Validation Type</label>
              <select className="bg-surface-container-low border border-outline-variant text-xs font-bold py-1 px-3 rounded appearance-none outline-none cursor-pointer pr-8">
                <option>GL vs. Automation Data</option>
                <option>GL vs. Bank Statement</option>
              </select>
            </div>
          </div>

          <div className="flex gap-2">
            <div className="relative">
              <button 
                onClick={() => setIsImportMenuOpen(!isImportMenuOpen)}
                className="flex items-center gap-1.5 bg-primary/10 text-primary hover:bg-primary/20 px-3 py-1.5 rounded transition-colors text-xs font-bold"
              >
                <Upload size={16} /> Import Files
              </button>
              
              {isImportMenuOpen && (
                <div className="absolute right-0 mt-2 w-48 bg-surface border border-outline-variant rounded-lg shadow-xl overflow-hidden z-50">
                  <button className="w-full text-left px-4 py-2.5 text-xs text-on-surface hover:bg-surface-container-low flex items-center gap-2 border-b border-outline-variant/30">
                    <FileUp size={14} className="text-on-surface-variant" /> Import Data PDF
                  </button>
                  <button className="w-full text-left px-4 py-2.5 text-xs text-on-surface hover:bg-surface-container-low flex items-center gap-2">
                    <FileUp size={14} className="text-on-surface-variant" /> Import GL PDF
                  </button>
                </div>
              )}
            </div>
            <button className="p-1.5 text-on-surface-variant hover:bg-surface-container rounded transition-colors">
              <MoreVertical size={18} />
            </button>
          </div>
        </div>

        {/* Main Comparison Area */}
        <div className="flex-1 flex gap-4 overflow-hidden h-full">
          
          {/* Left Side: Axeane GL (PDF Source) */}
          <div className="w-1/2 flex flex-col bg-surface border border-outline-variant rounded-lg overflow-hidden shadow-sm">
            <div className="flex items-center justify-between px-4 py-2 border-b border-outline-variant bg-surface-container-low shrink-0">
              <div className="flex items-center gap-2">
                <FileText className="text-on-surface-variant" size={16} />
                <span className="text-xs font-bold truncate max-w-[180px]">GL_Export_707019.pdf</span>
              </div>
              <div className="flex items-center gap-3">
                <ZoomOut className="text-on-surface-variant cursor-pointer hover:text-on-surface" size={16} />
                <span className="text-[10px] font-mono text-on-surface-variant">100%</span>
                <ZoomIn className="text-on-surface-variant cursor-pointer hover:text-on-surface" size={16} />
              </div>
            </div>
            
            <div className="flex-1 bg-surface-container-highest overflow-auto">
              <table className="w-full text-left border-collapse bg-surface text-[11px]">
                <thead className="sticky top-0 bg-surface-container-low border-b border-outline-variant z-10 shadow-sm">
                  <tr>
                    <th className="py-2 px-4 font-bold text-on-surface-variant uppercase">Date</th>
                    <th className="py-2 px-4 font-bold text-on-surface-variant uppercase">Description</th>
                    <th className="py-2 px-4 font-bold text-on-surface-variant uppercase text-right">Credit</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-outline-variant/30">
                  <tr className="hover:bg-primary/5 transition-colors">
                    <td className="p-3 font-mono">01/10/2023</td>
                    <td className="p-3">FAC-2023-001 (Client A)</td>
                    <td className="p-3 font-mono text-right">12,500.000</td>
                  </tr>
                  <tr className="hover:bg-primary/5 transition-colors">
                    <td className="p-3 font-mono">05/10/2023</td>
                    <td className="p-3">FAC-2023-002 (Client B)</td>
                    <td className="p-3 font-mono text-right text-error font-bold">1,200.000</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          {/* Right Side: Reconciled Data Table */}
          <div className="w-1/2 flex flex-col gap-4 overflow-hidden">
            <div className="flex-1 bg-surface border border-outline-variant rounded-lg overflow-hidden shadow-sm flex flex-col">
              <div className="overflow-y-auto flex-1">
                <table className="w-full text-left border-collapse text-[11px]">
                  <thead className="sticky top-0 bg-surface-container-low border-b border-outline-variant z-10 shadow-sm">
                    <tr>
                      <th className="py-2 px-4 font-bold text-on-surface-variant uppercase">Date</th>
                      <th className="py-2 px-4 font-bold text-on-surface-variant uppercase">Extracted Amount</th>
                      <th className="py-2 px-4 font-bold text-on-surface-variant uppercase text-center">Match</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-outline-variant/30 font-mono">
                    <tr className="hover:bg-surface-container-low transition-colors">
                      <td className="p-3">01/10/2023</td>
                      <td className="p-3 text-right">12,500.000</td>
                      <td className="p-3 text-center">
                        <div className="inline-flex items-center justify-center bg-green-100 border border-green-200 rounded-full px-2 py-0.5 gap-1">
                          <CheckCircle2 size={12} className="text-green-600" />
                          <span className="text-[9px] font-black text-green-700">MATCH</span>
                        </div>
                      </td>
                    </tr>
                    
                    <tr className="bg-error/5 hover:bg-error/10 transition-colors">
                      <td className="p-3">05/10/2023</td>
                      <td className="p-3 text-right text-error font-bold">1,195.000</td>
                      <td className="p-3 text-center">
                        <div className="inline-flex items-center justify-center bg-error-container border border-error/50 rounded-full px-2 py-0.5 gap-1">
                          <AlertTriangle size={12} className="text-error" />
                          <span className="text-[9px] font-black text-on-error-container uppercase">Diff</span>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            {/* Reconciliation Footer Summary */}
            <div className="bg-surface border border-outline-variant rounded-lg p-4 flex items-center justify-between shadow-sm shrink-0">
              <div>
                <span className="text-[10px] font-bold text-on-surface-variant uppercase tracking-widest block mb-1">Live Status</span>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-primary animate-pulse"></div>
                  <span className="text-xs font-bold">Automated Reconciler Running</span>
                </div>
              </div>
              
              <div className="flex items-center gap-6">
                <div className="flex flex-col items-end">
                  <span className="text-[10px] text-on-surface-variant uppercase font-bold">Items Matched</span>
                  <span className="text-sm font-mono font-black">124 / 125</span>
                </div>
                <div className="h-8 w-px bg-outline-variant"></div>
                <div className="bg-tertiary-fixed border border-outline-variant rounded-lg px-5 py-2 flex items-center gap-4">
                  <ShieldCheck size={20} className="text-on-tertiary-fixed" />
                  <div className="flex flex-col">
                    <span className="text-[9px] font-bold text-on-tertiary-fixed uppercase opacity-80">Total Variance</span>
                    <span className="font-mono text-md font-black text-on-tertiary-fixed">5.000 TND</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
