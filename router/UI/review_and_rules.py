# UI/review_and_rules.py
import tkinter as tk
from tkinter import ttk, messagebox
from Modules.FormulaEngine import FormulaEngine
from Debug.Logger import ColorLogger as log


class ReviewAndRulesTab:
    """
    Displays formulas as visual CARDS — one card per client group.
    Each card shows: match type, client name, row count, formula lines, balance.
    """

    # Color palette
    COLOR_SPECIFIC = "#E8F5E9"     # light green
    COLOR_DEFAULT  = "#FFF3E0"     # light orange
    COLOR_NONE     = "#FFEBEE"     # light red
    COLOR_HEADER_SPECIFIC = "#2E7D32"
    COLOR_HEADER_DEFAULT  = "#E65100"
    COLOR_HEADER_NONE     = "#C62828"

    def __init__(self, parent, shared_state):
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.state = shared_state
        self.engine = FormulaEngine()
        self.cards_container = None
        self._build_ui()

    # ------------------------------------------------------------------
    # UI scaffolding
    # ------------------------------------------------------------------
    def _build_ui(self):
        # Header
        header = ttk.Frame(self.frame)
        header.pack(fill="x", padx=20, pady=(15, 5))

        ttk.Label(header,
                  text="Formula Cards (grouped by client)",
                  font=("Segoe UI", 14, "bold")).pack(side="left")

        self.btn_generate = ttk.Button(header,
                                       text="🔧 Generate Formulas",
                                       command=self._generate)
        self.btn_generate.pack(side="right", padx=5)

        self.btn_reload_json = ttk.Button(header,
                                          text="🔄 Reload JSON",
                                          command=self._reload_json)
        self.btn_reload_json.pack(side="right", padx=5)

        # Summary bar
        self.summary_var = tk.StringVar(value="No formulas generated yet.")
        ttk.Label(self.frame,
                  textvariable=self.summary_var,
                  foreground="gray").pack(anchor="w", padx=20)

        # Scrollable canvas for cards
        canvas_frame = ttk.Frame(self.frame)
        canvas_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.canvas = tk.Canvas(canvas_frame, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(canvas_frame,
                                       orient="vertical",
                                       command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.cards_container = tk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.cards_container, anchor="nw"
        )

        self.cards_container.bind("<Configure>", self._on_container_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        # Mouse-wheel scroll
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_container_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def _reload_json(self):
        self.engine.accounts.reload()
        self.engine.rules.reload()
        messagebox.showinfo("Reloaded",
                            "JSON files reloaded. Click 'Generate' to refresh cards.")

    def _generate(self):
        rows = self.state.get("raw_data", [])
        if not rows:
            messagebox.showwarning("No Data",
                                   "Please import and parse a CSV file first.")
            return

        cards = self.engine.build_cards(rows)
        self.state["formula_cards"] = cards
        self._render_cards(cards)

        # Summary
        total_rows = sum(c["row_count"] for c in cards)
        specific = sum(1 for c in cards if c["match_type"] == "specific")
        default = sum(1 for c in cards if c["match_type"] == "default")
        unmatched = sum(1 for c in cards if c["match_type"] == "none")
        self.summary_var.set(
            f"{len(cards)} formulas  •  {total_rows} rows covered  •  "
            f"Specific: {specific}  •  Default: {default}  •  Unmatched: {unmatched}"
        )

    # ------------------------------------------------------------------
    # Card rendering
    # ------------------------------------------------------------------
    def _render_cards(self, cards):
        # Clear previous
        for w in self.cards_container.winfo_children():
            w.destroy()

        for card in cards:
            self._build_card(card)

    def _build_card(self, card):
        mt = card["match_type"]
        if mt == "specific":
            bg, header_fg = self.COLOR_SPECIFIC, self.COLOR_HEADER_SPECIFIC
            badge = "● SPECIFIC"
        elif mt == "default":
            bg, header_fg = self.COLOR_DEFAULT, self.COLOR_HEADER_DEFAULT
            badge = "● DEFAULT"
        else:
            bg, header_fg = self.COLOR_NONE, self.COLOR_HEADER_NONE
            badge = "● UNMATCHED"

        # Outer card frame
        outer = tk.Frame(self.cards_container,
                         bg=bg,
                         highlightbackground="#CCCCCC",
                         highlightthickness=1)
        outer.pack(fill="x", pady=8, padx=2)

        # ---- HEADER ----
        header = tk.Frame(outer, bg=bg)
        header.pack(fill="x", padx=12, pady=(10, 4))

        tk.Label(header,
                 text=badge,
                 bg=bg, fg=header_fg,
                 font=("Segoe UI", 9, "bold")).pack(side="left")

        tk.Label(header,
                 text=f"  Ref: {card['ref']} | {card['match_key']}",
                 bg=bg, fg="#1F2937",
                 font=("Segoe UI", 13, "bold")).pack(side="left")

        # Row count pill
        rates_str = "+".join(f"{int(r)}%" for r in card.get("tva_rates", [])) if card.get("tva_rates") else "—"
        pill = tk.Label(header,
                        text=f"  {card['row_count']} rows | TVA: {rates_str}  ",
                        bg=header_fg, fg="white",
                        font=("Segoe UI", 9, "bold"),
                        padx=8, pady=2)
        pill.pack(side="right")

        # Sample client
        tk.Label(header,
                 text=f"e.g. {card['sample_client'][:60]}",
                 bg=bg, fg="#64748B",
                 font=("Segoe UI", 9, "italic")).pack(side="right", padx=8)

        # ---- TOTALS ROW ----
        totals = tk.Frame(outer, bg=bg)
        totals.pack(fill="x", padx=12, pady=(0, 6))

        tk.Label(totals,
                 text=f"Total TTC: {card['total_ttc']:,.3f} TND",
                 bg=bg, fg="#1F2937",
                 font=("Segoe UI", 10, "bold")).pack(side="left")

        bal_color = "#16A34A" if card["is_balanced"] else "#DC2626"
        bal_text = "✓ BALANCED" if card["is_balanced"] else "✗ UNBALANCED"
        tk.Label(totals,
                 text=f"{bal_text}  (D: {card['total_debit']:,.3f} / C: {card['total_credit']:,.3f})",
                 bg=bg, fg=bal_color,
                 font=("Segoe UI", 9, "bold")).pack(side="right")

        # ---- FORMULA TABLE ----
        table = tk.Frame(outer, bg="white",
                         highlightbackground="#E5E7EB",
                         highlightthickness=1)
        table.pack(fill="x", padx=12, pady=(0, 10))

        # Header row
        cols = [("Step", 130), ("Account", 90),
                ("Label", 240), ("Debit", 100), ("Credit", 100)]
        hdr = tk.Frame(table, bg="#F3F4F6")
        hdr.pack(fill="x")
        for label, width in cols:
            tk.Label(hdr, text=label,
                     bg="#F3F4F6", fg="#475569",
                     font=("Segoe UI", 9, "bold"),
                     width=width // 7, anchor="w",
                     padx=6, pady=4).pack(side="left")

        # Data rows
        for line in card["formula_lines"]:
            row = tk.Frame(table, bg="white")
            row.pack(fill="x")

            tk.Label(row, text=line["step"],
                     bg="white", fg="#6366F1",
                     font=("Consolas", 9),
                     width=cols[0][1] // 7, anchor="w",
                     padx=6, pady=3).pack(side="left")
            tk.Label(row, text=line["account"] or "—",
                     bg="white", fg="#1F2937",
                     font=("Consolas", 9, "bold"),
                     width=cols[1][1] // 7, anchor="w",
                     padx=6, pady=3).pack(side="left")
            tk.Label(row, text=line["label"],
                     bg="white", fg="#334155",
                     font=("Segoe UI", 9),
                     width=cols[2][1] // 7, anchor="w",
                     padx=6, pady=3).pack(side="left")
            tk.Label(row,
                     text=f"{line['debit']:,.3f}" if line["debit"] else "",
                     bg="white", fg="#DC2626",
                     font=("Consolas", 9),
                     width=cols[3][1] // 7, anchor="e",
                     padx=6, pady=3).pack(side="left")
            tk.Label(row,
                     text=f"{line['credit']:,.3f}" if line["credit"] else "",
                     bg="white", fg="#16A34A",
                     font=("Consolas", 9),
                     width=cols[4][1] // 7, anchor="e",
                     padx=6, pady=3).pack(side="left")
                    