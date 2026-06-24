# Modules/auth.py
from playwright.async_api import Page
from Debug.Logger import ColorLogger as log

async def login(page: Page, username: str, password: str):
    """Handles the Axeane Kompta login screen."""
    await page.goto("https://kompta.axeane.com/views/login.html")
    await page.locator("input[name='username']").fill(username)
    await page.locator("input[name='password']").fill(password)
    await page.locator("button[type='submit']").click()
    
    # Wait for the login to succeed and the page to navigate away from login
    try:
        await page.wait_for_url(lambda url: "login.html" not in url, timeout=10000)
    except Exception:
        pass

async def setup_context(page: Page, config: dict, append_log_callback=None):
    """
    Ensures the user is logged in, and selects the configured company and year.
    If the user has provided the required configuration, it will attempt to automate it.
    """
    def _log(msg, level="INFO"):
        if append_log_callback:
            append_log_callback(msg, level)
        else:
            if level == "INFO": log.info(msg)
            elif level == "SUCCESS": log.success(msg)
            elif level == "ERROR": log.error(msg)
            else: log.warn(msg)

    # 1. Ensure we are at the home page
    await page.goto("https://kompta.axeane.com")
    await page.wait_for_load_state("networkidle")
    
    # 2. Check if we got redirected to login
    if "login.html" in page.url:
        _log("At login screen. Attempting auto-login...", "INFO")
        username = config.get("username", "")
        password = config.get("password", "")
        if not username or not password:
            _log("Username or password not set in settings. Cannot auto-login.", "ERROR")
            return False
            
        await login(page, username, password)
        _log("Login submitted. Waiting for dashboard...", "INFO")
        await page.wait_for_load_state("networkidle")
    else:
        _log("Already logged in.", "INFO")

    # 3. Context Setup (Company and Year)
    # Note: As requested in the implementation plan, the exact CSS selectors for the 
    # top-nav company and year dropdowns in Axeane Kompta are unknown without live access.
    # The following is a best-effort template using standard Angular/Axeane structures.
    # If this fails, the user must manually update the selectors below.
    
    entreprise = config.get("entreprise", "")
    exercice = config.get("exercice", "")
    
    if entreprise or exercice:
        _log(f"Attempting to set context: {entreprise} - {exercice} (Best Effort)", "INFO")
        
        try:
            # Most Angular ERPs have a global context selector in the navbar.
            # We attempt to find dropdowns that might contain the company/year.
            # USER: Update these selectors to match the actual Axeane Kompta header dropdowns!
            
            # --- Company Selection ---
            if entreprise:
                # Example: wait for navbar company dropdown
                company_dropdown = page.locator(".context-entreprise-selector, .company-select").first
                if await company_dropdown.count() > 0:
                    await company_dropdown.click()
                    await page.locator(f"text='{entreprise}'").first.click()
                    await page.wait_for_timeout(500)
            
            # --- Year Selection ---
            if exercice:
                year_dropdown = page.locator(".context-exercice-selector, .year-select").first
                if await year_dropdown.count() > 0:
                    await year_dropdown.click()
                    await page.locator(f"text='{exercice}'").first.click()
                    await page.wait_for_timeout(500)
                    
            _log("Context setup script executed.", "SUCCESS")
            
        except Exception as e:
            _log(f"Could not auto-select company/year (selectors might need updating): {e}", "WARNING")
            
    return True

