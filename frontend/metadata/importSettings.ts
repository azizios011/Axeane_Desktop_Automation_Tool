// metadata/importSettings.ts
export const DOCUMENT_TYPES = [
  { id: 'Vente', label: 'Ventes (Sales Invoices)', icon: 'FileText' },
  { id: 'Bank', label: 'Banque (Bank Statements)', icon: 'CreditCard' },
] as const;

export type DocType = typeof DOCUMENT_TYPES[number]['id'];

export const DEFAULT_COLUMNS = [
  "Client", "Reference", "Date", "TTC", "TVA %", "Montant TVA"
];