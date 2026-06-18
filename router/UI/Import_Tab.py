# UI/Import_Tab.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import json
import os
from Function.csv_parser import parse_vente_csv, strip_keys
from Debug.Logger import ColorLogger as log

class ImportTab:
    def __init__(self, parent, shared_state, callback_on_parse):
        self.frame = ttk.Frame(parent)
        self.state = shared_state
        self.callback = callback_on_parse
        self._build_ui()

    def _build_ui(self):
        title = ttk.Label(self.frame, text="1. Import & Map Raw Data", font=("Segoe UI", 14, "bold"))
        title.pack(pady=10, padx=20, anchor="w")

        # Top Controls
        ctrl_frame = ttk.Frame(self.frame)
        ctrl_frame.pack(fill="x", padx=20, pady=5)
        
        self.file_path = tk.StringVar()
        ttk.Entry(ctrl_frame, textvariable=self.file_path, width=50).pack(side="left", padx=5)
        ttk.Button(ctrl_frame, text="Browse CSV/Excel", command=self._browse_file).pack(side="left", padx=5)

        self.doc_type = tk.StringVar(value="Vente")
        ttk.Radiobutton(ctrl_frame, text="Ventes", variable=self.doc_type, value="Vente", command=self._on_type_change).pack(side="left", padx=20)
        ttk.Radiobutton(ctrl_frame, text="Banque", variable=self.doc_type, value="Bank", command=self._on_type_change).pack(side="left", padx=5)

        self.btn_process = ttk.Button(ctrl_frame, text="⚙️ Parse & Apply Rules", command=self._start_parsing)
        self.btn_process.pack(side="right", padx=10)

        # Raw Data Table Title
        raw_title = ttk.Label(self.frame, text="2. Raw CSV Preview (Columns in CSV order)", 
                              font=("Segoe UI", 12, "bold"))
        raw_title.pack(pady=(15, 5), padx=20, anchor="w")

        # Raw Data Treeview
        self.raw_tree_frame = ttk.Frame(self.frame)
        self.raw_tree_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.raw_tree = ttk.Treeview(self.raw_tree_frame, show="headings", height=10)
        self.raw_vsb = ttk.Scrollbar(self.raw_tree_frame, orient="vertical", command=self.raw_tree.yview)
        self.raw_hsb = ttk.Scrollbar(self.raw_tree_frame, orient="horizontal", command=self.raw_tree.xview)
        self.raw_tree.configure(yscrollcommand=self.raw_vsb.set, xscrollcommand=self.raw_hsb.set)
        
        self.raw_tree.grid(row=0, column=0, sticky="nsew")
        self.raw_vsb.grid(row=0, column=1, sticky="ns")
        self.raw_hsb.grid(row=1, column=0, sticky="ew")
        
        self.raw_tree_frame.grid_rowconfigure(0, weight=1)
        self.raw_tree_frame.grid_columnconfigure(0, weight=1)

        self.status_label = ttk.Label(self.frame, text="Status: Idle", foreground="gray")
        self.status_label.pack(pady=5)

    def _on_type_change(self):
        """Clears the table when switching document types"""
        self.raw_tree["columns"] = ()
        for item in self.raw_tree.get_children():
            self.raw_tree.delete(item)

    def _browse_file(self):
        path = filedialog.askopenfilename(filetypes=[("CSV/Excel", "*.csv *.xlsx")])
        if path:
            self.file_path.set(path)

    def _start_parsing(self):
        path = self.file_path.get()
        if not path:
            messagebox.showwarning("Missing File", "Please select a file first.")
            return

        self.status_label.config(text="Status: Processing in background...", foreground="blue")
        log.info(f"Starting parse for file: {path}")
        threading.Thread(target=self._parse_logic, args=(path,), daemon=True).start()

    def _parse_logic(self, path):
        try:
            doc_type = self.doc_type.get()
            log.info(f"Document type selected: {doc_type}")
            
            if doc_type == "Vente":
                result = parse_vente_csv(path)
                if result:
                    parsed_data, csv_headers = result
                else:
                    parsed_data, csv_headers = [], []
            else:
                # TODO: Implement parse_bank_csv
                log.warn("Bank parsing not yet implemented.")
                parsed_data, csv_headers = [], []

            if not parsed_data:
                self.frame.after(0, lambda: self.status_label.config(text="Status: No data parsed. Check logs.", foreground="red"))
                return

            # Update Raw Table UI safely
            self.frame.after(0, self._populate_raw_table, parsed_data, csv_headers)
            
            # Store raw data in shared state
            self.state["raw_data"] = parsed_data
            self.frame.after(0, self._on_parse_success, len(parsed_data))
            
        except Exception as e:
            log.error(f"Fatal error in _parse_logic: {e}")
            self.frame.after(0, lambda: self.status_label.config(text=f"Error: {str(e)}", foreground="red"))

    def _populate_raw_table(self, raw_data, csv_headers):
        """Clears and fills the raw CSV table with columns in CSV order"""
        # Clear existing data
        for item in self.raw_tree.get_children():
            self.raw_tree.delete(item)
        
        # Set columns in CSV order
        self.raw_tree["columns"] = csv_headers
        for col in csv_headers:
            self.raw_tree.heading(col, text=col)
            # Auto-size columns based on content (max 150px)
            max_width = max(len(str(col)) * 10, 80)
            for row in raw_data[:50]:  # Sample first 50 rows
                val_len = len(str(row.get(col, ""))) * 8
                max_width = max(max_width, min(val_len, 150))
            self.raw_tree.column(col, width=max_width, anchor="w")
            
        log.info(f"Table columns set in CSV order: {csv_headers}")
        
        # Insert data rows
        for row in raw_data:
            values = [row.get(col, "") for col in csv_headers]
            # Format floats nicely for display
            formatted_values = []
            for val in values:
                if isinstance(val, float):
                    formatted_values.append(f"{val:,.3f}")
                else:
                    formatted_values.append(val)
            self.raw_tree.insert("", "end", values=formatted_values)
            
        log.success(f"Populated raw table with {len(raw_data)} rows.")

    def _on_parse_success(self, count):
        self.status_label.config(text=f"Status: Success! Loaded {count} raw rows.", foreground="green")
        self.callback() # Triggers Table_Tab refresh
        