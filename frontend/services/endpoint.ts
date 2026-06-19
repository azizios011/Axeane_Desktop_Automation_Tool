// services/endpoint.ts
import { invoke } from '@tauri-apps/api/core';

export const AxeaneService = {
  // Triggers Python: parse_vente_csv(path)
  parseCSV: async (filePath: string, docType: string) => {
    return await invoke('parse_csv_command', { filePath, docType });
  },

  // Triggers native file picker
  openFilePicker: async () => {
    return await invoke<string | null>('open_file_dialog');
  }
};
