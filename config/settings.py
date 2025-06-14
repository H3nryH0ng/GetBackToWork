import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CONFIG_DIR = BASE_DIR / "config"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
CONFIG_DIR.mkdir(exist_ok=True)

# File paths
APP_CATEGORIES_FILE = CONFIG_DIR / "app_categories.json"
POINTS_HISTORY_FILE = DATA_DIR / "points_history.json"
USER_SETTINGS_FILE = DATA_DIR / "user_settings.json"
DAILY_REPORTS_FILE = DATA_DIR / "daily_reports.json"

# Point system settings
POINTS_PER_INTERVAL = 1  # Points earned per time interval
TIME_INTERVAL = 300  # 5 minutes in seconds
STREAK_THRESHOLD = 3600  # 1 hour in seconds
STREAK_BONUS = 0.1  # 10% bonus
DAILY_POINTS_CAP = 100  # Maximum points that can be earned per day
DAILY_ENTERTAINMENT_CAP = 50  # Maximum points that can be spent on entertainment

# Window monitoring settings
MONITOR_INTERVAL = 5  # Seconds between window checks
FUZZY_MATCH_THRESHOLD = 0.8  # Threshold for fuzzy matching window titles

# GUI settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
OVERLAY_OPACITY = 0.8
THEME = "light"  # Options: "light", "dark"

# Blocking levels
BLOCK_LEVELS = {
    "minimize": 1,
    "hide": 2,
    "terminate": 3
}

# Default user settings
DEFAULT_SETTINGS = {
    "points_per_interval": POINTS_PER_INTERVAL,
    "time_interval": TIME_INTERVAL,
    "streak_threshold": STREAK_THRESHOLD,
    "streak_bonus": STREAK_BONUS,
    "daily_points_cap": DAILY_POINTS_CAP,
    "daily_entertainment_cap": DAILY_ENTERTAINMENT_CAP,
    "monitor_interval": MONITOR_INTERVAL,
    "block_level": "minimize",
    "theme": THEME,
    "notifications_enabled": True,
    "startup_enabled": False,
    "overlay_opacity": OVERLAY_OPACITY
}

# Initialize points history
DEFAULT_POINTS_HISTORY = {
    "current_points": 0,
    "daily_points": 0,
    "total_points_earned": 0,
    "total_points_spent": 0,
    "history": []
}

# Initialize daily reports
DEFAULT_DAILY_REPORT = {
    "date": "",
    "points_earned": 0,
    "points_spent": 0,
    "productive_time": 0,
    "entertainment_time": 0,
    "streaks": 0
} 