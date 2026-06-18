# UI/Import_Tab.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading

class ImportTab:
    def __init__(self, parent, shared_state, callback_on_parse):
        self.frame = ttk.Frame(parent)
        self.state = shared_state
        self.callback = callback_on_parse
        self._build_ui()

    def _build_ui(self):
        title = ttk.Label(self.frame, text="Import & Process Accounting Data", font=("Segoe UI", 14, "bold"))
        title.pack(pady=20, padx=20, anchor="w")

        # File Selection
        file_frame = ttk.LabelFrame(self.frame, text="1. Select Source File", padding=20)
        file_frame.pack(fill="x", padx=20, pady=10)
        
        self.file_path = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.file_path, width=60).pack(side="left", padx=5)
        ttk.Button(file_frame, text="Browse CSV/Excel", command=self._browse_file).pack(side="left", padx=5)

        # Document Type
        type_frame = ttk.LabelFrame(self.frame, text="2. Document Type", padding=20)
        type_frame.pack(fill="x", padx=20, pady=10)
        
        self.doc_type = tk.StringVar(value="Vente")
        ttk.Radiobutton(type_frame, text="Ventes (Sales)", variable=self.doc_type, value="Vente").pack(side="left", padx=20)
        ttk.Radiobutton(type_frame, text="Banque (Bank)", variable=self.doc_type, value="Bank").pack(side="left", padx=20)

        # Process Button
        self.btn_process = ttk.Button(self.frame, text="⚙️ Parse & Apply Rules", command=self._start_parsing)
        self.btn_process.pack(pady=30)

        self.status_label = ttk.Label(self.frame, text="Status: Idle", foreground="gray")
        self.status_label.pack()

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
        
        # Run parsing in a background thread to keep UI responsive
        threading.Thread(target=self._parse_logic, args=(path,), daemon=True).start()

    def _parse_logic(self, path):
        try:
            # TODO: Import your actual Logic here
            # from Function.import import import_and_process_vente
            # from Function.import import import_and_process_bank
            
            doc_type = self.doc_type.get()
            
            # MOCK DATA FOR DEMONSTRATION
            mock_entries = [
                {"ref": "FC000761", "date": "15/06/2026", "account": "411032", "label": "TUNISIE AUTOMOTIVE", "debit": 302.080, "credit": 0.0},
                {"ref": "FC000761", "date": "15/06/2026", "account": "436719", "label": "TVA 19%", "debit": 0.0, "credit": 48.230},
                {"ref": "FC000761", "date": "15/06/2026", "account": "707019", "label": "Revenue 19%", "debit": 0.0, "credit": 252.850},
                {"ref": "FC000761", "date": "15/06/2026", "account": "437000", "label": "TIMBRE FISCAL", "debit": 0.0, "credit": 1.0}
            ]
            
            self.state["parsed_entries"] = mock_entries
            
            # Update UI safely from background thread
            self.frame.after(0, self._on_parse_success)
        except Exception as e:
            self.frame.after(0, lambda: self.status_label.config(text=f"Error: {str(e)}", foreground="red"))

    def _on_parse_success(self):
        count = len(self.state["parsed_entries"])
        self.status_label.config(text=f"Status: Success! Generated {count} journal lines.", foreground="green")
        self.callback() # Triggers Table_Tab refresh and auto-switches tabs
        