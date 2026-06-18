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

    def _display_formulas(self, cards):
        """Display all formula cards in the treeview"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        for card in cards:
            # Safely get values with fallbacks
            ref = card.get("ref", "UNKNOWN")
            sample_client = card.get("sample_client", "Unknown Client")
            match_key = card.get("match_key", "N/A")
            is_balanced = card.get("is_balanced", False)
            total_debit = card.get("total_debit", 0)
            total_credit = card.get("total_credit", 0)
            row_count = card.get("row_count", 0)
            formula_lines = card.get("formula_lines", [])

            # Parent row (Invoice header)
            balance_status = "✓" if is_balanced else "✗"
            parent_text = f"{ref} | {sample_client[:40]} | Profile: {match_key}"

            parent_id = self.tree.insert(
                "", "end",
                text=f"{parent_text} [{balance_status}]",
                values=(
                    ref,
                    "",
                    "",
                    "",
                    f"{total_debit:.3f}",
                    f"{total_credit:.3f}",
                    f"{row_count} rows"
                ),
                open=False
            )

            # Child rows (Journal entries)
            for i, line in enumerate(formula_lines):
                # Safely get row_num (generate if missing)
                row_num = line.get("row_num", i + 1)
                account = line.get("account", "")
                label = line.get("label", "")
                debit = line.get("debit", 0)
                credit = line.get("credit", 0)
                step = line.get("step", "")

                self.tree.insert(
                    parent_id, "end",
                    text="",
                    values=(
                        "",
                        row_num,
                        account,
                        label,
                        f"{debit:.3f}" if debit > 0 else "",
                        f"{credit:.3f}" if credit > 0 else "",
                        step
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
            