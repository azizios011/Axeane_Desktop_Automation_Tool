// modules/useSettingsModule.ts
import { useState } from 'react';

export function useSettingsModule() {
  // Logic matches Logic/accounts.py and Logic/Rules.py
  const [profiles, setProfiles] = useState([]);
  const [browserConfig, setBrowserConfig] = useState({
    mode: "Persistent Profile (Keep Login)",
    cdp_port: 9222,
    headless: false
  });

  const saveToBackend = async () => {
    // This would call an endpoint like AxeaneAPI.updateConfig(profiles, browserConfig)
    console.log("Syncing rules and browser settings to Python DB...");
  };

  return { profiles, setProfiles, browserConfig, setBrowserConfig, saveToBackend };
}
