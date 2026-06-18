# Models/EcritureTable.py
from Function.JS_Elements import AxeaneJS
from Debug.Logger import ColorLogger as log


class EcritureTable:
    """Fills the accounting lines table."""

    def __init__(self, page):
        self.page = page
        self.js = AxeaneJS(page)
        self.current_row = 0

    def reset(self):
        self.current_row = 0

    async def add_row(self):
        """Click the '+' button to add a new row."""
        await self.js.click_ng_button("ajouterEcriture()")
        await self.page.wait_for_timeout(400)
        self.current_row += 1
        log.debug(f"Table: Added row {self.current_row}")

    async def fill_row(self, account: str, libelle: str, debit: float, credit: float):
        """Fill one row with account, libelle, debit, and credit."""
        row_idx = self.current_row

        # Account (typeahead)
        # DOM uses IDs like cc_0_2, cc_0_3, cc_1_2, cc_1_3 depending on context
        # We'll try both patterns
        account_id = f"cc_{row_idx}_3"  # Modele2 pattern
        try:
            await self.page.locator(f"input#{account_id}").wait_for(state="visible", timeout=2000)
        except Exception:
            account_id = f"cc_{row_idx}_2"  # ModeleWithPiece pattern

        await self.js.select_typeahead(account_id, account)

        # Libellé
        libelle_id = f"exlibelle{row_idx}"
        await self.js.fill_ng_input(f"input#{libelle_id}", libelle)

        # Debit
        if debit and debit > 0:
            debit_id = f"debit-eav-{row_idx}"
            try:
                await self.page.locator(f"input#{debit_id}").wait_for(state="visible", timeout=2000)
            except Exception:
                debit_id = f"debit-eavp-{row_idx}"
            await self.js.fill_ng_input(f"input#{debit_id}", f"{debit:.3f}")

        # Credit
        if credit and credit > 0:
            credit_id = f"credit-eav-{row_idx}"
            try:
                await self.page.locator(f"input#{credit_id}").wait_for(state="visible", timeout=2000)
            except Exception:
                credit_id = f"credit-eavp-{row_idx}"
            await self.js.fill_ng_input(f"input#{credit_id}", f"{credit:.3f}")

        log.debug(f"Table: Row {row_idx} → {account} | D:{debit:.3f} C:{credit:.3f}")

    async def fill_formula(self, formula_lines: list):
        """Fill all rows from a formula card."""
        self.reset()
        for i, line in enumerate(formula_lines):
            if i > 0:
                await self.add_row()
            await self.fill_row(
                account=line["account"],
                libelle=line["label"],
                debit=line["debit"],
                credit=line["credit"],
            )
        