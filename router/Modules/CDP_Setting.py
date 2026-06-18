# Modules/CDP_Setting.py
import os
from playwright.async_api import async_playwright, Browser, Page

class CDPManager:
    MODE_NORMAL = "Standard Launch (Fresh session)"
    MODE_PERSISTENT = "Persistent Profile (Keep Login)"
    MODE_CDP_CONNECT = "Connect to Existing CDP (Attach to logged-in browser)"
    MODE_PWA = "PWA Mode (Standalone App)"

    def __init__(self, settings: dict):
        self.mode = settings.get("mode", self.MODE_NORMAL)
        self.cdp_port = settings.get("cdp_port", 9222)
        self.profile_dir = settings.get("profile_dir", "./axeane_browser_profile")
        self.pwa_url = settings.get("pwa_url", "https://kompta.axeane.com")
        self.headless = settings.get("headless", False)
        
        # New Browser Settings
        self.browser_type = settings.get("browser_type", "Chrome")
        self.executable_path = settings.get("executable_path", "")

    def _get_launch_kwargs(self):
        """Builds the arguments for playwright.chromium.launch() based on UI settings"""
        kwargs = {"headless": self.headless}
        
        # If user selected a specific browser type, use the 'channel' argument
        if self.browser_type == "Edge":
            kwargs["channel"] = "msedge"
        elif self.browser_type == "Chrome":
            kwargs["channel"] = "chrome"
            
        # If user provided a custom executable path, it overrides the channel
        if self.executable_path and os.path.exists(self.executable_path):
            kwargs["executable_path"] = self.executable_path
            # Remove channel if using custom path to avoid conflicts
            kwargs.pop("channel", None) 
            
        return kwargs

    async def get_browser_and_page(self) -> tuple[Browser, Page]:
        playwright = await async_playwright().start()
        browser = None
        page = None
        launch_args = self._get_launch_kwargs()

        if self.mode == self.MODE_CDP_CONNECT:
            print(f"[CDP] 🔌 Connecting to existing browser on port {self.cdp_port}...")
            browser = await playwright.chromium.connect_over_cdp(f"http://localhost:{self.cdp_port}")
            context = browser.contexts[0] if browser.contexts else await browser.new_context()
            page = context.pages[0] if context.pages else await context.new_page()

        elif self.mode == self.MODE_PERSISTENT:
            print(f"[CDP] 💾 Launching {self.browser_type} with persistent profile...")
            os.makedirs(self.profile_dir, exist_ok=True)
            # Persistent context requires slightly different args
            context = await playwright.chromium.launch_persistent_context(
                user_data_dir=self.profile_dir,
                **launch_args,
                args=["--disable-blink-features=AutomationControlled"]
            )
            browser = context.browser
            page = context.pages[0] if context.pages else await context.new_page()

        elif self.mode == self.MODE_PWA:
            print(f"[CDP] 🚀 Launching {self.browser_type} in PWA mode for {self.pwa_url}")
            launch_args["args"] = [f"--app={self.pwa_url}", "--disable-extensions"]
            browser = await playwright.chromium.launch(**launch_args)
            context = await browser.new_context()
            page = await context.new_page()
            if self.pwa_url not in page.url:
                await page.goto(self.pwa_url)

        else: # Normal Launch
            print(f"[CDP] 🌐 Launching standard {self.browser_type} instance...")
            browser = await playwright.chromium.launch(**launch_args)
            context = await browser.new_context()
            page = await context.new_page()

        return browser, page

    async def cleanup(self, browser: Browser):
        try:
            if self.mode == self.MODE_CDP_CONNECT:
                await browser.close() 
            elif self.mode == self.MODE_PERSISTENT:
                if browser.contexts:
                    await browser.contexts[0].close()
            else:
                await browser.close()
        except Exception as e:
            print(f"[CDP] Warning during cleanup: {e}")
            