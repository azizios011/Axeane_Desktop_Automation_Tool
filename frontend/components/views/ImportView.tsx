// components/views/ImportView.tsx
"use client";

import React from 'react';
import { CloudUpload, ChevronDown, FileText, ArrowRight, Table as TableIcon, Loader2 } from 'lucide-react';
import { useImportModule } from '@/modules/useImportModule';
import { DOCUMENT_TYPES } from '@/metadata/importSettings';

export function ImportView() {
  const { 
    docType, setDocType, 
    filePath, handleBrowse, 
    isParsing, handleProcess,
    previewData 
  } = useImportModule();

  return (
    <main className="ml-[var(--spacing-sidebar-width)] flex-1 flex flex-col h-full bg-background overflow-hidden">
      <header className="h-16 border-b border-outline-variant flex items-center justify-between px-6 bg-surface shrink-0">
        <h2 className="text-xl font-bold">1. Data Ingestion</h2>
        <div className="flex items-center gap-2">
          <span className={`px-3 py-1 rounded-full text-[10px] font-bold uppercase ${isParsing ? 'bg-primary/10 text-primary animate-pulse' : 'bg-secondary-container text-on-secondary-container'}`}>
            {isParsing ? 'Engine Parsing...' : 'Ready'}
          </span>
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden">
        {/* Left Control Panel */}
        <div className="w-[380px] flex flex-col border-r border-outline-variant bg-surface overflow-y-auto p-6 space-y-8 shadow-sm">
          
          {/* Document Type Selection */}
          <div className="space-y-3">
            <label className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">Document Type</label>
            <div className="grid grid-cols-1 gap-2">
              {DOCUMENT_TYPES.map((type) => (
                <button
                  key={type.id}
                  onClick={() => setDocType(type.id as any)}
                  className={`flex items-center justify-between p-3 rounded-xl border transition-all ${
                    docType === type.id 
                      ? 'border-primary bg-primary/5 ring-1 ring-primary' 
                      : 'border-outline-variant hover:border-outline bg-surface'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg ${docType === type.id ? 'bg-primary text-white' : 'bg-surface-container-high text-on-surface-variant'}`}>
                      <FileText size={18} />
                    </div>
                    <span className="text-sm font-semibold">{type.label}</span>
                  </div>
                  {docType === type.id && <div className="w-2 h-2 rounded-full bg-primary" />}
                </button>
              ))}
            </div>
          </div>

          {/* File Picker */}
          <div className="space-y-3">
            <label className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">Source File (CSV/Excel)</label>
            <div 
              onClick={handleBrowse}
              className="border-2 border-dashed border-outline-variant rounded-2xl bg-surface-container-low hover:bg-surface-container hover:border-primary/50 p-8 text-center cursor-pointer group transition-all"
            >
              <div className="w-12 h-12 rounded-2xl bg-primary/10 flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform text-primary">
                <CloudUpload size={24} />
              </div>
              <p className="text-sm font-bold text-on-surface">
                {filePath ? filePath.split(/[\\/]/).pop() : 'Click to select CSV'}
              </p>
              <p className="text-[11px] text-on-surface-variant mt-1 italic">
                {filePath ? 'File linked successfully' : 'Browse system files'}
              </p>
            </div>
          </div>

          {/* Action Button */}
          <button 
            disabled={!filePath || isParsing}
            onClick={() => handleProcess(() => console.log("Navigate to ProcessView"))}
            className="w-full py-4 rounded-xl bg-primary text-white font-bold flex items-center justify-center gap-3 shadow-lg shadow-primary/20 hover:opacity-90 disabled:grayscale disabled:opacity-50 transition-all mt-auto"
          >
            {isParsing ? <Loader2 className="animate-spin" /> : <ArrowRight size={18} />}
            {isParsing ? 'Applying Accounting Rules...' : 'Parse & Generate Formulas'}
          </button>
        </div>

        {/* Right Preview Panel (The Treeview Equivalent) */}
        <div className="flex-1 bg-surface-container-low flex flex-col overflow-hidden">
          <div className="h-12 border-b border-outline-variant bg-surface flex items-center px-4 justify-between shrink-0">
            <div className="flex items-center gap-2 text-on-surface-variant">
              <TableIcon size={16} />
              <span className="text-[10px] font-bold uppercase tracking-wider">Raw Data Preview</span>
            </div>
            {previewData.length > 0 && (
              <span className="text-[10px] font-mono bg-secondary-container px-2 py-0.5 rounded text-on-secondary-container">
                {previewData.length} Rows Detected
              </span>
            )}
          </div>
          
          <div className="flex-1 overflow-auto bg-surface-container-lowest">
            {previewData.length > 0 ? (
              <table className="w-full text-left border-collapse min-w-max">
                <thead className="sticky top-0 bg-surface-container-high z-10">
                  <tr>
                    {Object.keys(previewData[0]).map((key) => (
                      <th key={key} className="p-3 text-[10px] font-black uppercase text-on-surface-variant border-b border-outline-variant">
                        {key}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-outline-variant/30">
                  {previewData.map((row, idx) => (
                    <tr key={idx} className="hover:bg-primary/5 transition-colors">
                      {Object.values(row).map((val: any, vIdx) => (
                        <td key={vIdx} className="p-3 text-xs font-medium text-on-surface border-r border-outline-variant/10">
                          {typeof val === 'number' ? val.toFixed(3) : String(val)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="h-full flex flex-col items-center justify-center text-on-surface-variant opacity-40">
                <TableIcon size={48} strokeWidth={1} />
                <p className="text-sm font-medium mt-4">Waiting for data parsing...</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}
