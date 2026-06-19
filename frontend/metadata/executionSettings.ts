// metadata/executionSettings.ts
export const LOG_LEVEL_COLORS = {
  INFO: 'text-[#4ec9b0]',    // Teal
  SUCCESS: 'text-[#6a9955]', // Green
  ERROR: 'text-[#f44747]',   // Red
  NETWORK: 'text-[#569cd6]', // Blue
  SYSTEM: 'text-[#d4d4d4]'   // Gray/White
} as const;

export type LogLevel = keyof typeof LOG_LEVEL_COLORS;

export interface LogEntry {
  id: string;
  timestamp: string;
  level: LogLevel;
  message: string;
}
