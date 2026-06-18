# Modules/FormulaEngine.py
import json
from Logic.accounts import AccountManager
from Logic.Rules import RulesEngine
from Debug.Logger import ColorLogger as log
from collections import defaultdict


class FormulaEngine:
    """
    Groups invoice rows by client, then generates ONE formula per unique client.
    Returns a list of FormulaCard objects.
    """

    def __init__(self):
        self.accounts = AccountManager()
        self.rules = RulesEngine()
        # Load column mapping to translate CSV headers to internal field names
        self.column_mapping = self._load_column_mapping()

    def _load_column_mapping(self):
        """Load the column mapping from Vente_Structure.json"""
        try:
            with open("DB/Vente_Structure.json", 'r', encoding='utf-8') as f:
                structure = self._strip_keys(json.load(f))
            return structure.get("column_mapping", {})
        except Exception as e:
            log.error(f"Failed to load column mapping: {e}")
            return {}

    def _strip_keys(self, d):
        """Recursively strip whitespace from dictionary keys"""
        if isinstance(d, dict):
            return {k.strip(): self._strip_keys(v) for k, v in d.items()}
        elif isinstance(d, list):
            return [self._strip_keys(i) for i in d]
        return d

    def _get_field(self, row, field_name):
        """
        Get a field value from a row, trying both CSV column name and internal field name.
        For example, to get TTC: try "TTC" first, then "ttc"
        """
        # Try CSV column name first
        if field_name in row:
            return row[field_name]
        
        # Try to find the CSV column that maps to this internal field
        for csv_col, internal_field in self.column_mapping.items():
            if internal_field.strip() == field_name:
                if csv_col in row:
                    return row[csv_col]
        
        # Fallback: try common variations
        variations = {
            "client_name": ["Client", "client"],
            "ttc": ["TTC", "ttc"],
            "tva_rate": ["TVA %", "tva_rate", "TVA"],
            "tva_amt": ["Montant TVA", "tva_amt", "TVA Amount"],
            "net_ht": ["Tot. Net. HT", "net_ht"],
        }
        
        if field_name in variations:
            for var in variations[field_name]:
                if var in row:
                    return row[var]
        
        return None

    def build_cards(self, rows: list) -> list:
        """
        Process all rows and generate formula cards grouped by client.
        """
        # Group rows by client profile
        groups = defaultdict(list)
        
        for row in rows:
            # Extract client name using flexible field access
            client_field = self._get_field(row, "client_name") or ""
            
            # Get client profile
            info = self.accounts.get_profile(client_field)
            key = (info["match_key"] or "__UNMATCHED__", info["match_type"])
            groups[key].append((row, info))

        cards = []
        for (match_key, match_type), items in groups.items():
            # Use the first row as the sample for formula generation
            sample_row, sample_info = items[0]
            profile = sample_info["profile"]

            # Generate the formula
            formula_lines = self._generate_formula(sample_row, profile)

            # Calculate totals
            total_ttc = sum(float(self._get_field(r, "ttc") or 0) for r, _ in items)
            total_debit = sum(l["debit"] for l in formula_lines)
            total_credit = sum(l["credit"] for l in formula_lines)
            is_balanced = abs(total_debit - total_credit) < 0.01

            cards.append({
                "match_key": match_key,
                "match_type": match_type,
                "profile": profile,
                "row_count": len(items),
                "total_ttc": total_ttc,
                "formula_lines": formula_lines,
                "total_debit": total_debit,
                "total_credit": total_credit,
                "is_balanced": is_balanced,
                "sample_client": client_field,
            })

        # Sort: specific first, then default, then unmatched
        priority = {"specific": 0, "default": 1, "none": 2}
        cards.sort(key=lambda c: (priority.get(c["match_type"], 9), -c["row_count"]))

        log.success(f"Built {len(cards)} formula cards covering {len(rows)} rows")
        for c in cards:
            log.info(f"  • [{c['match_type'].upper():8s}] {c['match_key']:30s} "
                     f"→ {c['row_count']:3d} rows, TTC {c['total_ttc']:>11.3f}")

        return cards

    def _generate_formula(self, row, profile):
        """
        Generate the accounting formula (journal entries) for one invoice.
        """
        if not profile:
            return []

        lines = []
        
        # Extract amounts using flexible field access
        ttc = float(self._get_field(row, "ttc") or 0)
        tva_amt = float(self._get_field(row, "tva_amt") or 0)
        net_ht = float(self._get_field(row, "net_ht") or 0)
        tva_rate = float(self._get_field(row, "tva_rate") or 0)

        if ttc == 0:
            log.warn(f"Row has TTC=0, skipping formula generation")
            return []

        # Get tax accounts based on TVA rate
        tax_acc = self.rules.get_tax_accounts(tva_rate)
        
        if not tax_acc and tva_rate > 0:
            log.warn(f"No tax accounts configured for TVA rate {tva_rate}%")

        # Step 1: Client Total (Debit TTC)
        lines.append({
            "step": "client_total",
            "account": profile.get("compte_client"),
            "label": self._extract_client_label(self._get_field(row, "client_name") or ""),
            "debit": ttc,
            "credit": 0,
        })

        # Step 2: TVA Split (Credit TVA)
        if tax_acc and tva_amt > 0:
            lines.append({
                "step": "tax_split",
                "account": tax_acc["tva_account"],
                "label": f"TVA {int(tva_rate)}%",
                "debit": 0,
                "credit": tva_amt,
            })

        # Step 3: Revenue Split (Credit HT)
        if tax_acc and net_ht > 0:
            lines.append({
                "step": "revenue_split",
                "account": tax_acc["ht_account"],
                "label": f"Revenue {int(tva_rate)}%",
                "debit": 0,
                "credit": net_ht,
            })

        # Step 4: Timbre Fiscal (if applicable)
        if profile.get("use_timbre"):
            timbre_config = self.rules.rules.get("timbre_fiscal", {})
            timbre_amount = float(timbre_config.get("default_amount", 1.0))
            timbre_account = timbre_config.get("account", "437000")
            
            lines.append({
                "step": "timbre",
                "account": timbre_account,
                "label": "TIMBRE FISCAL",
                "debit": 0,
                "credit": timbre_amount,
            })

        # Step 5: Cash Reroute (if applicable)
        if profile.get("use_cash"):
            caisse_account = profile.get("compte_caisse", "541100")
            
            # Credit client account
            lines.append({
                "step": "cash_reroute_credit",
                "account": profile.get("compte_client"),
                "label": "Cash reroute",
                "debit": 0,
                "credit": ttc,
            })
            
            # Debit caisse account
            lines.append({
                "step": "cash_reroute_debit",
                "account": caisse_account,
                "label": "Caisse",
                "debit": ttc,
                "credit": 0,
            })

        return lines

    def _extract_client_label(self, client_field):
        """Extract clean client name from field like 'C000001 | PASSAGER'"""
        if " | " in client_field:
            return client_field.split(" | ", 1)[1].strip()
        return client_field.strip()
