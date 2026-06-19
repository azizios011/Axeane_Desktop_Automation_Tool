// metadata/apiConfig.ts
export const API_BASE_URL = "http://localhost:8000"; // The Python server address
export const API_ENDPOINTS = {
  UPLOAD: "/api/upload",
  PARSE: "/api/parse",
  FORMULAS: "/api/formulas",
  EXECUTE: "/api/execute",
  STATUS: "/api/status",
  STOP: "/api/stop",
} as const;
