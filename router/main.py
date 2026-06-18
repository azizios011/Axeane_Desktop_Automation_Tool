# main.py
import tkinter as tk
from tkinter import ttk
from UI.Settings_Tab import SettingsTab
from UI.Import_Tab import ImportTab
from UI.review_and_rules import ReviewAndRulesTab
from UI.Execution_Tab import ExecutionTab
from UI.PWA_Tab import PWATab

def main():
    root = tk.Tk()
    root.title("Axeane Kompta Automation Engine")
    root.geometry("1200x800")
    root.minsize(1000, 700)
    
    # ==========================================
    # SHARED STATE (Passed to all tabs)
    # ==========================================
    shared_state = {
        "raw_data": [],              # Output from Function/csv_parser.py
        "parsed_entries": [],        # Output from Logic/Rules.py
        "formulas": [],              # Output from Modules/FormulaEngine.py
        "config": {
            "username": "RIHAB1", 
            "password": "", 
            "entreprise": "CPR", 
            "exercice": "2026",
            "cdp_settings": {
                "mode": "Persistent Profile (Keep Login)",
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
    pwa_tab = PWATab(tabview, shared_state)
    import_tab = ImportTab(tabview, shared_state, lambda: tabview.select(review_tab.frame))
    review_tab = ReviewAndRulesTab(tabview, shared_state)
    execution_tab = ExecutionTab(tabview, shared_state, root)

    # Add Tabs to Notebook
    tabview.add(settings_tab.frame, text=" ⚙️ Settings ")
    tabview.add(pwa_tab.frame, text=" 🚀 Browser / CDP ")
    tabview.add(import_tab.frame, text=" 📥 Import Data ")
    tabview.add(review_tab.frame, text=" 🔧 Preview & Rules ")
    tabview.add(execution_tab.frame, text=" 🏁 Execution & Logs ")

    root.mainloop()

if __name__ == "__main__":
    main()
