# Modules/FormulaEngine.py
import json
import os
from collections import defaultdict
from Debug.Logger import ColorLogger as log


class FormulaEngine:
    """
    Generates accounting formula cards from raw CSV data.
    Handles both Vente (Sales) and Bank transactions.
    Groups rows by reference (for multi-TVA invoices) or by keyword (for bank).
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
            return client_field.split(" | ", 1)[1].strip()
        return client_field.strip()

    def _match_client_profile(self, client_name):
        """Match client name against profiles in Vente_Formats.json"""
        profiles = self.vente_formats.get("client_profiles", [])
        
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
        rates = self.vente_rules.get("accounting_logic", {}).get("tax_logic", {}).get("rates", [])
        try:
            target = float(tva_rate)
        except (TypeError, ValueError):
            return None, None
        
        for rate_config in rates:
            if float(rate_config.get("rate", -1)) == target:
                return rate_config.get("ht_account"), rate_config.get("tva_account")
        return None, None

    def _match_bank_keyword(self, label):
        """Match bank transaction label against keywords in Bank_Formats.json"""
        mappings = self.bank_formats.get("mappings", [])
        label_upper = label.upper() if label else ""
        
        for mapping in mappings:
            keyword = mapping.get("keyword", "").upper()
            if keyword and keyword in label_upper:
                return mapping
        
        return None

    def generate_vente_formula(self, rows_in_group):
        """
        Generate formula for a group of sale rows (same reference, possibly multiple TVA rates).
        Returns list of accounting entries.
        """
        if not rows_in_group:
            return []
        
        # Use first row for client info
        first_row = rows_in_group[0]
        client_name = self._extract_client_name(first_row.get("client_name", ""))
        profile, match_type, match_key = self._match_client_profile(client_name)
        
        if not profile:
            log.warn(f"No profile found for client: {client_name}")
            return []
        
        compte_client = profile.get("compte_client")
        use_timbre = profile.get("use_timbre", False)
        use_cash = profile.get("use_cash", False)
        
        # Calculate totals across all rows in group
        total_ttc = sum(float(r.get("ttc", 0) or 0) for r in rows_in_group)
        
        lines = []
        
        # Step 1: Client Total (Debit TTC)
        lines.append({
            "step": "client_total",
            "account": compte_client,
            "label": client_name,
            "debit": total_ttc,
            "credit": 0,
        })
        
        # Step 2 & 3: TVA and Revenue for each row (handle multi-TVA)
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
        
        # Step 4: Timbre Fiscal (if applicable)
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
        
        # Step 5: Cash Reroute (if applicable)
        if use_cash:
            caisse_account = profile.get("compte_caisse", "541100")
            
            lines.append({
                "step": "cash_reroute_credit",
                "account": compte_client,
                "label": "Cash reroute",
                "debit": 0,
                "credit": total_ttc,
            })
            
            lines.append({
                "step": "cash_reroute_debit",
                "account": caisse_account,
                "label": "Caisse",
                "debit": total_ttc,
                "credit": 0,
            })
        
        return lines

    def generate_bank_formula(self, row):
        """
        Generate formula for a single bank transaction.
        Returns list of accounting entries.
        """
        label = row.get("label", "")
        amount = float(row.get("amount", 0) or 0)
        
        # Match keyword
        mapping = self._match_bank_keyword(label)
        if not mapping:
            log.warn(f"No mapping found for bank label: {label}")
            return []
        
        # Determine inversion logic
        is_expense = amount < 0
        inversion = self.bank_rules.get("inversion_logic", {})
        
        if is_expense:
            logic = inversion.get("doc_debit_means", {})
            bank_action = logic.get("bank_action", "credit")
            counterpart_action = logic.get("counterpart_action", "debit")
        else:
            logic = inversion.get("doc_credit_means", {})
            bank_action = logic.get("bank_action", "debit")
            counterpart_action = logic.get("counterpart_action", "credit")
        
        bank_pivot = self.bank_rules.get("bank_account_pivot", "532100")
        abs_amount = abs(amount)
        
        lines = []
        
        # Bank pivot line
        lines.append({
            "step": "bank_pivot",
            "account": bank_pivot,
            "label": label,
            "debit": abs_amount if bank_action == "debit" else 0,
            "credit": abs_amount if bank_action == "credit" else 0,
        })
        
        # Counterpart line(s)
        if mapping.get("is_split"):
            # Handle TVA split
            tax_calc = self.bank_rules.get("tax_calculation", {})
            detect_keyword = tax_calc.get("detect_keyword", "DONT TVA:")
            
            if detect_keyword.upper() in label.upper():
                # Extract TVA amount from label
                try:
                    tva_part = label.split(detect_keyword)[-1].strip()
                    tva_amt = float(tva_part.replace(",", "").replace(" ", ""))
                    base_amt = abs_amount - tva_amt
                    
                    base_account = mapping.get("base_account", tax_calc.get("base_account", "627000"))
                    tax_account = mapping.get("tax_account", tax_calc.get("default_tax_account", "436619"))
                    
                    lines.append({
                        "step": "base",
                        "account": base_account,
                        "label": mapping.get("label", "Base"),
                        "debit": base_amt if counterpart_action == "debit" else 0,
                        "credit": base_amt if counterpart_action == "credit" else 0,
                    })
                    
                    lines.append({
                        "step": "tax",
                        "account": tax_account,
                        "label": "TVA",
                        "debit": tva_amt if counterpart_action == "debit" else 0,
                        "credit": tva_amt if counterpart_action == "credit" else 0,
                    })
                except Exception as e:
                    log.error(f"Failed to parse TVA split: {e}")
                    # Fallback to single line
                    lines.append({
                        "step": "counterpart",
                        "account": mapping.get("account", "627000"),
                        "label": mapping.get("label", "Unknown"),
                        "debit": abs_amount if counterpart_action == "debit" else 0,
                        "credit": abs_amount if counterpart_action == "credit" else 0,
                    })
            else:
                # No TVA detected, use single line
                lines.append({
                    "step": "counterpart",
                    "account": mapping.get("account", "627000"),
                    "label": mapping.get("label", "Unknown"),
                    "debit": abs_amount if counterpart_action == "debit" else 0,
                    "credit": abs_amount if counterpart_action == "credit" else 0,
                })
        else:
            # Single counterpart line
            lines.append({
                "step": "counterpart",
                "account": mapping.get("account", "627000"),
                "label": mapping.get("label", "Unknown"),
                "debit": abs_amount if counterpart_action == "debit" else 0,
                "credit": abs_amount if counterpart_action == "credit" else 0,
            })
        
        return lines

    def build_vente_cards(self, rows):
        """
        Build formula cards for sale transactions.
        Groups rows by reference to handle multi-TVA invoices.
        """
        log.info(f"Building vente cards for {len(rows)} rows...")
        
        # Group by reference
        ref_groups = defaultdict(list)
        for row in rows:
            ref = row.get("ref", "UNKNOWN")
            ref_groups[ref].append(row)
        
        cards = []
        for ref, rows_in_ref in ref_groups.items():
            # Generate formula for this reference group
            formula_lines = self.generate_vente_formula(rows_in_ref)
            
            # Extract client info from first row
            first_row = rows_in_ref[0]
            client_name = self._extract_client_name(first_row.get("client_name", ""))
            profile, match_type, match_key = self._match_client_profile(client_name)
            
            # Calculate totals
            total_ttc = sum(float(r.get("ttc", 0) or 0) for r in rows_in_ref)
            total_debit = sum(l["debit"] for l in formula_lines)
            total_credit = sum(l["credit"] for l in formula_lines)
            is_balanced = abs(total_debit - total_credit) < 0.01
            
            # Count unique TVA rates
            tva_rates = sorted(set(float(r.get("tva_rate", 0) or 0) for r in rows_in_ref if float(r.get("tva_rate", 0) or 0) > 0))
            
            card = {
                "ref": ref,
                "client_name": client_name,
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
            }
            
            cards.append(card)
        
        # Sort by reference
        cards.sort(key=lambda c: c["ref"])
        
        log.success(f"Built {len(cards)} vente cards")
        for c in cards:
            rates_str = "+".join(f"{int(r)}%" for r in c["tva_rates"]) if c["tva_rates"] else "N/A"
            balance_str = "✓" if c["is_balanced"] else "✗"
            log.info(f"  • {c['ref']:15s} | {c['match_key']:20s} | TVA: {rates_str:10s} | {c['row_count']} rows | TTC {c['total_ttc']:>11.3f} | {balance_str}")
        
        return cards

    def build_bank_cards(self, rows):
        """
        Build formula cards for bank transactions.
        Each row is a separate card (no grouping).
        """
        log.info(f"Building bank cards for {len(rows)} rows...")
        
        cards = []
        for row in rows:
            formula_lines = self.generate_bank_formula(row)
            
            # Extract info
            label = row.get("label", "")
            amount = float(row.get("amount", 0) or 0)
            mapping = self._match_bank_keyword(label)
            
            # Calculate totals
            total_debit = sum(l["debit"] for l in formula_lines)
            total_credit = sum(l["credit"] for l in formula_lines)
            is_balanced = abs(total_debit - total_credit) < 0.01
            
            card = {
                "ref": row.get("ref", "UNKNOWN"),
                "label": label,
                "match_key": mapping.get("keyword", "UNKNOWN") if mapping else "NO MATCH",
                "match_type": "specific" if mapping else "none",
                "mapping": mapping,
                "row_count": 1,
                "total_amount": amount,
                "formula_lines": formula_lines,
                "total_debit": total_debit,
                "total_credit": total_credit,
                "is_balanced": is_balanced,
            }
            
            cards.append(card)
        
        log.success(f"Built {len(cards)} bank cards")
        
        return cards

    def build_cards(self, rows, doc_type="Vente"):
        """
        Main entry point. Builds formula cards based on document type.
        """
        self.cards = []
        
        if doc_type == "Vente":
            self.cards = self.build_vente_cards(rows)
        elif doc_type == "Bank":
            self.cards = self.build_bank_cards(rows)
        else:
            log.error(f"Unknown document type: {doc_type}")
        
        return self.cards

    def get_summary(self):
        """Get a summary of all generated cards"""
        if not self.cards:
            return {}
        
        total_rows = sum(c["row_count"] for c in self.cards)
        balanced_count = sum(1 for c in self.cards if c["is_balanced"])
        
        return {
            "total_cards": len(self.cards),
            "total_rows": total_rows,
            "balanced_cards": balanced_count,
            "unbalanced_cards": len(self.cards) - balanced_count,
        }
        