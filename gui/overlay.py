import tkinter as tk
from tkinter import ttk
import random
from typing import List, Optional
import threading
import time
from pathlib import Path
import json

from config import settings
from .styles import get_style

class OverlayWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("GetB@ck2Work Overlay")
        self.root.attributes('-alpha', settings.OVERLAY_OPACITY)
        self.root.attributes('-topmost', True)
        self.root.overrideredirect(True)  # Remove window decorations
        
        # Load motivational messages
        self.messages = self._load_messages()
        
        # Setup GUI
        self._setup_styles()
        self._create_widgets()
        
        # Center the window
        self._center_window()
        
        # Start message rotation
        self._start_message_rotation()

    def _load_messages(self) -> List[str]:
        """Load motivational messages from file or use defaults."""
        try:
            messages_file = Path(__file__).parent / "assets" / "messages.json"
            if messages_file.exists():
                with open(messages_file, 'r') as f:
                    return json.load(f)['messages']
        except Exception:
            pass
        
        # Default messages if file not found or error
        return [
            "Time to get back to work!",
            "Your productivity points are running low!",
            "Stay focused, stay productive!",
            "Every minute counts!",
            "You can do better!",
            "Back to work, champ!",
            "Productivity is the key to success!",
            "Don't let distractions win!",
            "Your future self will thank you!",
            "Stay on track, stay successful!"
        ]

    def _setup_styles(self):
        """Setup custom styles for the overlay."""
        style = ttk.Style()
        style.theme_use('clam')
        
        config = get_style()
        colors = config['colors']
        fonts = config['fonts']
        
        # Configure overlay-specific styles
        style.configure('Overlay.TFrame',
                       background=colors['background'],
                       relief='solid',
                       borderwidth=2)
        style.configure('Overlay.TLabel',
                       background=colors['background'],
                       foreground=colors['text'],
                       font=fonts['header'],
                       wraplength=400)
        style.configure('Overlay.TButton',
                       background=colors['primary'],
                       foreground='white',
                       font=fonts['normal'],
                       padding=10)

    def _create_widgets(self):
        """Create and arrange overlay widgets."""
        # Main container
        self.main_frame = ttk.Frame(self.root, style='Overlay.TFrame', padding=20)
        self.main_frame.pack(expand=True, fill='both')
        
        # Message display
        self.message_label = ttk.Label(self.main_frame,
                                     text="",
                                     style='Overlay.TLabel',
                                     justify='center')
        self.message_label.pack(pady=20)
        
        # Haiku input
        self.haiku_frame = ttk.Frame(self.main_frame)
        self.haiku_frame.pack(pady=10)
        
        ttk.Label(self.haiku_frame,
                 text="Enter a haiku to continue:",
                 style='Overlay.TLabel').pack()
        
        self.haiku_entry = ttk.Entry(self.haiku_frame, width=40)
        self.haiku_entry.pack(pady=10)
        
        # Submit button
        self.submit_button = ttk.Button(self.haiku_frame,
                                      text="Submit",
                                      style='Overlay.TButton',
                                      command=self._check_haiku)
        self.submit_button.pack(pady=10)
        
        # Close button
        self.close_button = ttk.Button(self.main_frame,
                                     text="Close",
                                     style='Overlay.TButton',
                                     command=self._on_close)
        self.close_button.pack(pady=10)

    def _center_window(self):
        """Center the overlay window on the screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def _start_message_rotation(self):
        """Start rotating motivational messages."""
        def rotate_messages():
            while True:
                message = random.choice(self.messages)
                self.message_label.config(text=message)
                time.sleep(5)  # Change message every 5 seconds
        
        threading.Thread(target=rotate_messages, daemon=True).start()

    def _check_haiku(self):
        """Check if the entered text is a valid haiku."""
        haiku = self.haiku_entry.get().strip()
        lines = haiku.split('\n')
        
        if len(lines) != 3:
            self._show_error("A haiku must have exactly 3 lines!")
            return
        
        # Simple syllable counting (very basic implementation)
        def count_syllables(line: str) -> int:
            words = line.lower().split()
            count = 0
            for word in words:
                # Very basic syllable counting
                count += len([c for c in word if c in 'aeiouy'])
            return count
        
        syllables = [count_syllables(line) for line in lines]
        if syllables != [5, 7, 5]:
            self._show_error("Invalid haiku! Must follow 5-7-5 syllable pattern.")
            return
        
        # Valid haiku
        self._on_close()

    def _show_error(self, message: str):
        """Show an error message."""
        self.message_label.config(text=message, foreground='red')
        self.root.after(2000, self._start_message_rotation)  # Reset message after 2 seconds

    def _on_close(self):
        """Handle overlay closing."""
        self.root.destroy()

    def show(self):
        """Show the overlay window."""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        self.haiku_entry.focus()

    def hide(self):
        """Hide the overlay window."""
        self.root.withdraw()

    def run(self):
        """Start the overlay window."""
        self.root.mainloop() 