// modules/useImportModule.ts
import { useState } from 'react';
import { AxeaneAPI } from '../services/endpoint';

export function useImportModule(setSessionId: (id: string | null) => void) {
  const [docType, setDocType] = useState<'Vente' | 'Bank'>('Vente');
  const [file, setFile] = useState<File | null>(null);
  const [isParsing, setIsParsing] = useState(false);
  const [status, setStatus] = useState({ text: "Status: Idle", color: "text-gray-500" });
  
  // States for the Raw Data Preview (Python's self.raw_tree)
  const [rawData, setRawData] = useState<any[]>([]);
  const [csvHeaders, setCsvHeaders] = useState<string[]>([]);

  const handleFileChange = (selectedFile: File) => {
    setFile(selectedFile);

    if (selectedFile.name.toLowerCase().endsWith('.pdf')) {
      setDocType('Bank');
      setCsvHeaders([]);
      setRawData([]);
      setStatus({ text: `Selected: ${selectedFile.name}. Click Parse to upload.`, color: "text-gray-500" });
      return;
    }
    
    // Parse CSV locally for preview
    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target?.result as string;
      if (!text) return;
      
      const lines = text.split(/\r?\n/).filter(line => line.trim() !== '');
      if (lines.length === 0) return;
      
      // Parse headers (handling potential quotes/BOM)
      const headers = lines[0].replace(/^\uFEFF/, '').split(',').map(h => h.replace(/^"|"$/g, '').trim());
      
      const data = lines.slice(1, 101).map(line => { // Limit to 100 rows for preview performance
        const values: string[] = [];
        let inQuotes = false;
        let currentValue = '';
        for (let i = 0; i < line.length; i++) {
          const char = line[i];
          if (char === '"') {
            inQuotes = !inQuotes;
          } else if (char === ',' && !inQuotes) {
            values.push(currentValue.trim().replace(/^"|"$/g, ''));
            currentValue = '';
          } else {
            currentValue += char;
          }
        }
        values.push(currentValue.trim().replace(/^"|"$/g, ''));
        
        const row: any = {};
        headers.forEach((h, index) => {
          row[h] = values[index] || '';
        });
        return row;
      });
      
      setCsvHeaders(headers);
      setRawData(data);
      setStatus({ text: `Selected: ${selectedFile.name}. Click Parse to upload.`, color: "text-gray-500" });
    };
    reader.readAsText(selectedFile);
  };

  const handleStartParsing = async (onSuccess: () => void) => {
    if (!file) return;
    
    setIsParsing(true);
    setStatus({ text: "Uploading file to server...", color: "text-primary" });

    try {
      // 1. Upload the file
      const uploadRes = await AxeaneAPI.uploadFile(file);
      const session_id = uploadRes.session_id;
      setSessionId(session_id);
      
      setStatus({ text: "Initiating background parsing...", color: "text-primary" });
      
      // 2. Trigger parsing on backend
      await AxeaneAPI.parseData(session_id, docType);
      
      // 3. Poll status
      setStatus({ text: "Parsing CSV in background...", color: "text-primary" });
      
      const checkStatus = async () => {
        try {
          const statusRes = await AxeaneAPI.getStatus(session_id);
          if (statusRes.status === 'completed') {
            setStatus({ text: `Parsing complete. Generated formula cards successfully.`, color: "text-green-600" });
            setIsParsing(false);
            setTimeout(onSuccess, 800);
          } else if (statusRes.status === 'error') {
            setStatus({ text: `Parsing failed: ${statusRes.last_error || 'Unknown error'}`, color: "text-error" });
            setIsParsing(false);
          } else {
            // Still parsing, poll again in 1 second
            setTimeout(checkStatus, 1000);
          }
        } catch (err: any) {
          setStatus({ text: `Error checking status: ${err.message}`, color: "text-error" });
          setIsParsing(false);
        }
      };
      
      setTimeout(checkStatus, 1000);

    } catch (error: any) {
      setStatus({ text: `Parsing failed: ${error.message}`, color: "text-[#f44747]" });
      setIsParsing(false);
    }
  };

  return {
    docType, setDocType,
    file, handleFileChange,
    isParsing, handleStartParsing,
    status, rawData, csvHeaders
  };
}
