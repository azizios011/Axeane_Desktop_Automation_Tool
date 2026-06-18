# Models/EcritureTable.py
from Function.JS_Elements import AxeaneJS

class EcritureTable:
    def __init__(self, page):
        self.page = page
        self.js = AxeaneJS(page)

    async def add_new_row(self):
        # Triggers the AngularJS controller function
        await self.js.click_ng_button("ajouterEcriture()")
        # Wait for DOM to render the new row
        await self.page.wait_for_timeout(300)

    async def set_compte(self, row_index: int, account_code: str):
        # Axeane generates dynamic IDs for typeaheads: #cc_{rowIndex}_2
        input_selector = f"#cc_{row_index}_2"
        await self.js.select_typeahead(input_selector, account_code)

    async def set_libelle(self, row_index: int, label: str):
        # Axeane generates dynamic IDs for row libelles: #exlibelle{rowIndex}
        input_selector = f"#exlibelle{row_index}"
        await self.js.fill_ng_input(input_selector, label)

    async def set_debit(self, row_index: int, amount: float):
        # Axeane generates dynamic IDs for debits: #debit-eavp-{rowIndex}
        input_selector = f"#debit-eavp-{row_index}"
        await self.js.fill_ng_input(input_selector, str(amount))

    async def set_credit(self, row_index: int, amount: float):
        # Axeane generates dynamic IDs for credits: #credit-eavp-{rowIndex}
        input_selector = f"#credit-eavp-{row_index}"
        await self.js.fill_ng_input(input_selector, str(amount))
        