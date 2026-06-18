# Models/EcritureActions.py
from Function.JS_Elements import AxeaneJS
from Debug.Logger import ColorLogger as log


class EcritureActions:
    """Handles the action buttons (Save, Balance, Delete, etc.)."""

    SEL_SAVE = "#ec-save"
    SEL_BALANCE = 'button[ng-click="equilibrerEcriture()"]'
    SEL_ADD_ROW = 'button[ng-click="ajouterEcriture()"]'
    SEL_DELETE = 'button[ng-click="deleteEcritures()"]'

    def __init__(self, page):
        self.page = page
        self.js = AxeaneJS(page)

    async def save(self):
        """Click Save and wait for the form to reset."""
        await self.js.click_button_id("ec-save")
        # Wait for the form to reset (the ref field becomes empty again)
        await self.page.wait_for_timeout(1500)
        log.debug("Actions: Saved successfully")

    async def balance(self):
        """Click the Balance (Équilibrer) button."""
        await self.page.locator(self.SEL_BALANCE).click()
        await self.page.wait_for_timeout(500)
        log.debug("Actions: Balanced")

    async def delete_all(self):
        """Delete all rows in the current form."""
        await self.page.locator(self.SEL_DELETE).click()
        await self.page.wait_for_timeout(500)

    async def wait_for_form_ready(self, timeout: int = 10000):
        """Wait until the form is ready for a new entry."""
        # The ref field should be empty and visible
        ref_field = self.page.locator("#idDocumentInputMD2, #idDocumentInputTD")
        await ref_field.wait_for(state="visible", timeout=timeout)
        await self.page.wait_for_timeout(300)
        