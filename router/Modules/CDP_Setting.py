# Modules/CDP_Setting.py
import os
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

class CDPManager:
    """
    Manages Chrome DevTools Protocol (CDP) and PWA browser launch configurations.
    Allows connecting to an existing logged-in browser or using a persistent profile.
    """
    MODE_NORMAL = "Normal Launch"
    MODE_PERSISTENT = "Persistent Profile (Keep Login)"
    MODE_CDP_CONNECT = "Connect to Existing CDP"
    MODE_PWA = "PWA Mode (Standalone App)"

    def __init__(self, settings: dict):
        self.mode = settings.get("mode", self.MODE_NORMAL)
        self.cdp_port = settings.get("cdp_port", 9222)
        self.profile_dir = settings.get("profile_dir", "./axeane_browser_profile")
        self.pwa_url = settings.get("pwa_url", "https://kompta.axeane.com")
        self.headless = settings.get("headless", False)

    async def get_browser_and_page(self) -> tuple[Browser, Page]:
        """
        Launches or connects to the browser based on the selected mode.
        Returns a tuple of (Browser, Page).
        """
        playwright = await async_playwright().start()
        browser = None
        page = None

        if self.mode == self.MODE_CDP_CONNECT:
            print(f"[CDP] 🔌 Connecting to existing browser on port {self.cdp_port}...")
            try:
                browser = await playwright.chromium.connect_over_cdp(f"http://localhost:{self.cdp_port}")
                # Get the first available context and page, or create a new one
                if browser.contexts:
                    context = browser.contexts[0]
                    page = context.pages[0] if context.pages else await context.new_page()
                else:
                    context = await browser.new_context()
                    page = await context.new_page()
            except Exception as e:
                raise ConnectionError(
                    f"Failed to connect to CDP on port {self.cdp_port}. "
                    f"Did you launch Chrome with --remote-debugging-port={self.cdp_port}?"
                ) from e

        elif self.mode == self.MODE_PERSISTENT:
            print(f"[CDP] 💾 Launching with persistent profile: {self.profile_dir}")
            os.makedirs(self.profile_dir, exist_ok=True)
            # Persistent context keeps cookies/localStorage alive between runs
            context = await playwright.chromium.launch_persistent_context(
                user_data_dir=self.profile_dir,
                headless=self.headless,
                args=["--disable-blink-features=AutomationControlled"]
            )
            browser = context.browser # Note: persistent context acts as the browser
            page = context.pages[0] if context.pages else await context.new_page()

        elif self.mode == self.MODE_PWA:
            print(f"[CDP] 🚀 Launching in PWA (Standalone) mode for {self.pwa_url}")
            browser = await playwright.chromium.launch(
                headless=self.headless,
                args=[
                    f"--app={self.pwa_url}",
                    "--disable-extensions",
                    "--disable-blink-features=AutomationControlled"
                ]
            )
            context = await browser.new_context()
            page = await context.new_page()
            # In PWA mode, the URL is loaded via the --app flag, but we ensure it's active
            if self.pwa_url not in page.url:
                await page.goto(self.pwa_url)

        else: # Normal Launch
            print("[CDP] 🌐 Launching standard browser instance...")
            browser = await playwright.chromium.launch(headless=self.headless)
            context = await browser.new_context()
            page = await context.new_page()

        return browser, page

    async def cleanup(self, browser: Browser):
        """Safely closes the browser/context depending on how it was launched."""
        try:
            if self.mode == self.MODE_CDP_CONNECT:
                # Do NOT close the browser if we just connected to it!
                await browser.close() 
            elif self.mode == self.MODE_PERSISTENT:
                # Persistent context is closed directly
                await browser.contexts[0].close() if browser.contexts else None
            else:
                await browser.close()
        except Exception as e:
            print(f"[CDP] Warning during cleanup: {e}")
            