// modules/useExecutionModule.ts
import { useState, useRef } from 'react';
import { AxeaneAPI } from '../services/endpoint';

export function useExecutionModule(sessionId: string | null) {
  const [isExecuting, setIsExecuting] = useState(false);
  const [progress, setProgress] = useState({ current: 0, total: 0, percent: 0 });
  const [logs, setLogs] = useState<any[]>([]);
  const pollingRef = useRef<NodeJS.Timeout | null>(null);

  const startAutomation = async (mode: 'live' | 'dry_run') => {
    if (!sessionId) return;
    setIsExecuting(true);
    
    try {
      await AxeaneAPI.startAutomation(sessionId, mode);
      
      // Start Polling (Symmetry with Python's background tasks)
      pollingRef.current = setInterval(async () => {
        const status = await AxeaneAPI.getStatus(sessionId);
        
        setProgress({
          current: status.progress.current,
          total: status.progress.total,
          percent: Math.round(status.progress.percentage)
        });
        
        setLogs(status.logs); // Update the console with newest logs

        if (status.status === 'completed' || status.status === 'error') {
          stopPolling();
          setIsExecuting(false);
        }
      }, 800); // Poll every 800ms
    } catch (err) {
      setIsExecuting(false);
      console.error("Automation Start Failed:", err);
    }
  };

  const stopAutomation = async () => {
    if (!sessionId) return;
    await AxeaneAPI.stopAutomation(sessionId);
    stopPolling();
    setIsExecuting(false);
  };

  const stopPolling = () => {
    if (pollingRef.current) clearInterval(pollingRef.current);
  };

  return { isExecuting, progress, logs, startAutomation, stopAutomation };
}
