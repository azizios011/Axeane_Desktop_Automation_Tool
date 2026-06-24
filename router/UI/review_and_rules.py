# UI/review_and_rules.py
import tkinter as tk
from tkinter import ttk, messagebox
from Modules.FormulaEngine import FormulaEngine
from Debug.Logger import ColorLogger as log


class FormulaCard(tk.Frame):
    """Custom card widget for displaying formula templates"""
    
    def __init__(self, parent, card_data, **kwargs):
        super().__init__(parent, **kwargs)
        self.card_data = card_data
        self._build_card()
    
    def _build_card(self):
        match_type = self.card_data.get("match_type", "default")
        match_key = self.card_data.get("match_key", "UNKNOWN")
        invoice_count = self.card_data.get("invoice_count", 0)
        total_ttc = self.card_data.get("total_ttc", 0)
        tva_rates = self.card_data.get("tva_rates", [])
        use_cash = self.card_data.get("use_cash", False)
        use_timbre = self.card_data.get("use_timbre", False)
        formula_lines = self.card_data.get("formula_lines", [])
        
        # Card colors based on match type
        if match_type == "specific":
            header_bg = "#2E7D32"  # Green
            header_fg = "#FFFFFF"
            card_bg = "#E8F5E9"
            badge_bg = "#4CAF50"
        else:  # default
            header_bg = "#E65100"  # Orange
            header_fg = "#FFFFFF"
            card_bg = "#FFF3E0"
            badge_bg = "#FF9800"
        
        self.configure(bg=card_bg, relief="raised", bd=2, padx=10, pady=10)
        
        # Header section
        header = tk.Frame(self, bg=header_bg, padx=10, pady=8)
        header.pack(fill="x", pady=(0, 10))
        
        # Title row
        title_frame = tk.Frame(header, bg=header_bg)
        title_frame.pack(fill="x")
        
        tk.Label(
            title_frame,
            text=f"● {match_type.upper()}",
            bg=header_bg,
            fg=header_fg,
            font=("Segoe UI", 10, "bold")
        ).pack(side="left")
        
        tk.Label(
            title_frame,
            text=f"  {match_key}",
            bg=header_bg,
            fg=header_fg,
            font=("Segoe UI", 14, "bold")
        ).pack(side="left")
        
        # Invoice count badge
        tk.Label(
            title_frame,
            text=f"  {invoice_count} invoices  ",
            bg=badge_bg,
            fg="#FFFFFF",
            font=("Segoe UI", 10, "bold"),
            padx=10,
            pady=3
        ).pack(side="right")
        
        # Stats row
        stats_frame = tk.Frame(self, bg=card_bg)
        stats_frame.pack(fill="x", pady=(0, 10))
        
        # TTC
        tk.Label(
            stats_frame,
            text=f"Total TTC:",
            bg=card_bg,
            fg="#1F2937",
            font=("Segoe UI", 10, "bold")
        ).pack(side="left")
        
        tk.Label(
            stats_frame,
            text=f"  {total_ttc:,.3f} TND",
            bg=card_bg,
            fg="#1F2937",
            font=("Segoe UI", 10)
        ).pack(side="left")
        
        # TVA rates
        tva_str = "+".join(f"{int(r)}%" for r in tva_rates) if tva_rates else "N/A"
        tk.Label(
            stats_frame,
            text=f"  |  TVA: {tva_str}",
            bg=card_bg,
            fg="#64748B",
            font=("Segoe UI", 10)
        ).pack(side="left")
        
        # Flags
        flags_frame = tk.Frame(self, bg=card_bg)
        flags_frame.pack(fill="x", pady=(0, 10))
        
        if use_cash:
            tk.Label(
                flags_frame,
                text="💵 CASH",
                bg="#4CAF50",
                fg="#FFFFFF",
                font=("Segoe UI", 9, "bold"),
                padx=8,
                pady=2
            ).pack(side="left", padx=(0, 5))
        
        if use_timbre:
            tk.Label(
                flags_frame,
                text="📜 TIMBRE",
                bg="#2196F3",
                fg="#FFFFFF",
                font=("Segoe UI", 9, "bold"),
                padx=8,
                pady=2
            ).pack(side="left", padx=(0, 5))
        
        # Separator
        tk.Frame(self, bg="#CCCCCC", height=1).pack(fill="x", pady=10)
        
        # Formula lines section
        if formula_lines:
            tk.Label(
                self,
                text="Formula Lines:",
                bg=card_bg,
                fg="#1F2937",
                font=("Segoe UI", 10, "bold")
            ).pack(anchor="w", pady=(0, 5))
            
            lines_frame = tk.Frame(self, bg="#FFFFFF", relief="sunken", bd=1)
            lines_frame.pack(fill="x")
            
            for i, line in enumerate(formula_lines):
                line_frame = tk.Frame(lines_frame, bg="#FFFFFF" if i % 2 == 0 else "#F9F9F9")
                line_frame.pack(fill="x")
                
                # Step name
                tk.Label(
                    line_frame,
                    text=line.get("step", ""),
                    bg=line_frame["bg"],
                    fg="#6366F1",
                    font=("Consolas", 9),
                    width=20,
                    anchor="w",
                    padx=5,
                    pady=3
                ).pack(side="left")
                
                # Account
                tk.Label(
                    line_frame,
                    text=line.get("account", ""),
                    bg=line_frame["bg"],
                    fg="#1F2937",
                    font=("Consolas", 9, "bold"),
                    width=12,
                    anchor="w",
                    padx=5,
                    pady=3
                ).pack(side="left")
                
                # Label
                tk.Label(
                    line_frame,
                    text=line.get("label", ""),
                    bg=line_frame["bg"],
                    fg="#334155",
                    font=("Segoe UI", 9),
                    width=25,
                    anchor="w",
                    padx=5,
                    pady=3
                ).pack(side="left")
                
                # Debit/Credit
                debit = line.get("debit", 0)
                credit = line.get("credit", 0)
                
                if debit > 0:
                    tk.Label(
                        line_frame,
                        text=f"D: {debit:,.3f}",
                        bg=line_frame["bg"],
                        fg="#DC2626",
                        font=("Consolas", 9),
                        width=12,
                        anchor="e",
                        padx=5,
                        pady=3
                    ).pack(side="left")
                elif credit > 0:
                    tk.Label(
                        line_frame,
                        text=f"C: {credit:,.3f}",
                        bg=line_frame["bg"],
                        fg="#16A34A",
                        font=("Consolas", 9),
                        width=12,
                        anchor="e",
                        padx=5,
                        pady=3
                    ).pack(side="left")


class ReviewAndRulesTab:
    """Displays template cards showing how formulas are structured per client profile"""
    
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
                              text="Each card represents a client profile with its formula structure",
                              foreground="gray")
        info_label.pack(padx=20, anchor="w")
        
        # Control Panel
        ctrl_frame = ttk.Frame(self.frame)
        ctrl_frame.pack(fill="x", padx=20, pady=10)
        
        self.btn_generate = ttk.Button(ctrl_frame, text="🔧 Generate Template Cards", 
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
        
        # Scrollable canvas for cards
        canvas_frame = ttk.Frame(self.frame)
        canvas_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.canvas = tk.Canvas(canvas_frame, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        self.cards_container = tk.Frame(self.canvas, bg="#F5F5F5")
        self.canvas_window = self.canvas.create_window((0, 0), window=self.cards_container, anchor="nw")
        
        self.cards_container.bind("<Configure>", self._on_container_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
    
    def _on_container_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)
    
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
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
            
            # Generate execution formula cards
            formula_cards = self.engine.build_cards(raw_data)
            self.state["formula_cards"] = formula_cards
            
            # Update summary
            summary = self.engine.get_summary()
            summary_text = (
                f"✅ {summary['total_cards']} template profiles\n"
                f"📊 {summary['total_invoices']} invoices covered\n"
                f"💰 Total TTC: {summary['total_ttc']:,.3f} TND"
            )
            self.summary_label.config(text=summary_text)
            
            # Display cards
            self._display_cards(cards)
            
            log.success("Template generation complete")
            
        except Exception as e:
            log.error(f"Error generating templates: {e}")
            messagebox.showerror("Error", f"Failed to generate templates:\n{str(e)}")
            self.summary_label.config(text="Error generating templates")
        finally:
            self.btn_generate.config(state="normal")
    
    def _display_cards(self, cards):
        """Display template cards as visual cards"""
        # Clear existing cards
        for widget in self.cards_container.winfo_children():
            widget.destroy()
        
        # Create card for each template
        for card_data in cards:
            card = FormulaCard(self.cards_container, card_data)
            card.pack(fill="x", padx=10, pady=10)
        
        log.info(f"Displayed {len(cards)} template cards")
    
    def _clear_templates(self):
        """Clear all templates"""
        try:
            for widget in self.cards_container.winfo_children():
                widget.destroy()
            
            self.summary_label.config(text="No templates generated yet")
            self.state["template_cards"] = []
            log.info("Templates cleared")
        except Exception as e:
            log.error(f"Error clearing templates: {e}")

        