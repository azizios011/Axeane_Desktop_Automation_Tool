# Logic/accounts.py
import json
import os
from Debug.Logger import ColorLogger as log


class AccountManager:
    """
    Dynamically loads client profiles from Vente_Formats.json.
    Nothing is hardcoded — add a client to the JSON and it works immediately.
    """

    def __init__(self, formats_path="DB/Vente_Formats.json"):
        self.formats_path = formats_path
        self.profiles = []
        self.default_profile = None
        self._load()

    # ------------------------------------------------------------------
    # JSON loading (auto-strips trailing spaces from keys)
    # ------------------------------------------------------------------
    def _strip_keys(self, d):
        if isinstance(d, dict):
            return {k.strip(): self._strip_keys(v) for k, v in d.items()}
        if isinstance(d, list):
            return [self._strip_keys(i) for i in d]
        return d

    def _load(self):
        if not os.path.exists(self.formats_path):
            log.error(f"Formats file not found: {self.formats_path}")
            return

        with open(self.formats_path, "r", encoding="utf-8") as f:
            data = self._strip_keys(json.load(f))

        self.profiles = data.get("client_profiles", [])

        # Identify the DEFAULT fallback profile
        for p in self.profiles:
            if p.get("match", "").upper() == "DEFAULT":
                self.default_profile = p
                break

        specific_count = len(self.profiles) - (1 if self.default_profile else 0)
        log.info(f"Loaded {specific_count} specific client profiles + "
                 f"{'1 DEFAULT' if self.default_profile else 'NO DEFAULT'} "
                 f"from {self.formats_path}")

    def reload(self):
        """Re-read the JSON file (useful after user edits it)."""
        self._load()

    # ------------------------------------------------------------------
    # Profile matching
    # ------------------------------------------------------------------
    def get_profile(self, client_field: str) -> dict:
        """
        Returns a dict:
          {
            "profile":      {the matched profile dict},
            "match_type":   "specific" | "default" | "none",
            "match_key":    "PASSAGER" | "DEFAULT" | None
          }
        """
        if not client_field:
            return {"profile": self.default_profile,
                    "match_type": "default" if self.default_profile else "none",
                    "match_key": "DEFAULT" if self.default_profile else None}

        # Extract clean name from "C000001 | PASSAGER" format
        client_name = client_field
        if " | " in client_field:
            client_name = client_field.split(" | ", 1)[1].strip()
        client_upper = client_name.upper()

        # Try specific matches first (skip DEFAULT)
        for p in self.profiles:
            match_key = p.get("match", "").strip().upper()
            if match_key == "DEFAULT":
                continue
            if match_key and match_key in client_upper:
                return {"profile": p,
                        "match_type": "specific",
                        "match_key": match_key}

        # Fallback to DEFAULT
        if self.default_profile:
            return {"profile": self.default_profile,
                    "match_type": "default",
                    "match_key": "DEFAULT"}

        return {"profile": None, "match_type": "none", "match_key": None}
        