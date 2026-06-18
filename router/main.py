# main.py
import tkinter as tk
from tkinter import ttk
from UI.Settings_Tab import SettingsTab
from UI.Import_Tab import ImportTab
from UI.Table_Tab import TableTab
from UI.Execution_Tab import ExecutionTab
from UI.PWA_Tab import PWATab  # <-- NEW IMPORT

def main():
    root = tk.Tk()
    root.title("Axeane Kompta Automation Engine")
    root.geometry("1100x800")
    root.minsize(950, 700)
    
    # ==========================================
    # SHARED STATE (Passed to all tabs)
    # ==========================================
    shared_state = {
        "raw_data": [],
        "parsed_entries": [],
        "config": {
            "username": "RIHAB1", 
            "password": "", 
            "entreprise": "CPR", 
            "exercice": "2026",
            # NEW: Default CDP/PWA Settings
            "cdp_settings": {
                "mode": "Persistent Profile (Keep Login)", # Default to persistent so they don't have to login every time
                "cdp_port": 9222,
                "profile_dir": "./axeane_browser_profile",
                "pwa_url": "https://kompta.axeane.com",
                "headless": False
            }
        },
        "is_running": False,
        "logs": []
    }

    # UI Styling
    style = ttk.Style()
    style.theme_use('clam') 
    
    # Create Tabview
    tabview = ttk.Notebook(root)
    tabview.pack(fill='both', expand=True, padx=10, pady=10)

    # Initialize Tabs
    settings_tab = SettingsTab(tabview, shared_state)
    pwa_tab = PWATab(tabview, shared_state)       # <-- NEW TAB
    import_tab = ImportTab(tabview, shared_state, lambda: table_tab.refresh_table())
    table_tab = TableTab(tabview, shared_state)
    execution_tab = ExecutionTab(tabview, shared_state, root)

    # Add Tabs to Notebook
    tabview.add(settings_tab.frame, text=" ⚙️ Settings ")
    tabview.add(pwa_tab.frame, text=" 🚀 Browser / CDP ")  # <-- ADDED TO NOTEBOOK
    tabview.add(import_tab.frame, text=" 📥 Import Data ")
    tabview.add(table_tab.frame, text=" 📊 Preview & Rules ")
    tabview.add(execution_tab.frame, text=" 🏁 Execution & Logs ")

    root.mainloop()

if __name__ == "__main__":
    main()
    