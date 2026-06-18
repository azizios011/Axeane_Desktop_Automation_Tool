# Modules/FormulaEngine.py
import json
import os
from collections import defaultdict
from Debug.Logger import ColorLogger as log


class FormulaEngine:
    """
    Generates accounting formula cards from raw CSV data.
    Groups rows by reference (for multi-TVA invoices) or by client (for single invoices).
    """

    def __init__(self):
        self.vente_formats = self._load_json("DB/Vente_Formats.json")
        self.bank_formats = self._load_json("DB/Bank_Formats.json")
        self.vente_rules = self._load_json("DB/Vente_Rules.json")
        self.bank_rules = self._load_json("DB/Bank_Rules.json")
        self.cards = []

    def _load_json(self, path):
        """Load JSON with automatic key stripping"""
        if not os.path.exists(path):
            log.error(f"File not found: {path}")
            return {}
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return self._strip_keys(data)

    def _strip_keys(self, d):
        """Recursively strip whitespace from dictionary keys"""
        if isinstance(d, dict):
            return {k.strip(): self._strip_keys(v) for k, v in d.items()}
        elif isinstance(d, list):
            return [self._strip_keys(i) for i in d]
        return d

    def _extract_client_name(self, client_field):
        """Extract client name from CSV field like 'C000001 | PASSAGER'"""
        if not client_field:
            return ""
        if " | " in client_field:
            return client_field.split(" | ")[1].strip()
        return client_field.strip()

    def _match_client_profile(self, client_name):
        """Match client name against profiles in Vente_Formats.json"""
        profiles = self.vente_formats.get("client_profiles", [])
        
        # Try to match exact client name first
        for profile in profiles:
            if profile["match"].upper() in client_name.upper():
                return profile
        
        # Fallback to DEFAULT profile
        for profile in profiles:
            if profile["match"] == "DEFAULT":
                return profile
        
        return None

    def _get_tax_accounts(self, tva_rate):
        """Get HT and TVA accounts based on tax rate"""
        rates = self.vente_rules["accounting_logic"]["tax_logic"]["rates"]
        for rate_config in rates:
            if rate_config["rate"] == tva_rate:
                return rate_config["ht_account"], rate_config["tva_account"]
        return None, None

    def generate_formula(self, invoice):
        """
        Generate the complete formula (row sequence) for one invoice.
        Returns a list of rows that will be entered into EcritureTable.
        """
        rows = []
        row_num = 1
        
        # Extract client info
        client_name = self._extract_client_name(invoice.get("client_name", ""))
        profile = self._match_client_profile(client_name)
        
        if not profile:
            log.error(f"No profile found for client: {client_name}")
            return []
        
        compte_client = profile["compte_client"]
        use_timbre = profile.get("use_timbre", False)
        use_cash = profile.get("use_cash", False)
        
        # Get amounts
        ttc = float(invoice.get("ttc", 0))
        tva_amt = float(invoice.get("tva_amt", 0))
        net_ht = float(invoice.get("net_ht", 0))
        tva_rate = float(invoice.get("tva_rate", 0))
        
        # Get tax accounts
        ht_account, tva_account = self._get_tax_accounts(tva_rate)
        
        if not ht_account or not tva_account:
            log.error(f"No tax accounts found for rate {tva_rate}%")
            return []
        
        # Step 1: Client Total (Debit TTC)
        rows.append({
            "row_num": row_num,
            "account": compte_client,
            "label": client_name,
            "debit": ttc,
            "credit": 0,
            "step": "client_total"
        })
        row_num += 1
        
        # Step 2: TVA Split (Credit TVA)
        rows.append({
            "row_num": row_num,
            "account": tva_account,
            "label": f"TVA {int(tva_rate)}%",
            "debit": 0,
            "credit": tva_amt,
            "step": "tax_split"
        })
        row_num += 1
        
        # Step 3: Revenue Split (Credit HT)
        rows.append({
            "row_num": row_num,
            "account": ht_account,
            "label": f"Revenue {int(tva_rate)}%",
            "debit": 0,
            "credit": net_ht,
            "step": "revenue_split"
        })
        row_num += 1
        
        # Step 4: Timbre Fiscal (Credit 1.000) - if applicable
        if use_timbre:
            timbre_account = self.vente_rules["accounting_logic"]["timbre_fiscal"]["account"]
            timbre_amount = self.vente_rules["accounting_logic"]["timbre_fiscal"]["default_amount"]
            rows.append({
                "row_num": row_num,
                "account": timbre_account,
                "label": "TIMBRE FISCAL",
                "debit": 0,
                "credit": timbre_amount,
                "step": "timbre"
            })
            row_num += 1
        
        # Step 5: Cash Reroute - if applicable
        if use_cash:
            caisse_account = profile.get("compte_caisse", "541100")
            # Credit client account
            rows.append({
                "row_num": row_num,
                "account": compte_client,
                "label": f"Cash reroute - {client_name}",
                "debit": 0,
                "credit": ttc,
                "step": "cash_reroute_credit"
            })
            row_num += 1
            # Debit caisse account
            rows.append({
                "row_num": row_num,
                "account": caisse_account,
                "label": "Caisse",
                "debit": ttc,
                "credit": 0,
                "step": "cash_reroute_debit"
            })
            row_num += 1
        
        return rows

    def build_cards(self, rows):
        """
        Build formula cards from raw CSV rows.
        Groups by reference to handle multi-TVA invoices.
        """
        log.info(f"Building cards for {len(rows)} rows...")
        
        # Group by reference
        ref_groups = defaultdict(list)
        for row in rows:
            ref = row.get("ref", "UNKNOWN")
            ref_groups[ref].append(row)
        
        cards = []
        for ref, rows_in_ref in ref_groups.items():
            # Use first row for client info
            first_row = rows_in_ref[0]
            client_name = self._extract_client_name(first_row.get("client_name", ""))
            profile = self._match_client_profile(client_name)
            
            if not profile:
                log.warn(f"No profile found for client: {client_name}")
                continue
            
            # Generate formula for each row in the reference group
            all_formula_lines = []
            for row in rows_in_ref:
                formula_lines = self.generate_formula(row)
                all_formula_lines.extend(formula_lines)
            
            # Calculate totals
            total_ttc = sum(float(r.get("ttc", 0)) for r in rows_in_ref)
            total_debit = sum(l["debit"] for l in all_formula_lines)
            total_credit = sum(l["credit"] for l in all_formula_lines)
            is_balanced = abs(total_debit - total_credit) < 0.01
            
            # Count unique TVA rates
            tva_rates = sorted(set(float(r.get("tva_rate", 0)) for r in rows_in_ref if float(r.get("tva_rate", 0)) > 0))
            
            card = {
                "ref": ref,
                "client_name": client_name,
                "profile": profile,
                "row_count": len(rows_in_ref),
                "tva_rates": tva_rates,
                "total_ttc": total_ttc,
                "formula_lines": all_formula_lines,
                "total_debit": total_debit,
                "total_credit": total_credit,
                "is_balanced": is_balanced,
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
            log.info(f"  • {c['ref']:15s} | {c['client_name']:20s} | TVA: {rates_str:10s} | {c['row_count']} rows | TTC {c['total_ttc']:>11.3f} | {balance_str}")
        
        return cards

    def get_summary(self):
        """Get a summary of all generated cards"""
        if not self.cards:
            return {}
        
        total_rows = sum(c["row_count"] for c in self.cards)
        balanced_count = sum(1 for c in self.cards if c["is_balanced"])
        total_ttc = sum(c["total_ttc"] for c in self.cards)
        
        return {
            "total_cards": len(self.cards),
            "total_rows": total_rows,
            "balanced_cards": balanced_count,
            "unbalanced_cards": len(self.cards) - balanced_count,
            "total_ttc": total_ttc,
        }
        