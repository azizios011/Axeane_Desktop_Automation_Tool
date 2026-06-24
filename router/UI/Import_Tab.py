# UI/Import_Tab.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import json
import os
from Function.csv_parser import parse_bank_csv, parse_bank_pdf, parse_vente_csv, strip_keys
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
        raw_title = ttk.Label(self.frame, text="2. Raw CSV Preview (Columns mapped from Structure.json)", 
                              font=("Segoe UI", 12, "bold"))
        raw_title.pack(pady=(15, 5), padx=20, anchor="w")

        # Raw Data Treeview
        self.raw_tree_frame = ttk.Frame(self.frame)
        self.raw_tree_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.raw_tree = ttk.Treeview(self.raw_tree_frame, show="headings", height=10)
        self.raw_vsb = ttk.Scrollbar(self.raw_tree_frame, orient="vertical", command=self.raw_tree.yview)
        self.raw_tree.configure(yscrollcommand=self.raw_vsb.set)
        
        self.raw_tree.pack(side="left", fill="both", expand=True)
        self.raw_vsb.pack(side="right", fill="y")

        self.status_label = ttk.Label(self.frame, text="Status: Idle", foreground="gray")
        self.status_label.pack(pady=5)
        
        self._on_type_change()

    def _on_type_change(self):
        """Dynamically updates the Raw Treeview columns based on the selected Structure.json"""
        doc_type = self.doc_type.get()
        json_path = f"DB/{doc_type}_Structure.json"
        
        self.raw_tree["columns"] = ()
        
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    structure = strip_keys(json.load(f))
                
                col_mapping = structure.get("column_mapping", {})
                columns = list(col_mapping.keys())
                
                if columns:
                    self.raw_tree["columns"] = columns
                    for col in columns:
                        self.raw_tree.heading(col, text=col)
                        self.raw_tree.column(col, width=120, anchor="w")
                    log.debug(f"Treeview columns updated for {doc_type}: {columns}")
            except Exception as e:
                log.error(f"Error loading structure {json_path}: {e}")

    def _browse_file(self):
        path = filedialog.askopenfilename(filetypes=[("Import files", "*.csv *.xlsx *.pdf")])
        if path:
            self.file_path.set(path)
            if path.lower().endswith(".pdf"):
                self.doc_type.set("Bank")
                self._on_type_change()

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
                # Now returns (data, headers) tuple
                parsed_data, csv_headers = parse_vente_csv(path)
            else:
                if path.lower().endswith(".pdf"):
                    parsed_data, csv_headers = parse_bank_pdf(path)
                else:
                    parsed_data, csv_headers = parse_bank_csv(path)

            if not parsed_data:
                self.frame.after(0, lambda: self.status_label.config(text="Status: No data parsed. Check logs.", foreground="red"))
                return

            # Update Raw Table UI safely
            self.frame.after(0, self._populate_raw_table, parsed_data, csv_headers)
            
            # Store raw data in shared state
            self.state["raw_data"] = parsed_data
            self.frame.after(0, self._on_parse_success, len(parsed_data))
            
        except Exception as e:
            # FIX: Capture error message immediately to avoid scoping issues
            error_msg = str(e)
            log.error(f"Fatal error in _parse_logic: {error_msg}")
            self.frame.after(0, lambda: self.status_label.config(text=f"Error: {error_msg}", foreground="red"))

    def _populate_raw_table(self, raw_data, csv_headers):
        """Clears and fills the raw CSV table with columns in CSV order"""
        # Clear existing data
        for item in self.raw_tree.get_children():
            self.raw_tree.delete(item)
        
        # Set columns in CSV order
        self.raw_tree["columns"] = csv_headers
        for col in csv_headers:
            self.raw_tree.heading(col, text=col)
            # Auto-size columns
            max_width = max(len(str(col)) * 10, 80)
            for row in raw_data[:50]:
                val_len = len(str(row.get(col, ""))) * 8
                max_width = max(max_width, min(val_len, 150))
            self.raw_tree.column(col, width=max_width, anchor="w")
            
        log.info(f"Table columns set in CSV order: {csv_headers}")
        
        # Insert data rows
        for row in raw_data:
            values = [row.get(col, "") for col in csv_headers]
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
        self.callback()
        
