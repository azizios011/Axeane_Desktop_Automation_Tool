# UI/review_and_rules.py
import tkinter as tk
from tkinter import ttk, messagebox
from Modules.FormulaEngine import FormulaEngine
from Debug.Logger import ColorLogger as log


class ReviewAndRulesTab:
    """
    Displays the generated formulas showing exactly how each invoice will be entered row-by-row.
    """

    def __init__(self, parent, shared_state):
        self.frame = ttk.Frame(parent)
        self.state = shared_state
        self.engine = FormulaEngine()
        self._build_ui()

    def _build_ui(self):
        # Title
        title = ttk.Label(self.frame, text="Formula Preview & Rules",
                         font=("Segoe UI", 14, "bold"))
        title.pack(pady=10, padx=20, anchor="w")

        info_label = ttk.Label(self.frame,
                              text="Click 'Generate Formulas' to see exactly how each invoice will be entered row-by-row",
                              foreground="gray")
        info_label.pack(padx=20, anchor="w")

        # Control Panel
        ctrl_frame = ttk.Frame(self.frame)
        ctrl_frame.pack(fill="x", padx=20, pady=10)

        self.btn_generate = ttk.Button(ctrl_frame, text="🔧 Generate Formulas",
                                       command=self._generate_formulas)
        self.btn_generate.pack(side="left", padx=5)

        self.btn_clear = ttk.Button(ctrl_frame, text="🗑️ Clear",
                                   command=self._clear_formulas)
        self.btn_clear.pack(side="left", padx=5)

        # Summary Panel
        self.summary_frame = ttk.LabelFrame(self.frame, text="Summary", padding=10)
        self.summary_frame.pack(fill="x", padx=20, pady=10)

        self.summary_label = ttk.Label(self.summary_frame,
                                      text="No formulas generated yet",
                                      font=("Segoe UI", 10))
        self.summary_label.pack(anchor="w")

        # Formula Display (Treeview)
        display_frame = ttk.LabelFrame(self.frame, text="Formula Details", padding=10)
        display_frame.pack(fill="both", expand=True, padx=20, pady=10)

        columns = ("ref", "row_num", "account", "label", "debit", "credit", "step")
        self.tree = ttk.Treeview(display_frame, columns=columns, show="tree headings", height=15)

        # Define Headings
        self.tree.heading("#0", text="Invoice / Client")
        self.tree.heading("ref", text="Reference")
        self.tree.heading("row_num", text="Row #")
        self.tree.heading("account", text="Account")
        self.tree.heading("label", text="Label")
        self.tree.heading("debit", text="Débit")
        self.tree.heading("credit", text="Crédit")
        self.tree.heading("step", text="Step")

        # Define Column Widths
        self.tree.column("#0", width=250)
        self.tree.column("ref", width=100)
        self.tree.column("row_num", width=60, anchor="center")
        self.tree.column("account", width=100)
        self.tree.column("label", width=200)
        self.tree.column("debit", width=100, anchor="e")
        self.tree.column("credit", width=100, anchor="e")
        self.tree.column("step", width=120)

        # Scrollbars
        vsb = ttk.Scrollbar(display_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(display_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        display_frame.grid_rowconfigure(0, weight=1)
        display_frame.grid_columnconfigure(0, weight=1)

    def _generate_formulas(self):
        raw_data = self.state.get("raw_data", [])

        if not raw_data:
            messagebox.showwarning("No Data", "Please import and parse a CSV file first.")
            return

        log.info(f"Generating formulas for {len(raw_data)} invoices...")

        try:
            self.btn_generate.config(state="disabled")
            self.summary_label.config(text="Generating formulas...")
            self.frame.update_idletasks()

            # Generate formulas
            cards = self.engine.build_cards(raw_data)

            # Store in shared state
            self.state["formula_cards"] = cards

            # Update summary
            total_cards = len(cards)
            total_rows = sum(c["row_count"] for c in cards)
            balanced = sum(1 for c in cards if c["is_balanced"])
            unbalanced = total_cards - balanced

            summary_text = (
                f"✅ Generated {total_cards} formulas\n"
                f"📊 Total rows to enter: {total_rows}\n"
                f"✓ Balanced invoices: {balanced}\n"
                f"✗ Unbalanced invoices: {unbalanced}"
            )
            self.summary_label.config(text=summary_text)

            # Display formulas in treeview
            self._display_formulas(cards)

            log.success("Formula generation complete")

        except Exception as e:
            log.error(f"Error generating formulas: {e}")
            messagebox.showerror("Error", f"Failed to generate formulas:\n{str(e)}")
            self.summary_label.config(text="Error generating formulas")
        finally:
            self.btn_generate.config(state="normal")

# UI/review_and_rules.py — updated _display_formulas method

    def _display_formulas(self, cards):
        """Display template cards in the treeview"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        for card in cards:
            match_key = card.get("match_key", "UNKNOWN")
            match_type = card.get("match_type", "none")
            invoice_count = card.get("invoice_count", 0)
            total_ttc = card.get("total_ttc", 0)
            sample_client = card.get("sample_client", "")
            tva_rates = card.get("tva_rates", [])
            use_cash = card.get("use_cash", False)
            use_timbre = card.get("use_timbre", False)
            compte_client = card.get("compte_client", "")
            template_lines = card.get("template_lines", [])

            # Build parent row text
            rates_str = "+".join(f"{int(r)}%" for r in tva_rates) if tva_rates else "N/A"
            flags = []
            if use_cash:
                flags.append("CASH")
            if use_timbre:
                flags.append("TIMBRE")
            flags_str = " | ".join(flags) if flags else ""

            parent_text = (
                f"[{match_type.upper()}] {match_key} — "
                f"{invoice_count} invoices | TTC: {total_ttc:,.3f} | "
                f"TVA: {rates_str}"
            )
            if flags_str:
                parent_text += f" | {flags_str}"

            parent_id = self.tree.insert(
                "", "end",
                text=parent_text,
                values=(
                    match_key,
                    "",
                    compte_client,
                    f"Template: {sample_client[:40]}",
                    "",
                    "",
                    f"{len(template_lines)} lines"
                ),
                open=True
            )

            # Child rows: template formula lines
            for i, line in enumerate(template_lines, start=1):
                debit_str = f"{line['debit']:,.3f}" if line.get("debit", 0) > 0 else ""
                credit_str = f"{line['credit']:,.3f}" if line.get("credit", 0) > 0 else ""

                self.tree.insert(
                    parent_id, "end",
                    text="",
                    values=(
                        "",
                        i,
                        line.get("account", ""),
                        line.get("label", ""),
                        debit_str,
                        credit_str,
                        line.get("step", "")
                    )
                )
        log.info(f"Successfully displayed {len(cards)} formula cards in treeview")

    def _clear_formulas(self):
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)

            self.summary_label.config(text="No formulas generated yet")
            self.state["formula_cards"] = []
            log.info("Formulas cleared")
        except Exception as e:
            log.error(f"Error clearing formulas: {e}")
            