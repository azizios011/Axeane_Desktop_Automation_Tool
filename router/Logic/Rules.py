# Logic/Rules.py
import json
import os
from Debug.Logger import ColorLogger as log


class RulesEngine:
    """
    Dynamically loads accounting rules from Vente_Rules.json.
    Handles multi-TVA rate invoices (e.g., 7% + 19% on same reference).
    """

    def __init__(self, rules_path="DB/Vente_Rules.json"):
        self.rules_path = rules_path
        self.rules = {}
        self._load()

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

    def get_tax_accounts(self, tva_rate: float) -> dict:
        """Returns {"ht_account": ..., "tva_account": ...} or None."""
        rates = self.rules.get("tax_logic", {}).get("rates", [])
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

    def generate_formula_for_group(self, rows_in_group: list, profile: dict) -> list:
        """
        Generate formula for a group of rows (same reference, possibly multiple TVA rates).
        rows_in_group: list of (row_dict, tva_rate) tuples
        """
        if not profile or not rows_in_group:
            return []

        sequence = self.rules.get("entry_sequence", [])
        timbre_cfg = self.rules.get("timbre_fiscal", {})
        
        # Use the first row for client info and TTC
        first_row = rows_in_group[0][0]
        ttc = float(first_row.get("ttc", 0) or 0)
        
        lines = []

        for step in sequence:
            step_name = step.get("step", "")
            apply_once = step.get("apply_once_per_group", False)
            apply_per_rate = step.get("apply_per_rate", False)

            # ---- client_total ----
            if step_name == "client_total":
                lines.append({
                    "step": "client_total",
                    "account": profile.get("compte_client"),
                    "label": self._extract_client_label(first_row.get("client_name", "")),
                    "debit": ttc,
                    "credit": 0.0,
                })

            # ---- tax_split and revenue_split (apply per rate) ----
            elif step_name in ["tax_split", "revenue_split"]:
                if apply_per_rate:
                    # Generate entries for EACH TVA rate in the group
                    for row, tva_rate in rows_in_group:
                        tax_acc = self.get_tax_accounts(tva_rate)
                        if not tax_acc:
                            log.warn(f"No tax accounts for rate {tva_rate}%")
                            continue
                        
                        if step_name == "tax_split":
                            tva_amt = float(row.get("tva_amt", 0) or 0)
                            lines.append({
                                "step": f"tax_split_{int(tva_rate)}",
                                "account": tax_acc["tva_account"],
                                "label": f"TVA {int(tva_rate)}%",
                                "debit": 0.0,
                                "credit": tva_amt,
                            })
                        elif step_name == "revenue_split":
                            net_ht = float(row.get("net_ht", 0) or 0)
                            lines.append({
                                "step": f"revenue_split_{int(tva_rate)}",
                                "account": tax_acc["ht_account"],
                                "label": f"Revenue {int(tva_rate)}%",
                                "debit": 0.0,
                                "credit": net_ht,
                            })

            # ---- timbre (apply once per group) ----
            elif step_name == "timbre":
                if apply_once or self._eval_condition(step.get("condition", ""), profile):
                    lines.append({
                        "step": "timbre",
                        "account": timbre_cfg.get("account"),
                        "label": timbre_cfg.get("label", "TIMBRE FISCAL"),
                        "debit": 0.0,
                        "credit": float(timbre_cfg.get("default_amount", 1.0)),
                    })

            # ---- cash_reroute (apply once per group) ----
            elif step_name == "cash_reroute":
                if apply_once or self._eval_condition(step.get("condition", ""), profile):
                    for action in step.get("actions", []):
                        acc = action.get("account")
                        if acc == "formats.compte_client":
                            acc = profile.get("compte_client")
                        elif acc == "541100":
                            acc = profile.get("compte_caisse", "541100")
                        
                        lines.append({
                            "step": f"cash_reroute_{action.get('side')}",
                            "account": acc,
                            "label": "Cash reroute" if action.get("side") == "credit" else "Caisse",
                            "debit": ttc if action.get("side") == "debit" else 0.0,
                            "credit": ttc if action.get("side") == "credit" else 0.0,
                        })

        return lines

    def _eval_condition(self, cond: str, profile: dict) -> bool:
        """Minimal safe evaluator for conditions like 'formats.use_cash == true'."""
        if not cond:
            return False
        cond = cond.strip()
        if "==" not in cond:
            return False
        left, right = [x.strip() for x in cond.split("==", 1)]
        if left.startswith("formats."):
            key = left.split(".", 1)[1]
            val = profile.get(key)
        else:
            val = None

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
        