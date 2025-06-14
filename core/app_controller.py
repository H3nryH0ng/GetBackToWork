import psutil
import pygetwindow as gw
import time
import logging
from typing import Dict, List, Optional
import os
import sys
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AppController:
    def __init__(self):
        self.blocked_apps = set()
        self.block_level = settings.BLOCK_LEVELS[settings.DEFAULT_SETTINGS['block_level']]
        self.original_windows = {}  # Store original window states
        self.anti_cheat_processes = set()

    def set_block_level(self, level: str):
        """Set the blocking level (minimize, hide, terminate)."""
        if level in settings.BLOCK_LEVELS:
            self.block_level = settings.BLOCK_LEVELS[level]
        else:
            logger.error(f"Invalid block level: {level}")

    def block_application(self, window_title: str, process_name: str):
        """Block an application based on the current block level."""
        try:
            if self.block_level == 1:  # Minimize
                self._minimize_window(window_title)
            elif self.block_level == 2:  # Hide
                self._hide_window(window_title)
            elif self.block_level == 3:  # Terminate
                self._terminate_process(process_name)

            self.blocked_apps.add(process_name)
            logger.info(f"Blocked application: {process_name}")

        except Exception as e:
            logger.error(f"Error blocking application {process_name}: {str(e)}")

    def unblock_application(self, window_title: str, process_name: str):
        """Unblock a previously blocked application."""
        try:
            if process_name in self.blocked_apps:
                if self.block_level == 1:  # Minimize
                    self._restore_window(window_title)
                elif self.block_level == 2:  # Hide
                    self._show_window(window_title)
                # No need to handle terminate as process is already gone

                self.blocked_apps.remove(process_name)
                logger.info(f"Unblocked application: {process_name}")

        except Exception as e:
            logger.error(f"Error unblocking application {process_name}: {str(e)}")

    def _minimize_window(self, window_title: str):
        """Minimize a window."""
        try:
            window = gw.getWindowsWithTitle(window_title)
            if window:
                self.original_windows[window_title] = window[0].isMinimized
                window[0].minimize()
        except Exception as e:
            logger.error(f"Error minimizing window {window_title}: {str(e)}")

    def _hide_window(self, window_title: str):
        """Hide a window."""
        try:
            window = gw.getWindowsWithTitle(window_title)
            if window:
                self.original_windows[window_title] = window[0].isVisible
                window[0].hide()
        except Exception as e:
            logger.error(f"Error hiding window {window_title}: {str(e)}")

    def _terminate_process(self, process_name: str):
        """Terminate a process."""
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'].lower() == process_name.lower():
                    proc.terminate()
        except Exception as e:
            logger.error(f"Error terminating process {process_name}: {str(e)}")

    def _restore_window(self, window_title: str):
        """Restore a minimized window."""
        try:
            window = gw.getWindowsWithTitle(window_title)
            if window and self.original_windows.get(window_title, False):
                window[0].restore()
        except Exception as e:
            logger.error(f"Error restoring window {window_title}: {str(e)}")

    def _show_window(self, window_title: str):
        """Show a hidden window."""
        try:
            window = gw.getWindowsWithTitle(window_title)
            if window and not self.original_windows.get(window_title, True):
                window[0].show()
        except Exception as e:
            logger.error(f"Error showing window {window_title}: {str(e)}")

    def check_anti_cheat(self) -> bool:
        """
        Check for anti-cheat attempts.
        Returns: True if cheating detected, False otherwise
        """
        try:
            # Check for task manager
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'].lower() in ['taskmgr.exe', 'processhacker.exe']:
                    return True

            # Check for process name changes
            current_processes = {p.info['name'].lower() for p in psutil.process_iter(['name'])}
            if self.anti_cheat_processes and not self.anti_cheat_processes.issubset(current_processes):
                return True

            # Update known processes
            self.anti_cheat_processes = current_processes

            return False

        except Exception as e:
            logger.error(f"Error in anti-cheat check: {str(e)}")
            return False

    def is_process_blocked(self, process_name: str) -> bool:
        """Check if a process is currently blocked."""
        return process_name in self.blocked_apps

    def get_blocked_apps(self) -> List[str]:
        """Get list of currently blocked applications."""
        return list(self.blocked_apps)

    def clear_blocked_apps(self):
        """Clear all blocked applications."""
        self.blocked_apps.clear()
        self.original_windows.clear() 