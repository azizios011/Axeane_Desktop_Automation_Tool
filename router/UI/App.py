# UI/App.py
import tkinter as tk
from tkinter import ttk
from UI.Settings_Tab import SettingsTab
from UI.Import_Tab import ImportTab
from UI.Table_Tab import TableTab
from UI.Execution_Tab import ExecutionTab

class AxeaneApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Axeane Kompta Automation Engine")
        self.root.geometry("1100x750")
        self.root.minsize(950, 650)
        
        # ==========================================
        # SHARED STATE (Passed to all tabs)
        # ==========================================
        self.shared_state = {
            "raw_data": [],          # Output from Function/csv_parser.py
            "parsed_entries": [],    # Output from Logic/Rules.py (Ready for Axeane)
            "config": {
                "username": "RIHAB1", 
                "password": "", 
                "entreprise": "CPR", 
                "exercice": "2026"
            },
            "is_running": False,
            "logs": []
        }

        # UI Styling
        style = ttk.Style()
        style.theme_use('clam') # 'clam' provides a cleaner, more modern look
        
        # Create Tabview
        self.tabview = ttk.Notebook(self.root)
        self.tabview.pack(fill='both', expand=True, padx=10, pady=10)

        # Initialize Tabs
        self.settings_tab = SettingsTab(self.tabview, self.shared_state)
        self.import_tab = ImportTab(self.tabview, self.shared_state, self.on_data_parsed)
        self.table_tab = TableTab(self.tabview, self.shared_state)
        self.execution_tab = ExecutionTab(self.tabview, self.shared_state, self.root)

        # Add Tabs to Notebook
        self.tabview.add(self.settings_tab.frame, text=" ⚙️ Settings ")
        self.tabview.add(self.import_tab.frame, text=" 📥 Import Data ")
        self.tabview.add(self.table_tab.frame, text=" 📊 Preview & Rules ")
        self.tabview.add(self.execution_tab.frame, text=" 🚀 Execution & Logs ")

    def on_data_parsed(self):
        """Callback triggered by Import_Tab when parsing is done"""
        self.table_tab.refresh_table()
        # Auto-switch to the Table tab so the user can verify the data
        self.tabview.select(self.table_tab.frame)
        