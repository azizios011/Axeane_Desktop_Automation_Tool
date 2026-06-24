// services/endpoint.ts
import { API_BASE_URL, API_ENDPOINTS } from '../metadata/apiConfig';

/**
 * AXEANE FRONTEND API SERVICE
 * Pure HTTP implementation. Agnostic of Tauri or Python internals.
 */

export const AxeaneAPI = {
  
  // Generic helper for requests
  async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'API Request Failed');
    }

    return response.json();
  },

  // 1. Upload CSV
  async uploadFile(file: File) {
    const formData = new FormData();
    formData.append('file', file);

    return this.request<any>(API_ENDPOINTS.UPLOAD, {
      method: 'POST',
      body: formData, // Browser handles content-type for FormData
      headers: {}, // Remove default JSON header
    });
  },

  // 2. Trigger Parsing
  async parseData(sessionId: string, docType: string = 'Vente') {
    return this.request<any>(API_ENDPOINTS.PARSE, {
      method: 'POST',
      body: JSON.stringify({ session_id: sessionId, doc_type: docType }),
    });
  },

  // 3. Fetch Formula Cards (Review Tab)
  async getFormulas(sessionId: string) {
    return this.request<any>(`${API_ENDPOINTS.FORMULAS}?session_id=${sessionId}`, {
      method: 'GET',
    });
  },

  // 4. Start Automation (Execution Tab)
  async startAutomation(sessionId: string, mode: 'live' | 'dry_run', browserMode: 'headless' | 'visible' = 'headless') {
    return this.request<any>(API_ENDPOINTS.EXECUTE, {
      method: 'POST',
      body: JSON.stringify({ 
        session_id: sessionId, 
        mode: mode,
        browser_mode: browserMode
      }),
    });
  },

  // 5. Poll Status & Logs
  async getStatus(sessionId: string) {
    return this.request<any>(`${API_ENDPOINTS.STATUS}?session_id=${sessionId}`, {
      method: 'GET',
    });
  },

  // 6. Stop Automation
  async stopAutomation(sessionId: string) {
    return this.request<any>(`${API_ENDPOINTS.STOP}?session_id=${sessionId}`, {
      method: 'POST',
    });
  }
};
