# Modules/FormulaEngine.py
import json
import os
from collections import defaultdict
from Debug.Logger import ColorLogger as log


class FormulaEngine:
    """
    Generates accounting formula cards from raw CSV data.
    Supports two modes:
      - build_cards(): one card per invoice (grouped by reference) - for execution
      - build_template_cards(): one card per client profile - for preview
    """

    def __init__(self):
        self.vente_formats = self._load_json("DB/Vente_Formats.json")
        self.vente_rules = self._load_json("DB/Vente_Rules.json")
        self.bank_formats = self._load_json("DB/Bank_Formats.json")
        self.bank_rules = self._load_json("DB/Bank_rules.json")
        self.bank_structure = self._load_json("DB/Bank_Structure.json")
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

    def _match_bank_mapping(self, label):
        mappings = self.bank_formats.get("mappings", [])
        label_upper = (label or "").upper()

        for mapping in mappings:
            keyword = mapping.get("keyword", "").upper()
            if keyword and keyword in label_upper:
                return mapping, "keyword", keyword

        return {
            "keyword": "UNMAPPED",
            "account": self.bank_rules.get("tax_calculation", {}).get("base_account", "471000"),
            "label": "Unmapped Bank Transaction",
        }, "default", "UNMAPPED"

    def _bank_sides_for_amount(self, amount):
        inversion = self.bank_rules.get("inversion_logic", {})
        if amount >= 0:
            logic = inversion.get("doc_credit_means", {})
        else:
            logic = inversion.get("doc_debit_means", {})

        return (
            logic.get("bank_action", "debit"),
            logic.get("counterpart_action", "credit"),
            logic.get("category", "Bank"),
        )

    def _amount_on_side(self, side, amount):
        return {
            "debit": amount if side == "debit" else 0.0,
            "credit": amount if side == "credit" else 0.0,
        }

    def _extract_bank_tax_amount(self, label, total_amount):
        tax_cfg = self.bank_rules.get("tax_calculation", {})
        marker = tax_cfg.get("detect_keyword", "DONT TVA:")
        label_upper = (label or "").upper()
        marker_upper = marker.upper()

        if marker_upper in label_upper:
            after_marker = label_upper.split(marker_upper, 1)[1].strip()
            token = after_marker.split()[0] if after_marker else ""
            cleaned = token.strip(" :;,.").replace(",", ".")
            try:
                return min(abs(float(cleaned)), total_amount)
            except ValueError:
                log.warn(f"Could not parse bank tax amount from label: {label}")

        rate = float(tax_cfg.get("default_rate", 0.19) or 0)
        if rate <= 0:
            return 0.0
        return total_amount - (total_amount / (1 + rate))

    def _generate_bank_formula_lines(self, row, mapping):
        amount = float(row.get("abs_amount", abs(float(row.get("amount", 0) or 0))) or 0)
        label = row.get("label", "") or mapping.get("label", "Bank Transaction")
        bank_account = self.bank_rules.get("bank_account_pivot", "532100")
        bank_side, counterpart_side, _ = self._bank_sides_for_amount(float(row.get("amount", 0) or 0))

        lines = [{
            "step": "bank_pivot",
            "account": bank_account,
            "label": label,
            **self._amount_on_side(bank_side, amount),
        }]

        if mapping.get("is_split"):
            tax_amount = self._extract_bank_tax_amount(label, amount)
            base_amount = max(amount - tax_amount, 0.0)

            if base_amount > 0:
                lines.append({
                    "step": "counterpart_base",
                    "account": mapping.get("base_account") or self.bank_rules.get("tax_calculation", {}).get("base_account"),
                    "label": mapping.get("label", label),
                    **self._amount_on_side(counterpart_side, base_amount),
                })

            if tax_amount > 0:
                lines.append({
                    "step": "counterpart_tax",
                    "account": mapping.get("tax_account") or self.bank_rules.get("tax_calculation", {}).get("default_tax_account"),
                    "label": "TVA bancaire",
                    **self._amount_on_side(counterpart_side, tax_amount),
                })
        else:
            lines.append({
                "step": "counterpart",
                "account": mapping.get("account"),
                "label": mapping.get("label", label),
                **self._amount_on_side(counterpart_side, amount),
            })

        return lines

    def _generate_formula_lines(self, rows_in_ref, profile):
        """
        Generate accounting lines for a group of rows sharing the same reference.
        FIX: Take TTC from first row only (not sum across all rows).
        """
        if not profile or not rows_in_ref:
            return []

        lines = []
        first_row = rows_in_ref[0]
        client_name = self._extract_client_name(first_row.get("client_name", ""))
        
        # FIX: Take TTC from first row only
        ttc = float(first_row.get("ttc", 0) or 0)
        
        compte_client = profile.get("compte_client")
        use_timbre = profile.get("use_timbre", False)
        use_cash = profile.get("use_cash", False)

        # Step 1: Client Total (Debit TTC) - ONCE per invoice
        lines.append({
            "step": "client_total",
            "account": compte_client,
            "label": client_name,
            "debit": ttc,
            "credit": 0,
        })

        # Step 2 & 3: TVA and Revenue for EACH row (handles multi-TVA)
        for row in rows_in_ref:
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

        # Step 4: Timbre Fiscal (if applicable) - ONCE per invoice
        if use_timbre:
            timbre_cfg = self.vente_rules.get("accounting_logic", {}).get("timbre_fiscal", {})
            timbre_account = timbre_cfg.get("account", "437000")
            timbre_amount = float(timbre_cfg.get("default_amount", 1.0))
            lines.append({
                "step": "timbre",
                "account": timbre_account,
                "label": timbre_cfg.get("label", "TIMBRE FISCAL"),
                "debit": 0,
                "credit": timbre_amount,
            })

        # Step 5: Cash Reroute (if applicable) - ONCE per invoice
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

    def build_cards(self, rows):
        """
        Build formula cards from raw CSV rows (one per invoice).
        Groups by reference to handle multi-TVA invoices.
        Used for EXECUTION.
        """
        log.info(f"Building cards for {len(rows)} rows...")

        # Group by reference
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
                log.warn(f"No profile found for client: {client_name}")
                continue

            # Generate formula lines
            formula_lines = self._generate_formula_lines(rows_in_ref, profile)

            # FIX: Take TTC from first row only
            total_ttc = float(first_row.get("ttc", 0) or 0)

            total_debit = sum(l["debit"] for l in formula_lines)
            total_credit = sum(l["credit"] for l in formula_lines)
            is_balanced = abs(total_debit - total_credit) < 0.01

            # Collect unique TVA rates
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
                "sample_client": client_name,  # FIX: Add sample_client
            }
            cards.append(card)

            if not is_balanced:
                log.warn(f"Formula for {ref} is NOT balanced! Debit: {total_debit}, Credit: {total_credit}")

        # Sort by reference
        cards.sort(key=lambda c: c["ref"])

        self.cards = cards

        log.success(f"Built {len(cards)} cards")
        for c in cards:
            rates_str = "+".join(f"{int(r)}%" for r in c["tva_rates"]) if c["tva_rates"] else "N/A"
            balance_str = "✓" if c["is_balanced"] else "✗"
            log.info(f"  • {c['ref']:15s} | {c['sample_client'][:20]:20s} | TVA: {rates_str:10s} | {c['row_count']} rows | TTC {c['total_ttc']:>11.3f} | {balance_str}")

        return cards

    def build_bank_cards(self, rows):
        """
        Build formula cards from normalized bank rows.
        One card is generated per bank transaction.
        """
        log.info(f"Building bank cards for {len(rows)} rows...")

        cards = []
        for index, row in enumerate(rows, start=1):
            ref = row.get("ref") or f"BANK-{index:05d}"
            label = row.get("label", "")
            amount = float(row.get("amount", 0) or 0)
            abs_amount = abs(amount)

            mapping, match_type, match_key = self._match_bank_mapping(label)
            formula_lines = self._generate_bank_formula_lines(row, mapping)

            total_debit = sum(l["debit"] for l in formula_lines)
            total_credit = sum(l["credit"] for l in formula_lines)
            is_balanced = abs(total_debit - total_credit) < 0.01
            _, _, category = self._bank_sides_for_amount(amount)

            card = {
                "ref": ref,
                "doc_type": "Bank",
                "match_key": match_key,
                "match_type": match_type,
                "profile": mapping,
                "row_count": 1,
                "tva_rates": [],
                "total_ttc": abs_amount,
                "total_amount": abs_amount,
                "signed_amount": amount,
                "formula_lines": formula_lines,
                "total_debit": total_debit,
                "total_credit": total_credit,
                "is_balanced": is_balanced,
                "sample_client": label,
                "category": category,
                "journal": self.bank_structure.get("default_journal", "BQ"),
            }
            cards.append(card)

            if not is_balanced:
                log.warn(f"Bank formula for {ref} is NOT balanced! Debit: {total_debit}, Credit: {total_credit}")

        self.cards = cards

        log.success(f"Built {len(cards)} bank cards")
        for c in cards:
            balance_str = "OK" if c["is_balanced"] else "ERR"
            log.info(
                f"  - {c['ref']:15s} | {c['match_key'][:20]:20s} | "
                f"Amount {c['total_ttc']:>11.3f} | {balance_str}"
            )

        return cards

    def build_template_cards(self, rows):
        """
        Build TEMPLATE cards grouped by client profile.
        Each card represents ONE profile (PASSAGER, DEFAULT, etc.)
        and shows the formula template + how many invoices use it.
        Used for PREVIEW.
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
            sample_row = items[0]["row"]
            sample_formula = self._generate_formula_lines([sample_row], profile)

            # Sample info for display
            sample_client = items[0]["client_field"]
            sample_ref = sample_row.get("ref", "UNKNOWN")

            # Calculate balance for the sample formula
            total_debit = sum(l["debit"] for l in sample_formula)
            total_credit = sum(l["credit"] for l in sample_formula)
            is_balanced = abs(total_debit - total_credit) < 0.01

            card = {
                "ref": f"TEMPLATE_{match_key}",
                "match_key": match_key,
                "match_type": match_type,
                "profile": profile,
                "invoice_count": invoice_count,
                "row_count": invoice_count,  # For compatibility
                "total_ttc": total_ttc,
                "tva_rates": tva_rates,
                "formula_lines": sample_formula,
                "total_debit": total_debit,
                "total_credit": total_credit,
                "is_balanced": is_balanced,
                "sample_client": sample_client,  # FIX: Add sample_client
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

    def get_summary(self):
        """Get a summary of all generated cards."""
        if not self.cards:
            return {
                "total_cards": 0,
                "total_invoices": 0,
                "total_ttc": 0.0,
                "total_rows": 0,
                "balanced_cards": 0,
                "unbalanced_cards": 0,
            }

        # Detect if these are template cards or per-invoice cards
        if "invoice_count" in self.cards[0]:
            # Template cards
            total_invoices = sum(c["invoice_count"] for c in self.cards)
        else:
            # Per-invoice cards
            total_invoices = len(self.cards)

        total_ttc = sum(c.get("total_ttc", 0) for c in self.cards)
        total_rows = sum(c.get("row_count", 0) for c in self.cards)
        balanced_count = sum(1 for c in self.cards if c.get("is_balanced", False))

        return {
            "total_cards": len(self.cards),
            "total_invoices": total_invoices,
            "total_ttc": total_ttc,
            "total_rows": total_rows,
            "balanced_cards": balanced_count,
            "unbalanced_cards": len(self.cards) - balanced_count,
        }
