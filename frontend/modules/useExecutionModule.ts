// modules/useExecutionModule.ts
import { useState, useRef, useEffect } from 'react';
import { LogEntry, LogLevel } from '../metadata/executionSettings';
import { AxeaneAPI } from '../services/endpoint';

export function useExecutionModule(sessionId: string | null) {
  const [isRunning, setIsRunning] = useState(false);
  const [progress, setProgress] = useState({ current: 0, total: 0, success: 0, failed: 0, percent: 0 });
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const terminalRef = useRef<HTMLDivElement>(null);
  const pollIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Auto-scroll terminal: Python equivalent of self.log_text.see(tk.END)
  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [logs]);

  // Clean up polling interval on unmount
  useEffect(() => {
    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
    };
  }, []);

  const addLog = (message: string, level: LogLevel = 'INFO') => {
    const newLog: LogEntry = {
      id: `${Math.random().toString(36).substr(2, 9)}-${Date.now()}`,
      timestamp: new Date().toLocaleTimeString(),
      level,
      message
    };
    setLogs(prev => [...prev, newLog]);
  };

  const startAutomation = async (mode: 'live' | 'dry_run', browserMode: 'headless' | 'visible') => {
    if (!sessionId) {
      addLog("No active session. Please upload and parse data first.", "ERROR");
      return;
    }

    setIsRunning(true);
    setLogs([]); // Clear logs
    setProgress({ current: 0, total: 0, success: 0, failed: 0, percent: 0 });
    
    addLog(`Initiating automation in ${mode.toUpperCase()} mode (Browser: ${browserMode.toUpperCase()})...`, "INFO");

    try {
      // 1. Post to execute
      await AxeaneAPI.startAutomation(sessionId, mode, browserMode);
      addLog("Automation engine started on Python sidecar.", "SUCCESS");
      
      // 2. Start status polling loop
      const pollStatus = async () => {
        try {
          const res = await AxeaneAPI.getStatus(sessionId);
          
          // Update progress
          if (res.progress) {
            const current = res.progress.current || 0;
            const total = res.progress.total || 0;
            const percentage = Math.round(res.progress.percentage || 0);
            setProgress({
              current,
              total,
              success: current, // In our backend, success matches processed
              failed: 0,
              percent: percentage
            });
          }

          // Map and update logs
          if (res.logs && res.logs.length > 0) {
            const mappedLogs = res.logs.map((l: any, idx: number) => {
              let timeStr = "";
              try {
                timeStr = new Date(l.timestamp).toLocaleTimeString();
              } catch (e) {
                timeStr = l.timestamp;
              }
              return {
                id: `${idx}-${l.timestamp}`,
                timestamp: timeStr,
                level: (l.level || 'INFO') as LogLevel,
                message: l.message
              };
            });
            setLogs(mappedLogs);
          }

          // Check if finished
          if (res.status === 'completed' || res.status === 'error' || res.status === 'idle') {
            setIsRunning(false);
            if (pollIntervalRef.current) {
              clearInterval(pollIntervalRef.current);
              pollIntervalRef.current = null;
            }
            if (res.status === 'completed') {
              addLog("🏁 Execution completed successfully.", "SUCCESS");
            } else if (res.status === 'error') {
              addLog(`⛔ Execution failed: ${res.last_error || 'Unknown error'}`, "ERROR");
            } else {
              addLog("Execution stopped or went idle.", "WARNING");
            }
          }
        } catch (pollErr: any) {
          console.error("Error polling automation status:", pollErr);
          addLog(`Status poll error: ${pollErr.message}`, "ERROR");
        }
      };

      // Run immediately first
      await pollStatus();
      
      // Setup interval (500ms matching high density updating)
      pollIntervalRef.current = setInterval(pollStatus, 500);

    } catch (err: any) {
      addLog(`Failed to start execution: ${err.message}`, "ERROR");
      setIsRunning(false);
    }
  };

  const stopAutomation = async () => {
    if (!sessionId) return;
    try {
      addLog("Sending stop signal...", "WARNING");
      await AxeaneAPI.stopAutomation(sessionId);
      setIsRunning(false);
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
        pollIntervalRef.current = null;
      }
      addLog("⛔ Automation execution terminated by user request.", "ERROR");
    } catch (err: any) {
      addLog(`Error stopping automation: ${err.message}`, "ERROR");
    }
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
