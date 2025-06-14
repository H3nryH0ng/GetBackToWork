import tkinter as tk
from tkinter import ttk, messagebox
import pystray
from PIL import Image, ImageTk
import threading
import time
from datetime import datetime
import os
from pathlib import Path
from typing import Optional, Callable

from config import settings
from core.window_monitor import WindowMonitor
from core.point_system import PointSystem
from core.app_controller import AppController
from core.data_manager import DataManager
from .styles import get_style

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("GetB@ck2Work")
        self.root.geometry(f"{settings.WINDOW_WIDTH}x{settings.WINDOW_HEIGHT}")
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

        # Initialize components
        self.window_monitor = WindowMonitor()
        self.point_system = PointSystem()
        self.app_controller = AppController()
        self.data_manager = DataManager()

        # Setup GUI
        self._setup_styles()
        self._create_widgets()
        self._setup_system_tray()
        self._start_monitoring()

    def _setup_styles(self):
        """Setup custom styles for widgets."""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10))
        self.style.configure('Header.TLabel', font=('Arial', 16, 'bold'))
        self.style.configure('Points.TLabel', font=('Arial', 24, 'bold'))

    def _create_widgets(self):
        """Create and arrange all GUI widgets."""
        # Main container
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky="nsew")

        # Points display
        self.points_frame = ttk.Frame(self.main_frame)
        self.points_frame.grid(row=0, column=0, columnspan=2, pady=10)
        
        ttk.Label(self.points_frame, text="Current Points", 
                 style='Header.TLabel').grid(row=0, column=0, pady=5)
        self.points_label = ttk.Label(self.points_frame, text="0", 
                                    style='Points.TLabel')
        self.points_label.grid(row=1, column=0, pady=5)

        # Daily stats
        self.stats_frame = ttk.LabelFrame(self.main_frame, text="Daily Statistics", padding="10")
        self.stats_frame.grid(row=1, column=0, columnspan=2, pady=10, sticky="ew")
        
        self.stats_labels = {}
        stats = [
            ("Points Earned", "points_earned"),
            ("Points Spent", "points_spent"),
            ("Productive Time", "productive_time"),
            ("Entertainment Time", "entertainment_time"),
            ("Streaks", "streaks")
        ]
        
        for i, (label, key) in enumerate(stats):
            ttk.Label(self.stats_frame, text=label).grid(row=i, column=0, sticky="w", pady=2)
            self.stats_labels[key] = ttk.Label(self.stats_frame, text="0")
            self.stats_labels[key].grid(row=i, column=1, sticky="e", pady=2)

        # Control buttons
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(self.button_frame, text="Settings", 
                  command=self._open_settings).grid(row=0, column=0, padx=5)
        ttk.Button(self.button_frame, text="View History", 
                  command=self._open_history).grid(row=0, column=1, padx=5)
        ttk.Button(self.button_frame, text="Boss Mode", 
                  command=self._activate_boss_mode).grid(row=0, column=2, padx=5)

        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)

    def _setup_system_tray(self):
        """Setup system tray icon and menu."""
        # Create a simple icon (you should replace this with your own icon)
        icon_path = Path(__file__).parent / "assets" / "icon.png"
        if not icon_path.exists():
            # Create a simple icon if none exists
            img = Image.new('RGB', (64, 64), color='red')
            img.save(icon_path)
        
        image = Image.open(icon_path)
        menu = pystray.Menu(
            pystray.MenuItem("Show", self._show_window),
            pystray.MenuItem("Exit", self._quit_application)
        )
        self.tray_icon = pystray.Icon("GetB@ck2Work", image, "GetB@ck2Work", menu)
        
        # Start the tray icon in a separate thread
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def _start_monitoring(self):
        """Start the window monitoring in a separate thread."""
        def monitor_callback(window_title, category, time_spent):
            if category:
                points = self.point_system.calculate_points(category, time_spent)
                self.point_system.update_points(points, category, time_spent)
                self._update_display()
                
                # Handle entertainment apps
                if category == 'entertainment' and not self.point_system.can_access_entertainment():
                    self.app_controller.block_application(window_title, window_title)

        threading.Thread(target=self.window_monitor.start_monitoring, 
                        args=(monitor_callback,), daemon=True).start()

    def _update_display(self):
        """Update all display elements with current data."""
        # Update points
        self.points_label.config(text=str(self.point_system.get_current_points()))
        
        # Update daily stats
        stats = self.point_system.get_daily_stats()
        for key, label in self.stats_labels.items():
            value = stats.get(key, 0)
            if key in ['productive_time', 'entertainment_time']:
                # Convert seconds to hours and minutes
                hours = value // 3600
                minutes = (value % 3600) // 60
                value = f"{hours}h {minutes}m"
            label.config(text=str(value))

    def _open_settings(self):
        """Open the settings window."""
        # TODO: Implement settings window
        messagebox.showinfo("Settings", "Settings window coming soon!")

    def _open_history(self):
        """Open the points history window."""
        # TODO: Implement history window
        messagebox.showinfo("History", "History window coming soon!")

    def _activate_boss_mode(self):
        """Activate boss mode (switch to fake spreadsheet)."""
        # TODO: Implement boss mode
        messagebox.showinfo("Boss Mode", "Boss mode coming soon!")

    def _show_window(self):
        """Show the main window."""
        self.root.deiconify()
        self.root.lift()

    def _on_closing(self):
        """Handle window closing."""
        self.root.withdraw()  # Hide the window instead of closing

    def _quit_application(self):
        """Quit the application completely."""
        self.tray_icon.stop()
        self.root.quit()

    def run(self):
        """Start the main application loop."""
        self.root.mainloop() 