# main.py
import tkinter as tk
from tkinter import ttk
import traceback
import sys
import os

def exception_handler(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    print("\n=== FULL TRACEBACK ===")
    traceback.print_exception(exc_type, exc_value, exc_traceback)
    print("=====================\n")

sys.excepthook = exception_handler
# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import UI components
from UI.Settings_Tab import SettingsTab
from UI.PWA_Tab import PWATab
from UI.Import_Tab import ImportTab
from UI.review_and_rules import ReviewAndRulesTab
from UI.Execution_Tab import ExecutionTab

# Import core modules
from Logic.accounts import AccountManager
from Logic.Rules import RulesEngine
from Modules.FormulaEngine import FormulaEngine
from Debug.Logger import ColorLogger as log


def main():
    log.info("Starting Axeane Kompta Automation Engine...")
    
    # Initialize core engines
    try:
        account_manager = AccountManager()
        rules_engine = RulesEngine()
        formula_engine = FormulaEngine()
        log.success("Core engines initialized successfully")
    except Exception as e:
        log.error(f"Failed to initialize core engines: {e}")
        sys.exit(1)
    
    # Create main window
    root = tk.Tk()
    root.title("Axeane Kompta Automation Engine")
    root.geometry("1400x900")
    root.minsize(1200, 800)
    
    # Initialize shared state
    shared_state = {
        "raw_data": [],
        "parsed_entries": [],
        "formula_cards": [],
        "config": {
            "username": "",
            "password": "",
            "entreprise": "CPR",
            "exercice": "2026",
            "cdp_settings": {
                "mode": "Persistent Profile (Keep Login)",
                "cdp_port": 9222,
                "profile_dir": "./axeane_browser_profile",
                "pwa_url": "https://kompta.axeane.com",
                "headless": False,
                "browser_type": "Chrome",
                "executable_path": ""
            }
        },
        "is_running": False,
        "logs": [],
        "engines": {
            "account_manager": account_manager,
            "rules_engine": rules_engine,
            "formula_engine": formula_engine
        }
    }
    
    # Apply theme
    style = ttk.Style()
    style.theme_use('clam')
    
    # Create tabview
    tabview = ttk.Notebook(root)
    tabview.pack(fill='both', expand=True, padx=10, pady=10)
    
    # Initialize tabs
    settings_tab = SettingsTab(tabview, shared_state)
    pwa_tab = PWATab(tabview, shared_state)
    import_tab = ImportTab(tabview, shared_state, lambda: tabview.select(review_tab.frame))
    review_tab = ReviewAndRulesTab(tabview, shared_state)
    execution_tab = ExecutionTab(tabview, shared_state, root)
    
    # Add tabs to notebook
    tabview.add(settings_tab.frame, text=" ⚙️ Settings ")
    tabview.add(pwa_tab.frame, text=" 🚀 Browser / CDP ")
    tabview.add(import_tab.frame, text=" 📥 Import Data ")
    tabview.add(review_tab.frame, text=" 🔧 Preview & Rules ")
    tabview.add(execution_tab.frame, text=" 🏁 Execution & Logs ")
    
    log.success("UI initialized successfully")
    log.info("Ready to process accounting data")
    
    # Start main loop
    root.mainloop()


if __name__ == "__main__":
    main()
    