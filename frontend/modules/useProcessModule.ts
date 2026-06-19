// modules/useProcessModule.ts
import { useState, useRef, useEffect } from 'react';
import { AxeaneService } from '../services/endpoint';
import { TemplateCard } from '../types/axeane'; // Assuming you added the type

export function useProcessModule() {
  const [cards, setCards] = useState<any[]>([]);
  const [isExecuting, setIsExecuting] = useState(false);
  const [logs, setLogs] = useState<{msg: string, level: string}[]>([]);
  const [progress, setProgress] = useState({ current: 0, total: 0, percent: 0 });
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll logic for terminal
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  const handleGenerateTemplates = async () => {
    const result: any = await AxeaneService.generateTemplates("current_session");
    setCards(result);
  };

  const handleStartAutomation = async () => {
    setIsExecuting(true);
    // In a real app, you would listen to Tauri events for progress/logs
    await AxeaneService.startAutomation("current_session", "live");
  };

  const handleStop = async () => {
    await AxeaneService.stopAutomation();
    setIsExecuting(false);
  };

  return {
    cards, handleGenerateTemplates,
    isExecuting, handleStartAutomation, handleStop,
    logs, progress, scrollRef
  };
}
