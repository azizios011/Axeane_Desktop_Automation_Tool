// modules/useImportModule.ts
import { useState } from 'react';
import { AxeaneService } from '../services/endpoint';
import { DocType } from '../metadata/importSettings';

export function useImportModule() {
  const [docType, setDocType] = useState<DocType>('Vente');
  const [filePath, setFilePath] = useState<string | null>(null);
  const [isParsing, setIsParsing] = useState(false);
  const [previewData, setPreviewData] = useState<any[]>([]);

  const handleBrowse = async () => {
    const path = await AxeaneService.openFilePicker();
    if (path) setFilePath(path);
  };

  const handleProcess = async (onSuccess: () => void) => {
    if (!filePath) return;
    
    setIsParsing(true);
    try {
      const result: any = await AxeaneService.parseCSV(filePath, docType);
      setPreviewData(result.data); // result.data matches Python's parsed_data
      onSuccess(); // Triggers navigation to next tab
    } catch (error) {
      console.error("Parsing failed", error);
    } finally {
      setIsParsing(false);
    }
  };

  return {
    docType, setDocType,
    filePath, handleBrowse,
    isParsing, handleProcess,
    previewData
  };
}