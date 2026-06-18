# Moduls/Session.py
from playwright.async_api import async_playwright
from .auth import login

class AxeaneSession:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None

    async def start(self, user: str, pwd: str):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=False)
        self.page = await self.browser.new_page()
        await login(self.page, user, pwd)
        return self.page

    async def close(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            self.playwright.stop()
            