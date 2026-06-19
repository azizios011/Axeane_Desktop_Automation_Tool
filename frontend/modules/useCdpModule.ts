// modules/useCdpModule.ts
import { useState, useEffect } from 'react';
import { DEFAULT_PATHS } from '../metadata/cdpDefaults';

export function useCdpModule() {
  const [config, setConfig] = useState({
    auth: {
      username: "RIHAB1",
      password: "",
      enterprise: "CPR",
      exercice: "2026"
    },
    browser: {
      type: "Chrome" as "Chrome" | "Edge" | "Playwright",
      executable_path: DEFAULT_PATHS.Chrome,
      mode: "Persistent",
      cdp_port: 9222,
      profile_dir: "./axeane_browser_profile",
      pwa_url: "https://kompta.axeane.com",
      headless: false
    }
  });

  const [showPassword, setShowPassword] = useState(false);

  // Sync path when browser type changes (mimics Python _on_browser_change)
  const updateBrowserType = (type: any) => {
    setConfig(prev => ({
      ...prev,
      browser: {
        ...prev.browser,
        type,
        executable_path: DEFAULT_PATHS[type as keyof typeof DEFAULT_PATHS] || ""
      }
    }));
  };

  const updateField = (section: 'auth' | 'browser', field: string, value: any) => {
    setConfig(prev => ({
      ...prev,
      [section]: { ...prev[section], [field]: value }
    }));
  };

  const handleSave = () => {
    console.log("Saving Configuration to Local Storage/State:", config);
    // Logic to persist config will go here
  };

  return {
    config,
    updateField,
    updateBrowserType,
    showPassword,
    setShowPassword,
    handleSave
  };
}
