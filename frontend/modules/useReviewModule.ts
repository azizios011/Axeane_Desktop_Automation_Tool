// modules/useReviewModule.ts
import { useState } from 'react';
import { AxeaneAPI } from '../services/endpoint';

export function useReviewModule(sessionId: string | null) {
  const [formulaCards, setFormulaCards] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const refreshTemplates = async () => {
    if (!sessionId) return;
    setIsLoading(true);
    try {
      const response = await AxeaneAPI.getFormulas(sessionId);
      // Logic from Python: cards = engine.build_cards(raw_data)
      setFormulaCards(response.cards || []); 
    } catch (err) {
      console.error("Failed to load formula cards:", err);
    } finally {
      setIsLoading(false);
    }
  };

  return { formulaCards, isLoading, refreshTemplates };
}
