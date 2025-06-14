import logging
from typing import Optional, Dict, Any
from plyer import notification
import time
import threading
from pathlib import Path
import json

logger = logging.getLogger(__name__)

class NotificationManager:
    def __init__(self):
        self.notification_queue = []
        self.is_running = False
        self.thread = None
        self._load_notification_settings()

    def _load_notification_settings(self):
        """Load notification settings from file."""
        try:
            settings_file = Path(__file__).parent.parent / "config" / "notification_settings.json"
            if settings_file.exists():
                with open(settings_file, 'r') as f:
                    self.settings = json.load(f)
            else:
                self.settings = {
                    'enabled': True,
                    'sound': True,
                    'duration': 5,
                    'position': 'bottom-right'
                }
        except Exception as e:
            logger.error(f"Error loading notification settings: {str(e)}")
            self.settings = {
                'enabled': True,
                'sound': True,
                'duration': 5,
                'position': 'bottom-right'
            }

    def _save_notification_settings(self):
        """Save notification settings to file."""
        try:
            settings_file = Path(__file__).parent.parent / "config" / "notification_settings.json"
            with open(settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving notification settings: {str(e)}")

    def start(self):
        """Start the notification manager."""
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self._process_queue, daemon=True)
            self.thread.start()

    def stop(self):
        """Stop the notification manager."""
        self.is_running = False
        if self.thread:
            self.thread.join()

    def _process_queue(self):
        """Process the notification queue."""
        while self.is_running:
            if self.notification_queue:
                notification_data = self.notification_queue.pop(0)
                self._show_notification(**notification_data)
            time.sleep(0.1)

    def _show_notification(self, title: str, message: str, 
                         duration: Optional[int] = None,
                         sound: Optional[bool] = None):
        """Show a system notification."""
        if not self.settings['enabled']:
            return

        try:
            notification.notify(
                title=title,
                message=message,
                app_name="GetB@ck2Work",
                timeout=duration or self.settings['duration'],
                # Sound is handled by the system
            )
        except Exception as e:
            logger.error(f"Error showing notification: {str(e)}")

    def queue_notification(self, title: str, message: str,
                         duration: Optional[int] = None,
                         sound: Optional[bool] = None):
        """Queue a notification to be shown."""
        self.notification_queue.append({
            'title': title,
            'message': message,
            'duration': duration,
            'sound': sound
        })

    def show_points_update(self, points: int, category: str):
        """Show a points update notification."""
        if points > 0:
            title = "Points Earned!"
            message = f"You earned {points} points for being productive!"
        else:
            title = "Points Spent"
            message = f"You spent {abs(points)} points on entertainment."
        
        self.queue_notification(title, message)

    def show_streak_achieved(self, streak_duration: int):
        """Show a streak achievement notification."""
        hours = streak_duration // 3600
        minutes = (streak_duration % 3600) // 60
        
        title = "Productivity Streak!"
        message = f"You've been productive for {hours}h {minutes}m! Keep it up!"
        
        self.queue_notification(title, message)

    def show_daily_cap_reached(self, category: str):
        """Show a daily cap reached notification."""
        if category == 'productivity':
            title = "Daily Cap Reached"
            message = "You've reached your daily points earning cap!"
        else:
            title = "Entertainment Limit"
            message = "You've reached your daily entertainment points limit!"
        
        self.queue_notification(title, message)

    def show_blocked_app(self, app_name: str):
        """Show a blocked app notification."""
        title = "App Blocked"
        message = f"{app_name} has been blocked. Earn more points to continue!"
        
        self.queue_notification(title, message)

    def update_settings(self, settings: Dict[str, Any]):
        """Update notification settings."""
        self.settings.update(settings)
        self._save_notification_settings()

    def get_settings(self) -> Dict[str, Any]:
        """Get current notification settings."""
        return self.settings.copy() 