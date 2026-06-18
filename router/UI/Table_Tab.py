# UI/Table_Tab.py
import tkinter as tk
from tkinter import ttk

class TableTab:
    def __init__(self, parent, shared_state):
        self.frame = ttk.Frame(parent)
        self.state = shared_state
        self._build_ui()

    def _build_ui(self):
        title = ttk.Label(self.frame, text="Generated Journal Entries (Ready for Axeane)", font=("Segoe UI", 14, "bold"))
        title.pack(pady=10, padx=20, anchor="w")

        # Treeview (Table)
        columns = ("ref", "date", "account", "label", "debit", "credit")
        self.tree = ttk.Treeview(self.frame, columns=columns, show="headings", height=20)
        
        # Define Headings
        self.tree.heading("ref", text="Ref / Piece")
        self.tree.heading("date", text="Date")
        self.tree.heading("account", text="Account Code")
        self.tree.heading("label", text="Libellé")
        self.tree.heading("debit", text="Débit (TND)")
        self.tree.heading("credit", text="Crédit (TND)")

        # Define Column Widths
        self.tree.column("ref", width=100)
        self.tree.column("date", width=80)
        self.tree.column("account", width=100)
        self.tree.column("label", width=300)
        self.tree.column("debit", width=100, anchor="e")
        self.tree.column("credit", width=100, anchor="e")

        # Scrollbars
        vsb = ttk.Scrollbar(self.frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self.frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Grid Layout for Table
        self.tree.grid(row=1, column=0, sticky="nsew", padx=(20, 0), pady=10)
        vsb.grid(row=1, column=1, sticky="ns", pady=10)
        hsb.grid(row=2, column=0, sticky="ew", padx=(20, 0))
        
        self.frame.grid_rowconfigure(1, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)

    def refresh_table(self):
        """Clears and repopulates the table from shared_state"""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for entry in self.state["parsed_entries"]:
            self.tree.insert("", "end", values=(
                entry.get("ref", ""),
                entry.get("date", ""),
                entry.get("account", ""),
                entry.get("label", ""),
                f"{entry.get('debit', 0.0):.3f}" if entry.get("debit") else "",
                f"{entry.get('credit', 0.0):.3f}" if entry.get("credit") else ""
            ))
            