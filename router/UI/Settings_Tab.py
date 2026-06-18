# UI/Settings_Tab.py
import tkinter as tk
from tkinter import ttk

class SettingsTab:
    def __init__(self, parent, shared_state):
        self.frame = ttk.Frame(parent)
        self.state = shared_state
        self._build_ui()

    def _build_ui(self):
        # Title
        title = ttk.Label(self.frame, text="Axeane Context & Authentication", font=("Segoe UI", 14, "bold"))
        title.pack(pady=20, padx=20, anchor="w")

        # Frame for inputs
        form_frame = ttk.LabelFrame(self.frame, text="Login Credentials", padding=20)
        form_frame.pack(fill="x", padx=20, pady=10)

        ttk.Label(form_frame, text="Username:").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_user = ttk.Entry(form_frame, width=30)
        self.entry_user.insert(0, self.state["config"]["username"])
        self.entry_user.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(form_frame, text="Password:").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_pwd = ttk.Entry(form_frame, width=30, show="*")
        self.entry_pwd.grid(row=1, column=1, padx=10, pady=5)

        # Frame for Context
        ctx_frame = ttk.LabelFrame(self.frame, text="Accounting Context", padding=20)
        ctx_frame.pack(fill="x", padx=20, pady=10)

        ttk.Label(ctx_frame, text="Entreprise:").grid(row=0, column=0, sticky="w", pady=5)
        self.combo_ent = ttk.Combobox(ctx_frame, values=["CPR", "ESP", "GIS", "URAM"], state="readonly", width=27)
        self.combo_ent.set(self.state["config"]["entreprise"])
        self.combo_ent.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(ctx_frame, text="Exercice:").grid(row=1, column=0, sticky="w", pady=5)
        self.combo_ex = ttk.Combobox(ctx_frame, values=["2026", "2025", "2024"], state="readonly", width=27)
        self.combo_ex.set(self.state["config"]["exercice"])
        self.combo_ex.grid(row=1, column=1, padx=10, pady=5)

        # Save Button
        btn_save = ttk.Button(self.frame, text="💾 Save Configuration", command=self._save_config)
        btn_save.pack(pady=20)

    def _save_config(self):
        self.state["config"]["username"] = self.entry_user.get()
        self.state["config"]["password"] = self.entry_pwd.get()
        self.state["config"]["entreprise"] = self.combo_ent.get()
        self.state["config"]["exercice"] = self.combo_ex.get()
        # You can add a quick tooltip or status label here confirming save
        