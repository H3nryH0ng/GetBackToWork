# gui.py

import customtkinter
import tkinter as tk
from tkinter import messagebox

import tracker
import threading

import time

# For now, we will NOT import config_manager as requested.
# The functions below will use placeholder logic instead of real data persistence.
# from config_manager import (
#     load_config, save_config,
#     get_productivity_apps, get_entertainment_apps,
#     add_app_to_list, remove_app_from_list,
#     get_points, set_points, get_setting, set_setting
# )

# --- Global Variables for GUI Elements ---

detected_app = ""
detected_app_list = []

# These will hold references to widgets that need to be updated from various parts of the app.
points_label = None
status_indicator_label = None
active_app_label = None
productive_time_label = None
entertainment_time_label = None
activity_log_text = None

# Global variables for App Management tab UI elements
productivity_app_list_frame = None
entertainment_app_list_frame = None
app_name_entry = None
app_type_optionmenu = None

# Global variables for Point Redemption tab UI elements
redeem_points_entry = None
redeem_time_display_label = None
redemption_status_label = None # To show success/error messages

# Global variables for Settings tab UI elements
productive_points_per_min_entry = None
entertainment_points_per_min_entry = None
monitoring_interval_entry = None
startup_checkbox = None
appearance_mode_optionmenu = None
color_theme_optionmenu = None

# --- Dummy Data for UI (until backend integration) ---
_dummy_productivity_apps = ["VS Code", "Notion", "Google Chrome (Work)"]
_dummy_entertainment_apps = ["YouTube", "Netflix", "Steam"]
_dummy_current_points = 100 # Will be replaced by actual points from config
_dummy_points_per_minute_entertainment = 2 # 2 points for 1 minute of entertainment

# Dummy Settings values
_dummy_productive_points_per_minute = 1
_dummy_entertainment_points_per_minute = 0 # No points for entertainment by default
_dummy_monitoring_interval_seconds = 5
_dummy_start_on_startup = False # Boolean
_dummy_appearance_mode = "System"
_dummy_color_theme = "blue"


# --- Helper Functions (General GUI) ---

def switch_tab_to_redeem_points(tabview_widget):
    """
    Helper function to switch the tab to 'Point Redemption'.
    Requires access to the main CTkTabview widget.
    """
    tabview_widget.set("Point Redemption")
    print("Switched to Point Redemption tab.")
    if points_label:
        points_label.configure(text=str(_dummy_current_points))


# --- Dashboard Tab Functions ---

def create_dashboard_tab(tab_frame):
    """
    Populates the Dashboard tab with suggested GUI elements.
    Args:
        tab_frame (customtkinter.CTkFrame): The frame associated with the Dashboard tab.
    """
    tab_frame.columnconfigure(0, weight=1)

    # Current Points Balance
    points_frame = customtkinter.CTkFrame(tab_frame)
    points_frame.pack(pady=(20, 10), padx=20, fill="x")
    points_frame.columnconfigure(0, weight=1)

    customtkinter.CTkLabel(points_frame, text="Current Focus Points:", font=customtkinter.CTkFont(size=16, weight="bold")).grid(row=0, column=0, pady=(10, 0), padx=20, sticky="w")
    global points_label
    points_label = customtkinter.CTkLabel(points_frame, text=str(_dummy_current_points),
                                          font=customtkinter.CTkFont(size=48, weight="bold"), text_color="#FFD700")
    points_label.grid(row=1, column=0, pady=(0, 10), padx=20, sticky="ew")

    # A Textbox to show all detected apps
    global detected_apps_TB
    detected_apps_TB = customtkinter.CTkTextbox(tab_frame, height=100, width=400, state="disabled")
    detected_apps_TB.pack()

    # Monitoring Status Indicator
    status_frame = customtkinter.CTkFrame(tab_frame)
    status_frame.pack(pady=10, padx=20, fill="x")
    status_frame.columnconfigure(0, weight=1)
    status_frame.columnconfigure(1, weight=1)

    customtkinter.CTkLabel(status_frame, text="Monitoring Status:", font=customtkinter.CTkFont(size=14)).grid(row=0, column=0, pady=5, padx=20, sticky="w")
    global status_indicator_label
    status_indicator_label = customtkinter.CTkLabel(status_frame, text="Inactive", font=customtkinter.CTkFont(size=14, weight="bold"), text_color="red")
    status_indicator_label.grid(row=0, column=1, pady=5, padx=20, sticky="e")

    # Currently Active Application/Website
    active_app_frame = customtkinter.CTkFrame(tab_frame)
    active_app_frame.pack(pady=10, padx=20, fill="x")
    active_app_frame.columnconfigure(0, weight=1)
    active_app_frame.columnconfigure(1, weight=2)

    customtkinter.CTkLabel(active_app_frame, text="Currently Active:", font=customtkinter.CTkFont(size=14)).grid(row=0, column=0, pady=5, padx=20, sticky="w")
    global active_app_label
    active_app_label = customtkinter.CTkLabel(active_app_frame, text="N/A", font=customtkinter.CTkFont(size=14, slant="italic"))
    active_app_label.grid(row=0, column=1, pady=5, padx=20, sticky="w")

    # Session Productivity/Entertainment Time
    time_summary_frame = customtkinter.CTkFrame(tab_frame)
    time_summary_frame.pack(pady=10, padx=20, fill="x")
    time_summary_frame.columnconfigure(0, weight=1)
    time_summary_frame.columnconfigure(1, weight=1)

    customtkinter.CTkLabel(time_summary_frame, text="Productive Time (Session):", font=customtkinter.CTkFont(size=14)).grid(row=0, column=0, pady=5, padx=10, sticky="w")
    global productive_time_label
    productive_time_label = customtkinter.CTkLabel(time_summary_frame, text="00:00:00", font=customtkinter.CTkFont(size=14, weight="bold"))
    productive_time_label.grid(row=0, column=1, pady=5, padx=10, sticky="e")

    customtkinter.CTkLabel(time_summary_frame, text="Entertainment Time (Session):", font=customtkinter.CTkFont(size=14)).grid(row=1, column=0, pady=5, padx=10, sticky="w")
    global entertainment_time_label
    entertainment_time_label = customtkinter.CTkLabel(time_summary_frame, text="00:00:00", font=customtkinter.CTkFont(size=14, weight="bold"))
    entertainment_time_label.grid(row=1, column=1, pady=5, padx=10, sticky="e")

    # Recent Activity Log
    customtkinter.CTkLabel(tab_frame, text="Recent Activity:", font=customtkinter.CTkFont(size=14, weight="bold")).pack(pady=(10, 5), padx=20, anchor="w")
    global activity_log_text
    activity_log_text = customtkinter.CTkTextbox(tab_frame, height=150, activate_scrollbars=True, wrap="word")
    activity_log_text.pack(pady=(0, 20), padx=20, fill="both", expand=True)
    activity_log_text.insert("end", "Welcome to GetB@ck2Work!\n")
    activity_log_text.configure(state="disabled")

    # Quick Action Button (Redeem Points)
    redeem_button = customtkinter.CTkButton(tab_frame, text="Redeem Points", font=customtkinter.CTkFont(size=16, weight="bold"), command=lambda: switch_tab_to_redeem_points(tab_frame.master.master))
    redeem_button.pack(pady=(0, 20), padx=20)


def update_active_app_TB():
    global detected_apps_TB, detected_app, detected_app_list
    def update():
        while True:
            time.sleep(1)
            detected_app = tracker.get_active_app()
            if detected_app:
                detected_app_list.append(detected_app)
            if detected_app_list:
                detected_apps_TB.configure(text="")
                for app in detected_app_list:
                    detected_apps_TB.configure(text=app)
    threading.Thread(target=update, daemon=True).start()

# --- App Management Tab Functions (UI Only for now) ---

def refresh_app_lists():
    """
    Clears existing app list displays and repopulates them from dummy data.
    """
    global productivity_app_list_frame, entertainment_app_list_frame, _dummy_productivity_apps, _dummy_entertainment_apps

    for widget in productivity_app_list_frame.winfo_children():
        widget.destroy()
    for widget in entertainment_app_list_frame.winfo_children():
        widget.destroy()

    if _dummy_productivity_apps:
        for app_name in _dummy_productivity_apps:
            app_label_frame = customtkinter.CTkFrame(productivity_app_list_frame, fg_color="transparent")
            app_label_frame.pack(fill="x", pady=2, padx=5)
            app_label_frame.columnconfigure(0, weight=1)

            app_label = customtkinter.CTkLabel(app_label_frame, text=app_name, anchor="w", fg_color="transparent")
            app_label.grid(row=0, column=0, sticky="ew")

            remove_btn = customtkinter.CTkButton(app_label_frame, text="X", width=30, height=20,
                                                 command=lambda name=app_name: remove_app_gui(name, "productivity"))
            remove_btn.grid(row=0, column=1, padx=(5,0))
    else:
        customtkinter.CTkLabel(productivity_app_list_frame, text="No productivity apps added yet.").pack(pady=10)

    if _dummy_entertainment_apps:
        for app_name in _dummy_entertainment_apps:
            app_label_frame = customtkinter.CTkFrame(entertainment_app_list_frame, fg_color="transparent")
            app_label_frame.pack(fill="x", pady=2, padx=5)
            app_label_frame.columnconfigure(0, weight=1)

            app_label = customtkinter.CTkLabel(app_label_frame, text=app_name, anchor="w", fg_color="transparent")
            app_label.grid(row=0, column=0, sticky="ew")

            remove_btn = customtkinter.CTkButton(app_label_frame, text="X", width=30, height=20,
                                                 command=lambda name=app_name: remove_app_gui(name, "entertainment"))
            remove_btn.grid(row=0, column=1, padx=(5,0))
    else:
        customtkinter.CTkLabel(entertainment_app_list_frame, text="No entertainment apps added yet.").pack(pady=10)


def add_app_gui():
    """
    Handles adding a new app from the GUI input fields using dummy data.
    This will be connected to config_manager later.
    """
    global app_name_entry, app_type_optionmenu, _dummy_productivity_apps, _dummy_entertainment_apps
    app_name = app_name_entry.get().strip()
    app_type = app_type_optionmenu.get().lower()

    if not app_name:
        messagebox.showwarning("Input Error", "Please enter an application name.")
        return

    if app_type == "productivity":
        if app_name not in _dummy_productivity_apps:
            _dummy_productivity_apps.append(app_name)
            refresh_app_lists()
            app_name_entry.delete(0, "end")
            messagebox.showinfo("Success", f"'{app_name}' added to Productivity apps (dummy).")
        else:
            messagebox.showwarning("Already Exists", f"'{app_name}' is already in the Productivity list (dummy).")
    elif app_type == "entertainment":
        if app_name not in _dummy_entertainment_apps:
            _dummy_entertainment_apps.append(app_name)
            refresh_app_lists()
            app_name_entry.delete(0, "end")
            messagebox.showinfo("Success", f"'{app_name}' added to Entertainment apps (dummy).")
        else:
            messagebox.showwarning("Already Exists", f"'{app_name}' is already in the Entertainment list (dummy).")


def remove_app_gui(app_name, app_type):
    """
    Handles removing an app from the GUI using dummy data.
    This will be connected to config_manager later.
    """
    global _dummy_productivity_apps, _dummy_entertainment_apps

    if not messagebox.askyesno("Confirm Removal", f"Are you sure you want to remove '{app_name}' from {app_type} apps (dummy)?"):
        return

    if app_type == "productivity":
        if app_name in _dummy_productivity_apps:
            _dummy_productivity_apps.remove(app_name)
            refresh_app_lists()
            messagebox.showinfo("Success", f"'{app_name}' removed from Productivity apps (dummy).")
        else:
            messagebox.showerror("Error", f"Could not remove '{app_name}'. It might not be in the list (dummy).")
    elif app_type == "entertainment":
        if app_name in _dummy_entertainment_apps:
            _dummy_entertainment_apps.remove(app_name)
            refresh_app_lists()
            messagebox.showinfo("Success", f"'{app_name}' removed from Entertainment apps (dummy).")
        else:
            messagebox.showerror("Error", f"Could not remove '{app_name}'. It might not be in the list (dummy).")


def create_app_management_tab(tab_frame):
    """
    Populates the App Management tab with GUI elements.
    Args:
        tab_frame (customtkinter.CTkFrame): The frame associated with the App Management tab.
    """
    tab_frame.columnconfigure(0, weight=1)
    tab_frame.columnconfigure(1, weight=1)

    # Add New App Section
    add_app_frame = customtkinter.CTkFrame(tab_frame)
    add_app_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
    add_app_frame.columnconfigure(0, weight=1)

    customtkinter.CTkLabel(add_app_frame, text="Add/Remove Applications", font=customtkinter.CTkFont(size=16, weight="bold")).pack(pady=10)

    customtkinter.CTkLabel(add_app_frame, text="Application Name/Window Title:").pack(pady=(10, 0), padx=20, anchor="w")
    global app_name_entry
    app_name_entry = customtkinter.CTkEntry(add_app_frame, placeholder_text="e.g., VS Code, Google Chrome")
    app_name_entry.pack(pady=(0, 10), padx=20, fill="x")

    customtkinter.CTkLabel(add_app_frame, text="Category:").pack(pady=(10, 0), padx=20, anchor="w")
    global app_type_optionmenu
    app_type_optionmenu = customtkinter.CTkOptionMenu(add_app_frame, values=["Productivity", "Entertainment"])
    app_type_optionmenu.set("Productivity")
    app_type_optionmenu.pack(pady=(0, 20), padx=20, fill="x")

    add_button = customtkinter.CTkButton(add_app_frame, text="Add Application", command=add_app_gui)
    add_button.pack(pady=(0, 20), padx=20, fill="x")

    # App Lists Section
    lists_frame = customtkinter.CTkFrame(tab_frame)
    lists_frame.grid(row=0, column=1, padx=(0, 20), pady=20, sticky="nsew")
    lists_frame.columnconfigure(0, weight=1)
    lists_frame.rowconfigure(0, weight=1)
    lists_frame.rowconfigure(1, weight=1)

    # Productivity Apps List
    customtkinter.CTkLabel(lists_frame, text="Productivity Applications", font=customtkinter.CTkFont(size=14, weight="bold")).pack(pady=(10, 5))
    global productivity_app_list_frame
    productivity_app_list_frame = customtkinter.CTkScrollableFrame(lists_frame, height=200)
    productivity_app_list_frame.pack(pady=(0, 10), padx=10, fill="both", expand=True)

    # Entertainment Apps List
    customtkinter.CTkLabel(lists_frame, text="Entertainment Applications", font=customtkinter.CTkFont(size=14, weight="bold")).pack(pady=(10, 5))
    global entertainment_app_list_frame
    entertainment_app_list_frame = customtkinter.CTkScrollableFrame(lists_frame, height=200)
    entertainment_app_list_frame.pack(pady=(0, 10), padx=10, fill="both", expand=True)

    refresh_app_lists()


# --- Point Redemption Tab Functions (UI Only for now) ---

def update_redeem_time_display(event=None):
    """
    Calculates and updates the displayed entertainment time based on entered points.
    Uses dummy conversion rate.
    """
    global redeem_points_entry, redeem_time_display_label, _dummy_points_per_minute_entertainment, _dummy_current_points
    try:
        points_to_redeem = int(redeem_points_entry.get())
        if points_to_redeem < 0:
            redeem_time_display_label.configure(text="Points must be positive.")
            return

        if _dummy_points_per_minute_entertainment > 0:
            minutes = points_to_redeem / _dummy_points_per_minute_entertainment
            redeem_time_display_label.configure(text=f"Equals: {minutes:.1f} minutes")
        else:
            redeem_time_display_label.configure(text="Conversion rate not set.")
    except ValueError:
        redeem_time_display_label.configure(text="Enter a valid number.")

def perform_dummy_redemption():
    """
    Simulates the redemption process without actual point deduction.
    """
    global redeem_points_entry, redemption_status_label, _dummy_current_points

    try:
        points_to_redeem = int(redeem_points_entry.get())
    except ValueError:
        messagebox.showwarning("Input Error", "Please enter a valid number of points to redeem.")
        return

    if points_to_redeem <= 0:
        messagebox.showwarning("Input Error", "Points to redeem must be greater than zero.")
        return

    if points_to_redeem > _dummy_current_points:
        messagebox.showwarning("Not Enough Points", f"You only have {_dummy_current_points} points. You need {points_to_redeem} points.")
        redemption_status_label.configure(text="Not enough points!", text_color="red")
        return

    redeemable_minutes = points_to_redeem / _dummy_points_per_minute_entertainment
    messagebox.showinfo("Redemption Simulated", f"Successfully simulated redeeming {points_to_redeem} points for {redeemable_minutes:.1f} minutes of entertainment!")
    redemption_status_label.configure(text=f"Simulated! {points_to_redeem} pts redeemed.", text_color="green")
    redeem_points_entry.delete(0, "end")


def create_point_redemption_tab(tab_frame):
    """
    Populates the Point Redemption tab with GUI elements.
    Args:
        tab_frame (customtkinter.CTkFrame): The frame associated with the Point Redemption tab.
    """
    tab_frame.columnconfigure(0, weight=1)

    customtkinter.CTkLabel(tab_frame, text="Redeem Your Focus Points", font=customtkinter.CTkFont(size=20, weight="bold")).pack(pady=20)

    # Display current points
    redeem_current_points_frame = customtkinter.CTkFrame(tab_frame)
    redeem_current_points_frame.pack(pady=10, padx=20, fill="x")
    redeem_current_points_frame.columnconfigure(0, weight=1)
    customtkinter.CTkLabel(redeem_current_points_frame, text="Your Current Points:", font=customtkinter.CTkFont(size=16)).grid(row=0, column=0, sticky="w", padx=20, pady=5)
    customtkinter.CTkLabel(redeem_current_points_frame, text=str(_dummy_current_points), font=customtkinter.CTkFont(size=28, weight="bold"), text_color="#FFD700").grid(row=0, column=1, sticky="e", padx=20, pady=5)

    # Redemption input section
    input_frame = customtkinter.CTkFrame(tab_frame)
    input_frame.pack(pady=20, padx=20, fill="x")
    input_frame.columnconfigure(0, weight=1)

    customtkinter.CTkLabel(input_frame, text="Points to Redeem:", font=customtkinter.CTkFont(size=14)).pack(pady=(10, 0), padx=20, anchor="w")
    global redeem_points_entry
    redeem_points_entry = customtkinter.CTkEntry(input_frame, placeholder_text="Enter points (e.g., 100)")
    redeem_points_entry.pack(pady=(0, 10), padx=20, fill="x")
    redeem_points_entry.bind("<KeyRelease>", update_redeem_time_display)

    # Display conversion
    customtkinter.CTkLabel(input_frame, text=f"Conversion Rate: {int(_dummy_points_per_minute_entertainment)} points = 1 minute", font=customtkinter.CTkFont(size=12, slant="italic")).pack(pady=(0, 5), padx=20, anchor="w")
    global redeem_time_display_label
    redeem_time_display_label = customtkinter.CTkLabel(input_frame, text="Equals: 0.0 minutes", font=customtkinter.CTkFont(size=18, weight="bold"), text_color="cyan")
    redeem_time_display_label.pack(pady=(0, 10), padx=20)

    redeem_button = customtkinter.CTkButton(input_frame, text="Redeem Points", font=customtkinter.CTkFont(size=16, weight="bold"), command=perform_dummy_redemption)
    redeem_button.pack(pady=(10, 20), padx=20, fill="x")

    # Status message label
    global redemption_status_label
    redemption_status_label = customtkinter.CTkLabel(tab_frame, text="", font=customtkinter.CTkFont(size=14, weight="bold"))
    redemption_status_label.pack(pady=(0, 20), padx=20)


# --- Settings Tab Functions ---

def save_settings_gui():
    """
    Reads values from settings GUI elements and simulates saving them.
    Also applies theme/appearance changes immediately.
    """
    global productive_points_per_min_entry, entertainment_points_per_min_entry, \
           monitoring_interval_entry, startup_checkbox, \
           appearance_mode_optionmenu, color_theme_optionmenu, \
           _dummy_productive_points_per_minute, _dummy_entertainment_points_per_minute, \
           _dummy_monitoring_interval_seconds, _dummy_start_on_startup, \
           _dummy_appearance_mode, _dummy_color_theme

    # Validate and "save" point conversion settings
    try:
        new_prod_pts = int(productive_points_per_min_entry.get())
        new_ent_pts = int(entertainment_points_per_min_entry.get())
        if new_prod_pts < 0 or new_ent_pts < 0:
            messagebox.showwarning("Input Error", "Point values must be non-negative integers.")
            return
        _dummy_productive_points_per_minute = new_prod_pts
        _dummy_entertainment_points_per_minute = new_ent_pts
        print(f"Dummy Saved: Productive Points/Min: {new_prod_pts}, Entertainment Points/Min: {new_ent_pts}")
    except ValueError:
        messagebox.showwarning("Input Error", "Productivity/Entertainment points must be valid numbers.")
        return

    # Validate and "save" monitoring interval
    try:
        new_interval = int(monitoring_interval_entry.get())
        if new_interval <= 0:
            messagebox.showwarning("Input Error", "Monitoring interval must be a positive integer.")
            return
        _dummy_monitoring_interval_seconds = new_interval
        print(f"Dummy Saved: Monitoring Interval: {new_interval} seconds")
    except ValueError:
        messagebox.showwarning("Input Error", "Monitoring interval must be a valid number.")
        return

    # "Save" startup behavior
    _dummy_start_on_startup = bool(startup_checkbox.get())
    print(f"Dummy Saved: Start on Startup: {_dummy_start_on_startup}")

    # Apply and "save" appearance mode and color theme
    new_appearance_mode = appearance_mode_optionmenu.get()
    new_color_theme = color_theme_optionmenu.get()

    customtkinter.set_appearance_mode(new_appearance_mode)
    customtkinter.set_default_color_theme(new_color_theme)
    _dummy_appearance_mode = new_appearance_mode # Update dummy value
    _dummy_color_theme = new_color_theme # Update dummy value
    print(f"Applied and Dummy Saved: Appearance Mode: {new_appearance_mode}, Color Theme: {new_color_theme}")

    messagebox.showinfo("Settings Saved (Dummy)", "Settings have been updated! (Changes are not persistent yet)")


def create_settings_tab(tab_frame):
    """
    Populates the Settings tab with GUI elements.
    Args:
        tab_frame (customtkinter.CTkFrame): The frame associated with the Settings tab.
    """
    tab_frame.columnconfigure(0, weight=1) # Centralize content

    customtkinter.CTkLabel(tab_frame, text="Application Settings", font=customtkinter.CTkFont(size=20, weight="bold")).pack(pady=20)

    settings_frame = customtkinter.CTkFrame(tab_frame)
    settings_frame.pack(pady=10, padx=20, fill="x", expand=False) # Not expanding for more structured layout
    settings_frame.columnconfigure(0, weight=1)
    settings_frame.columnconfigure(1, weight=1)

    # --- Point Conversion Settings ---
    customtkinter.CTkLabel(settings_frame, text="Productivity Points per Minute:", font=customtkinter.CTkFont(size=14)).grid(row=0, column=0, pady=5, padx=20, sticky="w")
    global productive_points_per_min_entry
    productive_points_per_min_entry = customtkinter.CTkEntry(settings_frame, placeholder_text="e.g., 1")
    productive_points_per_min_entry.grid(row=0, column=1, pady=5, padx=20, sticky="ew")
    productive_points_per_min_entry.insert(0, str(_dummy_productive_points_per_minute)) # Set initial dummy value

    customtkinter.CTkLabel(settings_frame, text="Entertainment Points per Minute:", font=customtkinter.CTkFont(size=14)).grid(row=1, column=0, pady=5, padx=20, sticky="w")
    global entertainment_points_per_min_entry
    entertainment_points_per_min_entry = customtkinter.CTkEntry(settings_frame, placeholder_text="e.g., 0")
    entertainment_points_per_min_entry.grid(row=1, column=1, pady=5, padx=20, sticky="ew")
    entertainment_points_per_min_entry.insert(0, str(_dummy_entertainment_points_per_minute)) # Set initial dummy value


    # --- Monitoring Interval Setting ---
    customtkinter.CTkLabel(settings_frame, text="Monitoring Interval (seconds):", font=customtkinter.CTkFont(size=14)).grid(row=2, column=0, pady=5, padx=20, sticky="w")
    global monitoring_interval_entry
    monitoring_interval_entry = customtkinter.CTkEntry(settings_frame, placeholder_text="e.g., 5")
    monitoring_interval_entry.grid(row=2, column=1, pady=5, padx=20, sticky="ew")
    monitoring_interval_entry.insert(0, str(_dummy_monitoring_interval_seconds)) # Set initial dummy value


    # --- Start on Startup Setting ---
    global startup_checkbox
    startup_checkbox = customtkinter.CTkCheckBox(settings_frame, text="Start monitoring on application launch", font=customtkinter.CTkFont(size=14))
    startup_checkbox.grid(row=3, column=0, columnspan=2, pady=15, padx=20, sticky="w")
    if _dummy_start_on_startup: # Set initial state based on dummy value
        startup_checkbox.select()


    # --- Appearance Settings ---
    customtkinter.CTkLabel(settings_frame, text="Appearance Mode:", font=customtkinter.CTkFont(size=14)).grid(row=4, column=0, pady=5, padx=20, sticky="w")
    global appearance_mode_optionmenu
    appearance_mode_optionmenu = customtkinter.CTkOptionMenu(settings_frame, values=["System", "Light", "Dark"],
                                                             command=customtkinter.set_appearance_mode) # Direct command
    appearance_mode_optionmenu.grid(row=4, column=1, pady=5, padx=20, sticky="ew")
    appearance_mode_optionmenu.set(_dummy_appearance_mode) # Set initial value

    customtkinter.CTkLabel(settings_frame, text="Color Theme:", font=customtkinter.CTkFont(size=14)).grid(row=5, column=0, pady=5, padx=20, sticky="w")
    global color_theme_optionmenu
    color_theme_optionmenu = customtkinter.CTkOptionMenu(settings_frame, values=["blue", "dark-blue", "green"],
                                                         command=customtkinter.set_default_color_theme) # Direct command
    color_theme_optionmenu.grid(row=5, column=1, pady=5, padx=20, sticky="ew")
    color_theme_optionmenu.set(_dummy_color_theme) # Set initial value


    # --- Save Settings Button ---
    save_button = customtkinter.CTkButton(tab_frame, text="Save Settings", font=customtkinter.CTkFont(size=16, weight="bold"), command=save_settings_gui)
    save_button.pack(pady=30, padx=20, fill="x")


# --- Main Window Creation and Run ---

def create_main_window():
    """
    Creates and configures the main customtkinter window with tabs.
    """
    app = customtkinter.CTk()
    app.title("GetB@ck2Work")
    app.geometry("800x600")
    app.resizable(True, True)

    # Set initial appearance based on dummy settings (which could come from config later)
    customtkinter.set_appearance_mode(_dummy_appearance_mode)
    customtkinter.set_default_color_theme(_dummy_color_theme)

    tabview = customtkinter.CTkTabview(app, width=780, height=550)
    tabview.pack(pady=20, padx=20, fill="both", expand=True)

    tab_dashboard = tabview.add("Dashboard")
    tab_app_management = tabview.add("App Management")
    tab_point_redemption = tabview.add("Point Redemption")
    tab_settings = tabview.add("Settings")
    tab_mini_game = tabview.add("Mini Game")

    # --- Populate tabs with their specific content ---
    create_dashboard_tab(tab_dashboard)
    create_app_management_tab(tab_app_management)
    create_point_redemption_tab(tab_point_redemption)
    create_settings_tab(tab_settings) # New!

    # --- Content for other tabs (placeholder for now) ---
    customtkinter.CTkLabel(tab_mini_game, text="Welcome to the Mini Game Casino!").pack(pady=20, padx=20)

    # Update Dashboard points on startup with dummy value
    if points_label:
        points_label.configure(text=str(_dummy_current_points))

    return app

def run_gui():
    """
    Initializes and runs the GetB@ck2Work GUI application.
    """
    app = create_main_window()
    app.mainloop()

if __name__ == "__main__":
    run_gui()