// metadata/processSettings.ts
export const CARD_THEMES = {
  specific: {
    header: 'bg-green-700',
    body: 'bg-green-50',
    badge: 'bg-green-600',
    text: 'text-green-900'
  },
  default: {
    header: 'bg-orange-600',
    body: 'bg-orange-50',
    badge: 'bg-orange-500',
    text: 'text-orange-900'
  }
} as const;

export const LOG_COLORS = {
  INFO: 'text-blue-400',
  SUCCESS: 'text-green-400',
  ERROR: 'text-red-400',
  NETWORK: 'text-purple-400',
  DEFAULT: 'text-gray-300'
};
