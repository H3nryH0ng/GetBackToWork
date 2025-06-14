import psutil
import pygetwindow as gw
import time
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WindowMonitor:
    def __init__(self):
        self.app_categories = self._load_app_categories()
        self.current_window = None
        self.current_category = None
        self.start_time = None
        self.last_check_time = time.time()
        self._load_app_categories()

    def _load_app_categories(self) -> Dict:
        """Load application categories from JSON file."""
        try:
            with open(settings.APP_CATEGORIES_FILE, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"App categories file not found at {settings.APP_CATEGORIES_FILE}")
            return {"productivity": {"applications": [], "websites": []},
                   "entertainment": {"applications": [], "websites": []}}

    def get_active_window(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Get the currently active window and its category.
        Returns: (window_title, category)
        """
        try:
            active_window = gw.getActiveWindow()
            if not active_window:
                return None, None

            window_title = active_window.title
            process_name = self._get_process_name(active_window._hWnd)

            # Check if it's a browser
            if self._is_browser(process_name):
                category = self._categorize_browser_window(window_title)
            else:
                category = self._categorize_application(process_name)

            return window_title, category

        except Exception as e:
            logger.error(f"Error getting active window: {str(e)}")
            return None, None

    def _get_process_name(self, hwnd: int) -> str:
        """Get process name from window handle."""
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['pid'] == hwnd:
                    return proc.info['name'].lower()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        return ""

    def _is_browser(self, process_name: str) -> bool:
        """Check if the process is a web browser."""
        browsers = ['chrome.exe', 'firefox.exe', 'edge.exe', 'opera.exe']
        return process_name.lower() in browsers

    def _categorize_browser_window(self, window_title: str) -> Optional[str]:
        """Categorize browser window based on title."""
        for website in self.app_categories['productivity']['websites']:
            if website.lower() in window_title.lower():
                return 'productivity'

        for website in self.app_categories['entertainment']['websites']:
            if website.lower() in window_title.lower():
                return 'entertainment'

        return None

    def _categorize_application(self, process_name: str) -> Optional[str]:
        """Categorize application based on process name."""
        if process_name in self.app_categories['productivity']['applications']:
            return 'productivity'
        elif process_name in self.app_categories['entertainment']['applications']:
            return 'entertainment'
        return None

    def monitor_window(self) -> Tuple[Optional[str], Optional[str], float]:
        """
        Monitor the active window and return its details.
        Returns: (window_title, category, time_spent)
        """
        current_time = time.time()
        window_title, category = self.get_active_window()

        # If window or category changed
        if window_title != self.current_window or category != self.current_category:
            self.current_window = window_title
            self.current_category = category
            self.start_time = current_time
            self.last_check_time = current_time
            return window_title, category, 0

        # Calculate time spent
        time_spent = current_time - self.last_check_time
        self.last_check_time = current_time

        return window_title, category, time_spent

    def start_monitoring(self, callback):
        """
        Start monitoring windows and call the callback function with updates.
        Args:
            callback: Function to call with (window_title, category, time_spent)
        """
        while True:
            try:
                window_title, category, time_spent = self.monitor_window()
                if callback:
                    callback(window_title, category, time_spent)
                time.sleep(settings.MONITOR_INTERVAL)
            except Exception as e:
                logger.error(f"Error in window monitoring: {str(e)}")
                time.sleep(settings.MONITOR_INTERVAL) 