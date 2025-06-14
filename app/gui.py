import customtkinter as ctk
from tkinter import messagebox
import tracker
import time
import threading
import json
import save_app

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("GetB@ck2Work")
        self.geometry("1280x720")

        # Configure grid layout (1x1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- Initialize dummy data ---
        with open("productivity.json", 'r') as file:
            data = json.load(file) # Use json.load() for file objects
            self._dummy_productivity_apps = data.get("productivity_app", [])
            self._dummy_entertainment_apps = data.get("entertainment_app", [])

        with open("points.json", 'r') as file:
            points_data = json.load(file)
            self._dummy_current_points = points_data.get("points", "")

        self._dummy_points_per_minute_entertainment = 2
        self._dummy_productive_points_per_minute = 1
        self._dummy_entertainment_points_per_minute = 0
        self._dummy_monitoring_interval_seconds = 5
        self._dummy_start_on_startup = False
        self._dummy_appearance_mode = "System"
        self._dummy_color_theme = "blue"
        self.category = "Unclassified"

        # Initialize detected app variables
        self.detected_app = ""
        self.detected_app_list = []

        # Set initial appearance
        ctk.set_appearance_mode(self._dummy_appearance_mode)
        ctk.set_default_color_theme(self._dummy_color_theme)

        # Create tabview
        self.tabview = ctk.CTkTabview(self, width=500, height=300)
        self.tabview.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # Add tabs
        self.dashboard_tab = self.tabview.add("Dashboard")
        self.app_management_tab = self.tabview.add("App Management")
        self.point_redemption_tab = self.tabview.add("Point Redemption")
        self.settings_tab = self.tabview.add("Settings")
        self.mini_game_tab = self.tabview.add("Mini Game")

        # Set default tab
        self.tabview.set("Dashboard")

        # Create all tabs
        self.create_dashboard_tab()
        self.create_app_management_tab()
        self.create_point_redemption_tab()
        self.create_settings_tab()
        self.create_mini_game_tab()

        # Start background thread
        threading.Thread(target=self.update_active_app_TB, daemon=True).start()

    def switch_tab_to_redeem_points(self):
        """Helper function to switch the tab to 'Point Redemption'."""
        self.tabview.set("Point Redemption")
        print("Switched to Point Redemption tab.")
        if hasattr(self, 'points_label'):
            self.points_label.configure(text=str(self._dummy_current_points))

    def create_dashboard_tab(self):
        """Populates the Dashboard tab with suggested GUI elements."""
        self.dashboard_tab.columnconfigure(0, weight=1)

        # Current Points Balance
        self.points_frame = ctk.CTkFrame(self.dashboard_tab)
        self.points_frame.pack(pady=(20, 10), padx=20, fill="x")
        self.points_frame.columnconfigure(0, weight=1)

        ctk.CTkLabel(self.points_frame, text="Current Focus Points:", 
                    font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, pady=(10, 0), padx=20, sticky="w")
        
        self.points_label = ctk.CTkLabel(self.points_frame, text=str(self._dummy_current_points),
                                        font=ctk.CTkFont(size=48, weight="bold"), text_color="#FFD700")
        self.points_label.grid(row=1, column=0, pady=(0, 10), padx=20, sticky="ew")

        # Detected apps textbox
        self.detected_apps_TB = ctk.CTkTextbox(self.dashboard_tab, height=100, width=400, state="disabled")
        self.detected_apps_TB.pack()

        # Monitoring Status Indicator
        status_frame = ctk.CTkFrame(self.dashboard_tab)
        status_frame.pack(pady=10, padx=20, fill="x")
        status_frame.columnconfigure(0, weight=1)
        status_frame.columnconfigure(1, weight=1)

        ctk.CTkLabel(status_frame, text="Monitoring Status:", 
                    font=ctk.CTkFont(size=14)).grid(row=0, column=0, pady=5, padx=20, sticky="w")
        self.status_indicator_label = ctk.CTkLabel(status_frame, text="Inactive", 
                                                  font=ctk.CTkFont(size=14, weight="bold"), text_color="red")
        self.status_indicator_label.grid(row=0, column=1, pady=5, padx=20, sticky="e")

        # Session Productivity/Entertainment Time
        time_summary_frame = ctk.CTkFrame(self.dashboard_tab)
        time_summary_frame.pack(pady=10, padx=20, fill="x")
        time_summary_frame.columnconfigure(0, weight=1)
        time_summary_frame.columnconfigure(1, weight=1)

        ctk.CTkLabel(time_summary_frame, text="Productive Time (Session):", 
                    font=ctk.CTkFont(size=14)).grid(row=0, column=0, pady=5, padx=10, sticky="w")
        self.productive_time_label = ctk.CTkLabel(time_summary_frame, text="00:00:00", 
                                                 font=ctk.CTkFont(size=14, weight="bold"))
        self.productive_time_label.grid(row=0, column=1, pady=5, padx=10, sticky="e")

        ctk.CTkLabel(time_summary_frame, text="Entertainment Time (Session):", 
                    font=ctk.CTkFont(size=14)).grid(row=1, column=0, pady=5, padx=10, sticky="w")
        self.entertainment_time_label = ctk.CTkLabel(time_summary_frame, text="00:00:00", 
                                                    font=ctk.CTkFont(size=14, weight="bold"))
        self.entertainment_time_label.grid(row=1, column=1, pady=5, padx=10, sticky="e")

        self.category_label = ctk.CTkLabel(self.dashboard_tab, text="Detected App Category: Unclassified")
        self.category_label.pack()

    def update_active_app_TB(self):
        """Updates the detected apps textbox with current active app."""
        while True:
            time.sleep(1)
            self.detected_app = tracker.get_active_app()
            if self.detected_app:
                self.detected_app_list.append(self.detected_app)
                # Update the textbox from the main thread
                self.after(0, self.update_active_app)
                self.category = tracker.check_app(self.detected_app)
                with open("points.json", 'r') as file:
                    points_data = json.load(file)
                    self._dummy_current_points = points_data.get("points", "")
                    self.points_label.configure(text=self._dummy_current_points)
                


    def update_active_app(self):
        """Updates the textbox content - called from main thread."""
        if hasattr(self, 'detected_apps_TB'):
            self.detected_apps_TB.configure(state="normal")
            self.detected_apps_TB.delete("1.0", "end")
            self.detected_apps_TB.insert("1.0", "\n".join(self.detected_app_list))
            self.detected_apps_TB.configure(state="disabled")
            self.category_label.configure(text=f"Detected App Category: {self.category}")

    def refresh_app_lists(self):
        """Clears existing app list displays and repopulates them from dummy data."""
        for widget in self.productivity_app_list_frame.winfo_children():
            widget.destroy()
        for widget in self.entertainment_app_list_frame.winfo_children():
            widget.destroy()

        if self._dummy_productivity_apps:
            for app_name in self._dummy_productivity_apps:
                app_label_frame = ctk.CTkFrame(self.productivity_app_list_frame, fg_color="transparent")
                app_label_frame.pack(fill="x", pady=2, padx=5)
                app_label_frame.columnconfigure(0, weight=1)

                app_label = ctk.CTkLabel(app_label_frame, text=app_name, anchor="w", fg_color="transparent")
                app_label.grid(row=0, column=0, sticky="ew")

                remove_btn = ctk.CTkButton(app_label_frame, text="X", width=30, height=20,
                                          command=lambda name=app_name: self.remove_app_gui(name, "productivity"))
                remove_btn.grid(row=0, column=1, padx=(5,0))
        else:
            ctk.CTkLabel(self.productivity_app_list_frame, text="No productivity apps added yet.").pack(pady=10)

        if self._dummy_entertainment_apps:
            for app_name in self._dummy_entertainment_apps:
                app_label_frame = ctk.CTkFrame(self.entertainment_app_list_frame, fg_color="transparent")
                app_label_frame.pack(fill="x", pady=2, padx=5)
                app_label_frame.columnconfigure(0, weight=1)

                app_label = ctk.CTkLabel(app_label_frame, text=app_name, anchor="w", fg_color="transparent")
                app_label.grid(row=0, column=0, sticky="ew")

                remove_btn = ctk.CTkButton(app_label_frame, text="X", width=30, height=20,
                                          command=lambda name=app_name: self.remove_app_gui(name, "entertainment"))
                remove_btn.grid(row=0, column=1, padx=(5,0))
        else:
            ctk.CTkLabel(self.entertainment_app_list_frame, text="No entertainment apps added yet.").pack(pady=10)

    def add_app_gui(self):
        """Handles adding a new app from the GUI input fields using dummy data."""
        app_name = self.app_name_entry.get().strip()
        app_type = self.app_type_optionmenu.get().lower()

        if not app_name:
            messagebox.showwarning("Input Error", "Please enter an application name.")
            return

        if app_type == "productivity":
            if app_name not in self._dummy_productivity_apps:
                self._dummy_productivity_apps.append(app_name)
                save_app.save_app_to_productivity(app_name)
                self.refresh_app_lists()
                self.app_name_entry.delete(0, "end")
                messagebox.showinfo("Success", f"'{app_name}' added to Productivity apps (dummy).")
            else:
                messagebox.showwarning("Already Exists", f"'{app_name}' is already in the Productivity list (dummy).")
        elif app_type == "entertainment":
            if app_name not in self._dummy_entertainment_apps:
                self._dummy_entertainment_apps.append(app_name)
                save_app.save_app_to_entertainment(app_name)
                self.refresh_app_lists()
                self.app_name_entry.delete(0, "end")
                messagebox.showinfo("Success", f"'{app_name}' added to Entertainment apps (dummy).")
            else:
                messagebox.showwarning("Already Exists", f"'{app_name}' is already in the Entertainment list (dummy).")

    def remove_app_gui(self, app_name, app_type):
        """Handles removing an app from the GUI using dummy data."""
        if not messagebox.askyesno("Confirm Removal", f"Are you sure you want to remove '{app_name}' from {app_type} apps (dummy)?"):
            return

        if app_type == "productivity":
            if app_name in self._dummy_productivity_apps:
                self._dummy_productivity_apps.remove(app_name)
                save_app.remove_app_from_productivity(app_name)  # Simulate saving removal
                self.refresh_app_lists()
                messagebox.showinfo("Success", f"'{app_name}' removed from Productivity apps (dummy).")
                
            else:
                messagebox.showerror("Error", f"Could not remove '{app_name}'. It might not be in the list (dummy).")
        elif app_type == "entertainment":
            if app_name in self._dummy_entertainment_apps:
                self._dummy_entertainment_apps.remove(app_name)
                save_app.remove_app_from_entertainment(app_name)
                self.refresh_app_lists()
                messagebox.showinfo("Success", f"'{app_name}' removed from Entertainment apps (dummy).")
            else:
                messagebox.showerror("Error", f"Could not remove '{app_name}'. It might not be in the list (dummy).")

    def create_app_management_tab(self):
        """Populates the App Management tab with GUI elements."""
        self.app_management_tab.columnconfigure(0, weight=1)
        self.app_management_tab.columnconfigure(1, weight=1)

        # Add New App Section
        add_app_frame = ctk.CTkFrame(self.app_management_tab)
        add_app_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        add_app_frame.columnconfigure(0, weight=1)

        ctk.CTkLabel(add_app_frame, text="Add/Remove Applications", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

        ctk.CTkLabel(add_app_frame, text="Application Name/Window Title:").pack(pady=(10, 0), padx=20, anchor="w")
        self.app_name_entry = ctk.CTkEntry(add_app_frame, placeholder_text="e.g., VS Code, Google Chrome")
        self.app_name_entry.pack(pady=(0, 10), padx=20, fill="x")

        ctk.CTkLabel(add_app_frame, text="Category:").pack(pady=(10, 0), padx=20, anchor="w")
        self.app_type_optionmenu = ctk.CTkOptionMenu(add_app_frame, values=["Productivity", "Entertainment"])
        self.app_type_optionmenu.set("Productivity")
        self.app_type_optionmenu.pack(pady=(0, 20), padx=20, fill="x")

        add_button = ctk.CTkButton(add_app_frame, text="Add Application", command=self.add_app_gui)
        add_button.pack(pady=(0, 20), padx=20, fill="x")

        # App Lists Section
        lists_frame = ctk.CTkFrame(self.app_management_tab)
        lists_frame.grid(row=0, column=1, padx=(0, 20), pady=20, sticky="nsew")
        lists_frame.columnconfigure(0, weight=1)
        lists_frame.rowconfigure(0, weight=1)
        lists_frame.rowconfigure(1, weight=1)

        # Productivity Apps List
        ctk.CTkLabel(lists_frame, text="Productivity Applications", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5))
        self.productivity_app_list_frame = ctk.CTkScrollableFrame(lists_frame, height=200)
        self.productivity_app_list_frame.pack(pady=(0, 10), padx=10, fill="both", expand=True)

        # Entertainment Apps List
        ctk.CTkLabel(lists_frame, text="Entertainment Applications", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5))
        self.entertainment_app_list_frame = ctk.CTkScrollableFrame(lists_frame, height=200)
        self.entertainment_app_list_frame.pack(pady=(0, 10), padx=10, fill="both", expand=True)

        self.refresh_app_lists()

    def update_redeem_time_display(self, event=None):
        """Calculates and updates the displayed entertainment time based on entered points."""
        try:
            points_to_redeem = int(self.redeem_points_entry.get())
            if points_to_redeem < 0:
                self.redeem_time_display_label.configure(text="Points must be positive.")
                return

            if self._dummy_points_per_minute_entertainment > 0:
                minutes = points_to_redeem / self._dummy_points_per_minute_entertainment
                self.redeem_time_display_label.configure(text=f"Equals: {minutes:.1f} minutes")
            else:
                self.redeem_time_display_label.configure(text="Conversion rate not set.")
        except ValueError:
            self.redeem_time_display_label.configure(text="Enter a valid number.")

    def perform_dummy_redemption(self):
        """Simulates the redemption process without actual point deduction."""
        try:
            points_to_redeem = int(self.redeem_points_entry.get())
        except ValueError:
            messagebox.showwarning("Input Error", "Please enter a valid number of points to redeem.")
            return

        if points_to_redeem <= 0:
            messagebox.showwarning("Input Error", "Points to redeem must be greater than zero.")
            return

        if points_to_redeem > self._dummy_current_points:
            messagebox.showwarning("Not Enough Points", f"You only have {self._dummy_current_points} points. You need {points_to_redeem} points.")
            self.redemption_status_label.configure(text="Not enough points!", text_color="red")
            return

        redeemable_minutes = points_to_redeem / self._dummy_points_per_minute_entertainment
        messagebox.showinfo("Redemption Simulated", f"Successfully simulated redeeming {points_to_redeem} points for {redeemable_minutes:.1f} minutes of entertainment!")
        self.redemption_status_label.configure(text=f"Simulated! {points_to_redeem} pts redeemed.", text_color="green")
        self.redeem_points_entry.delete(0, "end")

    def create_point_redemption_tab(self):
        """Populates the Point Redemption tab with GUI elements."""
        self.point_redemption_tab.columnconfigure(0, weight=1)

        ctk.CTkLabel(self.point_redemption_tab, text="Redeem Your Focus Points", 
                    font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)

        # Display current points
        redeem_current_points_frame = ctk.CTkFrame(self.point_redemption_tab)
        redeem_current_points_frame.pack(pady=10, padx=20, fill="x")
        redeem_current_points_frame.columnconfigure(0, weight=1)
        ctk.CTkLabel(redeem_current_points_frame, text="Your Current Points:", 
                    font=ctk.CTkFont(size=16)).grid(row=0, column=0, sticky="w", padx=20, pady=5)
        ctk.CTkLabel(redeem_current_points_frame, text=str(self._dummy_current_points), 
                    font=ctk.CTkFont(size=28, weight="bold"), text_color="#FFD700").grid(row=0, column=1, sticky="e", padx=20, pady=5)

        # Redemption input section
        input_frame = ctk.CTkFrame(self.point_redemption_tab)
        input_frame.pack(pady=20, padx=20, fill="x")
        input_frame.columnconfigure(0, weight=1)

        ctk.CTkLabel(input_frame, text="Points to Redeem:", 
                    font=ctk.CTkFont(size=14)).pack(pady=(10, 0), padx=20, anchor="w")
        self.redeem_points_entry = ctk.CTkEntry(input_frame, placeholder_text="Enter points (e.g., 100)")
        self.redeem_points_entry.pack(pady=(0, 10), padx=20, fill="x")
        self.redeem_points_entry.bind("<KeyRelease>", self.update_redeem_time_display)

        # Display conversion
        ctk.CTkLabel(input_frame, text=f"Conversion Rate: {int(self._dummy_points_per_minute_entertainment)} points = 1 minute", 
                    font=ctk.CTkFont(size=12, slant="italic")).pack(pady=(0, 5), padx=20, anchor="w")
        self.redeem_time_display_label = ctk.CTkLabel(input_frame, text="Equals: 0.0 minutes", 
                                                     font=ctk.CTkFont(size=18, weight="bold"), text_color="cyan")
        self.redeem_time_display_label.pack(pady=(0, 10), padx=20)

        redeem_button = ctk.CTkButton(input_frame, text="Redeem Points", 
                                     font=ctk.CTkFont(size=16, weight="bold"), 
                                     command=self.perform_dummy_redemption)
        redeem_button.pack(pady=(10, 20), padx=20, fill="x")

        # Status message label
        self.redemption_status_label = ctk.CTkLabel(self.point_redemption_tab, text="", 
                                                   font=ctk.CTkFont(size=14, weight="bold"))
        self.redemption_status_label.pack(pady=(0, 20), padx=20)

    def save_settings_gui(self):
        """Reads values from settings GUI elements and simulates saving them."""
        # Validate and "save" point conversion settings
        try:
            new_prod_pts = int(self.productive_points_per_min_entry.get())
            new_ent_pts = int(self.entertainment_points_per_min_entry.get())
            if new_prod_pts < 0 or new_ent_pts < 0:
                messagebox.showwarning("Input Error", "Point values must be non-negative integers.")
                return
            self._dummy_productive_points_per_minute = new_prod_pts
            self._dummy_entertainment_points_per_minute = new_ent_pts
            print(f"Dummy Saved: Productive Points/Min: {new_prod_pts}, Entertainment Points/Min: {new_ent_pts}")
        except ValueError:
            messagebox.showwarning("Input Error", "Productivity/Entertainment points must be valid numbers.")
            return

        # Validate and "save" monitoring interval
        try:
            new_interval = int(self.monitoring_interval_entry.get())
            if new_interval <= 0:
                messagebox.showwarning("Input Error", "Monitoring interval must be a positive integer.")
                return
            self._dummy_monitoring_interval_seconds = new_interval
            print(f"Dummy Saved: Monitoring Interval: {new_interval} seconds")
        except ValueError:
            messagebox.showwarning("Input Error", "Monitoring interval must be a valid number.")
            return

        # "Save" startup behavior
        self._dummy_start_on_startup = bool(self.startup_checkbox.get())
        print(f"Dummy Saved: Start on Startup: {self._dummy_start_on_startup}")

        # Apply and "save" appearance mode and color theme
        new_appearance_mode = self.appearance_mode_optionmenu.get()
        new_color_theme = self.color_theme_optionmenu.get()

        ctk.set_appearance_mode(new_appearance_mode)
        ctk.set_default_color_theme(new_color_theme)
        self._dummy_appearance_mode = new_appearance_mode
        self._dummy_color_theme = new_color_theme
        print(f"Applied and Dummy Saved: Appearance Mode: {new_appearance_mode}, Color Theme: {new_color_theme}")

        messagebox.showinfo("Settings Saved (Dummy)", "Settings have been updated! (Changes are not persistent yet)")

    def create_settings_tab(self):
        """Populates the Settings tab with GUI elements."""
        self.settings_tab.columnconfigure(0, weight=1)

        ctk.CTkLabel(self.settings_tab, text="Application Settings", 
                    font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)

        settings_frame = ctk.CTkFrame(self.settings_tab)
        settings_frame.pack(pady=10, padx=20, fill="x", expand=False)
        settings_frame.columnconfigure(0, weight=1)
        settings_frame.columnconfigure(1, weight=1)

        # Point Conversion Settings
        ctk.CTkLabel(settings_frame, text="Productivity Points per Minute:", 
                    font=ctk.CTkFont(size=14)).grid(row=0, column=0, pady=5, padx=20, sticky="w")
        self.productive_points_per_min_entry = ctk.CTkEntry(settings_frame, placeholder_text="e.g., 1")
        self.productive_points_per_min_entry.grid(row=0, column=1, pady=5, padx=20, sticky="ew")
        self.productive_points_per_min_entry.insert(0, str(self._dummy_productive_points_per_minute))

        ctk.CTkLabel(settings_frame, text="Entertainment Points per Minute:", 
                    font=ctk.CTkFont(size=14)).grid(row=1, column=0, pady=5, padx=20, sticky="w")
        self.entertainment_points_per_min_entry = ctk.CTkEntry(settings_frame, placeholder_text="e.g., 0")
        self.entertainment_points_per_min_entry.grid(row=1, column=1, pady=5, padx=20, sticky="ew")
        self.entertainment_points_per_min_entry.insert(0, str(self._dummy_entertainment_points_per_minute))

        # Monitoring Interval Setting
        ctk.CTkLabel(settings_frame, text="Monitoring Interval (seconds):", 
                    font=ctk.CTkFont(size=14)).grid(row=2, column=0, pady=5, padx=20, sticky="w")
        self.monitoring_interval_entry = ctk.CTkEntry(settings_frame, placeholder_text="e.g., 5")
        self.monitoring_interval_entry.grid(row=2, column=1, pady=5, padx=20, sticky="ew")
        self.monitoring_interval_entry.insert(0, str(self._dummy_monitoring_interval_seconds))

        # Start on Startup Setting
        self.startup_checkbox = ctk.CTkCheckBox(settings_frame, text="Start monitoring on application launch", 
                                               font=ctk.CTkFont(size=14))
        self.startup_checkbox.grid(row=3, column=0, columnspan=2, pady=15, padx=20, sticky="w")
        if self._dummy_start_on_startup:
            self.startup_checkbox.select()

        # Appearance Settings
        ctk.CTkLabel(settings_frame, text="Appearance Mode:", 
                    font=ctk.CTkFont(size=14)).grid(row=4, column=0, pady=5, padx=20, sticky="w")
        self.appearance_mode_optionmenu = ctk.CTkOptionMenu(settings_frame, values=["System", "Light", "Dark"],
                                                           command=ctk.set_appearance_mode)
        self.appearance_mode_optionmenu.grid(row=4, column=1, pady=5, padx=20, sticky="ew")
        self.appearance_mode_optionmenu.set(self._dummy_appearance_mode)

        ctk.CTkLabel(settings_frame, text="Color Theme:", 
                    font=ctk.CTkFont(size=14)).grid(row=5, column=0, pady=5, padx=20, sticky="w")
        self.color_theme_optionmenu = ctk.CTkOptionMenu(settings_frame, values=["blue", "dark-blue", "green"],
                                                       command=ctk.set_default_color_theme)
        self.color_theme_optionmenu.grid(row=5, column=1, pady=5, padx=20, sticky="ew")
        self.color_theme_optionmenu.set(self._dummy_color_theme)

        # Save Settings Button
        save_button = ctk.CTkButton(self.settings_tab, text="Save Settings", 
                                   font=ctk.CTkFont(size=16, weight="bold"), 
                                   command=self.save_settings_gui)
        save_button.pack(pady=30, padx=20, fill="x")

    def create_mini_game_tab(self):
        """Creates placeholder content for the Mini Game tab."""
        ctk.CTkLabel(self.mini_game_tab, text="Welcome to the Mini Game Casino!").pack(pady=20, padx=20)

if __name__ == "__main__":
    app = App()
    app.mainloop()