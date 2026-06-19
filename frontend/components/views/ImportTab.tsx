"use client";

import React from 'react';
import { 
  Upload, FileUp, Landmark, Settings, 
  Table as TableIcon, ArrowRight, Search, Loader2 
} from 'lucide-react';
import { useImportModule } from '@/modules/useImportModule';
import { DOCUMENT_TYPES } from '@/metadata/importSettings';

export function ImportTab() {
  const { 
    docType, setDocType, 
    filePath, handleBrowse, 
    isParsing, handleStartParsing,
    status, rawData, csvHeaders
  } = useImportModule();

  return (
    <main className="flex-1 flex flex-col h-full bg-background overflow-hidden">
      <header className="h-16 border-b border-outline-variant bg-surface px-6 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-3">
          <Upload className="text-primary" size={20} />
          <h1 className="text-xl font-bold text-on-surface">1. Import & Map Raw Data</h1>
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden">
        {/* Left Side: Controls (Python _build_ui top section) */}
        <div className="w-[400px] border-r border-outline-variant bg-surface flex flex-col shrink-0 p-6 space-y-8">
          
          {/* File Selection */}
          <div className="space-y-3">
            <label className="text-[10px] font-black uppercase tracking-widest text-on-surface-variant">Data Source</label>
            <div className="flex gap-2">
              <input 
                type="text" 
                readOnly
                value={filePath}
                placeholder="No file selected..."
                className="flex-1 bg-surface-container-low border border-outline-variant rounded-xl px-4 py-2 text-xs font-mono outline-none" 
              />
              <button 
                onClick={handleBrowse}
                className="bg-surface-container-high border border-outline-variant px-4 py-2 rounded-xl text-xs font-bold hover:bg-surface-variant transition-colors"
              >
                Browse
              </button>
            </div>
          </div>

          {/* Doc Type Toggle (Python Radiobuttons) */}
          <div className="space-y-3">
            <label className="text-[10px] font-black uppercase tracking-widest text-on-surface-variant">Document Category</label>
            <div className="grid grid-cols-2 gap-3">
              {DOCUMENT_TYPES.map((type) => (
                <button
                  key={type.id}
                  onClick={() => setDocType(type.id as any)}
                  className={`flex flex-col items-center gap-2 p-4 rounded-2xl border-2 transition-all ${
                    docType === type.id 
                      ? 'border-primary bg-primary/5 ring-1 ring-primary' 
                      : 'border-outline-variant bg-surface hover:bg-surface-container-low'
                  }`}
                >
                  {type.id === 'Vente' ? <FileUp size={20} /> : <Landmark size={20} />}
                  <span className="text-xs font-bold">{type.label.split(' ')[0]}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Action Button */}
          <div className="pt-4 space-y-4">
            <button 
              disabled={!filePath || isParsing}
              onClick={() => handleStartParsing(() => console.log("Next Tab"))}
              className="w-full py-4 bg-primary text-white rounded-2xl font-bold flex items-center justify-center gap-3 shadow-lg shadow-primary/20 hover:opacity-90 disabled:grayscale transition-all"
            >
              {isParsing ? <Loader2 className="animate-spin" size={20} /> : <Settings size={20} />}
              Parse & Apply Rules
            </button>
            
            <p className={`text-center text-xs font-bold ${status.color}`}>
              {status.text}
            </p>
          </div>
        </div>

        {/* Right Side: Raw Preview (Python Treeview Equivalent) */}
        <div className="flex-1 bg-surface-container-low flex flex-col overflow-hidden">
          <div className="h-12 border-b border-outline-variant bg-surface flex items-center px-6 justify-between">
            <div className="flex items-center gap-2 text-on-surface-variant">
              <TableIcon size={16} />
              <span className="text-[10px] font-black uppercase tracking-widest">Raw CSV Preview</span>
            </div>
            <div className="relative">
              <Search className="absolute left-3 top-2 text-on-surface-variant" size={14} />
              <input 
                type="text" 
                placeholder="Filter rows..." 
                className="bg-surface-container-low border border-outline-variant rounded-lg pl-9 pr-3 py-1 text-[11px] outline-none focus:border-primary"
              />
            </div>
          </div>

          <div className="flex-1 overflow-auto bg-surface">
            {rawData.length > 0 ? (
              <table className="w-full text-left border-collapse min-w-max">
                <thead className="sticky top-0 bg-surface-container-high z-10">
                  <tr>
                    {csvHeaders.map((header) => (
                      <th key={header} className="p-3 text-[10px] font-black uppercase text-on-surface-variant border-b border-outline-variant border-r last:border-r-0">
                        {header}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-outline-variant/30">
                  {rawData.map((row, idx) => (
                    <tr key={idx} className="hover:bg-primary/5 transition-colors">
                      {csvHeaders.map((header) => (
                        <td key={header} className="p-3 text-xs font-medium text-on-surface font-mono border-r border-outline-variant/10 last:border-r-0">
                          {typeof row[header] === 'number' ? row[header].toFixed(3) : row[header]}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="h-full flex flex-col items-center justify-center opacity-30 text-on-surface-variant">
                <TableIcon size={64} strokeWidth={1} />
                <p className="mt-4 font-bold text-sm">No data loaded yet</p>
                <p className="text-xs italic">Select a file and click Parse to preview contents</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}
