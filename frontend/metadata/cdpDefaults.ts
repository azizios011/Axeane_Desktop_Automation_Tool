// metadata/cdpDefaults.ts
export const BROWSER_TYPES = ["Chrome", "Edge", "Playwright Chromium"] as const;

export const LAUNCH_MODES = [
  { id: "Normal", label: "Standard Launch (Fresh session)" },
  { id: "Persistent", label: "Persistent Profile (Keep Login)" },
  { id: "CDP", label: "Connect to Existing CDP" },
  { id: "PWA", label: "PWA Mode (Standalone App)" },
] as const;

export const ENTERPRISE_OPTIONS = ["CPR", "ESP", "GIS", "URAM"];
export const EXERCICE_OPTIONS = ["2026", "2025", "2024"];

export const DEFAULT_PATHS = {
  Chrome: "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
  Edge: "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
  Playwright: "",
};
