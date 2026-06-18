# UI/Execution_Tab.py
import tkinter as tk
from tkinter import ttk, scrolledtext
from Modules.CDP_Setting import CDPManager
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
        """
        This is where you integrate your Moduls/Session.py and Models/
        """
        cdp_manager = CDPManager(self.state["config"]["cdp_settings"])
        browser, page = cdp_manager.get_browser_and_page()
        
        try:
            total_entries = len(self.state["parsed_entries"])
            self._append_log(f"Found {total_entries} lines to process.", "INFO")
            
            # MOCK LOOP FOR DEMONSTRATION
            for i in range(total_entries):
                if not self.state["is_running"]:
                    self._append_log("Execution cancelled by user.", "ERROR")
                    break
                    
                entry = self.state["parsed_entries"][i]
                self._append_log(f"Processing {entry['ref']} | {entry['account']} | {entry['label']}", "NETWORK")
                
                # Simulate Playwright work
                import time
                time.sleep(0.2) 
                
                # Update Progress Bar safely
                progress_val = ((i + 1) / total_entries) * 100
                self.root.after(0, self._update_progress, progress_val)

            self._append_log("✅ Automation completed successfully!", "SUCCESS")
            
        except Exception as e:
            self._append_log(f"❌ Fatal Error: {str(e)}", "ERROR")
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
        