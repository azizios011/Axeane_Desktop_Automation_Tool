# UI/PWA_Tab.py
import tkinter as tk
from tkinter import ttk, messagebox
from Modules.CDP_Setting import CDPManager

class PWATab:
    def __init__(self, parent, shared_state):
        self.frame = ttk.Frame(parent)
        self.state = shared_state
        self._build_ui()
        self._load_current_settings()

    def _build_ui(self):
        title = ttk.Label(self.frame, text="Browser & CDP Configuration", font=("Segoe UI", 14, "bold"))
        title.pack(pady=20, padx=20, anchor="w")

        # --- Launch Mode Selection ---
        mode_frame = ttk.LabelFrame(self.frame, text="1. Browser Launch Mode", padding=15)
        mode_frame.pack(fill="x", padx=20, pady=10)

        self.mode_var = tk.StringVar()
        modes = [
            (CDPManager.MODE_NORMAL, "Standard Launch (Fresh session every time)"),
            (CDPManager.MODE_PERSISTENT, "Persistent Profile (Remembers Axeane login & cookies)"),
            (CDPManager.MODE_CDP_CONNECT, "Connect to Existing CDP (Attach to already logged-in Chrome)"),
            (CDPManager.MODE_PWA, "PWA Mode (Launch Axeane as a standalone desktop app)")
        ]
        
        for i, (val, text) in enumerate(modes):
            ttk.Radiobutton(mode_frame, text=text, variable=self.mode_var, value=val, command=self._on_mode_change).grid(row=i, column=0, sticky="w", pady=5)

        # --- Configuration Details ---
        config_frame = ttk.LabelFrame(self.frame, text="2. Mode Specific Settings", padding=15)
        config_frame.pack(fill="x", padx=20, pady=10)

        # CDP Port
        ttk.Label(config_frame, text="CDP Debugging Port:").grid(row=0, column=0, sticky="w", pady=5)
        self.cdp_port_entry = ttk.Entry(config_frame, width=15)
        self.cdp_port_entry.grid(row=0, column=1, sticky="w", padx=10, pady=5)
        self.cdp_hint = ttk.Label(config_frame, text="(Run Chrome with --remote-debugging-port=9222)", foreground="gray")
        self.cdp_hint.grid(row=0, column=2, sticky="w", padx=10)

        # Profile Dir
        ttk.Label(config_frame, text="Profile Directory:").grid(row=1, column=0, sticky="w", pady=5)
        self.profile_dir_entry = ttk.Entry(config_frame, width=40)
        self.profile_dir_entry.grid(row=1, column=1, columnspan=2, sticky="w", padx=10, pady=5)

        # PWA URL
        ttk.Label(config_frame, text="PWA Target URL:").grid(row=2, column=0, sticky="w", pady=5)
        self.pwa_url_entry = ttk.Entry(config_frame, width=40)
        self.pwa_url_entry.grid(row=2, column=1, columnspan=2, sticky="w", padx=10, pady=5)

        # Headless toggle
        self.headless_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(config_frame, text="Run in Background (Headless)", variable=self.headless_var).grid(row=3, column=0, columnspan=3, sticky="w", pady=10)

        # --- Save Button ---
        btn_save = ttk.Button(self.frame, text="💾 Save CDP Settings", command=self._save_settings)
        btn_save.pack(pady=20)

        # --- Info Box ---
        info_frame = ttk.LabelFrame(self.frame, text="💡 How to use 'Connect to Existing CDP'", padding=10)
        info_frame.pack(fill="x", padx=20, pady=10)
        info_text = (
            "1. Close all Chrome windows.\n"
            "2. Open Command Prompt / Terminal and run:\n"
            "   chrome.exe --remote-debugging-port=9222\n"
            "3. Log into Axeane Kompta manually in that Chrome window.\n"
            "4. Select 'Connect to Existing CDP' here and click Start in Execution Tab."
        )
        ttk.Label(info_frame, text=info_text, justify="left", font=("Consolas", 9)).pack(anchor="w")

    def _on_mode_change(self):
        """Enables/Disables inputs based on the selected mode."""
        mode = self.mode_var.get()
        state_cdp = "normal" if mode == CDPManager.MODE_CDP_CONNECT else "disabled"
        state_prof = "normal" if mode == CDPManager.MODE_PERSISTENT else "disabled"
        state_pwa = "normal" if mode == CDPManager.MODE_PWA else "disabled"
        state_headless = "normal" if mode != CDPManager.MODE_CDP_CONNECT else "disabled"

        self.cdp_port_entry.config(state=state_cdp)
        self.cdp_hint.config(foreground="gray" if state_cdp == "normal" else "lightgray")
        
        self.profile_dir_entry.config(state=state_prof)
        self.pwa_url_entry.config(state=state_pwa)
        
        # Cannot run headless if connecting to existing UI
        if state_headless == "disabled":
            self.headless_var.set(False)

    def _load_current_settings(self):
        """Loads settings from shared_state into the UI."""
        settings = self.state["config"].get("cdp_settings", {})
        self.mode_var.set(settings.get("mode", CDPManager.MODE_NORMAL))
        self.cdp_port_entry.insert(0, settings.get("cdp_port", 9222))
        self.profile_dir_entry.insert(0, settings.get("profile_dir", "./axeane_browser_profile"))
        self.pwa_url_entry.insert(0, settings.get("pwa_url", "https://kompta.axeane.com"))
        self.headless_var.set(settings.get("headless", False))
        self._on_mode_change() # Trigger UI state update

    def _save_settings(self):
        """Saves UI inputs back to shared_state."""
        try:
            port = int(self.cdp_port_entry.get()) if self.cdp_port_entry.get() else 9222
        except ValueError:
            messagebox.showerror("Invalid Input", "CDP Port must be a valid integer.")
            return

        self.state["config"]["cdp_settings"] = {
            "mode": self.mode_var.get(),
            "cdp_port": port,
            "profile_dir": self.profile_dir_entry.get(),
            "pwa_url": self.pwa_url_entry.get(),
            "headless": self.headless_var.get()
        }
        messagebox.showinfo("Success", "CDP Settings saved successfully!\nThey will be applied on the next Execution run.")