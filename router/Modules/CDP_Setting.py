# Modules/CDP_Setting.py
import os
import subprocess
import asyncio
from playwright.async_api import async_playwright
from Debug.Logger import ColorLogger as log

# ── Constants ─────────────────────────────────────────────────────────────────
PWA_URL = "https://kompta.axeane.com"

# Connection mode identifiers (match the UI combobox values)
MODE_PWA_CDP    = "Launch PWA (CDP)"          # spawn browser in --app mode + CDP
MODE_CDP_CONNECT = "Connect to Existing CDP"  # attach to already-running browser


class CDPManager:
    """Manages Chrome DevTools Protocol (CDP) browser launch and connection.

    Supported modes
    ───────────────
    MODE_PWA_CDP     → Spawns a new Chrome/Edge process in PWA (--app) mode
                       with --remote-debugging-port, then connects Playwright
                       over CDP automatically.

    MODE_CDP_CONNECT → Does NOT launch a browser — attaches Playwright over CDP
                       to an already-running browser instance that was started
                       externally with --remote-debugging-port=<port>.
    """

    def __init__(self, settings: dict):
        self.browser_type    = settings.get("browser_type", "Chrome")
        self.executable_path = settings.get("executable_path", "")
        self.mode            = settings.get("mode", MODE_PWA_CDP)
        self.cdp_port        = int(settings.get("cdp_port", 9222))
        self.profile_dir     = os.path.abspath(
            settings.get("profile_dir", "./axeane_browser_profile")
        )
        self.pwa_url         = settings.get("pwa_url", PWA_URL)

        # Runtime state
        self.playwright      = None
        self.browser         = None
        self.page            = None
        self.browser_process = None   # only set in MODE_PWA_CDP

    # ── Executable resolution ─────────────────────────────────────────────────

    def _get_executable_path(self) -> str:
        """Return the browser executable, auto-detecting from default install paths."""
        if self.executable_path and os.path.exists(self.executable_path):
            return self.executable_path

        if self.browser_type == "Edge":
            candidates = [
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            ]
        else:  # Chrome (default)
            candidates = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            ]

        for path in candidates:
            if os.path.exists(path):
                return path

        return ""

    # ── Subprocess args ───────────────────────────────────────────────────────

    def _build_pwa_args(self) -> list:
        """Build CLI args to launch the browser in PWA + CDP mode."""
        exe = self._get_executable_path()
        if not exe:
            raise FileNotFoundError(
                f"Could not find {self.browser_type} executable. "
                "Please set the Executable Path field manually."
            )

        os.makedirs(self.profile_dir, exist_ok=True)

        return [
            exe,
            # CDP remote debugging endpoint
            f"--remote-debugging-port={self.cdp_port}",
            # Persistent user profile (keeps login session)
            f"--user-data-dir={self.profile_dir}",
            # PWA / standalone app mode — no address bar, no tabs UI
            f"--app={self.pwa_url}",
            # Stealth / hardening
            "--disable-blink-features=AutomationControlled",
            "--no-first-run",
            "--no-default-browser-check",
        ]

    # ── Shared Playwright connection helper ───────────────────────────────────

    async def _connect_playwright(self) -> tuple:
        """Connect Playwright to the CDP endpoint and return (browser, page)."""
        log.info(f"Connecting Playwright over CDP → http://localhost:{self.cdp_port}")

        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.connect_over_cdp(
            f"http://localhost:{self.cdp_port}"
        )

        # Get the first available page or open a new one
        if self.browser.contexts:
            ctx = self.browser.contexts[0]
            self.page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        else:
            ctx = await self.browser.new_context()
            self.page = await ctx.new_page()

        # If the page is blank, navigate to the PWA URL
        if not self.page.url or self.page.url in ("about:blank", ""):
            log.info(f"Page is blank — navigating to {self.pwa_url}")
            await self.page.goto(self.pwa_url, wait_until="domcontentloaded")

        log.success(f"Playwright connected — page: {self.page.url}")
        return self.browser, self.page

    # ── Public API ────────────────────────────────────────────────────────────

    async def launch_pwa_cdp(self) -> tuple:
        """MODE_PWA_CDP — Spawn a new browser in PWA mode with CDP, then connect.

        Steps:
          1. Launch the browser subprocess with --app=<url> + --remote-debugging-port.
          2. Wait up to 5 s for the debug endpoint to become available.
          3. Connect Playwright over CDP.

        Returns (browser, page).
        """
        args = self._build_pwa_args()
        log.info(f"[PWA-CDP] Launching {self.browser_type} in PWA mode")
        log.info(f"[PWA-CDP] URL     : {self.pwa_url}")
        log.info(f"[PWA-CDP] Port    : {self.cdp_port}")
        log.info(f"[PWA-CDP] Profile : {self.profile_dir}")

        self.browser_process = subprocess.Popen(
            args,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        # Poll for up to 5 seconds for the debug endpoint to come up
        log.info("[PWA-CDP] Waiting for browser debug endpoint…")
        for attempt in range(10):
            await asyncio.sleep(0.5)
            if self.browser_process.poll() is not None:
                raise RuntimeError(
                    f"{self.browser_type} process exited immediately (code "
                    f"{self.browser_process.returncode}). "
                    "Make sure no other browser instance is already using "
                    f"port {self.cdp_port}, and the executable path is correct."
                )
            # Try to reach the CDP JSON endpoint
            try:
                import urllib.request
                urllib.request.urlopen(
                    f"http://localhost:{self.cdp_port}/json/version", timeout=1
                )
                log.info(f"[PWA-CDP] Debug endpoint ready after {(attempt + 1) * 0.5:.1f}s")
                break
            except Exception:
                continue
        else:
            raise TimeoutError(
                f"Browser debug endpoint on port {self.cdp_port} did not become "
                "available within 5 seconds."
            )

        return await self._connect_playwright()

    async def connect_cdp(self) -> tuple:
        """MODE_CDP_CONNECT — Attach to an already-running browser via CDP.

        The browser must have been started manually (or by another process) with:
            --remote-debugging-port=<cdp_port>

        Returns (browser, page).
        """
        log.info(f"[CDP-CONNECT] Attaching to existing browser on port {self.cdp_port}")
        return await self._connect_playwright()

    async def cleanup(self):
        """Close Playwright connection and (in PWA mode) terminate the subprocess."""
        try:
            if self.browser:
                await self.browser.close()
                self.browser = None
        except Exception as e:
            log.warning(f"Browser close warning: {e}")

        try:
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None
        except Exception as e:
            log.warning(f"Playwright stop warning: {e}")

        try:
            if self.browser_process and self.browser_process.poll() is None:
                self.browser_process.terminate()
                self.browser_process.wait(timeout=5)
                log.info("Browser subprocess terminated")
        except Exception as e:
            log.warning(f"Process termination warning: {e}")

        self.page            = None
        self.browser_process = None