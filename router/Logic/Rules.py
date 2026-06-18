# Logic/rules.py
import json
import os
from Debug.Logger import ColorLogger as log


class RulesEngine:
    """
    Dynamically loads accounting rules from Vente_Rules.json.
    Nothing is hardcoded — edit the JSON and the engine adapts.
    """

    def __init__(self, rules_path="DB/Vente_Rules.json"):
        self.rules_path = rules_path
        self.rules = {}
        self._load()

    # ------------------------------------------------------------------
    # JSON loading
    # ------------------------------------------------------------------
    def _strip_keys(self, d):
        if isinstance(d, dict):
            return {k.strip(): self._strip_keys(v) for k, v in d.items()}
        if isinstance(d, list):
            return [self._strip_keys(i) for i in d]
        return d

    def _load(self):
        if not os.path.exists(self.rules_path):
            log.error(f"Rules file not found: {self.rules_path}")
            return

        with open(self.rules_path, "r", encoding="utf-8") as f:
            data = self._strip_keys(json.load(f))

        self.rules = data.get("accounting_logic", {})
        seq_count = len(self.rules.get("entry_sequence", []))
        rate_count = len(self.rules.get("tax_logic", {}).get("rates", []))
        log.info(f"Loaded {seq_count} entry steps + {rate_count} TVA rates "
                 f"from {self.rules_path}")

    def reload(self):
        self._load()

    # ------------------------------------------------------------------
    # Tax lookup (from JSON tax_logic.rates)
    # ------------------------------------------------------------------
    def get_tax_accounts(self, tva_rate: float) -> dict:
        """Returns {"ht_account": ..., "tva_account": ...} or None."""
        rates = self.rules.get("tax_logic", {}).get("rates", [])
        # Normalize: JSON may store rate as int 19 or float 19.0
        try:
            target = float(tva_rate)
        except (TypeError, ValueError):
            return None

        for r in rates:
            if float(r.get("rate", -1)) == target:
                return {
                    "ht_account": r.get("ht_account"),
                    "tva_account": r.get("tva_account"),
                }
        return None

    # ------------------------------------------------------------------
    # Formula generation (driven by entry_sequence)
    # ------------------------------------------------------------------
    def generate_formula(self, invoice: dict, profile: dict) -> list:
        """
        Reads `entry_sequence` from JSON and builds the accounting lines.
        Returns list of dicts: {step, account, label, debit, credit}
        """
        if not profile:
            return []

        sequence = self.rules.get("entry_sequence", [])
        timbre_cfg = self.rules.get("timbre_fiscal", {})
        tva_rate = float(invoice.get("tva_rate", 0) or 0)
        tax_acc = self.get_tax_accounts(tva_rate)

        lines = []

        for step in sequence:
            step_name = step.get("step", "")

            # ---- client_total ----
            if step_name == "client_total":
                lines.append({
                    "step": "client_total",
                    "account": profile.get("compte_client"),
                    "label": self._extract_client_label(invoice.get("client_name", "")),
                    "debit": float(invoice.get("ttc", 0) or 0),
                    "credit": 0.0,
                })

            # ---- tax_split ----
            elif step_name == "tax_split":
                if tax_acc:
                    lines.append({
                        "step": "tax_split",
                        "account": tax_acc["tva_account"],
                        "label": f"TVA {int(tva_rate)}%",
                        "debit": 0.0,
                        "credit": float(invoice.get("tva_amt", 0) or 0),
                    })
                else:
                    log.warn(f"No TVA account configured for rate {tva_rate}%")

            # ---- revenue_split ----
            elif step_name == "revenue_split":
                if tax_acc:
                    lines.append({
                        "step": "revenue_split",
                        "account": tax_acc["ht_account"],
                        "label": f"Revenue {int(tva_rate)}%",
                        "debit": 0.0,
                        "credit": float(invoice.get("net_ht", 0) or 0),
                    })

            # ---- timbre ----
            elif step_name == "timbre":
                cond = step.get("condition", "")
                if self._eval_condition(cond, profile):
                    lines.append({
                        "step": "timbre",
                        "account": timbre_cfg.get("account"),
                        "label": timbre_cfg.get("label", "TIMBRE FISCAL"),
                        "debit": 0.0,
                        "credit": float(timbre_cfg.get("default_amount", 1.0)),
                    })

            # ---- cash_reroute ----
            elif step_name == "cash_reroute":
                cond = step.get("condition", "")
                if self._eval_condition(cond, profile):
                    ttc = float(invoice.get("ttc", 0) or 0)
                    for action in step.get("actions", []):
                        acc = action.get("account")
                        # Resolve "formats.compte_client" placeholder
                        if acc == "formats.compte_client":
                            acc = profile.get("compte_client")
                        lines.append({
                            "step": f"cash_reroute_{action.get('side')}",
                            "account": acc,
                            "label": "Cash reroute" if action.get("side") == "credit" else "Caisse",
                            "debit": ttc if action.get("side") == "debit" else 0.0,
                            "credit": ttc if action.get("side") == "credit" else 0.0,
                        })

        return lines

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _eval_condition(self, cond: str, profile: dict) -> bool:
        """Minimal safe evaluator for conditions like 'formats.use_cash == true'."""
        if not cond:
            return False
        cond = cond.strip()
        if "==" not in cond:
            return False
        left, right = [x.strip() for x in cond.split("==", 1)]
        # Resolve left side: "formats.use_cash" -> profile["use_cash"]
        if left.startswith("formats."):
            key = left.split(".", 1)[1]
            val = profile.get(key)
        else:
            val = None

        # Parse right side
        right_lower = right.lower()
        if right_lower == "true":
            expected = True
        elif right_lower == "false":
            expected = False
        else:
            try:
                expected = float(right)
            except ValueError:
                expected = right

        return val == expected

    def _extract_client_label(self, client_field: str) -> str:
        if " | " in client_field:
            return client_field.split(" | ", 1)[1].strip()
        return client_field.strip()
        