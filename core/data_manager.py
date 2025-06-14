import json
import os
import shutil
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
import threading
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DataManager, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self._file_locks = {}
        self._backup_dir = settings.DATA_DIR / "backups"
        self._backup_dir.mkdir(exist_ok=True)
        self._initialize_data_files()

    def _initialize_data_files(self):
        """Initialize all data files with default values if they don't exist."""
        files_to_init = {
            settings.POINTS_HISTORY_FILE: settings.DEFAULT_POINTS_HISTORY,
            settings.USER_SETTINGS_FILE: settings.DEFAULT_SETTINGS,
            settings.DAILY_REPORTS_FILE: []
        }

        for file_path, default_data in files_to_init.items():
            if not file_path.exists():
                self._atomic_write(file_path, default_data)

    def _get_file_lock(self, file_path: Path) -> threading.Lock:
        """Get or create a lock for a specific file."""
        if file_path not in self._file_locks:
            self._file_locks[file_path] = threading.Lock()
        return self._file_locks[file_path]

    def _atomic_write(self, file_path: Path, data: Any):
        """Write data to a file atomically."""
        with self._get_file_lock(file_path):
            temp_file = file_path.with_suffix('.tmp')
            try:
                with open(temp_file, 'w') as f:
                    json.dump(data, f, indent=4)
                temp_file.replace(file_path)
            except Exception as e:
                logger.error(f"Error writing to {file_path}: {str(e)}")
                if temp_file.exists():
                    temp_file.unlink()
                raise

    def _create_backup(self, file_path: Path):
        """Create a backup of a file."""
        if not file_path.exists():
            return

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = self._backup_dir / f"{file_path.stem}_{timestamp}{file_path.suffix}"
        
        try:
            shutil.copy2(file_path, backup_file)
            # Keep only the last 5 backups
            backups = sorted(self._backup_dir.glob(f"{file_path.stem}_*{file_path.suffix}"))
            if len(backups) > 5:
                for old_backup in backups[:-5]:
                    old_backup.unlink()
        except Exception as e:
            logger.error(f"Error creating backup of {file_path}: {str(e)}")

    def read_data(self, file_path: Path) -> Any:
        """Read data from a file with error handling and backup."""
        with self._get_file_lock(file_path):
            try:
                if not file_path.exists():
                    return None

                with open(file_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.error(f"JSON decode error in {file_path}")
                self._create_backup(file_path)
                return None
            except Exception as e:
                logger.error(f"Error reading {file_path}: {str(e)}")
                return None

    def write_data(self, file_path: Path, data: Any):
        """Write data to a file with backup and validation."""
        with self._get_file_lock(file_path):
            try:
                # Create backup before writing
                self._create_backup(file_path)
                
                # Validate data structure
                if file_path == settings.POINTS_HISTORY_FILE:
                    self._validate_points_history(data)
                elif file_path == settings.USER_SETTINGS_FILE:
                    self._validate_user_settings(data)
                elif file_path == settings.DAILY_REPORTS_FILE:
                    self._validate_daily_reports(data)

                # Write data
                self._atomic_write(file_path, data)

            except Exception as e:
                logger.error(f"Error writing to {file_path}: {str(e)}")
                raise

    def _validate_points_history(self, data: Dict):
        """Validate points history data structure."""
        required_keys = {'current_points', 'daily_points', 'total_points_earned', 
                        'total_points_spent', 'history'}
        if not all(key in data for key in required_keys):
            raise ValueError("Invalid points history data structure")

    def _validate_user_settings(self, data: Dict):
        """Validate user settings data structure."""
        required_keys = set(settings.DEFAULT_SETTINGS.keys())
        if not all(key in data for key in required_keys):
            raise ValueError("Invalid user settings data structure")

    def _validate_daily_reports(self, data: list):
        """Validate daily reports data structure."""
        if not isinstance(data, list):
            raise ValueError("Daily reports must be a list")
        
        required_keys = {'date', 'points_earned', 'points_spent', 
                        'productive_time', 'entertainment_time', 'streaks'}
        for report in data:
            if not all(key in report for key in required_keys):
                raise ValueError("Invalid daily report data structure")

    def restore_from_backup(self, file_path: Path) -> bool:
        """Restore a file from its most recent backup."""
        try:
            backups = sorted(self._backup_dir.glob(f"{file_path.stem}_*{file_path.suffix}"))
            if not backups:
                return False

            latest_backup = backups[-1]
            shutil.copy2(latest_backup, file_path)
            return True
        except Exception as e:
            logger.error(f"Error restoring backup for {file_path}: {str(e)}")
            return False

    def cleanup_old_backups(self, days: int = 7):
        """Remove backups older than specified days."""
        try:
            cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
            for backup_file in self._backup_dir.glob("*"):
                if backup_file.stat().st_mtime < cutoff:
                    backup_file.unlink()
        except Exception as e:
            logger.error(f"Error cleaning up old backups: {str(e)}") 