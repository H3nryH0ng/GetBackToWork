from typing import Dict, Any
import tkinter as tk
from tkinter import ttk

def get_style() -> Dict[str, Any]:
    """Get the application's style configuration."""
    return {
        'colors': {
            'primary': '#4a90e2',
            'secondary': '#f5f5f5',
            'accent': '#50c878',
            'warning': '#ff6b6b',
            'text': '#333333',
            'text_light': '#666666',
            'background': '#ffffff',
            'background_dark': '#f0f0f0'
        },
        'fonts': {
            'header': ('Arial', 16, 'bold'),
            'subheader': ('Arial', 14, 'bold'),
            'normal': ('Arial', 10),
            'small': ('Arial', 8),
            'points': ('Arial', 24, 'bold')
        },
        'padding': {
            'small': 5,
            'normal': 10,
            'large': 20
        }
    }

def apply_style(root: tk.Tk):
    """Apply the application's style to the root window."""
    style = ttk.Style()
    style.theme_use('clam')
    
    # Get style configuration
    config = get_style()
    colors = config['colors']
    fonts = config['fonts']
    
    # Configure common styles
    style.configure('TFrame', background=colors['background'])
    style.configure('TLabel', 
                   background=colors['background'],
                   foreground=colors['text'],
                   font=fonts['normal'])
    style.configure('TButton',
                   background=colors['primary'],
                   foreground='white',
                   font=fonts['normal'],
                   padding=config['padding']['normal'])
    
    # Configure custom styles
    style.configure('Header.TLabel',
                   font=fonts['header'],
                   foreground=colors['primary'])
    style.configure('Subheader.TLabel',
                   font=fonts['subheader'],
                   foreground=colors['text'])
    style.configure('Points.TLabel',
                   font=fonts['points'],
                   foreground=colors['accent'])
    style.configure('Warning.TLabel',
                   font=fonts['normal'],
                   foreground=colors['warning'])
    
    # Configure button styles
    style.configure('Primary.TButton',
                   background=colors['primary'],
                   foreground='white')
    style.configure('Secondary.TButton',
                   background=colors['secondary'],
                   foreground=colors['text'])
    style.configure('Warning.TButton',
                   background=colors['warning'],
                   foreground='white')
    
    # Configure frame styles
    style.configure('Card.TFrame',
                   background=colors['background'],
                   relief='solid',
                   borderwidth=1)
    style.configure('Header.TFrame',
                   background=colors['primary'],
                   relief='flat')
    
    # Configure entry styles
    style.configure('TEntry',
                   fieldbackground=colors['background'],
                   foreground=colors['text'],
                   font=fonts['normal'])
    
    # Configure combobox styles
    style.configure('TCombobox',
                   fieldbackground=colors['background'],
                   background=colors['background'],
                   foreground=colors['text'],
                   font=fonts['normal'])
    
    # Configure scrollbar styles
    style.configure('TScrollbar',
                   background=colors['secondary'],
                   arrowcolor=colors['text'])
    
    # Configure progressbar styles
    style.configure('TProgressbar',
                   background=colors['primary'],
                   troughcolor=colors['secondary'])
    
    # Configure notebook styles
    style.configure('TNotebook',
                   background=colors['background'],
                   tabmargins=[2, 5, 2, 0])
    style.configure('TNotebook.Tab',
                   background=colors['secondary'],
                   foreground=colors['text'],
                   padding=config['padding']['normal'])
    
    # Configure treeview styles
    style.configure('Treeview',
                   background=colors['background'],
                   foreground=colors['text'],
                   fieldbackground=colors['background'])
    style.configure('Treeview.Heading',
                   background=colors['secondary'],
                   foreground=colors['text'],
                   font=fonts['normal'])
    
    # Configure hover effects
    style.map('TButton',
              background=[('active', colors['primary'])],
              foreground=[('active', 'white')])
    style.map('TEntry',
              fieldbackground=[('focus', colors['background'])],
              foreground=[('focus', colors['text'])])
    style.map('TCombobox',
              fieldbackground=[('readonly', colors['background'])],
              selectbackground=[('readonly', colors['primary'])])
    
    # Configure disabled states
    style.map('TButton',
              background=[('disabled', colors['secondary'])],
              foreground=[('disabled', colors['text_light'])])
    style.map('TEntry',
              fieldbackground=[('disabled', colors['secondary'])],
              foreground=[('disabled', colors['text_light'])])
    style.map('TLabel',
              foreground=[('disabled', colors['text_light'])]) 