# Logic/accounts.py
import json
import os

class AccountManager:
    def __init__(self):
        self.vente_formats = self._load_json("DB/Vente_Formats.json")
        self.bank_formats = self._load_json("DB/Bank_Formats.json")

    def _load_json(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_client_account(self, client_name: str) -> str:
        # Logic to match client_name against self.vente_formats['client_profiles ']
        pass
