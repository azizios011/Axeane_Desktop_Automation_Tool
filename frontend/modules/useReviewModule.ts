// modules/useReviewModule.ts
import { useState } from 'react';

export function useReviewModule() {
  const [templateCards, setTemplateCards] = useState<any[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [summary, setSummary] = useState<any>(null);

  const handleGenerateTemplates = () => {
    setIsGenerating(true);
    
    // Simulation of Python's FormulaEngine.build_template_cards()
    setTimeout(() => {
      const mockCards = [
        {
          match_type: 'specific',
          match_key: 'PASSAGER',
          invoice_count: 148,
          total_ttc: 4520.450,
          tva_rates: [19, 7],
          use_cash: true,
          use_timbre: true,
          formula_lines: [
            { step: 'client_total', account: '411000', label: 'PASSAGER', debit: 302.080, credit: 0 },
            { step: 'tax_split_19', account: '436719', label: 'TVA 19%', debit: 0, credit: 48.072 },
            { step: 'revenue_split_19', account: '707019', label: 'Revenue 19%', debit: 0, credit: 253.008 },
            { step: 'timbre', account: '437000', label: 'TIMBRE FISCAL', debit: 0, credit: 1.000 },
          ]
        },
        {
          match_type: 'default',
          match_key: 'DEFAULT',
          invoice_count: 216,
          total_ttc: 89430.120,
          tva_rates: [19],
          use_cash: false,
          use_timbre: true,
          formula_lines: [
            { step: 'client_total', account: '411000', label: 'CLIENT DIVERS', debit: 150.000, credit: 0 },
            { step: 'tax_split_19', account: '436719', label: 'TVA 19%', debit: 0, credit: 23.950 },
            { step: 'revenue_split_19', account: '707019', label: 'Revenue 19%', debit: 0, credit: 126.050 },
          ]
        }
      ];

      setTemplateCards(mockCards);
      setSummary({
        total_profiles: mockCards.length,
        total_invoices: 364,
        total_ttc: 93950.570
      });
      setIsGenerating(false);
    }, 1000);
  };

  const handleClear = () => {
    setTemplateCards([]);
    setSummary(null);
  };

  return { templateCards, isGenerating, summary, handleGenerateTemplates, handleClear };
}
