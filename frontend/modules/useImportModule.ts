// modules/useImportModule.ts
import { useState } from 'react';
import { AxeaneAPI } from '../services/endpoint';

export function useImportModule() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [rawData, setRawData] = useState<any[]>([]);
  const [isParsing, setIsParsing] = useState(false);

  const handleUploadAndParse = async (file: File, docType: string) => {
    setIsParsing(true);
    try {
      // 1. Upload to Python
      const uploadRes = await AxeaneAPI.uploadFile(file);
      const sid = uploadRes.session_id;
      setSessionId(sid);

      // 2. Trigger Parse in Python
      await AxeaneAPI.parseData(sid, docType);
      
      // 3. Optional: Fetch preview immediately if your backend returns it
      // or wait for polling. For now, we assume success.
      return sid;
    } catch (err) {
      console.error("Import Flow Failed:", err);
    } finally {
      setIsParsing(false);
    }
  };

  return { sessionId, rawData, isParsing, handleUploadAndParse };
}
