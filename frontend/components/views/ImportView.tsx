"use client";

import React from 'react';
import { CloudUpload, ChevronDown, Info, FileText, ZoomOut, ZoomIn, Maximize, ArrowRight } from 'lucide-react';

export function ImportView() {
  return (
    <main className="ml-[var(--spacing-sidebar-width)] flex-1 flex flex-col h-full bg-background overflow-hidden">
      <header className="h-16 border-b border-outline-variant flex items-center justify-between px-6 bg-surface shrink-0">
        <h2 className="text-xl font-bold">Document Import</h2>
        <div className="flex items-center gap-4 text-on-surface-variant">
          <Info size={18}/>
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden">
        {/* Left Settings */}
        <div className="w-[40%] flex flex-col border-r border-outline-variant bg-surface-container-low overflow-y-auto p-6 space-y-8">
          <div className="space-y-2">
            <label className="text-[10px] font-bold uppercase tracking-widest text-secondary">Document Type</label>
            <div className="relative">
              <select className="w-full appearance-none bg-surface border border-outline-variant rounded-md pl-3 pr-10 py-2.5 text-sm outline-none focus:border-primary">
                <option>Banque (BQ) - Bank Statements</option>
                <option>Vente (VT) - Sales Invoices</option>
                <option>Achat (AC) - Purchases</option>
              </select>
              <ChevronDown className="absolute right-3 top-3 text-on-surface-variant pointer-events-none" size={16} />
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-[10px] font-bold uppercase tracking-widest text-secondary">Upload PDF</label>
            <div className="border-2 border-dashed border-outline-variant rounded-xl bg-surface hover:bg-surface-container p-10 text-center cursor-pointer group transition-all">
              <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
                <CloudUpload className="text-primary" size={24} />
              </div>
              <p className="text-sm font-bold mb-1">Drag and drop your PDF</p>
              <p className="text-xs text-on-surface-variant mb-4">Maximum size: 20MB</p>
              <button className="bg-surface border border-outline-variant py-1.5 px-4 rounded-md text-xs font-bold hover:bg-surface-container-high transition-colors">Select File</button>
            </div>
          </div>

          <div className="pt-6 flex justify-end gap-3">
            <button className="px-6 py-2 rounded-lg bg-primary text-white text-xs font-bold flex items-center gap-2 shadow-sm hover:opacity-90">
              Process Document <ArrowRight size={16} />
            </button>
          </div>
        </div>

        {/* Right Preview */}
        <div className="flex-1 bg-surface-container-highest flex flex-col relative">
          <div className="h-10 border-b border-outline-variant bg-surface flex items-center justify-between px-4 shrink-0">
            <span className="text-[10px] font-bold uppercase text-on-surface-variant">Document Preview</span>
            <div className="flex gap-4">
              <ZoomOut size={16} className="text-on-surface-variant cursor-pointer"/>
              <ZoomIn size={16} className="text-on-surface-variant cursor-pointer"/>
              <Maximize size={16} className="text-on-surface-variant cursor-pointer"/>
            </div>
          </div>
          
          <div className="flex-1 flex flex-col items-center justify-center p-8 bg-[#f5f5f7]">
            <div className="w-48 h-64 bg-white shadow-xl border border-outline-variant rounded-lg flex items-center justify-center relative">
               <FileText className="text-outline-variant opacity-20" size={64} />
            </div>
            <h3 className="text-sm font-bold mt-6">No File Loaded</h3>
            <p className="text-xs text-on-surface-variant mt-1">Upload a PDF to view content</p>
          </div>
        </div>
      </div>
    </main>
  );
}
