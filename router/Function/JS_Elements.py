# Function/JS_Elements.py
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError
import asyncio

class AxeaneJS:
    """
    Handles interactions with AngularJS specific elements in Axeane Kompta.
    Standard Playwright methods often fail to trigger AngularJS digest cycles,
    so this class uses targeted events and JS evaluations.
    """
    def __init__(self, page: Page):
        self.page = page

    # ==========================================
    # 1. STANDARD NG-MODEL INPUTS
    # ==========================================
    async def fill_ng_input(self, selector: str, value: str):
        """
        Fills an input bound to ng-model and ensures AngularJS updates the scope.
        Used for: Date, Ref/Doc Number, Label, Debit, Credit.
        """
        el = self.page.locator(selector)
        await el.click()
        await el.fill(value)
        # Trigger blur and change events to force AngularJS digest cycle
        await el.dispatch_event('blur')
        await el.dispatch_event('change')
        await self.page.wait_for_timeout(100)

    # ==========================================
    # 2. NYA-BS-SELECT DROPDOWNS
    # ==========================================
    async def select_nya_bs_select(self, ng_model: str, option_text: str):
        """
        Selects an option from a nya-bs-select dropdown.
        Used for: Journal, Month, Currency, Treasury Operation.
        """
        # Locate the ol element by ng-model
        ol_selector = f'ol[ng-model="{ng_model}"].nya-bs-select'
        ol_el = self.page.locator(ol_selector)
        
        # Click the dropdown button to open it
        button = ol_el.locator('button.dropdown-toggle')
        await button.click()
        
        # Wait for the dropdown menu to be visible
        dropdown_ul = ol_el.locator('ul.dropdown-menu.inner')
        await dropdown_ul.wait_for(state='visible')
        
        # Find and click the option
        option = dropdown_ul.locator(f'li:has-text("{option_text}")').first
        await option.click()
        
        # Wait for dropdown to close and ng-change to process
        await dropdown_ul.wait_for(state='hidden')
        await self.page.wait_for_timeout(200) 

    # ==========================================
    # 3. UIB-TYPEAHEAD (ACCOUNT SEARCH)
    # ==========================================
    async def select_typeahead(self, input_selector: str, search_text: str):
        """
        Selects an option from a uib-typeahead input.
        Used for: Compte Comptable (Account selection).
        """
        input_el = self.page.locator(input_selector)
        await input_el.click()
        await input_el.fill(search_text)
        
        # Wait for the typeahead popup to appear
        popup_selector = 'ul[uib-typeahead-popup][style*="display: block"]'
        popup = self.page.locator(popup_selector).last
        await popup.wait_for(state='visible', timeout=5000)
        
        # Click the matching option
        option = popup.locator(f'li:has-text("{search_text}")').first
        await option.click()
        
        # Trigger blur to ensure model update
        await input_el.dispatch_event('blur')
        await self.page.wait_for_timeout(200)

    # ==========================================
    # 4. BUTTONS & TABLE ACTIONS
    # ==========================================
    async def click_ng_button(self, ng_click_expr: str):
        """
        Clicks a button by its ng-click expression.
        """
        button = self.page.locator(f'button[ng-click="{ng_click_expr}"]')
        await button.click()
        # Wait for network to settle after button click (e.g., saving)
        try:
            await self.page.wait_for_load_state('networkidle', timeout=5000)
        except PlaywrightTimeoutError:
            pass 

    async def add_table_row(self):
        """Clicks the 'Add Row' (+) button in the ecriture table."""
        await self.click_ng_button('ajouterEcriture()')

    async def save_ecriture(self):
        """Clicks the 'Save' (Enregistrer) button."""
        await self.click_ng_button('saveEcriture()')

    async def balance_ecriture(self):
        """Clicks the 'Balance' (Equilibrer) button."""
        await self.click_ng_button('equilibrerEcriture()')

    async def get_table_row_count(self):
        """Returns the number of rows currently in the ecriture table."""
        rows = self.page.locator('table.td-t tbody tr.td-row')
        return await rows.count()
        