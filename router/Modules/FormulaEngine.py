# Modules/FormulaEngine.py
from Logic.accounts import AccountManager
from Logic.rules import RulesEngine
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

    def build_cards(self, rows: list) -> list:
        """
        Input:  list of parsed invoice dicts (one per CSV row)
        Output: list of FormulaCard dicts, one per unique client match
        """
        # Group rows by (match_key, match_type)
        groups = defaultdict(list)
        for row in rows:
            client_field = row.get("client_name", "") or ""
            info = self.accounts.get_profile(client_field)
            key = (info["match_key"] or "__UNMATCHED__", info["match_type"])
            groups[key].append((row, info))

        cards = []
        for (match_key, match_type), items in groups.items():
            # Use the first row as the "sample" for formula generation
            sample_row, sample_info = items[0]
            profile = sample_info["profile"]

            # Generate the formula (all rows in this group share it)
            formula_lines = self.rules.generate_formula(sample_row, profile)

            # Aggregate totals
            total_ttc = sum(float(r.get("ttc", 0) or 0) for r, _ in items)
            total_debit = sum(l["debit"] for l in formula_lines)
            total_credit = sum(l["credit"] for l in formula_lines)
            is_balanced = abs(total_debit - total_credit) < 0.01

            cards.append({
                "match_key": match_key,
                "match_type": match_type,           # "specific" | "default" | "none"
                "profile": profile,
                "row_count": len(items),
                "total_ttc": total_ttc,
                "formula_lines": formula_lines,
                "total_debit": total_debit,
                "total_credit": total_credit,
                "is_balanced": is_balanced,
                "sample_client": sample_row.get("client_name", ""),
            })

        # Sort: specific first, then default, then unmatched; largest groups first
        priority = {"specific": 0, "default": 1, "none": 2}
        cards.sort(key=lambda c: (priority.get(c["match_type"], 9),
                                  -c["row_count"]))

        log.success(f"Built {len(cards)} formula cards covering {len(rows)} rows")
        for c in cards:
            log.info(f"  • [{c['match_type'].upper():8s}] {c['match_key']:30s} "
                     f"→ {c['row_count']:3d} rows, TTC {c['total_ttc']:>11.3f}")

        return cards
        