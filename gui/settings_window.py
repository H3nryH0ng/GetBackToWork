import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, Optional
import json
from pathlib import Path

from config import settings
from core.data_manager import DataManager
from .styles import get_style

class SettingsWindow:
    def __init__(self, parent: Optional[tk.Tk] = None):
        self.parent = parent
        self.root = tk.Toplevel(parent) if parent else tk.Tk()
        self.root.title("GetB@ck2Work Settings")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        # Initialize components
        self.data_manager = DataManager()
        self.current_settings = self._load_settings()
        
        # Setup GUI
        self._setup_styles()
        self._create_widgets()
        
        # Center the window
        self._center_window()

    def _load_settings(self) -> Dict[str, Any]:
        """Load current settings from file."""
        try:
            return self.data_manager.read_data(settings.USER_SETTINGS_FILE)
        except Exception:
            return settings.DEFAULT_SETTINGS.copy()

    def _setup_styles(self):
        """Setup custom styles for the settings window."""
        style = ttk.Style()
        style.theme_use('clam')
        
        config = get_style()
        colors = config['colors']
        fonts = config['fonts']
        
        # Configure settings-specific styles
        style.configure('Settings.TFrame',
                       background=colors['background'],
                       relief='solid',
                       borderwidth=1)
        style.configure('Settings.TLabel',
                       background=colors['background'],
                       foreground=colors['text'],
                       font=fonts['normal'])
        style.configure('Settings.TButton',
                       background=colors['primary'],
                       foreground='white',
                       font=fonts['normal'],
                       padding=5)

    def _create_widgets(self):
        """Create and arrange settings widgets."""
        # Main container
        self.main_frame = ttk.Frame(self.root, style='Settings.TFrame', padding=20)
        self.main_frame.pack(expand=True, fill='both')
        
        # Create notebook for different setting categories
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(expand=True, fill='both', pady=10)
        
        # General settings tab
        self.general_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.general_frame, text='General')
        self._create_general_settings()
        
        # Points settings tab
        self.points_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.points_frame, text='Points')
        self._create_points_settings()
        
        # App settings tab
        self.apps_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.apps_frame, text='Applications')
        self._create_app_settings()
        
        # Theme settings tab
        self.theme_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.theme_frame, text='Theme')
        self._create_theme_settings()
        
        # Buttons
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(pady=10)
        
        ttk.Button(self.button_frame,
                  text="Save",
                  style='Settings.TButton',
                  command=self._save_settings).pack(side='left', padx=5)
        
        ttk.Button(self.button_frame,
                  text="Cancel",
                  style='Settings.TButton',
                  command=self._on_cancel).pack(side='left', padx=5)

    def _create_general_settings(self):
        """Create general settings widgets."""
        # Block level
        ttk.Label(self.general_frame,
                 text="Block Level:",
                 style='Settings.TLabel').grid(row=0, column=0, sticky='w', pady=5)
        
        self.block_level = ttk.Combobox(self.general_frame,
                                      values=list(settings.BLOCK_LEVELS.keys()),
                                      state='readonly')
        self.block_level.set(self.current_settings['block_level'])
        self.block_level.grid(row=0, column=1, sticky='w', pady=5)
        
        # Notifications
        self.notifications_var = tk.BooleanVar(
            value=self.current_settings['notifications_enabled'])
        ttk.Checkbutton(self.general_frame,
                       text="Enable Notifications",
                       variable=self.notifications_var,
                       style='Settings.TLabel').grid(row=1, column=0,
                                                   columnspan=2,
                                                   sticky='w',
                                                   pady=5)
        
        # Startup
        self.startup_var = tk.BooleanVar(
            value=self.current_settings['startup_enabled'])
        ttk.Checkbutton(self.general_frame,
                       text="Start with Windows",
                       variable=self.startup_var,
                       style='Settings.TLabel').grid(row=2, column=0,
                                                   columnspan=2,
                                                   sticky='w',
                                                   pady=5)

    def _create_points_settings(self):
        """Create points-related settings widgets."""
        # Points per interval
        ttk.Label(self.points_frame,
                 text="Points per interval:",
                 style='Settings.TLabel').grid(row=0, column=0,
                                             sticky='w',
                                             pady=5)
        
        self.points_per_interval = ttk.Spinbox(self.points_frame,
                                             from_=1,
                                             to=10,
                                             width=5)
        self.points_per_interval.set(self.current_settings['points_per_interval'])
        self.points_per_interval.grid(row=0, column=1, sticky='w', pady=5)
        
        # Time interval
        ttk.Label(self.points_frame,
                 text="Time interval (minutes):",
                 style='Settings.TLabel').grid(row=1, column=0,
                                             sticky='w',
                                             pady=5)
        
        self.time_interval = ttk.Spinbox(self.points_frame,
                                       from_=1,
                                       to=60,
                                       width=5)
        self.time_interval.set(self.current_settings['time_interval'] // 60)
        self.time_interval.grid(row=1, column=1, sticky='w', pady=5)
        
        # Streak settings
        ttk.Label(self.points_frame,
                 text="Streak threshold (minutes):",
                 style='Settings.TLabel').grid(row=2, column=0,
                                             sticky='w',
                                             pady=5)
        
        self.streak_threshold = ttk.Spinbox(self.points_frame,
                                          from_=30,
                                          to=120,
                                          width=5)
        self.streak_threshold.set(self.current_settings['streak_threshold'] // 60)
        self.streak_threshold.grid(row=2, column=1, sticky='w', pady=5)
        
        # Streak bonus
        ttk.Label(self.points_frame,
                 text="Streak bonus (%):",
                 style='Settings.TLabel').grid(row=3, column=0,
                                             sticky='w',
                                             pady=5)
        
        self.streak_bonus = ttk.Spinbox(self.points_frame,
                                      from_=5,
                                      to=50,
                                      width=5)
        self.streak_bonus.set(int(self.current_settings['streak_bonus'] * 100))
        self.streak_bonus.grid(row=3, column=1, sticky='w', pady=5)

    def _create_app_settings(self):
        """Create application-related settings widgets."""
        # App categories
        ttk.Label(self.apps_frame,
                 text="Application Categories",
                 style='Settings.TLabel').pack(pady=5)
        
        # Create treeview for app categories
        self.app_tree = ttk.Treeview(self.apps_frame,
                                    columns=('Category', 'Type'),
                                    show='headings')
        self.app_tree.heading('Category', text='Category')
        self.app_tree.heading('Type', text='Type')
        self.app_tree.pack(expand=True, fill='both', pady=5)
        
        # Load app categories
        self._load_app_categories()
        
        # Buttons for managing categories
        button_frame = ttk.Frame(self.apps_frame)
        button_frame.pack(pady=5)
        
        ttk.Button(button_frame,
                  text="Add",
                  style='Settings.TButton',
                  command=self._add_category).pack(side='left', padx=5)
        
        ttk.Button(button_frame,
                  text="Edit",
                  style='Settings.TButton',
                  command=self._edit_category).pack(side='left', padx=5)
        
        ttk.Button(button_frame,
                  text="Remove",
                  style='Settings.TButton',
                  command=self._remove_category).pack(side='left', padx=5)

    def _create_theme_settings(self):
        """Create theme-related settings widgets."""
        # Theme selection
        ttk.Label(self.theme_frame,
                 text="Theme:",
                 style='Settings.TLabel').grid(row=0, column=0,
                                             sticky='w',
                                             pady=5)
        
        self.theme_var = tk.StringVar(value=self.current_settings['theme'])
        ttk.Radiobutton(self.theme_frame,
                       text="Light",
                       variable=self.theme_var,
                       value="light",
                       style='Settings.TLabel').grid(row=0, column=1,
                                                   sticky='w',
                                                   pady=5)
        
        ttk.Radiobutton(self.theme_frame,
                       text="Dark",
                       variable=self.theme_var,
                       value="dark",
                       style='Settings.TLabel').grid(row=1, column=1,
                                                   sticky='w',
                                                   pady=5)
        
        # Overlay opacity
        ttk.Label(self.theme_frame,
                 text="Overlay Opacity:",
                 style='Settings.TLabel').grid(row=2, column=0,
                                             sticky='w',
                                             pady=5)
        
        self.opacity_var = tk.DoubleVar(
            value=self.current_settings['overlay_opacity'])
        self.opacity_scale = ttk.Scale(self.theme_frame,
                                     from_=0.1,
                                     to=1.0,
                                     variable=self.opacity_var,
                                     orient='horizontal')
        self.opacity_scale.grid(row=2, column=1, sticky='w', pady=5)

    def _load_app_categories(self):
        """Load application categories into the treeview."""
        try:
            categories = self.data_manager.read_data(settings.APP_CATEGORIES_FILE)
            for category, data in categories.items():
                for app_type, apps in data.items():
                    for app in apps:
                        self.app_tree.insert('', 'end', values=(app, f"{category} - {app_type}"))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load app categories: {str(e)}")

    def _add_category(self):
        """Add a new application category."""
        # TODO: Implement add category dialog
        messagebox.showinfo("Coming Soon", "Add category feature coming soon!")

    def _edit_category(self):
        """Edit an existing application category."""
        # TODO: Implement edit category dialog
        messagebox.showinfo("Coming Soon", "Edit category feature coming soon!")

    def _remove_category(self):
        """Remove an application category."""
        selected = self.app_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a category to remove")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to remove this category?"):
            self.app_tree.delete(selected)

    def _save_settings(self):
        """Save current settings."""
        try:
            # Update settings dictionary
            self.current_settings.update({
                'block_level': self.block_level.get(),
                'notifications_enabled': self.notifications_var.get(),
                'startup_enabled': self.startup_var.get(),
                'points_per_interval': int(self.points_per_interval.get()),
                'time_interval': int(self.time_interval.get()) * 60,  # Convert to seconds
                'streak_threshold': int(self.streak_threshold.get()) * 60,  # Convert to seconds
                'streak_bonus': float(self.streak_bonus.get()) / 100,  # Convert to decimal
                'theme': self.theme_var.get(),
                'overlay_opacity': self.opacity_var.get()
            })
            
            # Save to file
            self.data_manager.write_data(settings.USER_SETTINGS_FILE,
                                       self.current_settings)
            
            messagebox.showinfo("Success", "Settings saved successfully!")
            self._on_close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")

    def _on_cancel(self):
        """Handle cancel button click."""
        if messagebox.askyesno("Confirm", "Discard changes?"):
            self._on_close()

    def _on_close(self):
        """Handle window closing."""
        self.root.destroy()

    def _center_window(self):
        """Center the settings window on the screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def run(self):
        """Start the settings window."""
        self.root.mainloop() 