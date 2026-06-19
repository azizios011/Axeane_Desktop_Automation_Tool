// metadata/rulesDefinitions.ts
export const ENTRY_STEPS = [
  { id: 'client_total', label: 'Client Total (Debit)', description: 'Gross TTC amount' },
  { id: 'tax_split', label: 'TVA Split (Credit)', description: 'Calculated per rate' },
  { id: 'revenue_split', label: 'Revenue/HT (Credit)', description: 'Net amount per rate' },
  { id: 'timbre', label: 'Timbre Fiscal', description: 'Fixed stamp fee' },
  { id: 'cash_reroute', label: 'Cash Reroute', description: 'Moves client debit to Caisse' },
] as const;

export const DEFAULT_TVA_RATES = [
  { rate: 19, ht: "707019", tva: "436719" },
  { rate: 13, ht: "707013", tva: "436713" },
  { rate: 7, ht: "707007", tva: "436707" },
];
