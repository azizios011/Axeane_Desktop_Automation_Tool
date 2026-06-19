// modules/useImportModule.ts
import { useState } from 'react';

export function useImportModule() {
  const [docType, setDocType] = useState<'Vente' | 'Bank'>('Vente');
  const [filePath, setFilePath] = useState<string>("");
  const [isParsing, setIsParsing] = useState(false);
  const [status, setStatus] = useState({ text: "Status: Idle", color: "text-gray-500" });
  
  // States for the Raw Data Preview (Python's self.raw_tree)
  const [rawData, setRawData] = useState<any[]>([]);
  const [csvHeaders, setCsvHeaders] = useState<string[]>([]);

  const handleBrowse = () => {
    // Future: const path = await AxeaneAPI.openFileDialog();
    // setFilePath(path);
    setFilePath("C:\\Users\\Admin\\Documents\\journal_vte_mars.csv");
  };

  const handleStartParsing = async (onSuccess: () => void) => {
    if (!filePath) return;
    
    setIsParsing(true);
    setStatus({ text: "Status: Processing in background...", color: "text-primary" });

    try {
      // Simulation of Python's parse_vente_csv
      setTimeout(() => {
        const mockData = [
          { "Client": "C000001 | PASSAGER", "Reference": "FC000761", "Date": "02/03/2026", "TTC": 302.080, "TVA %": "19.00 %" },
          { "Client": "C000203 | AUTO CLASSE", "Reference": "FC000782", "Date": "04/03/2026", "TTC": 4871.682, "TVA %": "7.00 %" },
        ];
        const mockHeaders = ["Client", "Reference", "Date", "TTC", "TVA %"];
        
        setRawData(mockData);
        setCsvHeaders(mockHeaders);
        setStatus({ text: `Status: Success! Loaded ${mockData.length} raw rows.`, color: "text-green-600" });
        setIsParsing(false);
        
        // Python: self.callback() -> Switch to Review tab
        setTimeout(onSuccess, 1000); 
      }, 1500);

    } catch (error) {
      setStatus({ text: "Status: Error parsing file", color: "text-error" });
      setIsParsing(false);
    }
  };

  return {
    docType, setDocType,
    filePath, handleBrowse,
    isParsing, handleStartParsing,
    status, rawData, csvHeaders
  };
}
