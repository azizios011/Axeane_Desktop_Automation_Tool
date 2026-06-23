# Modules/CDP_Setting.py
import os
import subprocess
import asyncio
from playwright.async_api import async_playwright
from Debug.Logger import ColorLogger as log

PWA_URL = "https://kompta.axeane.com"


class CDPManager:
    """Manages Chrome DevTools Protocol (CDP) browser launch and connection.

    Launch flow:
        1. launch_and_connect()  →  spawns the browser subprocess in PWA/app
           mode with --remote-debugging-port, then immediately connects
           Playwright over CDP.
        2. cleanup()             →  closes Playwright + terminates subprocess.
    """

    def __init__(self, settings: dict):
        self.browser_type   = settings.get("browser_type", "Chrome")
        self.executable_path = settings.get("executable_path", "")
        self.mode           = settings.get("mode", "Persistent Profile (Keep Login)")
        self.cdp_port       = settings.get("cdp_port", 9222)
        self.profile_dir    = os.path.abspath(
            settings.get("profile_dir", "./axeane_browser_profile")
        )
        self.pwa_url        = settings.get("pwa_url", PWA_URL)

        self.playwright     = None
        self.browser        = None
        self.page           = None
        self.browser_process = None

    # ──────────────────────────────────────────────────────────────
    # Internal helpers
    # ──────────────────────────────────────────────────────────────

    def _get_executable_path(self) -> str:
        """Return the browser executable path, auto-detecting if not set."""
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

    def _build_args(self) -> list:
        """Build the list of CLI arguments for the browser subprocess."""
        exe = self._get_executable_path()
        if not exe:
            raise FileNotFoundError(
                f"Could not find {self.browser_type} executable. "
                "Please set the path manually in the Browser Settings."
            )

        os.makedirs(self.profile_dir, exist_ok=True)

        args = [
            exe,
            # ── CDP debugging ──
            f"--remote-debugging-port={self.cdp_port}",
            # ── Persistent user profile ──
            f"--user-data-dir={self.profile_dir}",
            # ── PWA / standalone app mode ──
            f"--app={self.pwa_url}",
            # ── Misc hardening ──
            "--disable-blink-features=AutomationControlled",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-extensions-except=",
        ]

        return args

    # ──────────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────────

    async def launch_and_connect(self):
        """Launch the browser in PWA mode then connect Playwright over CDP.

        Returns (browser, page) on success, raises on failure.
        """
        args = self._build_args()
        log.info(f"Launching {self.browser_type} in PWA mode → {self.pwa_url}")
        log.info(f"CDP port: {self.cdp_port}  |  Profile: {self.profile_dir}")

        # ── 1. Spawn the browser subprocess ──
        self.browser_process = subprocess.Popen(
            args,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        # ── 2. Wait for the browser to open its debug endpoint ──
        log.info("Waiting for browser to start...")
        await asyncio.sleep(3)

        if self.browser_process.poll() is not None:
            raise RuntimeError(
                f"{self.browser_type} process exited immediately. "
                "Check the executable path and that no other instance is using "
                f"port {self.cdp_port}."
            )

        # ── 3. Connect Playwright over CDP ──
        log.info(f"Connecting Playwright over CDP on port {self.cdp_port}...")
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.connect_over_cdp(
            f"http://localhost:{self.cdp_port}"
        )

        # ── 4. Grab the first page (the PWA window) ──
        if self.browser.contexts:
            context = self.browser.contexts[0]
            self.page = context.pages[0] if context.pages else await context.new_page()
        else:
            context = await self.browser.new_context()
            self.page = await context.new_page()

        # Navigate to the PWA URL if the page is blank
        if not self.page.url or self.page.url == "about:blank":
            await self.page.goto(self.pwa_url, wait_until="domcontentloaded")

        log.success(
            f"Connected to {self.browser_type} PWA  —  page: {self.page.url}"
        )
        return self.browser, self.page

    async def cleanup(self):
        """Close Playwright connection and terminate the browser process."""
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
                log.info("Browser process terminated")
        except Exception as e:
            log.warning(f"Process termination warning: {e}")

        self.page = None
        self.browser_process = None