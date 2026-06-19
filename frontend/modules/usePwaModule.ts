// modules/usePwaModule.ts
import { useState } from 'react';
import { DEFAULT_PATHS } from '../metadata/cdpDefaults';

export function usePwaModule() {
  const [cdpSettings, setCdpSettings] = useState({
    browser_type: "Chrome",
    executable_path: DEFAULT_PATHS["Chrome"],
    mode: "Persistent Profile (Keep Login)",
    cdp_port: 9222,
    profile_dir: "./axeane_browser_profile",
    pwa_url: "https://kompta.axeane.com",
    headless: false
  });

  const updateBrowserType = (type: string) => {
    const newPath = DEFAULT_PATHS[type as keyof typeof DEFAULT_PATHS] || "";
    setCdpSettings(prev => ({
      ...prev,
      browser_type: type,
      executable_path: newPath
    }));
  };

  const updateField = (field: string, value: any) => {
    setCdpSettings(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSave = () => {
    console.log("Saving CDP Configuration to Python Sidecar:", cdpSettings);
    // Future: AxeaneAPI.saveCdpConfig(cdpSettings)
  };

  return {
    cdpSettings,
    updateBrowserType,
    updateField,
    handleSave
  };
}
