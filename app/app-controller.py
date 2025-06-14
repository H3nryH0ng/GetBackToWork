"""
App Controller Module for GetB@ck2Work
Handles app blocking, process management, and window control across platforms
"""

import os
import sys
import time
import subprocess
import threading
import psutil
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import logging

# Platform-specific imports
if sys.platform == "win32":
    import win32gui
    import win32process
    import win32con
    import win32api
# If you were to run this on macOS, you would need pyobjc installed and uncomment this block:
# elif sys.platform == "darwin":
#     try:
#         from AppKit import NSWorkspace
#         from Quartz import (
#             CGWindowListCopyWindowInfo,
#             kCGWindowListOptionOnScreenOnly,
#             kCGWindowListExcludeDesktopElements,
#             kCGNullWindowID,
#             kCGWindowOwnerPID,
#             kCGWindowName
#         )
#     except ImportError:
#         logging.error("PyObjC not installed. macOS features will be limited.")
#         NSWorkspace = None
#         CGWindowListCopyWindowInfo = None


# Set logging level to INFO for general operation.
# Change to logging.DEBUG for detailed troubleshooting.
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')


class BlockAction(Enum):
    CLOSE = "close"
    MINIMIZE = "minimize"
    BACKGROUND = "background"
    WARN = "warn"


@dataclass
class AppInfo:
    process_name: str
    window_title: str
    pid: int
    executable_path: str
    category: str = "unknown" # 'productivity', 'entertainment', 'neutral', 'unknown'


class AppController:
    """
    Cross-platform application controller for monitoring, categorizing,
    and blocking applications based on configured rules.
    """

    def __init__(self, on_activity_callback: Optional[Callable] = None):
        # Lists for app categorization
        self.entertainment_apps = set() # Apps to restrict/block
        self.productivity_apps = set()  # Apps that earn points
        self.neutral_apps = set()       # Apps that neither earn nor deduct points

        self.running = False
        self.monitor_thread = None
        self.activity_callback = on_activity_callback # Callback for active app changes/violations
        self.block_action = BlockAction.WARN # Default block action: warn
        self.warning_shown = {} # To manage warning frequency for 'WARN' action

        # Whitelist for essential system processes and this app itself
        self.process_whitelist = {
            "getb@ck2work", # Assuming your main app process name
            "python", "python.exe",
            "cmd.exe", "powershell.exe", "explorer.exe", # Windows specific
            "gnome-shell", "kwin_x11", "compiz", "xfwm4", # Common Linux WMs
            "dock", "finder", "loginwindow" # macOS specific
        }
        
        # Store PID of the current AppController process for self-integrity checks
        self._my_pid = os.getpid()
        self._my_process_name = psutil.Process(self._my_pid).name()

        self.logger = logging.getLogger(__name__) # Get logger instance

        # Platform-specific initialization
        self._init_platform_specific()

    def _init_platform_specific(self):
        """Initialize platform-specific components based on OS"""
        self.platform = sys.platform
        if self.platform == "win32":
            self._init_windows()
        elif self.platform == "darwin":
            self._init_macos()
        elif self.platform.startswith("linux"):
            self._init_linux()

    def _init_windows(self):
        """Initialize Windows-specific components"""
        self.logger.info("Initializing Windows app controller.")

    def _init_macos(self):
        """Initialize macOS-specific components (currently commented out for Windows-only usage)"""
        self.logger.info("Initializing macOS app controller (functionality limited as it requires PyObjC).")
        # if NSWorkspace is None: # Uncomment if you enable macOS imports
        #     self.logger.warning("NSWorkspace is not available. macOS window detection might fail. Please ensure 'pyobjc' is installed.")

    def _init_linux(self):
        """Initialize Linux-specific components"""
        self.logger.info("Initializing Linux app controller.")

    def add_entertainment_app(self, app_identifier: str):
        """Add an app identifier to the list of entertainment apps (to be restricted)"""
        self.entertainment_apps.add(app_identifier.lower())
        self.logger.info(f"Added '{app_identifier}' to entertainment apps.")

    def remove_entertainment_app(self, app_identifier: str):
        """Remove an app identifier from the entertainment list"""
        self.entertainment_apps.discard(app_identifier.lower())
        self.logger.info(f"Removed '{app_identifier}' from entertainment apps.")

    def add_productivity_app(self, app_identifier: str):
        """Add an app identifier to the list of productivity apps (to earn points)"""
        self.productivity_apps.add(app_identifier.lower())
        self.logger.info(f"Added '{app_identifier}' to productivity apps.")

    def remove_productivity_app(self, app_identifier: str):
        """Remove an app identifier from the productivity list"""
        self.productivity_apps.discard(app_identifier.lower())
        self.logger.info(f"Removed '{app_identifier}' from productivity apps.")

    def add_neutral_app(self, app_identifier: str):
        """Add an app identifier to the list of neutral apps (no points effect)"""
        self.neutral_apps.add(app_identifier.lower())
        self.logger.info(f"Added '{app_identifier}' to neutral apps.")

    def remove_neutral_app(self, app_identifier: str):
        """Remove an app identifier from the neutral list"""
        self.neutral_apps.discard(app_identifier.lower())
        self.logger.info(f"Removed '{app_identifier}' from neutral apps.")

    def set_block_action(self, action: BlockAction):
        """Set the action to take when an entertainment app is detected without sufficient points"""
        self.block_action = action
        self.logger.info(f"Block action set to: {action.value}.")

    def categorize_app(self, app_info: AppInfo) -> str:
        """Determines the category of an application (productivity, entertainment, neutral, unknown)"""
        if not app_info:
            return "unknown"

        process_name_lower = app_info.process_name.lower()
        window_title_lower = app_info.window_title.lower()
        executable_path_lower = app_info.executable_path.lower()

        # Check against whitelist (e.g., system processes, self)
        for wl_entry in self.process_whitelist:
            if (wl_entry in process_name_lower or
                wl_entry in window_title_lower or
                wl_entry in executable_path_lower):
                return "neutral" # Whitelisted apps are generally neutral

        # Check entertainment apps
        for ent_app in self.entertainment_apps:
            if (ent_app in process_name_lower or
                ent_app in window_title_lower or
                ent_app in executable_path_lower):
                return "entertainment"

        # Check productivity apps
        for prod_app in self.productivity_apps:
            if (prod_app in process_name_lower or
                prod_app in window_title_lower or
                prod_app in executable_path_lower):
                return "productivity"
        
        # Check neutral apps (user-defined neutral, not system whitelist)
        for neutral_app in self.neutral_apps:
            if (neutral_app in process_name_lower or
                neutral_app in window_title_lower or
                neutral_app in executable_path_lower):
                return "neutral"

        return "unknown" # Default if no category matches

    def is_entertainment_app_blocked(self, app_info: AppInfo, has_points: bool = True) -> bool:
        """
        Checks if an app is an entertainment app AND should be blocked.
        It should be blocked if it's an entertainment app AND has_points is False.
        """
        if self.categorize_app(app_info) == "entertainment" and not has_points:
            self.logger.debug(f"DEBUG: Entertainment app '{app_info.process_name}' detected without sufficient points.")
            return True
        self.logger.debug(f"DEBUG: App '{app_info.process_name}' is not an entertainment app or user has points.")
        return False

    def get_active_window_info(self) -> Optional[AppInfo]:
        """Get information about the currently active window based on the current platform"""
        if self.platform == "win32":
            return self._get_active_window_windows()
        elif self.platform == "darwin":
            return self._get_active_window_macos()
        elif self.platform.startswith("linux"):
            return self._get_active_window_linux()
        return None

    def _get_active_window_windows(self) -> Optional[AppInfo]:
        """Get active window info on Windows using win32api/win32gui and psutil"""
        try:
            hwnd = win32gui.GetForegroundWindow()
            self.logger.debug(f"DEBUG: GetForegroundWindow returned HWND: {hwnd}")

            if hwnd == 0: # No foreground window (e.g., desktop)
                self.logger.debug("DEBUG: No active foreground window (HWND is 0).")
                return None

            window_title = win32gui.GetWindowText(hwnd)
            self.logger.debug(f"DEBUG: GetWindowText returned: '{window_title}'")

            # Sometimes GetWindowText returns empty for certain windows,
            # or for console windows where the title is just the path.
            if not window_title and hwnd:
                self.logger.debug("DEBUG: Window title is empty. Attempting to get from process name.")
                # Get PID to try and find process name as fallback title
                _, pid_check = win32process.GetWindowThreadProcessId(hwnd)
                try:
                    process_check = psutil.Process(pid_check)
                    window_title = process_check.name() # Use process name as fallback title
                    self.logger.debug(f"DEBUG: Fallback window title from process name: '{window_title}'")
                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    self.logger.debug(f"DEBUG: Could not get process info for fallback title (PID {pid_check}): {e}")
                    pass # Keep window_title empty if process info unavailable

            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            self.logger.debug(f"DEBUG: GetWindowThreadProcessId returned PID: {pid}")

            if not pid:
                self.logger.debug("DEBUG: PID is 0 or invalid, cannot get process info.")
                return None

            try:
                process = psutil.Process(pid)
                process_name = process.name()
                executable_path = process.exe()
                self.logger.debug(f"DEBUG: Process found: Name='{process_name}', Executable='{executable_path}'")
            except psutil.NoSuchProcess:
                self.logger.debug(f"DEBUG: No such process found for PID: {pid}. It might have just closed.")
                return None
            except psutil.AccessDenied:
                self.logger.warning(f"WARNING: Access denied to process with PID: {pid}. Cannot get full details.")
                # Return partial info if access denied, as we have PID and process name.
                # In some cases, we might not get executable_path.
                try:
                    process_name = psutil.Process(pid).name()
                    executable_path = "" # Cannot get path if denied access
                except Exception:
                    process_name = "unknown"
                    executable_path = "unknown"
                self.logger.debug(f"DEBUG: Returning partial info due to access denied for PID {pid}: Name='{process_name}'")
                return AppInfo(
                    process_name=process_name,
                    window_title=window_title,
                    pid=pid,
                    executable_path=executable_path
                )
            except Exception as e:
                self.logger.error(f"ERROR: Error getting process details for PID {pid}: {e}")
                return None

            return AppInfo(
                process_name=process_name,
                window_title=window_title,
                pid=pid,
                executable_path=executable_path
            )
        except Exception as e:
            self.logger.error(f"ERROR: Error in _get_active_window_windows: {e}")
            return None

    def _get_active_window_macos(self) -> Optional[AppInfo]:
        """Get active window info on macOS (requires PyObjC, commented out for Windows-only)"""
        # if NSWorkspace is None or CGWindowListCopyWindowInfo is None: # Uncomment if you enable macOS imports
        #     self.logger.error("macOS specific modules (PyObjC) not available. Cannot get active window info.")
        #     return None
        # try:
        #     workspace = NSWorkspace.sharedWorkspace()
        #     active_app = workspace.activeApplication()
        #
        #     if not active_app:
        #         return None
        #
        #     process_name = active_app['NSApplicationName']
        #     pid = active_app['NSApplicationProcessIdentifier']
        #     executable_path = active_app.get('NSApplicationPath', '')
        #
        #     # Get window title using Quartz
        #     window_list = CGWindowListCopyWindowInfo(
        #         kCGWindowListOptionOnScreenOnly | kCGWindowListExcludeDesktopElements,
        #         kCGNullWindowID
        #     )
        #
        #     window_title = ""
        #     for window in window_list:
        #         if window.get(kCGWindowOwnerPID) == pid:
        #             window_title = window.get(kCGWindowName, '')
        #             if window_title:
        #                 break
        #
        #     return AppInfo(
        #         process_name=process_name,
        #         window_title=window_title,
        #         pid=pid,
        #         executable_path=executable_path
        #     )
        # except Exception as e:
        #     self.logger.error(f"Error getting macOS active window: {e}")
        self.logger.debug("DEBUG: _get_active_window_macos called but functionality is disabled/unavailable.")
        return None # Return None if macOS functionality is not enabled/available

    def _get_active_window_linux(self) -> Optional[AppInfo]:
        """Get active window info on Linux using xdotool or wmctrl"""
        try:
            # Try xdotool first (more reliable for active window)
            result = subprocess.run(['xdotool', 'getactivewindow'],
                                    capture_output=True, text=True, check=True)
            window_id = result.stdout.strip()
            self.logger.debug(f"DEBUG: Linux active window ID from xdotool: {window_id}")

            # Get window title
            result = subprocess.run(['xdotool', 'getwindowname', window_id],
                                    capture_output=True, text=True, check=True)
            window_title = result.stdout.strip()
            self.logger.debug(f"DEBUG: Linux window title from xdotool: '{window_title}'")

            # Get PID
            result = subprocess.run(['xdotool', 'getwindowpid', window_id],
                                    capture_output=True, text=True, check=True)
            pid = int(result.stdout.strip())
            self.logger.debug(f"DEBUG: Linux PID from xdotool: {pid}")

            process = psutil.Process(pid)
            process_name = process.name()
            executable_path = process.exe()
            self.logger.debug(f"DEBUG: Linux Process found: Name='{process_name}', Executable='{executable_path}'")

            return AppInfo(
                process_name=process_name,
                window_title=window_title,
                pid=pid,
                executable_path=executable_path
            )
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            self.logger.warning(f"WARNING: xdotool not found or failed ({e}). Falling back to wmctrl for Linux active window detection (less precise for 'active').")
            # Fallback to wmctrl if xdotool fails or is not found
            try:
                # wmctrl provides -l -p (list windows, PIDs)
                result = subprocess.run(['wmctrl', '-l', '-p'],
                                        capture_output=True, text=True, check=True)
                lines = result.stdout.strip().split('\n')

                # Note: wmctrl -l -p doesn't directly tell you which window is active.
                # A robust solution on Linux for 'active window' often involves parsing
                # `xprop -root _NET_ACTIVE_WINDOW` to get the active window ID, then finding
                # that ID in the wmctrl output. For simplicity, if xdotool fails,
                # this fallback might just return the first process it successfully identifies.
                for line in lines:
                    parts = line.split(None, 4)
                    if len(parts) >= 5:
                        # window_id_wm = parts[0] # Example: 0x01e00003
                        pid_wm = int(parts[2])
                        window_title_wm = parts[4]

                        try:
                            process = psutil.Process(pid_wm)
                            process_name = process.name()
                            executable_path = process.exe()
                            self.logger.debug(f"DEBUG: Linux (wmctrl) Found App: Name='{process_name}', Title='{window_title_wm}'")
                            return AppInfo(
                                process_name=process_name,
                                window_title=window_title_wm,
                                pid=pid_wm,
                                executable_path=executable_path
                            )
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            continue # Skip processes we can't access or that exited
            except (subprocess.CalledProcessError, FileNotFoundError) as e2:
                self.logger.error(f"ERROR: Neither xdotool nor wmctrl found or failed on Linux: {e2}")
            return None
        except Exception as e:
            self.logger.error(f"ERROR: Unexpected error in _get_active_window_linux: {e}")
            return None

    def _execute_block_action(self, app_info: AppInfo) -> bool:
        """Executes the specific blocking action on an app"""
        try:
            if self.block_action == BlockAction.CLOSE:
                return self._close_app(app_info)
            elif self.block_action == BlockAction.MINIMIZE:
                return self._minimize_app(app_info)
            elif self.block_action == BlockAction.BACKGROUND:
                return self._send_to_background(app_info)
            elif self.block_action == BlockAction.WARN:
                return self._warn_user(app_info)
        except Exception as e:
            self.logger.error(f"ERROR: Error executing block action for '{app_info.process_name}': {e}")
            return False
        return False # Should not be reached


    def _close_app(self, app_info: AppInfo) -> bool:
        """Close (terminate) the application by its PID"""
        try:
            process = psutil.Process(app_info.pid)
            process.terminate() # Request termination

            # Give it a short time to terminate gracefully
            try:
                process.wait(timeout=3)
                self.logger.info(f"Successfully terminated app: '{app_info.process_name}' (PID: {app_info.pid})")
                return True
            except psutil.TimeoutExpired:
                self.logger.warning(f"WARNING: App '{app_info.process_name}' (PID: {app_info.pid}) did not terminate, attempting to kill.")
                process.kill() # Force kill
                self.logger.info(f"Force killed app: '{app_info.process_name}' (PID: {app_info.pid})")
                return True
        except psutil.NoSuchProcess:
            self.logger.info(f"App '{app_info.process_name}' (PID: {app_info.pid}) already terminated or not found.")
            return True # Consider it successful if it's already gone
        except Exception as e:
            self.logger.error(f"ERROR: Error closing app '{app_info.process_name}' (PID: {app_info.pid}): {e}")
            return False

    def _minimize_app(self, app_info: AppInfo) -> bool:
        """Minimize the application window on Windows, macOS, or Linux"""
        self.logger.info(f"Minimizing app: '{app_info.process_name}' - '{app_info.window_title}'")
        if self.platform == "win32":
            try:
                # FindWindow is usually by title, but may also need class name for some apps
                hwnd = win32gui.FindWindow(None, app_info.window_title)
                if hwnd:
                    win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
                    self.logger.info(f"Successfully minimized Windows app: '{app_info.window_title}'")
                    return True
                else:
                    self.logger.warning(f"WARNING: Could not find window handle for '{app_info.window_title}' to minimize on Windows.")
            except Exception as e:
                self.logger.error(f"ERROR: Error minimizing Windows app '{app_info.process_name}': {e}")

        elif self.platform == "darwin":
            # if NSWorkspace is None: # Uncomment if you enable macOS imports
            #     self.logger.error("macOS specific modules (PyObjC) not available. Cannot minimize app.")
            #     return False
            # try:
            #     script = f'''
            #     tell application "{app_info.process_name}"
            #         set miniaturized of every window to true
            #     end tell
            #     '''
            #     subprocess.run(['osascript', '-e', script], check=True, capture_output=True)
            #     self.logger.info(f"Successfully minimized macOS app: '{app_info.process_name}'")
            #     return True
            # except subprocess.CalledProcessError as e:
            #     self.logger.error(f"Error minimizing macOS app '{app_info.process_name}' via osascript: {e.stderr.strip()}")
            # except Exception as e:
            #     self.logger.error(f"Unexpected error minimizing macOS app '{app_info.process_name}': {e}")
            self.logger.debug("DEBUG: _minimize_app called for macOS but functionality is disabled/unavailable.")
            pass

        elif self.platform.startswith("linux"):
            try:
                # xdotool requires window ID, not PID for minimize. Search by PID.
                # '--limit 1' to get only one window in case multiple exist for a PID.
                window_id_cmd = ['xdotool', 'search', '--pid', str(app_info.pid), '--limit', '1']
                result = subprocess.run(window_id_cmd, capture_output=True, text=True, check=False)
                if result.returncode == 0 and result.stdout.strip():
                    window_id = result.stdout.strip()
                    subprocess.run(['xdotool', 'windowminimize', window_id], check=True, capture_output=True)
                    self.logger.info(f"Successfully minimized Linux app: '{app_info.process_name}' (Window ID: {window_id})")
                    return True
                else:
                    self.logger.warning(f"WARNING: Could not find window ID for PID {app_info.pid} to minimize on Linux. xdotool search output: {result.stderr.strip()}")
            except subprocess.CalledProcessError as e:
                self.logger.error(f"ERROR: Error minimizing Linux app '{app_info.process_name}' via xdotool: {e.stderr.strip()}")
            except FileNotFoundError:
                self.logger.error("ERROR: xdotool command not found. Please install xdotool for Linux window control.")
            except Exception as e:
                self.logger.error(f"ERROR: Unexpected error minimizing Linux app '{app_info.process_name}': {e}")

        return False

    def _send_to_background(self, app_info: AppInfo) -> bool:
        """Send application to background (Windows-specific, minimizes as fallback for others)"""
        self.logger.info(f"Sending app to background: '{app_info.process_name}' - '{app_info.window_title}'")
        if self.platform == "win32":
            try:
                hwnd = win32gui.FindWindow(None, app_info.window_title)
                if hwnd:
                    # Set window to bottom of Z-order
                    win32gui.SetWindowPos(hwnd, win32con.HWND_BOTTOM,
                                         0, 0, 0, 0,
                                         win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
                    # Optional: Deactivate the window. Be careful, this can be aggressive.
                    # win32gui.SetForegroundWindow(0)
                    self.logger.info(f"Successfully sent Windows app '{app_info.window_title}' to background.")
                    return True
                else:
                    self.logger.warning(f"WARNING: Could not find window handle for '{app_info.window_title}' to send to background on Windows.")
            except Exception as e:
                self.logger.error(f"ERROR: Error sending Windows app '{app_info.process_name}' to background: {e}")

        # For other platforms, minimize as a practical 'send to background'
        self.logger.info(f"Falling back to minimize for background action on {self.platform} for app: '{app_info.process_name}'")
        return self._minimize_app(app_info)

    def _warn_user(self, app_info: AppInfo) -> bool:
        """Show warning to user about blocked app (via callback if provided)"""
        app_key = app_info.process_name.lower() # Use lowercased process name as key for warning frequency
        current_time = time.time()

        # Only show warning once per app per session or every 5 minutes (300 seconds)
        if (app_key not in self.warning_shown or
            current_time - self.warning_shown[app_key] > 300):

            self.warning_shown[app_key] = current_time

            # Trigger the external callback if provided
            if self.activity_callback: # Changed to activity_callback as per project brief
                self.logger.debug(f"DEBUG: Calling activity callback for '{app_info.process_name}' (event: 'blocked_app_access').")
                self.activity_callback(app_info, "blocked_app_access") # Pass app_info and event type
            else:
                self.logger.info("INFO: No activity callback set, so no custom warning displayed.")

            self.logger.warning(f"BLOCKED ACCESS: Attempt detected for '{app_info.process_name}' ('{app_info.window_title}').")
            return True # Indicate that a warning was just issued

        self.logger.debug(f"DEBUG: Warning for '{app_info.process_name}' skipped due to frequency limit.")
        return False # Indicate no warning was issued (due to frequency limit)

    def _check_self_integrity(self) -> bool:
        """
        Basic anti-cheat: Checks if this app's own process is still running and healthy.
        More advanced checks (e.g., file integrity, root process monitoring) would be external.
        """
        try:
            current_process = psutil.Process(self._my_pid)
            if not current_process.is_running() or current_process.name().lower() != self._my_process_name.lower():
                self.logger.critical("CRITICAL: Self-integrity check failed! This app's process might have been terminated or tampered with.")
                # In a real app, you might trigger a system alert, log to a persistent file,
                # or attempt to re-launch a watchdog process here.
                return False
            # Check if CPU usage is extremely low (could indicate suspension)
            # This is a very rough check and can have false positives.
            if current_process.cpu_percent(interval=0.1) < 0.1: # Very low CPU for 0.1s
                self.logger.debug("DEBUG: Self-integrity: Very low CPU usage detected, might be suspended.")
            return True
        except psutil.NoSuchProcess:
            self.logger.critical("CRITICAL: Self-integrity check failed: This app's process is no longer running!")
            return False
        except Exception as e:
            self.logger.error(f"ERROR: Unexpected error during self-integrity check: {e}")
            return False

    def start_monitoring(self, check_interval: float = 1.0):
        """Start monitoring for blocked apps in a separate daemon thread"""
        if self.running:
            self.logger.info("Monitoring is already running.")
            return

        self.running = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(check_interval,),
            daemon=True # Daemon thread exits automatically when the main program exits
        )
        self.monitor_thread.start()
        self.logger.info("Started app monitoring thread.")

    def stop_monitoring(self):
        """Stop the application monitoring thread cleanly"""
        if not self.running:
            self.logger.info("Monitoring is not running.")
            return

        self.running = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.logger.info("Stopping app monitoring thread... Waiting for it to finish (max 5 seconds).")
            self.monitor_thread.join(timeout=5.0) # Give thread some time to shut down
            if self.monitor_thread.is_alive():
                self.logger.warning("WARNING: Monitor thread did not terminate cleanly within timeout. It might still be running briefly.")
        self.logger.info("Stopped app monitoring.")

    def _monitor_loop(self, check_interval: float):
        """Main loop that continuously monitors the active window for changes and blocked apps"""
        last_app_info: Optional[AppInfo] = None # Stores info of the previously active app
        self.logger.debug("DEBUG: Monitor loop started.")

        while self.running:
            try:
                # Self-integrity check
                if not self._check_self_integrity():
                    self.logger.critical("CRITICAL: Self-integrity check failed. Stopping monitoring.")
                    self.stop_monitoring() # Stop self if integrity compromised
                    break # Exit the loop

                current_app_info = self.get_active_window_info()

                # Determine app category and log if it changes
                current_app_category = "unknown"
                if current_app_info:
                    current_app_category = self.categorize_app(current_app_info)
                    current_app_info.category = current_app_category # Update AppInfo object

                    # Log active app info if it changes or if it's the very first one
                    if (last_app_info is None or
                        current_app_info.process_name != last_app_info.process_name or
                        current_app_info.window_title != last_app_info.window_title):
                        self.logger.info(f"Active App: {current_app_info.process_name} - '{current_app_info.window_title}' (Category: {current_app_category.upper()})")
                        last_app_info = current_app_info
                else:
                    # Log when no foreground window is active (e.g., desktop)
                    if last_app_info is not None:
                        self.logger.info("Active App: None (Desktop or no active window)")
                        last_app_info = None # Reset last_app_info if nothing is active

                # Trigger activity callback for *all* active app changes (for points system)
                if self.activity_callback and current_app_info:
                    self.activity_callback(current_app_info, "active_app_changed")

                # Check if the current active app is an entertainment app and should be blocked (lack of points)
                # This `has_points` argument would be provided by the central point system.
                # For now, let's assume `has_points=False` to test blocking by uncommenting below.
                # In a real system, you'd fetch this from the point system.
                simulate_no_points = False # Change to True to test blocking
                
                if self.is_entertainment_app_blocked(current_app_info, has_points=not simulate_no_points):
                    self.logger.warning(f"BLOCKED: Entertainment app '{current_app_info.process_name}' detected without sufficient points!")
                    self._execute_block_action(current_app_info) # Take configured block action

                time.sleep(check_interval) # Pause for the defined interval
            except Exception as e:
                self.logger.error(f"ERROR: Unexpected error in monitoring loop: {e}")
                time.sleep(check_interval) # Still sleep to prevent tight loop on error
        self.logger.debug("DEBUG: Monitor loop exited.") # Log when the loop finishes

    def get_running_processes(self) -> List[AppInfo]:
        """Get list of all currently running processes on the system (excluding detailed window titles)"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                # Get basic process info
                process_name = proc.info['name']
                executable_path = proc.info['exe'] or "" # .exe can be None for some system processes

                # Note: window_title for ALL running processes is complex and OS-specific.
                # For this function, it's left empty as it's not readily available for non-foreground windows.
                processes.append(AppInfo(
                    process_name=process_name,
                    window_title="", # Window title is unknown for non-active processes here
                    pid=proc.info['pid'],
                    executable_path=executable_path
                ))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # Process may have exited or permissions denied, skip it
                continue
            except Exception as e:
                self.logger.debug(f"DEBUG: Could not get info for process {proc.info.get('pid', 'N/A')}: {e}")
        return processes

    def force_close_all_categorized_apps(self, category: str):
        """Force close all currently running apps belonging to a specific category (e.g., 'entertainment')"""
        self.logger.info(f"Attempting to force close all running apps in category: '{category}'.")
        processes = self.get_running_processes()
        closed_count = 0

        for proc_info in processes:
            # We must use a temporary AppInfo for categorize_app as it expects process name/exe path
            temp_app_info = AppInfo(
                process_name=proc_info.process_name,
                window_title="", # Window title is unknown when checking all processes
                pid=proc_info.pid,
                executable_path=proc_info.executable_path
            )

            if self.categorize_app(temp_app_info) == category.lower():
                self.logger.info(f"Found running '{category}' app to force close: '{temp_app_info.process_name}' (PID: {temp_app_info.pid})")
                if self._close_app(temp_app_info): # Use the internal _close_app method
                    closed_count += 1

        self.logger.info(f"Force closed {closed_count} '{category}' applications.")
        return closed_count

    def __del__(self):
        """Cleanup when controller object is destroyed (attempts to stop monitoring)"""
        # This is not guaranteed to run in all shutdown scenarios, so explicit stop_monitoring is better.
        self.stop_monitoring()
        self.logger.debug("DEBUG: AppController object destroyed.")


# --- Main execution block for testing/demonstration ---
# This block MUST be outdented to the top level (no indentation)
# so that the AppController class is fully defined before it's used.
if __name__ == "__main__":
    print("Starting GetB@ck2Work App Controller...")

    # Instantiate the controller
    controller = AppController()

    # --- Configure App Categories ---
    # Add some example entertainment apps to test blocking
    # These are case-insensitive and match against process name, window title, or executable path
    controller.add_entertainment_app("chrome.exe") # Example: Chrome is entertainment
    controller.add_entertainment_app("spotify.exe")
    controller.add_entertainment_app("steam")
    controller.add_entertainment_app("discord")
    controller.add_entertainment_app("netflix") # Will match browser if title includes "netflix"
    controller.add_entertainment_app("youtube") # Will match browser if title includes "youtube"

    # Add some example productivity apps
    controller.add_productivity_app("code.exe") # Visual Studio Code
    controller.add_productivity_app("notepad.exe")
    controller.add_productivity_app("msword.exe")
    controller.add_productivity_app("excel.exe")
    controller.add_productivity_app("notion") # Will match browser title/process if using Notion web/desktop app

    # Add some example neutral apps (explicitly not earning/deducting points)
    controller.add_neutral_app("calculator.exe")


    # --- Set a block action (default is WARN) ---
    # Uncomment one of these lines to change the action when an entertainment app is detected
    # AND simulate_no_points is True
    # controller.set_block_action(BlockAction.MINIMIZE)
    # controller.set_block_action(BlockAction.CLOSE)
    # controller.set_block_action(BlockAction.BACKGROUND)


    # --- Example for a custom activity/violation callback ---
    # This function would be called when the active app changes, or when a blocked app is accessed.
    # In a full application, this would update the GUI, point system, etc.
    def my_activity_callback(app_info: AppInfo, event_type: str):
        print(f"\n--- Callback Triggered: {event_type.upper()} ---")
        print(f"  App: {app_info.process_name} (PID: {app_info.pid})")
        print(f"  Title: '{app_info.window_title}'")
        print(f"  Category: {app_info.category.upper()}")
        
        if event_type == "blocked_app_access":
            print("  ACTION: Attempted to access a restricted entertainment app without points!")
            # Example of how you could show a persistent GUI message (requires a GUI framework)
            # import ctypes
            # ctypes.windll.user32.MessageBoxW(0, f"Blocked App: {app_info.window_title}\n(Category: {app_info.category.upper()})\n\nEarn more productivity points to access entertainment!", "GetB@ck2Work Alert!", 0x1000)
        elif event_type == "active_app_changed":
            print(f"  INFO: Active application changed.")
        print("------------------------------------\n")

    # Uncomment the line below to enable the custom activity callback
    controller.activity_callback = my_activity_callback

    # --- Simulate Point System Logic (for testing blocking) ---
    # Set to True to make the controller *attempt* to block entertainment apps.
    # This `simulate_no_points` variable is passed to `is_entertainment_app_blocked`.
    # In a real system, the `has_points` argument would come from the actual point system logic.
    simulate_no_points = True # Change this to False if you want to test *not* blocking
    if simulate_no_points:
        controller.logger.warning("\nWARNING: 'simulate_no_points' is TRUE. Entertainment apps will be blocked by default.")
        controller.logger.warning(f"Blocking action is set to: {controller.block_action.value.upper()}\n")
    else:
        controller.logger.info("\nINFO: 'simulate_no_points' is FALSE. Entertainment apps will NOT be blocked (assuming user has points).\n")


    # Start the monitoring thread
    # check_interval: How often (in seconds) to check the active window. Lower value = more frequent checks.
    controller.start_monitoring(check_interval=0.5) # Check every 0.5 seconds for responsiveness

    # Keep the main thread alive. The daemon monitor_thread will run in the background.
    # Without this loop, the script would exit immediately after starting the daemon thread.
    print("Monitoring active applications. Look for 'Active App:' messages and '--- Callback Triggered ---' above.")
    print("To stop monitoring, press Ctrl+C in this terminal window.")

    try:
        while True:
            time.sleep(1) # Main thread sleeps, allowing daemon thread to run efficiently
    except KeyboardInterrupt:
        print("\nCtrl+C detected. Stopping monitoring...")
        controller.stop_monitoring() # Ensure clean shutdown of the thread
        print("Program exited.")