# UI/Execution_Tab.py
import tkinter as tk
from tkinter import ttk, scrolledtext
from Modules.CDP_Setting import CDPManager
from Modules.AxeaneOrchestrator import AxeaneOrchestrator
import threading
import asyncio

class ExecutionTab:
    def __init__(self, parent, shared_state, root):
        self.frame = ttk.Frame(parent)
        self.state = shared_state
        self.root = root # Needed to update UI from background threads
        self._build_ui()

    def _build_ui(self):
        # Top Control Bar
        ctrl_frame = ttk.Frame(self.frame)
        ctrl_frame.pack(fill="x", padx=20, pady=15)

        self.btn_start = ttk.Button(ctrl_frame, text="🚀 Start Automation", command=self._start_execution)
        self.btn_start.pack(side="left", padx=5)

        self.btn_stop = ttk.Button(ctrl_frame, text="⛔ Stop", state="disabled", command=self._stop_execution)
        self.btn_stop.pack(side="left", padx=5)

        self.progress = ttk.Progressbar(ctrl_frame, mode="determinate", length=300)
        self.progress.pack(side="right", padx=10)

        # Live Log Viewer
        log_frame = ttk.LabelFrame(self.frame, text="Live Execution Logs & Network Debug", padding=10)
        log_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, font=("Consolas", 10), bg="#1e1e1e", fg="#d4d4d4", insertbackground="white")
        self.log_text.pack(fill="both", expand=True)
        
        # Color tags for logs
        self.log_text.tag_config("INFO", foreground="#4ec9b0")
        self.log_text.tag_config("SUCCESS", foreground="#6a9955")
        self.log_text.tag_config("ERROR", foreground="#f44747")
        self.log_text.tag_config("NETWORK", foreground="#569cd6")

    def _append_log(self, message, level="INFO"):
        """Thread-safe log appending"""
        self.root.after(0, self._insert_text, f"[{level}] {message}\n", level)

    def _insert_text(self, text, tag):
        self.log_text.insert(tk.END, text, tag)
        self.log_text.see(tk.END)

    def _start_execution(self):
        if self.state["is_running"]:
            return
            
        self.state["is_running"] = True
        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")
        self.progress["value"] = 0
        
        self._append_log("Initializing Playwright Browser...", "INFO")
        
        # Run the heavy Playwright logic in a background thread
        threading.Thread(target=self._run_playwright_loop, daemon=True).start()

    def _run_playwright_loop(self):
        """The real execution loop using AxeaneOrchestrator."""
        try:
            cards = self.state.get("formula_cards", [])
            if not cards:
                self._append_log("No formula cards found. Generate formulas first!", "ERROR")
                return

            self._append_log(f"Found {len(cards)} formula cards to process.", "INFO")

            # Launch browser
            cdp_settings = self.state["config"].get("cdp_settings", {})
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            async def _run():
                cdp = CDPManager(cdp_settings)
                browser, page = await cdp.get_browser_and_page()
                try:
                    # Navigate to the writing screen if not already there
                    if "ecritureComponentModele" not in page.url:
                        self._append_log("Navigating to Saisie des écritures...", "INFO")
                        await page.goto("https://kompta.axeane.com/views/comptageneral/traitement/ecritures/ecranEcritureMainModele2.html")
                        await page.wait_for_timeout(3000)

                    # Create orchestrator
                    orchestrator = AxeaneOrchestrator(page, self.state)

                    # Progress callback
                    def on_progress(current, total, success, failed):
                        pct = (current / total) * 100
                        self.root.after(0, self._update_progress, pct)
                        self._append_log(f"[{current}/{total}] {success}✓ {failed}✗", "INFO")

                    # Run!
                    success, failed = await orchestrator.run_all(cards, on_progress)
                    self._append_log(f"🏁 Complete: {success} succeeded, {failed} failed", "SUCCESS")

                finally:
                    await cdp.cleanup(browser)

            loop.run_until_complete(_run())
            loop.close()

        except Exception as e:
            self._append_log(f"❌ Fatal: {e}", "ERROR")
        finally:
            self.root.after(0, self._reset_ui)

    def _update_progress(self, val):
        self.progress["value"] = val

    def _reset_ui(self):
        self.state["is_running"] = False
        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")

    def _stop_execution(self):
        self.state["is_running"] = False
        self._append_log("Stopping after current operation...", "ERROR")
        