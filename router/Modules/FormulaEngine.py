# Modules/FormulaEngine.py
import json
import os
from collections import defaultdict
from Debug.Logger import ColorLogger as log


class FormulaEngine:
    """
    Generates accounting formula cards from raw CSV data.
    Supports two modes:
      - build_cards(): one card per invoice (grouped by reference)
      - build_template_cards(): one card per client profile (template view)
    """

    def __init__(self):
        self.vente_formats = self._load_json("DB/Vente_Formats.json")
        self.bank_formats = self._load_json("DB/Bank_Formats.json")
        self.vente_rules = self._load_json("DB/Vente_Rules.json")
        self.bank_rules = self._load_json("DB/Bank_Rules.json")
        self.cards = []

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

    def _generate_formula_for_rows(self, rows_in_group, profile):
        """Generate accounting lines for a group of rows sharing the same reference/profile."""
        if not profile or not rows_in_group:
            return []

        lines = []
        first_row = rows_in_group[0]
        client_name = self._extract_client_name(first_row.get("client_name", ""))
        ttc = float(first_row.get("ttc", 0) or 0)
        compte_client = profile.get("compte_client")
        use_timbre = profile.get("use_timbre", False)
        use_cash = profile.get("use_cash", False)

        # Client total (debit) — once per invoice
        lines.append({
            "step": "client_total",
            "account": compte_client,
            "label": client_name,
            "debit": ttc,
            "credit": 0,
        })

        # TVA + Revenue for each row (handles multi-TVA)
        for row in rows_in_group:
            tva_rate = float(row.get("tva_rate", 0) or 0)
            tva_amt = float(row.get("tva_amt", 0) or 0)
            net_ht = float(row.get("net_ht", 0) or 0)
            ht_account, tva_account = self._get_tax_accounts(tva_rate)

            if tva_account and tva_amt > 0:
                lines.append({
                    "step": f"tax_split_{int(tva_rate)}",
                    "account": tva_account,
                    "label": f"TVA {int(tva_rate)}%",
                    "debit": 0,
                    "credit": tva_amt,
                })
            if ht_account and net_ht > 0:
                lines.append({
                    "step": f"revenue_split_{int(tva_rate)}",
                    "account": ht_account,
                    "label": f"Revenue {int(tva_rate)}%",
                    "debit": 0,
                    "credit": net_ht,
                })

        # Timbre (once per invoice)
        if use_timbre:
            timbre_cfg = self.vente_rules.get("accounting_logic", {}).get("timbre_fiscal", {})
            lines.append({
                "step": "timbre",
                "account": timbre_cfg.get("account", "437000"),
                "label": timbre_cfg.get("label", "TIMBRE FISCAL"),
                "debit": 0,
                "credit": float(timbre_cfg.get("default_amount", 1.0)),
            })

        # Cash reroute
        if use_cash:
            caisse_account = profile.get("compte_caisse", "541100")
            lines.append({
                "step": "cash_reroute_credit",
                "account": compte_client,
                "label": "Cash reroute",
                "debit": 0,
                "credit": ttc,
            })
            lines.append({
                "step": "cash_reroute_debit",
                "account": caisse_account,
                "label": "Caisse",
                "debit": ttc,
                "credit": 0,
            })

        return lines

    # ============================================================
    # NEW: Template cards grouped by client PROFILE
    # ============================================================
    def build_template_cards(self, rows):
        """
        Build ONE template card per client profile.
        Each card shows:
          - Profile name (PASSAGER, DEFAULT, TUNISIE AUTOMOTIVE, etc.)
          - How many invoices match this profile
          - Total TTC across all matching invoices
          - A sample formula (from the first matching invoice)
          - Sample client name and reference for display
        """
        log.info(f"Building template cards for {len(rows)} rows...")

        # Group rows by profile match_key
        profile_groups = defaultdict(list)
        for row in rows:
            client_field = row.get("client_name", "") or ""
            client_name = self._extract_client_name(client_field)
            profile, match_type, match_key = self._match_client_profile(client_name)
            if not profile:
                continue
            profile_groups[match_key].append({
                "row": row,
                "profile": profile,
                "match_type": match_type,
                "match_key": match_key,
                "client_field": client_field,
            })

        cards = []
        for match_key, items in profile_groups.items():
            profile = items[0]["profile"]
            match_type = items[0]["match_type"]
            invoice_count = len(items)

            # Aggregate totals
            total_ttc = sum(float(item["row"].get("ttc", 0) or 0) for item in items)

            # Collect unique TVA rates across all invoices
            tva_rates = sorted(set(
                float(item["row"].get("tva_rate", 0) or 0)
                for item in items
                if float(item["row"].get("tva_rate", 0) or 0) > 0
            ))

            # Generate a SAMPLE formula from the first invoice
            # (structure is the same for all invoices in this profile)
            sample_row = items[0]["row"]
            sample_formula = self._generate_formula_for_rows([sample_row], profile)

            # Sample info for display
            sample_client = items[0]["client_field"]
            sample_ref = sample_row.get("ref", "UNKNOWN")

            # Build a TEMPLATE version of the formula (with placeholders for amounts)
            # Keep the sample formula as-is for preview purposes
            template_lines = sample_formula

            card = {
                "match_key": match_key,
                "match_type": match_type,
                "profile": profile,
                "invoice_count": invoice_count,
                "total_ttc": total_ttc,
                "tva_rates": tva_rates,
                "formula_lines": template_lines,
                "sample_client": sample_client,
                "sample_ref": sample_ref,
                "use_cash": profile.get("use_cash", False),
                "use_timbre": profile.get("use_timbre", False),
                "compte_client": profile.get("compte_client"),
            }
            cards.append(card)

        # Sort: specific profiles first (by invoice count desc), then default
        priority = {"specific": 0, "default": 1, "none": 2}
        cards.sort(key=lambda c: (priority.get(c["match_type"], 9), -c["invoice_count"]))

        self.cards = cards

        log.success(f"Built {len(cards)} template cards")
        for c in cards:
            rates_str = "+".join(f"{int(r)}%" for r in c["tva_rates"]) if c["tva_rates"] else "N/A"
            flags = []
            if c["use_cash"]:
                flags.append("CASH")
            if c["use_timbre"]:
                flags.append("TIMBRE")
            flags_str = " | ".join(flags) if flags else "-"
            log.info(
                f"  • [{c['match_type'].upper():8s}] {c['match_key']:25s} | "
                f"{c['invoice_count']:3d} invoices | TTC {c['total_ttc']:>12.3f} | "
                f"TVA: {rates_str:10s} | Flags: {flags_str}"
            )

        return cards

    # ============================================================
    # Legacy: per-invoice cards (grouped by reference)
    # ============================================================
    def build_cards(self, rows):
        """Build one card per invoice (grouped by reference)."""
        log.info(f"Building per-invoice cards for {len(rows)} rows...")

        ref_groups = defaultdict(list)
        for row in rows:
            ref = row.get("ref", "UNKNOWN")
            ref_groups[ref].append(row)

        cards = []
        for ref, rows_in_ref in ref_groups.items():
            first_row = rows_in_ref[0]
            client_field = first_row.get("client_name", "") or ""
            client_name = self._extract_client_name(client_field)
            profile, match_type, match_key = self._match_client_profile(client_name)
            if not profile:
                continue

            formula_lines = self._generate_formula_for_rows(rows_in_ref, profile)

            total_ttc = float(first_row.get("ttc", 0) or 0)
            total_debit = sum(l["debit"] for l in formula_lines)
            total_credit = sum(l["credit"] for l in formula_lines)
            is_balanced = abs(total_debit - total_credit) < 0.01

            tva_rates = sorted(set(
                float(r.get("tva_rate", 0) or 0)
                for r in rows_in_ref
                if float(r.get("tva_rate", 0) or 0) > 0
            ))

            card = {
                "ref": ref,
                "match_key": match_key,
                "match_type": match_type,
                "profile": profile,
                "row_count": len(rows_in_ref),
                "tva_rates": tva_rates,
                "total_ttc": total_ttc,
                "formula_lines": formula_lines,
                "total_debit": total_debit,
                "total_credit": total_credit,
                "is_balanced": is_balanced,
                "sample_client": client_field,
            }
            cards.append(card)

            if not is_balanced:
                log.warn(f"Formula for {ref} is NOT balanced! D:{total_debit} C:{total_credit}")

        cards.sort(key=lambda c: c.get("ref", ""))
        self.cards = cards

        log.success(f"Built {len(cards)} per-invoice cards")
        for c in cards:
            rates_str = "+".join(f"{int(r)}%" for r in c["tva_rates"]) if c["tva_rates"] else "N/A"
            bal = "✓" if c["is_balanced"] else "✗"
            log.info(
                f"  • {c.get('ref', '?'):15s} | {c['sample_client'][:20]:20s} | "
                f"TVA: {rates_str:10s} | {c['row_count']} rows | TTC {c['total_ttc']:>11.3f} | {bal}"
            )

        return cards

    def get_summary(self):
        if not self.cards:
            return {"total_cards": 0, "total_invoices": 0, "total_ttc": 0}

        # Detect if these are template cards or per-invoice cards
        if self.cards and "invoice_count" in self.cards[0]:
            # Template cards
            total_invoices = sum(c["invoice_count"] for c in self.cards)
        else:
            # Per-invoice cards
            total_invoices = len(self.cards)

        total_ttc = sum(c["total_ttc"] for c in self.cards)

        return {
            "total_cards": len(self.cards),
            "total_invoices": total_invoices,
            "total_ttc": total_ttc,
        }
        