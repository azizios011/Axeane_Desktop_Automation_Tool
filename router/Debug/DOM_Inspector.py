# Debug/DOM_Inspector.py
import os
from datetime import datetime

class DOMInspector:
    def __init__(self, page, log_dir="Debug/logs/dom"):
        self.page = page
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)

    async def snapshot(self, css_selector: str, name: str = "snapshot"):
        """Saves the innerHTML of a specific element to a file."""
        try:
            html = await self.page.inner_html(css_selector)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = os.path.join(self.log_dir, f"{timestamp}_{name}.html")
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"[DEBUG] 📸 DOM Snapshot saved: {filepath}")
        except Exception as e:
            print(f"[DEBUG] ❌ DOM Snapshot failed for {css_selector}: {e}")

    async def full_page_snapshot(self, name: str = "full_page"):
        """Saves the entire page HTML (useful for massive failures)."""
        try:
            html = await self.page.content()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = os.path.join(self.log_dir, f"{timestamp}_{name}.html")
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html)
        except Exception as e:
            print(f"[DEBUG] ❌ Full page snapshot failed: {e}")
            