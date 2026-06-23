# UI/PWA_Tab.py
import tkinter as tk
from tkinter import ttk, filedialog
import asyncio
import threading
from datetime import datetime
from Modules.CDP_Setting import CDPManager, PWA_URL, MODE_PWA_CDP, MODE_CDP_CONNECT
from Debug.Logger import ColorLogger as log


class PWATab:
    def __init__(self, parent, shared_state, root):
        self.frame       = ttk.Frame(parent)
        self.state       = shared_state
        self.root        = root
        self.cdp_manager = None
        self.browser     = None
        self.page        = None
        self._build_ui()

    # ──────────────────────────────────────────────────────────────
    # UI construction
    # ──────────────────────────────────────────────────────────────

    def _build_ui(self):
        title = ttk.Label(
            self.frame,
            text="Browser Engine — PWA / CDP",
            font=("Segoe UI", 14, "bold"),
        )
        title.pack(pady=10, padx=20, anchor="w")

        # ── SECTION 1: Connection Mode ────────────────────────────
        mode_frame = ttk.LabelFrame(self.frame, text="1. Connection Mode", padding=10)
        mode_frame.pack(fill="x", padx=20, pady=(10, 4))

        self.mode_var = tk.StringVar(value=MODE_PWA_CDP)

        rb_pwa = ttk.Radiobutton(
            mode_frame,
            text="🚀  Launch PWA (CDP)  — open Axeane as a standalone app window + auto-connect",
            variable=self.mode_var,
            value=MODE_PWA_CDP,
            command=self._on_mode_change,
        )
        rb_pwa.pack(anchor="w", pady=2)

        rb_cdp = ttk.Radiobutton(
            mode_frame,
            text="🔌  Connect to Existing CDP  — attach to a browser already running with --remote-debugging-port",
            variable=self.mode_var,
            value=MODE_CDP_CONNECT,
            command=self._on_mode_change,
        )
        rb_cdp.pack(anchor="w", pady=2)

        # ── SECTION 2: Browser Settings ───────────────────────────
        sf = ttk.LabelFrame(self.frame, text="2. Browser Settings", padding=10)
        sf.pack(fill="x", padx=20, pady=4)
        sf.columnconfigure(1, weight=1)

        # Browser type (only relevant for PWA mode)
        ttk.Label(sf, text="Browser Type:").grid(row=0, column=0, sticky="w", pady=4)
        self.browser_type = ttk.Combobox(
            sf, values=["Chrome", "Edge"], state="readonly", width=20
        )
        self.browser_type.set("Chrome")
        self.browser_type.grid(row=0, column=1, sticky="w", padx=10, pady=4)

        # PWA URL (only relevant for PWA mode)
        ttk.Label(sf, text="PWA URL:").grid(row=1, column=0, sticky="w", pady=4)
        self.pwa_url_var = tk.StringVar(value=PWA_URL)
        self.entry_pwa_url = ttk.Entry(sf, textvariable=self.pwa_url_var, width=55)
        self.entry_pwa_url.grid(row=1, column=1, sticky="ew", padx=10, pady=4)

        # Executable path (only for PWA mode)
        ttk.Label(sf, text="Executable Path:").grid(row=2, column=0, sticky="w", pady=4)
        path_frame = ttk.Frame(sf)
        path_frame.grid(row=2, column=1, sticky="ew", padx=10, pady=4)
        self.exec_path = tk.StringVar()
        self.entry_exec = ttk.Entry(path_frame, textvariable=self.exec_path, width=44)
        self.entry_exec.pack(side="left", fill="x", expand=True)
        self.btn_browse = ttk.Button(
            path_frame, text="Browse…", command=self._browse_browser
        )
        self.btn_browse.pack(side="left", padx=5)
        ttk.Label(sf, text="Leave blank to auto-detect", foreground="gray",
                  font=("Segoe UI", 8)).grid(row=3, column=1, sticky="w", padx=10)

        # Profile dir (only for PWA mode)
        ttk.Label(sf, text="Profile Directory:").grid(row=4, column=0, sticky="w", pady=4)
        self.profile_dir_var = tk.StringVar(value="./axeane_browser_profile")
        self.entry_profile = ttk.Entry(sf, textvariable=self.profile_dir_var, width=55)
        self.entry_profile.grid(row=4, column=1, sticky="ew", padx=10, pady=4)

        # CDP Port (relevant for both modes)
        ttk.Label(sf, text="CDP Debug Port:").grid(row=5, column=0, sticky="w", pady=4)
        self.cdp_port = ttk.Entry(sf, width=8)
        self.cdp_port.insert(0, "9222")
        self.cdp_port.grid(row=5, column=1, sticky="w", padx=10, pady=4)

        # ── SECTION 3: Control buttons ─────────────────────────────
        cf = ttk.LabelFrame(self.frame, text="3. Browser Control", padding=10)
        cf.pack(fill="x", padx=20, pady=4)

        btn_row = ttk.Frame(cf)
        btn_row.pack(fill="x")

        self.btn_launch = ttk.Button(
            btn_row, text="🚀 Launch PWA (CDP)", command=self._start
        )
        self.btn_launch.pack(side="left", padx=5)

        self.btn_disconnect = ttk.Button(
            btn_row, text="❌ Disconnect & Close",
            command=self._disconnect_browser, state="disabled"
        )
        self.btn_disconnect.pack(side="left", padx=5)

        self.status_label = ttk.Label(
            cf, text="Status: Not connected", foreground="gray"
        )
        self.status_label.pack(anchor="w", pady=6)

        # ── SECTION 4: Activity Log ────────────────────────────────
        lf = ttk.LabelFrame(self.frame, text="4. Activity Log", padding=10)
        lf.pack(fill="both", expand=True, padx=20, pady=10)

        self.log_text = tk.Text(
            lf, height=10, wrap=tk.WORD,
            font=("Consolas", 9), bg="#1e1e1e", fg="#d4d4d4",
            insertbackground="white",
        )
        self.log_text.pack(fill="both", expand=True, side="left")

        sb = ttk.Scrollbar(lf, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")

        # Apply initial mode state
        self._on_mode_change()

    # ──────────────────────────────────────────────────────────────
    # Mode toggle
    # ──────────────────────────────────────────────────────────────

    def _on_mode_change(self):
        """Enable/disable fields and update the launch button label based on mode."""
        is_pwa = self.mode_var.get() == MODE_PWA_CDP

        # Fields only relevant to PWA launch
        pwa_only_widgets = [
            self.browser_type,
            self.entry_pwa_url,
            self.entry_exec,
            self.btn_browse,
            self.entry_profile,
        ]
        state = "normal" if is_pwa else "disabled"
        for w in pwa_only_widgets:
            w.config(state=state)

        # Update launch button label
        if is_pwa:
            self.btn_launch.config(text="🚀 Launch PWA (CDP)")
        else:
            self.btn_launch.config(text="🔌 Connect to Existing CDP")

    # ──────────────────────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────────────────────

    def _browse_browser(self):
        path = filedialog.askopenfilename(
            title="Select Browser Executable",
            filetypes=[("Executables", "*.exe"), ("All Files", "*.*")],
        )
        if path:
            self.exec_path.set(path)

    def _log(self, message: str, level: str = "INFO"):
        """Thread-safe log append."""
        self.root.after(0, self._insert_log, message, level)

    def _insert_log(self, message: str, level: str):
        ts = datetime.now().strftime("%H:%M:%S")
        color_map = {
            "INFO":    "#d4d4d4",
            "SUCCESS": "#6a9955",
            "ERROR":   "#f44747",
            "WARNING": "#ce9178",
        }
        tag = f"tag_{level}"
        if tag not in self.log_text.tag_names():
            self.log_text.tag_config(tag, foreground=color_map.get(level, "#d4d4d4"))
        self.log_text.insert(tk.END, f"[{ts}] [{level}] {message}\n", tag)
        self.log_text.see(tk.END)

    def _get_settings(self) -> dict:
        return {
            "browser_type":    self.browser_type.get(),
            "executable_path": self.exec_path.get().strip(),
            "cdp_port":        int(self.cdp_port.get().strip() or 9222),
            "profile_dir":     self.profile_dir_var.get().strip() or "./axeane_browser_profile",
            "pwa_url":         self.pwa_url_var.get().strip() or PWA_URL,
            "mode":            self.mode_var.get(),
        }

    # ──────────────────────────────────────────────────────────────
    # Start (dispatches to correct mode)
    # ──────────────────────────────────────────────────────────────

    def _start(self):
        mode = self.mode_var.get()
        self.btn_launch.config(state="disabled")
        self.btn_disconnect.config(state="disabled")

        if mode == MODE_PWA_CDP:
            self.status_label.config(text="Status: Launching PWA…", foreground="orange")
            self._log(f"Launching {self.browser_type.get()} in PWA (CDP) mode…", "INFO")
            threading.Thread(target=self._worker_pwa_cdp, daemon=True).start()

        elif mode == MODE_CDP_CONNECT:
            self.status_label.config(text="Status: Connecting to existing CDP…", foreground="orange")
            self._log(f"Connecting to existing browser on port {self.cdp_port.get()}…", "INFO")
            threading.Thread(target=self._worker_cdp_connect, daemon=True).start()

    # ──────────────────────────────────────────────────────────────
    # Worker threads
    # ──────────────────────────────────────────────────────────────

    def _worker_pwa_cdp(self):
        """Background thread: launch browser in PWA mode + connect via CDP."""
        try:
            settings = self._get_settings()
            self._log(f"PWA URL : {settings['pwa_url']}", "INFO")
            self._log(f"Port    : {settings['cdp_port']}", "INFO")
            self._log(f"Profile : {settings['profile_dir']}", "INFO")

            self.cdp_manager = CDPManager(settings)

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self.browser, self.page = loop.run_until_complete(
                self.cdp_manager.launch_pwa_cdp()
            )
            self.root.after(0, self._on_success)

        except FileNotFoundError as e:
            self._log(str(e), "ERROR")
            self.root.after(0, self._on_failed)
        except TimeoutError as e:
            self._log(str(e), "ERROR")
            self.root.after(0, self._on_failed)
        except Exception as e:
            self._log(f"Launch error: {e}", "ERROR")
            log.error(f"PWA launch error: {e}")
            self.root.after(0, self._on_failed)

    def _worker_cdp_connect(self):
        """Background thread: connect Playwright to an existing CDP browser."""
        try:
            settings = self._get_settings()
            self.cdp_manager = CDPManager(settings)

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self.browser, self.page = loop.run_until_complete(
                self.cdp_manager.connect_cdp()
            )
            self.root.after(0, self._on_success)

        except Exception as e:
            self._log(f"Connection error: {e}", "ERROR")
            log.error(f"CDP connect error: {e}")
            self.root.after(0, self._on_failed)

    # ──────────────────────────────────────────────────────────────
    # Outcome callbacks (always run on main thread via root.after)
    # ──────────────────────────────────────────────────────────────

    def _on_success(self):
        url = (self.page.url if self.page else "—")
        self.btn_launch.config(state="disabled")
        self.btn_disconnect.config(state="normal")
        self.status_label.config(text=f"Status: ✅ Connected — {url}", foreground="green")
        self._log(f"Connected — page: {url}", "SUCCESS")

        # Expose to other tabs via shared state
        self.state["browser"] = self.browser
        self.state["page"]    = self.page

    def _on_failed(self):
        self.btn_launch.config(state="normal")
        self.btn_disconnect.config(state="disabled")
        self.status_label.config(text="Status: ❌ Failed — see log", foreground="red")

    # ──────────────────────────────────────────────────────────────
    # Disconnect
    # ──────────────────────────────────────────────────────────────

    def _disconnect_browser(self):
        self.btn_disconnect.config(state="disabled")
        self.status_label.config(text="Status: Disconnecting…", foreground="orange")
        self._log("Disconnecting…", "INFO")

        def _worker():
            try:
                if self.cdp_manager:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(self.cdp_manager.cleanup())
            except Exception as e:
                log.warning(f"Disconnect warning: {e}")
            finally:
                self.root.after(0, self._on_disconnect_done)

        threading.Thread(target=_worker, daemon=True).start()

    def _on_disconnect_done(self):
        self.btn_launch.config(state="normal")
        self.btn_disconnect.config(state="disabled")
        self.status_label.config(text="Status: Disconnected", foreground="gray")
        self._log("Browser closed and disconnected", "INFO")

        # Clear shared state
        self.state.pop("browser", None)
        self.state.pop("page", None)
        self.cdp_manager = None
        self.browser     = None
        self.page        = None