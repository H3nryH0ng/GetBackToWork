import sys
import os
from pathlib import Path
import logging
import threading
import time

from gui.main_window import MainWindow
from gui.overlay import OverlayWindow
from core.window_monitor import WindowMonitor
from core.point_system import PointSystem
from core.app_controller import AppController
from core.data_manager import DataManager
from config import settings

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def ensure_directories():
    """Ensure all required directories exist."""
    directories = [
        settings.DATA_DIR,
        settings.CONFIG_DIR,
        settings.DATA_DIR / "backups",
        Path(__file__).parent / "gui" / "assets"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

def check_dependencies():
    """Check if all required dependencies are installed."""
    try:
        import psutil
        import pygetwindow
        import pyautogui
        import pystray
        from PIL import Image
        import plyer
        import schedule
        import pygame
    except ImportError as e:
        logger.error(f"Missing dependency: {str(e)}")
        print(f"Error: Missing dependency - {str(e)}")
        print("Please install all required dependencies using:")
        print("pip install -r requirements.txt")
        sys.exit(1)

def initialize_data():
    """Initialize data files with default values if they don't exist."""
    data_manager = DataManager()
    
    # Initialize points history
    if not settings.POINTS_HISTORY_FILE.exists():
        data_manager.write_data(settings.POINTS_HISTORY_FILE,
                              settings.DEFAULT_POINTS_HISTORY)
    
    # Initialize user settings
    if not settings.USER_SETTINGS_FILE.exists():
        data_manager.write_data(settings.USER_SETTINGS_FILE,
                              settings.DEFAULT_SETTINGS)
    
    # Initialize daily reports
    if not settings.DAILY_REPORTS_FILE.exists():
        data_manager.write_data(settings.DAILY_REPORTS_FILE, [])

def main():
    """Main application entry point."""
    try:
        # Setup
        ensure_directories()
        check_dependencies()
        initialize_data()
        
        # Create and run main window
        app = MainWindow()
        app.run()
        
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 