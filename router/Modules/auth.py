# Moduls/auth.py
from playwright.async_api import Page

async def login(page: Page, username: str, password: str):
    """Handles the Axeane Kompta login screen."""
    await page.goto("https://kompta.axeane.com/views/login.html")
    await page.fill("input[name='username']", username) # Adjust selector if needed
    await page.fill("input[name='password']", password)
    await page.click("button[type='submit']")
    await page.wait_for_url("**/ecranEcritureMainModele2.html")
