// modules/useExecutionModule.ts
import { useState, useRef, useEffect } from 'react';
import { LogEntry, LogLevel } from '../metadata/executionSettings';

export function useExecutionModule() {
  const [isRunning, setIsRunning] = useState(false);
  const [progress, setProgress] = useState({ current: 0, total: 0, success: 0, failed: 0, percent: 0 });
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const terminalRef = useRef<HTMLDivElement>(null);

  // Auto-scroll terminal: Python equivalent of self.log_text.see(tk.END)
  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [logs]);

  const addLog = (message: string, level: LogLevel = 'INFO') => {
    const newLog: LogEntry = {
      id: Math.random().toString(36).substr(2, 9),
      timestamp: new Date().toLocaleTimeString(),
      level,
      message
    };
    setLogs(prev => [...prev, newLog]);
  };

  const startAutomation = async () => {
    setIsRunning(true);
    setLogs([]); // Clear logs
    setProgress({ current: 0, total: 361, success: 0, failed: 0, percent: 0 });
    
    addLog("Initializing Playwright Browser...", "INFO");
    addLog("Connecting to Axeane CDP session...", "NETWORK");

    // Simulation of the run_all loop from AxeaneOrchestrator.py
    let current = 0;
    const total = 361;
    let success = 0;
    
    const interval = setInterval(() => {
      current++;
      success++;
      const pct = (current / total) * 100;
      
      setProgress(prev => ({ ...prev, current, success, percent: Math.round(pct) }));
      
      if (current % 5 === 0) {
        addLog(`Successfully processed entry ${current} | Reference: FC000${760 + current}`, "SUCCESS");
      }

      if (current >= total) {
        clearInterval(interval);
        setIsRunning(false);
        addLog(`🏁 Complete: ${success} succeeded, 0 failed`, "SUCCESS");
      }
    }, 200);
  };

  const stopAutomation = () => {
    setIsRunning(false);
    addLog("⛔ Stopping after current operation...", "ERROR");
  };

  const clearLogs = () => setLogs([]);

  return {
    isRunning,
    progress,
    logs,
    terminalRef,
    startAutomation,
    stopAutomation,
    clearLogs
  };
}
