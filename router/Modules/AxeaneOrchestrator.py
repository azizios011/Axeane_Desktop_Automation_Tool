# Modules/AxeaneOrchestrator.py
import asyncio
from Models.EcritureHeader import EcritureHeader
from Models.EcritureTable import EcritureTable
from Models.EcritureActions import EcritureActions
from Debug.Logger import ColorLogger as log

MONTHS_FR = [
    "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
    "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
]

class AxeaneOrchestrator:
    """
    Orchestrates the filling of individual invoices into Axeane.
    It uses the Formula Cards as templates for the accounting lines.
    """
    def __init__(self, page, shared_state):
        self.page = page
        self.state = shared_state
        self.header = EcritureHeader(page)
        self.table = EcritureTable(page)
        self.actions = EcritureActions(page)
        self._stop_flag = False

    def stop(self):
        self._stop_flag = True

    def _get_mois_text(self, date_str):
        """Converts '02/03/2026' to 'Mars 2026'."""
        try:
            parts = date_str.strip().split("/")
            day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
            return f"{MONTHS_FR[month - 1]} {year}"
        except:
            return "Mars 2026" # Fallback

    def _find_card_for_row(self, row, cards):
        """Finds which formula card (template) applies to this specific row."""
        from Logic.accounts import AccountManager
        am = AccountManager()
        client_name = row.get("client_name", "")
        info = am.get_profile(client_name)
        match_key = info["match_key"]
        
        # Find the card with the matching match_key
        for card in cards:
            if card["match_key"] == match_key:
                return card
        
        # Fallback to DEFAULT card
        for card in cards:
            if card["match_type"] == "default":
                return card
        return None

    def _generate_lines_for_row(self, row, card):
        """Generates the specific accounting lines for a single row using the card's profile."""
        from Logic.rules import RulesEngine
        rules = RulesEngine()
        # This recalculates the exact debits/credits for this specific row's amounts
        return rules.generate_formula(row, card["profile"])

    async def fill_one_invoice(self, row, card):
        """Fills the Axeane form for a single invoice row."""
        ref = row.get("ref", "UNKNOWN")
        date_str = row.get("date", "")
        client_name = row.get("client_name", "")
        
        # 1. Generate specific lines for this row
        lines = self._generate_lines_for_row(row, card)
        
        # 2. Determine journal (CA for cash clients, VT for others)
        journal = "CA" if card["profile"].get("use_cash") else "VT"
        mois_text = self._get_mois_text(date_str)
        
        # Clean ref (e.g., "FC000761/2026" -> "FC000761")
        clean_ref = ref.split("/")[0] if "/" in ref else ref
        
        log.info(f"Filling {clean_ref} | {client_name[:30]} | {len(lines)} lines | Journal: {journal}")

        # 3. Fill header
        await self.header.fill_all(
            date_str=date_str,
            journal=journal,
            mois=mois_text,
            ref=clean_ref,
            libelle=client_name[:120].upper(),
        )

        # 4. Fill table rows
        await self.table.fill_formula(lines)

        # 5. Save
        await self.actions.save()

        # 6. Wait for form to reset for the next entry
        await self.actions.wait_for_form_ready()

        log.success(f"✅ {clean_ref} saved successfully")

    async def run_all(self, raw_data, cards, progress_callback=None):
        """Runs through all raw data rows, using the cards as templates."""
        self._stop_flag = False
        total = len(raw_data)
        success = 0
        failed = 0

        log.info(f"🚀 Starting automation for {total} invoices...")

        for i, row in enumerate(raw_data):
            if self._stop_flag:
                log.warn("⛔ Stopped by user")
                break

            # Find the template (card) for this specific row
            card = self._find_card_for_row(row, cards)
            if not card:
                log.error(f"No formula card found for {row.get('client_name')}")
                failed += 1
                continue

            try:
                await self.fill_one_invoice(row, card)
                success += 1
            except Exception as e:
                failed += 1
                # Now it will correctly print the actual ref instead of '?'
                log.error(f"❌ Failed {row.get('ref', '?')}: {e}")
                
                # Try to recover by clearing the form
                try:
                    await self.actions.delete_all()
                    await self.actions.wait_for_form_ready()
                except Exception:
                    pass

            if progress_callback:
                progress_callback(i + 1, total, success, failed)

            # Small delay to avoid overwhelming the browser/AngularJS
            await asyncio.sleep(0.5)

        log.success(f"🏁 Done! {success} succeeded, {failed} failed out of {total}")
        return success, failed
        