# UI/PWA_Tab.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import asyncio
import threading
from Modules.CDP_Setting import CDPManager
from Debug.Logger import ColorLogger as log


class PWATab:
    def __init__(self, parent, shared_state, root):
        self.frame = ttk.Frame(parent)
        self.state = shared_state
        self.root = root  # Store the root window
        self.cdp_manager = None
        self.browser = None
        self.page = None
        self._build_ui()

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
                                         values=["Chrome", "Edge"], 
                                         state="readonly", width=25)
        self.browser_type.set("Chrome")
        self.browser_type.grid(row=0, column=1, sticky="w", padx=10, pady=5)

        # Executable path
        ttk.Label(settings_frame, text="Executable Path:").grid(row=1, column=0, sticky="w", pady=5)
        path_frame = ttk.Frame(settings_frame)
        path_frame.grid(row=1, column=1, sticky="ew", padx=10, pady=5)
        self.exec_path = tk.StringVar()
        ttk.Entry(path_frame, textvariable=self.exec_path, width=40).pack(side="left", fill="x", expand=True)
        ttk.Button(path_frame, text="Browse", command=self._browse_browser).pack(side="left", padx=5)

        # Launch mode
        ttk.Label(settings_frame, text="Launch Mode:").grid(row=2, column=0, sticky="w", pady=5)
        self.mode_var = tk.StringVar()
        mode_combo = ttk.Combobox(settings_frame, 
                                  values=[
                                      "Standard Launch (Fresh session)",
                                      "Persistent Profile (Keep Login)",
                                      "Connect to Existing CDP",
                                  ], 
                                  state="readonly", width=35)
        mode_combo.set("Persistent Profile (Keep Login)")
        mode_combo.grid(row=2, column=1, sticky="w", padx=10, pady=5)

        # CDP Port
        ttk.Label(settings_frame, text="CDP Port:").grid(row=3, column=0, sticky="w", pady=5)
        self.cdp_port = ttk.Entry(settings_frame, width=10)
        self.cdp_port.insert(0, "9222")
        self.cdp_port.grid(row=3, column=1, sticky="w", padx=10, pady=5)

        # ── SECTION 2: Browser Control ──
        control_frame = ttk.LabelFrame(self.frame, text="2. Browser Control", padding=10)
        control_frame.pack(fill="x", padx=20, pady=10)

        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill="x")

        self.btn_launch = ttk.Button(btn_frame, text="🚀 Launch Browser", 
                                     command=self._launch_browser)
        self.btn_launch.pack(side="left", padx=5)

        self.btn_connect = ttk.Button(btn_frame, text="🔌 Connect", 
                                      command=self._connect_browser, state="disabled")
        self.btn_connect.pack(side="left", padx=5)

        self.btn_disconnect = ttk.Button(btn_frame, text="❌ Disconnect", 
                                         command=self._disconnect_browser, state="disabled")
        self.btn_disconnect.pack(side="left", padx=5)

        self.status_label = ttk.Label(control_frame, text="Status: Not launched", 
                                      foreground="gray")
        self.status_label.pack(anchor="w", pady=5)

        # ── SECTION 3: Activity Log ──
        log_frame = ttk.LabelFrame(self.frame, text="3. Activity Log", padding=10)
        log_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.log_text = tk.Text(log_frame, height=10, wrap=tk.WORD, 
                                font=("Consolas", 9), bg="#1e1e1e", fg="#d4d4d4")
        self.log_text.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def _browse_browser(self):
        path = filedialog.askopenfilename(
            title="Select Browser Executable",
            filetypes=[("Executables", "*.exe"), ("All Files", "*.*")]
        )
        if path:
            self.exec_path.set(path)

    def _log(self, message, level="INFO"):
        """Log message to the log text widget."""
        self.root.after(0, self._insert_log, message, level)

    def _insert_log(self, message, level):
        """Insert log message into text widget."""
        self.log_text.insert(tk.END, f"[{level}] {message}\n")
        self.log_text.see(tk.END)

    def _get_settings(self) -> dict:
        """Get current settings as dict."""
        return {
            "browser_type": self.browser_type.get(),
            "executable_path": self.exec_path.get(),
            "mode": self.mode_var.get(),
            "cdp_port": int(self.cdp_port.get() or 9222),
            "profile_dir": "./axeane_browser_profile",
        }

    def _launch_browser(self):
        """Launch the browser in a background thread."""
        self.btn_launch.config(state="disabled")
        self.status_label.config(text="Status: Launching...", foreground="orange")
        self._log("Launching browser...", "INFO")

        def _launch():
            try:
                settings = self._get_settings()
                self.cdp_manager = CDPManager(settings)
                
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                success = loop.run_until_complete(self.cdp_manager.launch_browser())
                
                if success:
                    self.root.after(0, self._on_launch_success)
                else:
                    self.root.after(0, self._on_launch_failed)
                    
            except Exception as e:
                log.error(f"Launch error: {e}")
                self.root.after(0, self._on_launch_failed)

        threading.Thread(target=_launch, daemon=True).start()

    def _on_launch_success(self):
        """Called when browser launches successfully."""
        self.btn_launch.config(state="disabled")
        self.btn_connect.config(state="normal")
        self.status_label.config(text="Status: Browser launched - Click Connect", foreground="green")
        self._log("Browser launched successfully", "SUCCESS")

    def _on_launch_failed(self):
        """Called when browser launch fails."""
        self.btn_launch.config(state="normal")
        self.status_label.config(text="Status: Launch failed", foreground="red")
        self._log("Browser launch failed", "ERROR")

    def _connect_browser(self):
        """Connect to the launched browser."""
        self.btn_connect.config(state="disabled")
        self.status_label.config(text="Status: Connecting...", foreground="orange")
        self._log("Connecting to browser...", "INFO")

        def _connect():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                self.browser, self.page = loop.run_until_complete(
                    self.cdp_manager.connect_to_browser()
                )
                
                self.root.after(0, self._on_connect_success)
                
            except Exception as e:
                log.error(f"Connection error: {e}")
                self.root.after(0, self._on_connect_failed)

        threading.Thread(target=_connect, daemon=True).start()

    def _on_connect_success(self):
        """Called when connection succeeds."""
        self.btn_connect.config(state="disabled")
        self.btn_disconnect.config(state="normal")
        self.status_label.config(text="Status: Connected", foreground="green")
        self._log("Connected to browser successfully", "SUCCESS")
        
        # Store in shared state
        self.state["browser"] = self.browser
        self.state["page"] = self.page

    def _on_connect_failed(self):
        """Called when connection fails."""
        self.btn_connect.config(state="normal")
        self.status_label.config(text="Status: Connection failed", foreground="red")
        self._log("Connection failed", "ERROR")

    def _disconnect_browser(self):
        """Disconnect from browser."""
        self.btn_disconnect.config(state="disabled")
        self.status_label.config(text="Status: Disconnecting...", foreground="orange")
        self._log("Disconnecting...", "INFO")

        def _disconnect():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                loop.run_until_complete(self.cdp_manager.cleanup())
                
                self.root.after(0, self._on_disconnect_success)
                
            except Exception as e:
                log.error(f"Disconnect error: {e}")
                self.root.after(0, self._on_disconnect_success)

        threading.Thread(target=_disconnect, daemon=True).start()

    def _on_disconnect_success(self):
        """Called when disconnect completes."""
        self.btn_launch.config(state="normal")
        self.btn_connect.config(state="disabled")
        self.btn_disconnect.config(state="disabled")
        self.status_label.config(text="Status: Disconnected", foreground="gray")
        self._log("Disconnected from browser", "INFO")
        
        # Clear from shared state
        self.state.pop("browser", None)
        self.state.pop("page", None)
        self.cdp_manager = None
        self.browser = None
        self.page = None
        