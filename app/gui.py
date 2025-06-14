# gui.py

import customtkinter
import tkinter as tk # Needed for some widget properties, specifically CTkTextbox in dashboard

# Global variables to hold references to GUI elements that need updating by backend
# Initialize them to None; they will be assigned when create_dashboard_tab runs
points_label = None
status_indicator_label = None
active_app_label = None
productive_time_label = None
entertainment_time_label = None
activity_log_text = None

def switch_tab_to_redeem_points(tabview_widget):
    """
    Helper function to switch the tab to 'Point Redemption'.
    Requires access to the main CTkTabview widget.
    """
    tabview_widget.set("Point Redemption")
    print("Switched to Point Redemption tab.") # For debugging

def create_dashboard_tab(tab_frame):
    """
    Populates the Dashboard tab with suggested GUI elements.
    Args:
        tab_frame (customtkinter.CTkFrame): The frame associated with the Dashboard tab.
    """
    # Use a grid layout for better organization
    tab_frame.columnconfigure(0, weight=1) # Allow column to expand

    # --- 1. Current Points Balance ---
    points_frame = customtkinter.CTkFrame(tab_frame)
    points_frame.pack(pady=(20, 10), padx=20, fill="x")
    points_frame.columnconfigure(0, weight=1)

    customtkinter.CTkLabel(points_frame, text="Current Focus Points:", font=customtkinter.CTkFont(size=16, weight="bold")).grid(row=0, column=0, pady=(10, 0), padx=20, sticky="w")
    # Placeholder for points. This will be updated by backend.
    global points_label # This makes the global variable accessible for assignment
    points_label = customtkinter.CTkLabel(points_frame, text="0", font=customtkinter.CTkFont(size=48, weight="bold"), text_color="#FFD700") # Gold color for points
    points_label.grid(row=1, column=0, pady=(0, 10), padx=20, sticky="ew")

    # --- 2. Monitoring Status Indicator ---
    status_frame = customtkinter.CTkFrame(tab_frame)
    status_frame.pack(pady=10, padx=20, fill="x")
    status_frame.columnconfigure(0, weight=1)
    status_frame.columnconfigure(1, weight=1)

    customtkinter.CTkLabel(status_frame, text="Monitoring Status:", font=customtkinter.CTkFont(size=14)).grid(row=0, column=0, pady=5, padx=20, sticky="w")
    # Placeholder for status. This will be updated by backend.
    global status_indicator_label
    status_indicator_label = customtkinter.CTkLabel(status_frame, text="Inactive", font=customtkinter.CTkFont(size=14, weight="bold"), text_color="red")
    status_indicator_label.grid(row=0, column=1, pady=5, padx=20, sticky="e")

    # --- 3. Currently Active Application/Website ---
    active_app_frame = customtkinter.CTkFrame(tab_frame)
    active_app_frame.pack(pady=10, padx=20, fill="x")
    active_app_frame.columnconfigure(0, weight=1)
    active_app_frame.columnconfigure(1, weight=2) # Give more space to the app name

    customtkinter.CTkLabel(active_app_frame, text="Currently Active:", font=customtkinter.CTkFont(size=14)).grid(row=0, column=0, pady=5, padx=20, sticky="w")
    # Placeholder for active app. This will be updated by backend.
    global active_app_label
    active_app_label = customtkinter.CTkLabel(active_app_frame, text="N/A", font=customtkinter.CTkFont(size=14, slant="italic"))
    active_app_label.grid(row=0, column=1, pady=5, padx=20, sticky="w")

    # --- 4. Session Productivity/Entertainment Time ---
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

    # --- 5. Recent Activity Log (Simple Textbox for now) ---
    customtkinter.CTkLabel(tab_frame, text="Recent Activity:", font=customtkinter.CTkFont(size=14, weight="bold")).pack(pady=(10, 5), padx=20, anchor="w")
    global activity_log_text
    activity_log_text = customtkinter.CTkTextbox(tab_frame, height=150, activate_scrollbars=True, wrap="word")
    activity_log_text.pack(pady=(0, 20), padx=20, fill="both", expand=True)
    activity_log_text.insert("end", "Welcome to GetB@ck2Work!\n")
    activity_log_text.configure(state="disabled") # Make it read-only initially

    # --- 6. Quick Action Button (Redeem Points) ---
    # The 'tab_frame.master.master' is a bit of a hacky way to get the CTkTabview widget
    # when working with deeply nested widgets without using classes.
    # It essentially goes from tab_frame -> parent frame (the tab content) -> CTkTabview.
    redeem_button = customtkinter.CTkButton(tab_frame, text="Redeem Points", font=customtkinter.CTkFont(size=16, weight="bold"), command=lambda: switch_tab_to_redeem_points(tab_frame.master.master))
    redeem_button.pack(pady=(0, 20), padx=20)


def create_main_window():
    """
    Creates and configures the main customtkinter window with tabs.
    """
    app = customtkinter.CTk()
    app.title("GetB@ck2Work")
    app.geometry("800x600") # Set initial window size
    app.resizable(True, True) # Allow resizing

    # Set default appearance mode and color theme
    customtkinter.set_appearance_mode("System") # Can be "System", "Dark", "Light"
    customtkinter.set_default_color_theme("blue") # Can be "blue", "dark-blue", "green"

    # Create a tabview widget
    # The tabview will expand to fill the entire window
    tabview = customtkinter.CTkTabview(app, width=780, height=550)
    tabview.pack(pady=20, padx=20, fill="both", expand=True)

    # Add the tabs
    tab_dashboard = tabview.add("Dashboard")
    tab_app_management = tabview.add("App Management")
    tab_point_redemption = tabview.add("Point Redemption")
    tab_settings = tabview.add("Settings")
    tab_mini_game = tabview.add("Mini Game")

    # --- Populate the Dashboard tab with its specific content ---
    create_dashboard_tab(tab_dashboard)

    # --- Content for other tabs (placeholder for now) ---
    customtkinter.CTkLabel(tab_app_management, text="Manage your apps here.").pack(pady=20, padx=20)
    customtkinter.CTkLabel(tab_point_redemption, text="Redeem your points for entertainment time.").pack(pady=20, padx=20)
    customtkinter.CTkLabel(tab_settings, text="Configure GetB@ck2Work settings.").pack(pady=20, padx=20)

    return app

def run_gui():
    """
    Initializes and runs the GetB@ck2Work GUI application.
    """
    app = create_main_window()
    app.mainloop()

if __name__ == "__main__":
    run_gui()