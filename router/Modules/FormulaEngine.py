# Modules/FormulaEngine.py
import json
import os
from collections import defaultdict
from Debug.Logger import ColorLogger as log


class FormulaEngine:
    """
    Groups invoices by CLIENT PROFILE (not by reference).
    Creates ONE template card per profile showing the formula structure.
    """

    def __init__(self):
        self.vente_formats = self._load_json("DB/Vente_Formats.json")
        self.vente_rules = self._load_json("DB/Vente_Rules.json")

    def _load_json(self, path):
        if not os.path.exists(path):
            log.error(f"File not found: {path}")
            return {}
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return self._strip_keys(data)

    def _strip_keys(self, d):
        if isinstance(d, dict):
            return {k.strip(): self._strip_keys(v) for k, v in d.items()}
        elif isinstance(d, list):
            return [self._strip_keys(i) for i in d]
        return d

    def _extract_client_name(self, client_field):
        if not client_field:
            return ""
        if " | " in client_field:
            return client_field.split(" | ", 1)[1].strip()
        return client_field.strip()

    def _match_client_profile(self, client_name):
        """Returns (profile_dict, match_type, match_key)"""
        profiles = self.vente_formats.get("client_profiles", [])
        client_upper = client_name.upper()

        for profile in profiles:
            match_key = profile.get("match", "").upper()
            if match_key == "DEFAULT":
                continue
            if match_key and match_key in client_upper:
                return profile, "specific", match_key

        for profile in profiles:
            if profile.get("match", "").upper() == "DEFAULT":
                return profile, "default", "DEFAULT"

        return None, "none", "UNMATCHED"

    def _get_tax_accounts(self, tva_rate):
        rates = self.vente_rules.get("accounting_logic", {}).get("tax_logic", {}).get("rates", [])
        try:
            target = float(tva_rate)
        except (TypeError, ValueError):
            return None, None

        for rate_config in rates:
            if float(rate_config.get("rate", -1)) == target:
                return rate_config.get("ht_account"), rate_config.get("tva_account")
        return None, None

    def _generate_template_formula(self, profile, sample_invoices):
        """
        Generate the TEMPLATE formula for a profile.
        Uses the first invoice as a sample, but includes ALL TVA rates found across all invoices.
        """
        if not profile or not sample_invoices:
            return []

        lines = []
        compte_client = profile.get("compte_client")
        use_timbre = profile.get("use_timbre", False)
        use_cash = profile.get("use_cash", False)

        # Use first invoice as sample for amounts
        sample = sample_invoices[0]
        ttc = float(sample.get("ttc", 0) or 0)

        # Collect ALL unique TVA rates from all invoices in this group
        all_tva_rates = set()
        for inv in sample_invoices:
            rate = float(inv.get("tva_rate", 0) or 0)
            if rate > 0:
                all_tva_rates.add(rate)

        # Step 1: Client Total (Debit TTC)
        lines.append({
            "step": "client_total",
            "account": compte_client,
            "label": "Client (from profile)",
            "debit": ttc,
            "credit": 0,
        })

        # Step 2 & 3: For each unique TVA rate found, show TVA + Revenue lines
        for rate in sorted(all_tva_rates):
            ht_account, tva_account = self._get_tax_accounts(rate)

            if tva_account:
                lines.append({
                    "step": f"tax_split_{int(rate)}",
                    "account": tva_account,
                    "label": f"TVA {int(rate)}%",
                    "debit": 0,
                    "credit": 0,  # Template: amount varies per invoice
                })

            if ht_account:
                lines.append({
                    "step": f"revenue_split_{int(rate)}",
                    "account": ht_account,
                    "label": f"Revenue {int(rate)}%",
                    "debit": 0,
                    "credit": 0,  # Template: amount varies per invoice
                })

        # Step 4: Timbre Fiscal (if applicable)
        if use_timbre:
            timbre_cfg = self.vente_rules.get("accounting_logic", {}).get("timbre_fiscal", {})
            lines.append({
                "step": "timbre",
                "account": timbre_cfg.get("account", "437000"),
                "label": timbre_cfg.get("label", "TIMBRE FISCAL"),
                "debit": 0,
                "credit": float(timbre_cfg.get("default_amount", 1.0)),
            })

        # Step 5: Cash Reroute (if applicable)
        if use_cash:
            caisse_account = profile.get("compte_caisse", "541100")
            lines.append({
                "step": "cash_reroute_credit",
                "account": compte_client,
                "label": "Cash reroute (credit client)",
                "debit": 0,
                "credit": ttc,
            })
            lines.append({
                "step": "cash_reroute_debit",
                "account": caisse_account,
                "label": "Caisse (debit)",
                "debit": ttc,
                "credit": 0,
            })

        return lines

    def build_cards(self, rows):
        """
        Build TEMPLATE cards grouped by client profile.
        Each card represents ONE profile (PASSAGER, DEFAULT, etc.)
        and shows the formula template + how many invoices use it.
        """
        log.info(f"Building template cards for {len(rows)} rows...")

        # Group rows by profile match_key
        profile_groups = defaultdict(list)
        for row in rows:
            client_name = self._extract_client_name(row.get("client_name", ""))
            profile, match_type, match_key = self._match_client_profile(client_name)
            group_key = match_key  # "PASSAGER", "DEFAULT", "TUNISIE AUTOMOTIVE", etc.
            profile_groups[group_key].append({
                "row": row,
                "profile": profile,
                "match_type": match_type,
                "match_key": match_key,
            })

        cards = []
        for match_key, items in profile_groups.items():
            profile = items[0]["profile"]
            match_type = items[0]["match_type"]

            if not profile:
                log.warn(f"No profile found for group: {match_key}")
                continue

            # Generate template formula
            sample_rows = [item["row"] for item in items]
            template_lines = self._generate_template_formula(profile, sample_rows)

            # Calculate totals across ALL invoices in this group
            total_ttc = sum(float(item["row"].get("ttc", 0) or 0) for item in items)
            invoice_count = len(items)

            # Collect unique TVA rates
            tva_rates = sorted(set(
                float(item["row"].get("tva_rate", 0) or 0)
                for item in items
                if float(item["row"].get("tva_rate", 0) or 0) > 0
            ))

            # Sample client name for display
            sample_client = self._extract_client_name(items[0]["row"].get("client_name", ""))

            card = {
                "match_key": match_key,
                "match_type": match_type,
                "profile": profile,
                "invoice_count": invoice_count,
                "total_ttc": total_ttc,
                "tva_rates": tva_rates,
                "template_lines": template_lines,
                "sample_client": sample_client,
                "use_cash": profile.get("use_cash", False),
                "use_timbre": profile.get("use_timbre", False),
                "compte_client": profile.get("compte_client"),
            }

            cards.append(card)

        # Sort: specific profiles first, then default
        priority = {"specific": 0, "default": 1, "none": 2}
        cards.sort(key=lambda c: (priority.get(c["match_type"], 9), -c["invoice_count"]))

        log.success(f"Built {len(cards)} template cards")
        for c in cards:
            rates_str = "+".join(f"{int(r)}%" for r in c["tva_rates"]) if c["tva_rates"] else "N/A"
            cash_str = " [CASH]" if c["use_cash"] else ""
            log.info(
                f"  • [{c['match_type'].upper():8s}] {c['match_key']:25s} | "
                f"{c['invoice_count']:3d} invoices | TTC {c['total_ttc']:>12.3f} | "
                f"TVA: {rates_str}{cash_str}"
            )

        return cards

    def get_summary(self):
        if not hasattr(self, 'cards') or not self.cards:
            return {
                "total_cards": 0,
                "total_invoices": 0,
                "total_ttc": 0,
            }

        total_invoices = sum(c["invoice_count"] for c in self.cards)
        total_ttc = sum(c["total_ttc"] for c in self.cards)

        return {
            "total_cards": len(self.cards),
            "total_invoices": total_invoices,
            "total_ttc": total_ttc,
        }
        