# UI/review_and_rules.py
import tkinter as tk
from tkinter import ttk, messagebox
from Modules.FormulaEngine import FormulaEngine
from Debug.Logger import ColorLogger as log


class ReviewAndRulesTab:
    """
    Displays template cards showing how formulas are structured per client profile.
    """

    def __init__(self, parent, shared_state):
        self.frame = ttk.Frame(parent)
        self.state = shared_state
        self.engine = FormulaEngine()
        self._build_ui()

    def _build_ui(self):
        # Title
        title = ttk.Label(self.frame, text="Template Formulas by Client Profile", 
                         font=("Segoe UI", 14, "bold"))
        title.pack(pady=10, padx=20, anchor="w")

        info_label = ttk.Label(self.frame, 
                              text="Each card represents a client profile. Expand to see the formula structure.",
                              foreground="gray")
        info_label.pack(padx=20, anchor="w")

        # Control Panel
        ctrl_frame = ttk.Frame(self.frame)
        ctrl_frame.pack(fill="x", padx=20, pady=10)

        self.btn_generate = ttk.Button(ctrl_frame, text="🔧 Generate Templates", 
                                       command=self._generate_templates)
        self.btn_generate.pack(side="left", padx=5)

        self.btn_clear = ttk.Button(ctrl_frame, text="🗑️ Clear", 
                                   command=self._clear_templates)
        self.btn_clear.pack(side="left", padx=5)

        # Summary Panel
        self.summary_frame = ttk.LabelFrame(self.frame, text="Summary", padding=10)
        self.summary_frame.pack(fill="x", padx=20, pady=10)

        self.summary_label = ttk.Label(self.summary_frame, 
                                      text="No templates generated yet",
                                      font=("Segoe UI", 10))
        self.summary_label.pack(anchor="w")

        # Treeview for template cards
        display_frame = ttk.LabelFrame(self.frame, text="Template Cards", padding=10)
        display_frame.pack(fill="both", expand=True, padx=20, pady=10)

        columns = ("match_type", "invoice_count", "total_ttc", "tva_rates", "flags")
        self.tree = ttk.Treeview(display_frame, columns=columns, show="tree headings", height=15)

        # Define Headings
        self.tree.heading("#0", text="Profile Name")
        self.tree.heading("match_type", text="Type")
        self.tree.heading("invoice_count", text="Invoices")
        self.tree.heading("total_ttc", text="Total TTC")
        self.tree.heading("tva_rates", text="TVA Rates")
        self.tree.heading("flags", text="Flags")

        # Define Column Widths
        self.tree.column("#0", width=200)
        self.tree.column("match_type", width=80, anchor="center")
        self.tree.column("invoice_count", width=80, anchor="center")
        self.tree.column("total_ttc", width=120, anchor="e")
        self.tree.column("tva_rates", width=100, anchor="center")
        self.tree.column("flags", width=150)

        # Scrollbars
        vsb = ttk.Scrollbar(display_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")

        display_frame.grid_rowconfigure(0, weight=1)
        display_frame.grid_columnconfigure(0, weight=1)

    def _generate_templates(self):
        raw_data = self.state.get("raw_data", [])

        if not raw_data:
            messagebox.showwarning("No Data", "Please import and parse a CSV file first.")
            return

        log.info(f"Generating template cards for {len(raw_data)} rows...")

        try:
            self.btn_generate.config(state="disabled")
            self.summary_label.config(text="Generating templates...")
            self.frame.update_idletasks()

            # Generate template cards
            cards = self.engine.build_template_cards(raw_data)
            self.state["template_cards"] = cards

            # Update summary
            total_invoices = sum(c["invoice_count"] for c in cards)
            summary_text = (
                f"✅ Generated {len(cards)} template profiles\n"
                f"📊 Total invoices covered: {total_invoices}\n"
            )
            self.summary_label.config(text=summary_text)

            # Display templates
            self._display_templates(cards)

            log.success("Template generation complete")

        except Exception as e:
            log.error(f"Error generating templates: {e}")
            messagebox.showerror("Error", f"Failed to generate templates:\n{str(e)}")
            self.summary_label.config(text="Error generating templates")
        finally:
            self.btn_generate.config(state="normal")

    def _display_templates(self, cards):
        """Display template cards with formula lines as children"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        for card in cards:
            try:
                # Build flags string
                flags = []
                if card.get("use_cash"):
                    flags.append("💵 CASH")
                if card.get("use_timbre"):
                    flags.append("📜 TIMBRE")
                flags_str = " | ".join(flags) if flags else "-"

                # Build TVA rates string
                tva_rates = card.get("tva_rates", [])
                tva_str = "+".join(f"{int(r)}%" for r in tva_rates) if tva_rates else "N/A"

                # Parent row (template card)
                parent_id = self.tree.insert(
                    "", "end",
                    text=card.get("match_key", "UNKNOWN"),
                    values=(
                        card.get("match_type", "unknown").upper(),
                        card.get("invoice_count", 0),
                        f"{card.get('total_ttc', 0):,.3f}",
                        tva_str,
                        flags_str
                    ),
                    open=True  # Expand by default
                )

                # Child rows (formula lines)
                for i, line in enumerate(card.get("formula_lines", []), start=1):
                    debit_str = f"{line.get('debit', 0):,.3f}" if line.get("debit", 0) > 0 else ""
                    credit_str = f"{line.get('credit', 0):,.3f}" if line.get("credit", 0) > 0 else ""

                    self.tree.insert(
                        parent_id, "end",
                        text=f"  {i}. {line.get('step', '')}",
                        values=(
                            "",
                            "",
                            "",
                            f"{line.get('account', '')} | {line.get('label', '')}",
                            f"D:{debit_str} C:{credit_str}" if debit_str or credit_str else ""
                        )
                    )

            except Exception as e:
                log.warn(f"Error adding template card to treeview: {e}")
                continue

        log.info(f"Displayed {len(cards)} template cards in treeview")

    def _clear_templates(self):
        """Clear all templates"""
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)

            self.summary_label.config(text="No templates generated yet")
            self.state["template_cards"] = []
            log.info("Templates cleared")
        except Exception as e:
            log.error(f"Error clearing templates: {e}")
            