// modules/useReviewModule.ts
import { useState, useEffect } from 'react';
import { AxeaneAPI } from '../services/endpoint';

export function useReviewModule(sessionId: string | null) {
  const [templateCards, setTemplateCards] = useState<any[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [summary, setSummary] = useState<any>(null);

  const fetchFormulas = async () => {
    if (!sessionId) return;
    setIsGenerating(true);
    try {
      const response = await AxeaneAPI.getFormulas(sessionId);
      setTemplateCards(response.cards || []);
      setSummary({
        total_profiles: response.total_cards,
        total_invoices: response.total_rows,
        total_ttc: response.cards ? response.cards.reduce((sum: number, c: any) => sum + (c.total_ttc || 0), 0) : 0,
        balanced_cards: response.balanced_cards,
        unbalanced_cards: response.unbalanced_cards
      });
    } catch (error) {
      console.error("Error loading formulas:", error);
    } finally {
      setIsGenerating(false);
    }
  };

  useEffect(() => {
    if (sessionId) {
      fetchFormulas();
    } else {
      setTemplateCards([]);
      setSummary(null);
    }
  }, [sessionId]);

  const handleGenerateTemplates = () => {
    fetchFormulas();
  };

  const handleClear = () => {
    setTemplateCards([]);
    setSummary(null);
  };

  return { templateCards, isGenerating, summary, handleGenerateTemplates, handleClear };
}
