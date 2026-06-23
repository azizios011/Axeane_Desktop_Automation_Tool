# Modules/CDP_Setting.py
import os
import subprocess
import asyncio
from playwright.async_api import async_playwright
from Debug.Logger import ColorLogger as log


class CDPManager:
    """Manages Chrome DevTools Protocol (CDP) browser launch and connection."""

    def __init__(self, settings: dict):
        self.browser_type = settings.get("browser_type", "Chrome")
        self.executable_path = settings.get("executable_path", "")
        self.mode = settings.get("mode", "Persistent Profile (Keep Login)")
        self.cdp_port = settings.get("cdp_port", 9222)
        self.profile_dir = settings.get("profile_dir", "./axeane_browser_profile")
        self.playwright = None
        self.browser = None
        self.page = None
        self.browser_process = None

    def _get_executable_path(self) -> str:
        """Get the browser executable path."""
        if self.executable_path and os.path.exists(self.executable_path):
            return self.executable_path
        
        # Default paths
        if self.browser_type == "Edge":
            paths = [
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            ]
        else:  # Chrome
            paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            ]
        
        for path in paths:
            if os.path.exists(path):
                return path
        
        return ""

    async def launch_browser(self) -> bool:
        """Launch the browser with debugging enabled."""
        try:
            exe_path = self._get_executable_path()
            if not exe_path:
                log.error(f"Could not find {self.browser_type} executable")
                return False
            
            # Create user data directory if it doesn't exist
            os.makedirs(self.profile_dir, exist_ok=True)
            
            # Build launch arguments
            args = [
                exe_path,
                f"--remote-debugging-port={self.cdp_port}",
                f"--user-data-dir={self.profile_dir}",
                "--disable-blink-features=AutomationControlled",
                "--no-first-run",
                "--no-default-browser-check",
            ]
            
            log.info(f"Launching {self.browser_type} with args: {args}")
            
            # Launch browser as subprocess
            self.browser_process = subprocess.Popen(
                args,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            
            # Wait for browser to start
            await asyncio.sleep(3)
            
            if self.browser_process.poll() is None:
                log.success(f"Browser launched successfully on port {self.cdp_port}")
                return True
            else:
                log.error("Browser process terminated unexpectedly")
                return False
                
        except Exception as e:
            log.error(f"Failed to launch browser: {e}")
            return False

    async def connect_to_browser(self):
        """Connect to the running browser via CDP."""
        try:
            self.playwright = await async_playwright().start()
            
            log.info(f"Connecting to browser on port {self.cdp_port}...")
            self.browser = await self.playwright.chromium.connect_over_cdp(
                f"http://localhost:{self.cdp_port}"
            )
            
            # Get or create page
            if self.browser.contexts:
                context = self.browser.contexts[0]
                self.page = context.pages[0] if context.pages else await context.new_page()
            else:
                context = await self.browser.new_context()
                self.page = await context.new_page()
            
            log.success("Connected to browser successfully")
            return self.browser, self.page
            
        except Exception as e:
            log.error(f"Failed to connect to browser: {e}")
            raise

    async def cleanup(self):
        """Clean up browser and playwright."""
        try:
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            if self.browser_process:
                self.browser_process.terminate()
                self.browser_process.wait(timeout=5)
            log.info("Browser cleanup completed")
        except Exception as e:
            log.warn(f"Cleanup warning: {e}")
            