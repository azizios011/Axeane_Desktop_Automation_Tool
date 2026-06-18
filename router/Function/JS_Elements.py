# Function/JS_Elements.py
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError
from Debug.Logger import ColorLogger as log


class AxeaneJS:
    """Handles AngularJS-specific interactions with Axeane Kompta."""

    def __init__(self, page: Page):
        self.page = page

    # ── Standard ng-model inputs ──────────────────────────────────
    async def fill_ng_input(self, selector: str, value: str, clear_first: bool = True):
        el = self.page.locator(selector)
        await el.wait_for(state="visible", timeout=5000)
        if clear_first:
            await el.click(click_count=3)  # triple-click to select all
            await el.press("Backspace")
        await el.fill(str(value))
        await el.dispatch_event("blur")
        await el.dispatch_event("change")
        await self.page.wait_for_timeout(150)

    # ── nya-bs-select dropdowns ───────────────────────────────────
    async def select_nya_bs_select(self, ol_id: str, option_text: str):
        """Select an option from a nya-bs-select dropdown by its ID."""
        ol = self.page.locator(f"ol#{ol_id}.nya-bs-select")
        await ol.wait_for(state="visible", timeout=5000)
        button = ol.locator("button.dropdown-toggle")
        await button.click()
        dropdown = ol.locator("ul.dropdown-menu.inner")
        await dropdown.wait_for(state="visible", timeout=3000)
        # Find the option by exact text match
        option = dropdown.locator(f"li > a:has-text('{option_text}')").first
        await option.click()
        await dropdown.wait_for(state="hidden", timeout=3000)
        await self.page.wait_for_timeout(300)

    async def select_nya_by_ng_model(self, ng_model: str, option_text: str):
        """Fallback: select by ng-model attribute."""
        ol = self.page.locator(f'ol[ng-model="{ng_model}"].nya-bs-select')
        await ol.locator("button.dropdown-toggle").click()
        dropdown = ol.locator("ul.dropdown-menu.inner")
        await dropdown.wait_for(state="visible", timeout=3000)
        await dropdown.locator(f"li > a:has-text('{option_text}')").first.click()
        await dropdown.wait_for(state="hidden", timeout=3000)
        await self.page.wait_for_timeout(300)

    # ── uib-typeahead (account search) ────────────────────────────
    async def select_typeahead(self, input_id: str, search_text: str):
        """Type into a uib-typeahead input and select the first matching option."""
        inp = self.page.locator(f"input#{input_id}")
        await inp.wait_for(state="visible", timeout=5000)
        await inp.click(click_count=3)
        await inp.fill(search_text)
        # Wait for the typeahead popup
        popup = self.page.locator('ul[uib-typeahead-popup][style*="display: block"]').last
        await popup.wait_for(state="visible", timeout=5000)
        # Click the first matching option
        option = popup.locator(f"li:has-text('{search_text}')").first
        await option.click()
        await inp.dispatch_event("blur")
        await self.page.wait_for_timeout(200)

    # ── ng-click buttons ──────────────────────────────────────────
    async def click_ng_button(self, ng_click_expr: str):
        btn = self.page.locator(f'button[ng-click="{ng_click_expr}"]')
        await btn.wait_for(state="visible", timeout=5000)
        await btn.click()
        try:
            await self.page.wait_for_load_state("networkidle", timeout=5000)
        except PlaywrightTimeoutError:
            pass

    async def click_button_id(self, button_id: str):
        btn = self.page.locator(f"button#{button_id}")
        await btn.wait_for(state="visible", timeout=5000)
        await btn.click()
        try:
            await self.page.wait_for_load_state("networkidle", timeout=8000)
        except PlaywrightTimeoutError:
            pass

    # ── AngularJS scope helpers ───────────────────────────────────
    async def get_scope_value(self, selector: str, var_path: str):
        """Read a value from AngularJS scope."""
        js = f"""
            const el = document.querySelector('{selector}');
            if (!el) return null;
            const scope = angular.element(el).scope();
            if (!scope) return null;
            return eval('scope.' + '{var_path}');
        """
        return await self.page.evaluate(js)

    async def set_scope_value(self, selector: str, var_path: str, value):
        """Write a value to AngularJS scope and trigger digest."""
        import json
        js = f"""
            const el = document.querySelector('{selector}');
            const scope = angular.element(el).scope();
            scope.{var_path} = {json.dumps(value)};
            if (!scope.$$phase) scope.$apply();
        """
        await self.page.evaluate(js)
        