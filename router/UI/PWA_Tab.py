# UI/PWA_Tab.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import asyncio
import threading
from datetime import datetime
from Modules.CDP_Setting import CDPManager
from Function.FormFiller import AxeaneFormFiller
from Debug.Logger import ColorLogger as log


class PWATab:
    def __init__(self, parent, shared_state, root=None):
        self.frame = ttk.Frame(parent)
        self.state = shared_state
        self.root = root or parent.winfo_toplevel()
        self.browser = None
        self.page = None
        self.filler = None
        self._build_ui()
        self._load_current_settings()

    def _build_ui(self):
        title = ttk.Label(self.frame, text="Browser Engine & Real-Time Control", 
                         font=("Segoe UI", 14, "bold"))
        title.pack(pady=10, padx=20, anchor="w")

        # ── SECTION 1: Browser Settings ──
        settings_frame = ttk.LabelFrame(self.frame, text="1. Browser Settings", padding=10)
        settings_frame.pack(fill="x", padx=20, pady=10)

        # Browser type
        ttk.Label(settings_frame, text="Browser Type:").grid(row=0, column=0, sticky="w", pady=5)
        self.browser_type = ttk.Combobox(settings_frame, 
                                         values=["Chrome", "Edge", "Playwright Chromium"], 
                                         state="readonly", width=25)
        self.browser_type.grid(row=0, column=1, sticky="w", padx=10, pady=5)

        # Launch mode
        ttk.Label(settings_frame, text="Launch Mode:").grid(row=1, column=0, sticky="w", pady=5)
        modes = [
            ("Standard Launch (Fresh session)", "Standard"),
            ("Persistent Profile (Keep Login)", "Persistent"),
            ("Connect to Existing CDP", "CDP"),
            ("PWA Mode (Standalone)", "PWA"),
        ]
        mode_combo = ttk.Combobox(settings_frame, 
                                  values=[m[0] for m in modes], 
                                  state="readonly", width=35)
        mode_combo.grid(row=1, column=1, sticky="w", padx=10, pady=5)
        self.mode_var = mode_combo

        # CDP Port
        ttk.Label(settings_frame, text="CDP Port:").grid(row=2, column=0, sticky="w", pady=5)
        self.cdp_port = ttk.Entry(settings_frame, width=10)
        self.cdp_port.insert(0, "9222")
        self.cdp_port.grid(row=2, column=1, sticky="w", padx=10, pady=5)

        # ── SECTION 2: Connection Control ──
        conn_frame = ttk.LabelFrame(self.frame, text="2. Connection Control", padding=10)
        conn_frame.pack(fill="x", padx=20, pady=10)

        btn_frame = ttk.Frame(conn_frame)
        btn_frame.pack(fill="x")

        self.btn_connect = ttk.Button(btn_frame, text="🔌 Connect Browser", 
                                      command=self._connect_browser)
        self.btn_connect.pack(side="left", padx=5)

        self.btn_test = ttk.Button(btn_frame, text="🧪 Test Connection", 
                                   command=self._test_connection, state="disabled")
        self.btn_test.pack(side="left", padx=5)

        self.btn_disconnect = ttk.Button(btn_frame, text="❌ Disconnect", 
                                         command=self._disconnect_browser, state="disabled")
        self.btn_disconnect.pack(side="left", padx=5)

        # Status display
        self.status_label = ttk.Label(conn_frame, text="Status: Not connected", 
                                      foreground="gray")
        self.status_label.pack(anchor="w", pady=5)

        # ── SECTION 3: Real-Time Navigation ──
        nav_frame = ttk.LabelFrame(self.frame, text="3. Real-Time Navigation", padding=10)
        nav_frame.pack(fill="x", padx=20, pady=10)

        nav_btn_frame = ttk.Frame(nav_frame)
        nav_btn_frame.pack(fill="x")

        self.btn_navigate_saisie = ttk.Button(nav_btn_frame, text="📝 Go to Saisie des écritures", 
                                               command=self._navigate_to_saisie, state="disabled")
        self.btn_navigate_saisie.pack(side="left", padx=5)

        self.btn_reset_form = ttk.Button(nav_btn_frame, text="🔄 Reset Form", 
                                         command=self._reset_form, state="disabled")
        self.btn_reset_form.pack(side="left", padx=5)

        # ── SECTION 4: Test Filling ──
        test_frame = ttk.LabelFrame(self.frame, text="4. Test Form Filling", padding=10)
        test_frame.pack(fill="x", padx=20, pady=10)

        test_btn_frame = ttk.Frame(test_frame)
        test_btn_frame.pack(fill="x")

        self.btn_fill_test = ttk.Button(test_btn_frame, text="🧪 Fill Test Invoice", 
                                        command=self._fill_test_invoice, state="disabled")
        self.btn_fill_test.pack(side="left", padx=5)

        self.btn_fill_selected = ttk.Button(test_btn_frame, text="📋 Fill Selected Invoice", 
                                            command=self._fill_selected_invoice, state="disabled")
        self.btn_fill_selected.pack(side="left", padx=5)

        # ── Log Output ──
        log_frame = ttk.LabelFrame(self.frame, text="5. Activity Log", padding=10)
        log_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.log_text = tk.Text(log_frame, height=10, wrap=tk.WORD, 
                                font=("Consolas", 9), bg="#1e1e1e", fg="#d4d4d4")
        self.log_text.pack(fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def _load_current_settings(self):
        """Load settings from shared_state."""
        settings = self.state.get("config", {}).get("cdp_settings", {})
        self.browser_type.set(settings.get("browser_type", "Chrome"))
        self.mode_var.set(settings.get("mode", "Persistent Profile (Keep Login)"))
        self.cdp_port.delete(0, tk.END)
        self.cdp_port.insert(0, str(settings.get("cdp_port", 9222)))

    def _log(self, message, level="INFO"):
        """Log message to the log text widget."""
        self.root.after(0, self._insert_log, message, level)

    def _insert_log(self, message, level):
        """Insert log message into text widget."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] [{level}] {message}\n")
        self.log_text.see(tk.END)

    # ──────────────────────────────────────────────
    # BROWSER CONNECTION
    # ──────────────────────────────────────────────
    def _connect_browser(self):
        """Connect to browser in a background thread."""
        self.btn_connect.config(state="disabled")
        self.status_label.config(text="Status: Connecting...", foreground="orange")
        self._log("Connecting to browser...", "INFO")

        def _connect():
            try:
                # Get settings
                settings = {
                    "browser_type": self.browser_type.get(),
                    "mode": self.mode_var.get(),
                    "cdp_port": int(self.cdp_port.get()),
                }
                self.state["config"]["cdp_settings"] = settings

                # Launch browser
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                cdp = CDPManager(settings)
                self.browser, self.page = loop.run_until_complete(cdp.get_browser_and_page())
                self.filler = AxeaneFormFiller(self.page)

                # Update UI
                self.root.after(0, self._on_connected)
            except Exception as e:
                self.root.after(0, lambda: self._on_connection_failed(str(e)))

        threading.Thread(target=_connect, daemon=True).start()

    def _on_connected(self):
        """Called when browser is connected."""
        self.btn_connect.config(state="disabled")
        self.btn_test.config(state="normal")
        self.btn_disconnect.config(state="normal")
        self.btn_navigate_saisie.config(state="normal")
        self.btn_fill_test.config(state="normal")
        self.btn_fill_selected.config(state="normal")
        self.status_label.config(text="Status: Connected", foreground="green")
        self._log("Browser connected successfully", "SUCCESS")

    def _on_connection_failed(self, error):
        """Called when connection fails."""
        self.btn_connect.config(state="normal")
        self.status_label.config(text="Status: Connection failed", foreground="red")
        self._log(f"Connection failed: {error}", "ERROR")

    def _disconnect_browser(self):
        """Disconnect from browser."""
        try:
            if self.browser:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.browser.close())
                self.browser = None
                self.page = None
                self.filler = None

            self.btn_connect.config(state="normal")
            self.btn_test.config(state="disabled")
            self.btn_disconnect.config(state="disabled")
            self.btn_navigate_saisie.config(state="disabled")
            self.btn_fill_test.config(state="disabled")
            self.btn_fill_selected.config(state="disabled")
            self.status_label.config(text="Status: Disconnected", foreground="gray")
            self._log("Browser disconnected", "INFO")
        except Exception as e:
            self._log(f"Disconnect error: {e}", "ERROR")

    # ──────────────────────────────────────────────
    # REAL-TIME ACTIONS
    # ──────────────────────────────────────────────
    def _test_connection(self):
        """Test connection to Axeane."""
        if not self.filler:
            self._log("Not connected", "ERROR")
            return

        def _test():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success, url = loop.run_until_complete(self.filler.test_connection())
            if success:
                self._log(f"Connected to: {url}", "SUCCESS")
            else:
                self._log(f"Not on Axeane: {url}", "WARNING")

        threading.Thread(target=_test, daemon=True).start()

    def _navigate_to_saisie(self):
        """Navigate to Saisie des écritures."""
        if not self.filler:
            self._log("Not connected", "ERROR")
            return

        def _navigate():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self.filler.navigate_to_saisie())
                self._log("Navigated to Saisie des écritures", "SUCCESS")
            except Exception as e:
                self._log(f"Navigation failed: {e}", "ERROR")

        threading.Thread(target=_navigate, daemon=True).start()

    def _reset_form(self):
        """Reset the current form."""
        if not self.filler:
            self._log("Not connected", "ERROR")
            return

        def _reset():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self.filler.reset_form())
                self._log("Form reset", "SUCCESS")
            except Exception as e:
                self._log(f"Reset failed: {e}", "ERROR")

        threading.Thread(target=_reset, daemon=True).start()

    def _fill_test_invoice(self):
        """Fill a test invoice for demonstration."""
        if not self.filler:
            self._log("Not connected", "ERROR")
            return

        def _fill():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                # Test invoice data
                test_data = {
                    "header": {
                        "journal": "VT",
                        "mois": "Mars 2026",
                        "ref": "TEST001",
                        "libelle": "TEST CLIENT",
                        "date": "15/03/2026",
                    },
                    "lines": [
                        {"account": "411000", "label": "TEST CLIENT", "debit": 1000.0, "credit": 0},
                        {"account": "436719", "label": "TVA 19%", "debit": 0, "credit": 159.66},
                        {"account": "707019", "label": "Revenue 19%", "debit": 0, "credit": 840.34},
                    ],
                }

                loop.run_until_complete(self.filler.fill_invoice(
                    header_data=test_data["header"],
                    formula_lines=test_data["lines"],
                ))
                self._log("Test invoice filled (not saved)", "SUCCESS")
            except Exception as e:
                self._log(f"Fill failed: {e}", "ERROR")

        threading.Thread(target=_fill, daemon=True).start()

    def _fill_selected_invoice(self):
        """Fill the selected invoice from the formula cards."""
        if not self.filler:
            self._log("Not connected", "ERROR")
            return

        # Get selected card from shared_state
        # This would need to be connected to the Table_Tab selection
        self._log("Fill selected invoice - not yet implemented", "WARNING")
        