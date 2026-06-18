# UI/Table_Tab.py
import tkinter as tk
from tkinter import ttk

class TableTab:
    def __init__(self, parent, shared_state):
        self.frame = ttk.Frame(parent)
        self.state = shared_state
        self._build_ui()

    def _build_ui(self):
        # 1. Title (using pack)
        title = ttk.Label(
            self.frame, 
            text="Generated Accounting Formulas (Rules Applied)", 
            font=("Segoe UI", 14, "bold")
        )
        title.pack(pady=(10, 0), padx=20, anchor="w")

        # 2. Info Label (using pack)
        info_label = ttk.Label(
            self.frame, 
            text="Parent = Document Header | Children = Generated Journal Lines", 
            foreground="gray"
        )
        info_label.pack(padx=20, anchor="w")

        # 3. Container for Treeview and Scrollbar 
        # This frame will expand to fill all remaining vertical space
        tree_container = ttk.Frame(self.frame)
        tree_container.pack(fill="both", expand=True, padx=20, pady=10)

        # Hierarchical Treeview for Formulas
        columns = ("type", "account", "description", "debit", "credit")
        self.tree = ttk.Treeview(tree_container, columns=columns, show="tree headings", height=20)
        
        # Define Headings
        self.tree.heading("#0", text="Document / Step")
        self.tree.heading("type", text="Side")
        self.tree.heading("account", text="Account")
        self.tree.heading("description", text="Label / Formula")
        self.tree.heading("debit", text="Débit (TND)")
        self.tree.heading("credit", text="Crédit (TND)")

        # Define Column Widths
        self.tree.column("#0", width=250)
        self.tree.column("type", width=60, anchor="center")
        self.tree.column("account", width=100)
        self.tree.column("description", width=250)
        self.tree.column("debit", width=100, anchor="e")
        self.tree.column("credit", width=100, anchor="e")

        # Scrollbar
        vsb = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        # Pack tree and scrollbar inside the container (still using pack, no grid!)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

    def refresh_table(self):
        """Clears and repopulates the tree with hierarchical formulas"""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Group entries by 'ref' (Invoice Number) to create the formula structure
        grouped_entries = {}
        for entry in self.state.get("parsed_entries", []):
            ref = entry.get("ref", "UNKNOWN")
            if ref not in grouped_entries:
                grouped_entries[ref] = {"header": entry, "lines": []}
            grouped_entries[ref]["lines"].append(entry)

        for ref, data in grouped_entries.items():
            header = data["header"]
            # Create Parent Row (The Document Header)
            parent_text = f"{ref} | {header.get('date', '')} | {header.get('client_name', '')} | TTC: {header.get('ttc', 0)}"
            parent_id = self.tree.insert("", "end", text=parent_text, values=("", "", "", "", ""), open=True)
            
            # Create Child Rows (The Accounting Formula Lines)
            for line in data["lines"]:
                side = "DEBIT" if line.get("debit", 0) > 0 else "CREDIT"
                d_val = f"{line.get('debit', 0):.3f}" if line.get("debit", 0) > 0 else ""
                c_val = f"{line.get('credit', 0):.3f}" if line.get("credit", 0) > 0 else ""
                
                self.tree.insert(parent_id, "end", text="", values=(
                    side,
                    line.get("account", ""),
                    line.get("label", ""),
                    d_val,
                    c_val
                ))
