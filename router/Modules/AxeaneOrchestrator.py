# Modules/AxeaneOrchestrator.py
import asyncio
from datetime import datetime
from Models.EcritureHeader import EcritureHeader
from Models.EcritureTable import EcritureTable
from Models.EcritureActions import EcritureActions
from Debug.Logger import ColorLogger as log


# Month name mapping (French)
MONTHS_FR = {
    1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril",
    5: "Mai", 6: "Juin", 7: "Juillet", 8: "Août",
    9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre"
}


class AxeaneOrchestrator:
    """Orchestrates the filling of all formula cards into Axeane."""

    def __init__(self, page, shared_state):
        self.page = page
        self.state = shared_state
        self.header = EcritureHeader(page)
        self.table = EcritureTable(page)
        self.actions = EcritureActions(page)
        self._stop_flag = False

    def stop(self):
        self._stop_flag = True

    def _parse_date(self, date_str: str):
        """Parse dd/mm/yyyy date string."""
        try:
            return datetime.strptime(date_str.strip(), "%d/%m/%Y")
        except Exception:
            return datetime.now()

    def _mois_text(self, date_obj: datetime) -> str:
        """Convert date to Axeane month dropdown text (e.g., 'Mars 2026')."""
        return f"{MONTHS_FR[date_obj.month]} {date_obj.year}"

    async def fill_one_invoice(self, card: dict, progress_callback=None):
        """Fill one invoice (one formula card) into Axeane."""
        ref = card["ref"]
        date_str = card["date"]
        client_name = card["client_name"]
        formula_lines = card["formula_lines"]
        match_key = card["match_key"]

        date_obj = self._parse_date(date_str)
        mois_text = self._mois_text(date_obj)

        # Determine journal: if client uses cash, use CA; otherwise VT
        journal = "CA" if card.get("profile", {}).get("use_cash") else "VT"

        log.info(f"Filling {ref} | {client_name[:30]} | {len(formula_lines)} rows | Journal: {journal}")

        # 1. Fill header
        await self.header.fill_all(
            date_str=date_str,
            journal=journal,
            mois=mois_text,
            ref=ref.split("/")[0] if "/" in ref else ref,  # FC000761 from FC000761/2026
            libelle=client_name[:120].upper(),
        )

        # 2. Fill table rows
        await self.table.fill_formula(formula_lines)

        # 3. Balance (optional — Axeane auto-balances, but this ensures it)
        # await self.actions.balance()

        # 4. Save
        await self.actions.save()

        # 5. Wait for form to reset
        await self.actions.wait_for_form_ready()

        log.success(f"✅ {ref} saved successfully")

    async def run_all(self, cards: list, progress_callback=None):
        """Run through all formula cards."""
        self._stop_flag = False
        total = len(cards)
        success = 0
        failed = 0

        log.info(f"🚀 Starting automation for {total} invoices...")

        for i, card in enumerate(cards):
            if self._stop_flag:
                log.warn("⛔ Stopped by user")
                break

            try:
                await self.fill_one_invoice(card, progress_callback)
                success += 1
            except Exception as e:
                failed += 1
                log.error(f"❌ Failed {card.get('ref', '?')}: {e}")
                # Try to recover by deleting and waiting
                try:
                    await self.actions.delete_all()
                    await self.actions.wait_for_form_ready()
                except Exception:
                    pass

            if progress_callback:
                progress_callback(i + 1, total, success, failed)

            # Small delay between invoices to avoid overwhelming Axeane
            await asyncio.sleep(0.5)

        log.success(f"🏁 Done! {success} succeeded, {failed} failed out of {total}")
        return success, failed
        