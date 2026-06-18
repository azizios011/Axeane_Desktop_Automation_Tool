# Debug/Network.py
import json
import os
from datetime import datetime
from playwright.async_api import Request, Response

class NetworkInterceptor:
    def __init__(self, page, log_dir="Debug/logs/network"):
        self.page = page
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Attach Playwright listeners
        self.page.on("request", self._handle_request)
        self.page.on("response", self._handle_response)
        print(f"[DEBUG] 🌐 Network Interceptor started. Logs saving to: {self.log_dir}")

    def _handle_request(self, request: Request):
        url = request.url
        # Filter for Axeane API calls
        if "axeaneapi.ch/service" in url or "kompta.axeane.com" in url:
            method = request.method
            if method in ["POST", "PUT"]:
                post_data = request.post_data
                if post_data:
                    try:
                        payload = json.loads(post_data)
                        self._log_json(f"REQ_{method}_{self._sanitize_url(url)}", payload, direction="OUT")
                    except json.JSONDecodeError:
                        pass # Form data or non-JSON

    def _handle_response(self, response: Response):
        url = response.url
        if "axeaneapi.ch/service" in url or "kompta.axeane.com" in url:
            try:
                # Only parse if the response is actually JSON
                if "application/json" in response.headers.get("content-type", ""):
                    data = response.json()
                    self._log_json(f"RES_{response.status}_{self._sanitize_url(url)}", data, direction="IN")
            except Exception:
                pass 

    def _sanitize_url(self, url):
        # Clean up URL to make it a valid filename
        return url.split("?")[0].replace("/", "_").replace(":", "")[-60:]

    def _log_json(self, prefix, data, direction):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"{timestamp}_{prefix}.json"
        filepath = os.path.join(self.log_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
        # Print a quick summary to the console
        arrow = ">>>" if direction == "OUT" else "<<<"
        print(f"[DEBUG] 🌐 {arrow} {prefix} ({len(json.dumps(data))} bytes) -> {filepath}")