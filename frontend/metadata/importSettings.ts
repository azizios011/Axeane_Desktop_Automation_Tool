// metadata/importSettings.ts
export const DOCUMENT_TYPES = [
  { id: 'Vente', label: 'Ventes (Sales Invoices)', icon: 'FileUp' },
  { id: 'Bank', label: 'Banque (Bank Statements)', icon: 'Landmark' },
] as const;

export type DocType = typeof DOCUMENT_TYPES[number]['id'];
