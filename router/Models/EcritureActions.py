# Models/EcritureActions.py
from Function.JS_Elements import AxeaneJS

class EcritureActions:
    def __init__(self, page):
        self.page = page
        self.js = AxeaneJS(page)

    async def click_save(self):
        # Selector from DOM: button#ec-save (ng-click="saveEcriture()")
        await self.js.click_ng_button("saveEcriture()")
        # Wait for the network request to finish and the form to reset
        await self.page.wait_for_load_state('networkidle')

    async def click_balance(self):
        # Triggers the AngularJS controller function to auto-balance Debit/Credit
        await self.js.click_ng_button("equilibrerEcriture()")
        await self.page.wait_for_timeout(500)

    async def click_add_row(self):
        await self.js.click_ng_button("ajouterEcriture()")
        
    async def click_delete_all(self):
        await self.js.click_ng_button("resetEcritures()")
        