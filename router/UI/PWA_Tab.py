# UI/PWA_Tab.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from Modules.CDP_Setting import CDPManager

class PWATab:
    def __init__(self, parent, shared_state):
        self.frame = ttk.Frame(parent)
        self.state = shared_state
        self._build_ui()
        self._load_current_settings()

    def _build_ui(self):
        title = ttk.Label(self.frame, text="Browser Engine & CDP Configuration", font=("Segoe UI", 14, "bold"))
        title.pack(pady=20, padx=20, anchor="w")

        # --- 1. Browser Engine Selection ---
        engine_frame = ttk.LabelFrame(self.frame, text="1. Browser Engine & Executable", padding=15)
        engine_frame.pack(fill="x", padx=20, pady=10)

        ttk.Label(engine_frame, text="Browser Type:").grid(row=0, column=0, sticky="w", pady=5)
        self.browser_type = ttk.Combobox(engine_frame, values=["Chrome", "Edge", "Playwright Chromium"], state="readonly", width=25)
        self.browser_type.grid(row=0, column=1, sticky="w", padx=10, pady=5)
        self.browser_type.bind("<<ComboboxSelected>>", self._on_browser_change)

        ttk.Label(engine_frame, text="Executable Path:").grid(row=1, column=0, sticky="w", pady=5)
        path_frame = ttk.Frame(engine_frame)
        path_frame.grid(row=1, column=1, sticky="ew", padx=10, pady=5)
        
        self.exec_path = tk.StringVar()
        self.exec_entry = ttk.Entry(path_frame, textvariable=self.exec_path, width=40)
        self.exec_entry.pack(side="left", fill="x", expand=True)
        ttk.Button(path_frame, text="Browse", command=self._browse_browser).pack(side="left", padx=5)
        
        engine_frame.columnconfigure(1, weight=1)

        # --- 2. Launch Mode ---
        mode_frame = ttk.LabelFrame(self.frame, text="2. Launch Mode", padding=15)
        mode_frame.pack(fill="x", padx=20, pady=10)

        self.mode_var = tk.StringVar()
        modes = [
            (CDPManager.MODE_NORMAL, "Standard Launch (Fresh session)"),
            (CDPManager.MODE_PERSISTENT, "Persistent Profile (Keep Login)"),
            (CDPManager.MODE_CDP_CONNECT, "Connect to Existing CDP (Attach to logged-in browser)"),
            (CDPManager.MODE_PWA, "PWA Mode (Standalone App)")
        ]
        for i, (val, text) in enumerate(modes):
            ttk.Radiobutton(mode_frame, text=text, variable=self.mode_var, value=val).grid(row=i, column=0, sticky="w", pady=5)

        # --- 3. Mode Specific Settings ---
        config_frame = ttk.LabelFrame(self.frame, text="3. Mode Specific Settings", padding=15)
        config_frame.pack(fill="x", padx=20, pady=10)

        ttk.Label(config_frame, text="CDP Port:").grid(row=0, column=0, sticky="w", pady=5)
        self.cdp_port_entry = ttk.Entry(config_frame, width=15)
        self.cdp_port_entry.grid(row=0, column=1, sticky="w", padx=10, pady=5)

        ttk.Label(config_frame, text="Profile Dir:").grid(row=1, column=0, sticky="w", pady=5)
        self.profile_dir_entry = ttk.Entry(config_frame, width=40)
        self.profile_dir_entry.grid(row=1, column=1, sticky="w", padx=10, pady=5)

        ttk.Label(config_frame, text="PWA URL:").grid(row=2, column=0, sticky="w", pady=5)
        self.pwa_url_entry = ttk.Entry(config_frame, width=40)
        self.pwa_url_entry.grid(row=2, column=1, sticky="w", padx=10, pady=5)

        self.headless_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(config_frame, text="Run in Background (Headless)", variable=self.headless_var).grid(row=3, column=0, columnspan=2, sticky="w", pady=10)

        # --- Save Button ---
        ttk.Button(self.frame, text="💾 Save Configuration", command=self._save_settings).pack(pady=20)

    def _on_browser_change(self, event=None):
        """Auto-fills default executable paths based on selection"""
        b_type = self.browser_type.get()
        if b_type == "Chrome":
            self.exec_path.set(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
        elif b_type == "Edge":
            self.exec_path.set(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
        else:
            self.exec_path.set("") # Let Playwright handle it

    def _browse_browser(self):
        path = filedialog.askopenfilename(
            title="Select Browser Executable",
            filetypes=[("Executables", "*.exe"), ("All Files", "*.*")]
        )
        if path:
            self.exec_path.set(path)
            if "msedge" in path.lower():
                self.browser_type.set("Edge")
            elif "chrome" in path.lower():
                self.browser_type.set("Chrome")

    def _load_current_settings(self):
        settings = self.state["config"].get("cdp_settings", {})
        self.browser_type.set(settings.get("browser_type", "Chrome"))
        self.exec_path.set(settings.get("executable_path", ""))
        self.mode_var.set(settings.get("mode", CDPManager.MODE_PERSISTENT))
        self.cdp_port_entry.insert(0, settings.get("cdp_port", 9222))
        self.profile_dir_entry.insert(0, settings.get("profile_dir", "./axeane_browser_profile"))
        self.pwa_url_entry.insert(0, settings.get("pwa_url", "https://kompta.axeane.com"))
        self.headless_var.set(settings.get("headless", False))
        self._on_browser_change() # Trigger default path fill if empty

    def _save_settings(self):
        try:
            port = int(self.cdp_port_entry.get()) if self.cdp_port_entry.get() else 9222
        except ValueError:
            messagebox.showerror("Invalid Input", "CDP Port must be a valid integer.")
            return

        self.state["config"]["cdp_settings"] = {
            "browser_type": self.browser_type.get(),
            "executable_path": self.exec_path.get(),
            "mode": self.mode_var.get(),
            "cdp_port": port,
            "profile_dir": self.profile_dir_entry.get(),
            "pwa_url": self.pwa_url_entry.get(),
            "headless": self.headless_var.get()
        }
        messagebox.showinfo("Success", "Browser settings saved successfully!")
        