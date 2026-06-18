# Modules/FormulaEngine.py
import json
from Debug.Logger import ColorLogger as log

class FormulaEngine:
    """
    Generates the exact row-by-row formula for each invoice based on:
    - CSV data (parsed invoices)
    - Vente_Formats.json (client profiles)
    - Vente_Rules.json (accounting logic)
    """
    
    def __init__(self):
        self.vente_formats = self._load_json("DB/Vente_Formats.json")
        self.vente_rules = self._load_json("DB/Vente_Rules.json")
        self.formulas = []
        
    def _load_json(self, path):
        """Load JSON with automatic key stripping"""
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
    
    def process_all_invoices(self, invoices):
        """
        Process all invoices and generate formulas.
        Returns a list of formula objects.
        """
        self.formulas = []
        
        for invoice in invoices:
            ref = invoice.get("ref", "UNKNOWN")
            client_name = self._extract_client_name(invoice.get("client_name", ""))
            profile = self._match_client_profile(client_name)
            
            rows = self.generate_formula(invoice)
            
            # Calculate totals for verification
            total_debit = sum(row["debit"] for row in rows)
            total_credit = sum(row["credit"] for row in rows)
            is_balanced = abs(total_debit - total_credit) < 0.001
            
            formula = {
                "ref": ref,
                "client_name": client_name,
                "matched_profile": profile["match"] if profile else "NO MATCH",
                "rows": rows,
                "total_debit": total_debit,
                "total_credit": total_credit,
                "is_balanced": is_balanced,
                "row_count": len(rows)
            }
            
            self.formulas.append(formula)
            
            if not is_balanced:
                log.warn(f"Formula for {ref} is NOT balanced! Debit: {total_debit}, Credit: {total_credit}")
        
        log.success(f"Generated {len(self.formulas)} formulas from {len(invoices)} invoices")
        return self.formulas
    
    def get_summary(self):
        """Get a summary of all generated formulas"""
        if not self.formulas:
            return {}
        
        total_rows = sum(f["row_count"] for f in self.formulas)
        balanced_count = sum(1 for f in self.formulas if f["is_balanced"])
        
        return {
            "total_invoices": len(self.formulas),
            "total_rows": total_rows,
            "balanced_invoices": balanced_count,
            "unbalanced_invoices": len(self.formulas) - balanced_count
        }
        