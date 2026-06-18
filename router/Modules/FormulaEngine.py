# Modules/FormulaEngine.py
import json
import os
from collections import defaultdict
from Debug.Logger import ColorLogger as log


class FormulaEngine:
    """
    Groups invoice rows by reference, then generates formulas.
    Handles multi-TVA invoices (same reference, different TVA rates).
    """

    def __init__(self):
        self.accounts = self._load_json("DB/Vente_Formats.json")
        self.rules = self._load_json("DB/Vente_Rules.json")

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
            return client_field.split(" | ", 1)[1].strip()
        return client_field.strip()

    def _match_client_profile(self, client_name):
        """Match client name against profiles in Vente_Formats.json"""
        profiles = self.accounts.get("client_profiles", [])
        
        # Try to match exact client name first
        for profile in profiles:
            match_key = profile.get("match", "").upper()
            if match_key == "DEFAULT":
                continue
            if match_key and match_key in client_name.upper():
                return profile, "specific", match_key
        
        # Fallback to DEFAULT profile
        for profile in profiles:
            if profile.get("match", "").upper() == "DEFAULT":
                return profile, "default", "DEFAULT"
        
        return None, "none", None

    def _get_tax_accounts(self, tva_rate):
        """Get HT and TVA accounts based on tax rate"""
        rates = self.rules.get("accounting_logic", {}).get("tax_logic", {}).get("rates", [])
        try:
            target = float(tva_rate)
        except (TypeError, ValueError):
            return None, None
        
        for rate_config in rates:
            if float(rate_config.get("rate", -1)) == target:
                return rate_config.get("ht_account"), rate_config.get("tva_account")
        return None, None

    def _generate_formula_lines(self, rows_in_group, profile):
        """
        Generate accounting lines for a group of rows (same reference).
        For multi-TVA invoices, generates lines for each TVA rate.
        """
        if not profile or not rows_in_group:
            return []
        
        lines = []
        
        # Use first row for client info and TTC (all rows share the same TTC)
        first_row = rows_in_group[0]
        client_name = self._extract_client_name(first_row.get("client_name", ""))
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
        
        # Step 4: Timbre Fiscal (if applicable) - ONCE per invoice
        if use_timbre:
            timbre_cfg = self.rules.get("accounting_logic", {}).get("timbre_fiscal", {})
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
            profile, match_type, match_key = self._match_client_profile(client_name)
            
            if not profile:
                log.warn(f"No profile found for client: {client_name}")
                continue
            
            # Generate formula lines for this reference group
            formula_lines = self._generate_formula_lines(rows_in_ref, profile)
            
            # Calculate totals - TTC is from first row only (all rows share same TTC)
            total_ttc = float(first_row.get("ttc", 0) or 0)
            total_debit = sum(l["debit"] for l in formula_lines)
            total_credit = sum(l["credit"] for l in formula_lines)
            is_balanced = abs(total_debit - total_credit) < 0.01
            
            # Count unique TVA rates
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
                "sample_client": client_name,
            }
            
            cards.append(card)
            
            if not is_balanced:
                log.warn(f"Formula for {ref} is NOT balanced! Debit: {total_debit}, Credit: {total_credit}")
        
        # Sort by reference
        cards.sort(key=lambda c: c["ref"])
        
        log.success(f"Built {len(cards)} cards")
        for c in cards:
            rates_str = "+".join(f"{int(r)}%" for r in c["tva_rates"]) if c["tva_rates"] else "N/A"
            balance_str = "✓" if c["is_balanced"] else "✗"
            log.info(f"  • {c['ref']:15s} | {c['sample_client'][:20]:20s} | TVA: {rates_str:10s} | {c['row_count']} rows | TTC {c['total_ttc']:>11.3f} | {balance_str}")
        
        return cards

    def get_summary(self):
        """Get a summary of all generated cards"""
        if not hasattr(self, 'cards') or not self.cards:
            return {
                "total_cards": 0,
                "total_rows": 0,
                "balanced_cards": 0,
                "unbalanced_cards": 0,
            }
        
        total_rows = sum(c["row_count"] for c in self.cards)
        balanced_count = sum(1 for c in self.cards if c["is_balanced"])
        
        return {
            "total_cards": len(self.cards),
            "total_rows": total_rows,
            "balanced_cards": balanced_count,
            "unbalanced_cards": len(self.cards) - balanced_count,
        }
        