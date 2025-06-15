import customtkinter as ctk
from tkinter import messagebox
import tracker
import time
import threading
import json
import save_app
import random
import os

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Initialize required JSON files
        self._initialize_json_files()

        # Configure window
        self.title("GetB@ck2Work")
        self.geometry("1280x720")

        # Configure grid layout (1x1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Initialize difficulty level
        self.difficulty_level = "chill"  # Default difficulty
        self._load_difficulty_settings()

        # --- Initialize dummy data ---
        with open("productivity.json", 'r') as file:
            data = json.load(file) # Use json.load() for file objects
            self.productivity_apps = data.get("productivity_app", [])
            self.entertainment_apps = data.get("entertainment_app", [])

        with open("points.json", 'r') as file:
            points_data = json.load(file)
            self.current_points = points_data.get("points", "")

        self.points_per_minute_entertainment = 2
        self.productive_points_per_minute = 1
        self.entertainment_points_per_minute = 0
        self.monitoring_interval_seconds = 5
        self.start_on_startup = False
        self.appearance_mode = "System"
        self.color_theme = "blue"
        self.category = "Unclassified"

        # Initialize detected app variables
        self.detected_app = ""
        self.detected_app_list = []
        self.all_app_list = tracker.get_all_app_list()

        self.outcomes = [
            ("🎯", "Extra Focus Points!", "give_points"),
            ("💡", "Productivity Tip!", "show_tip"),
            ("😳", "Dare Time!", "show_dare"),
            ("💀", "All Points Lost!", "lose_all_points")
        ]

        self.tips = [
            "Take a 5-minute break every 25 minutes (Pomodoro Technique)",
            "Use the 2-minute rule: if a task takes less than 2 minutes, do it now",
            "Start your day with the most important task",
            "Use the Eisenhower Matrix to prioritize tasks",
            "Practice deep work: focus on one task for 90 minutes",
            "Use the 80/20 rule: focus on the 20% of tasks that yield 80% of results",
            "Create a 'not-to-do' list to avoid distractions",
            "Use the 'eat the frog' method: tackle your hardest task first",
            "Batch similar tasks together",
            "Use the 'touch it once' rule: handle each task only once"
        ]

        self.dares = [
            "Text your mom you love her. No context.",
            "Post 'I love productivity!' on your social media",
            "Send a voice message to a friend saying 'I'm being productive!'",
            "Take a selfie with your most productive face and send it to a friend",
            "Record yourself doing a productivity dance and send it to a friend",
            "Call a friend and tell them about your productivity goals",
            "Post a screenshot of your current task on social media",
            "Send a motivational quote to 3 friends",
            "Record yourself saying 'I am a productivity machine!' and send it to a friend",
            "Take a video of yourself organizing your workspace and send it to a friend"
        ]

        # Set initial appearance
        ctk.set_appearance_mode(self.appearance_mode)
        ctk.set_default_color_theme(self.color_theme)

        # Create tabview
        self.tabview = ctk.CTkTabview(self, width=500, height=300)
        self.tabview.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # Add tabs
        self.dashboard_tab = self.tabview.add("Dashboard")
        self.app_management_tab = self.tabview.add("App Management")
        self.mini_game_tab = self.tabview.add("Mini Game")
        self.settings_tab = self.tabview.add("Settings")  # New settings tab

        # Set default tab
        self.tabview.set("Dashboard")

        # Create all tabs
        self.create_dashboard_tab()
        self.create_app_management_tab()
        self.create_mini_game_tab()
        self.create_settings_tab()  # Create settings tab

        # Start background thread
        threading.Thread(target=self.update_active_app_TB, daemon=True).start()

    def _initialize_json_files(self):
        """Initialize required JSON files if they don't exist."""
        # Initialize productivity.json
        if not os.path.exists("productivity.json"):
            initial_productivity_data = {
                "productivity_app": [],
                "entertainment_app": []
            }
            with open("productivity.json", 'w') as f:
                json.dump(initial_productivity_data, f, indent=4)

        # Initialize points.json
        if not os.path.exists("points.json"):
            initial_points_data = {
                "points": 0
            }
            with open("points.json", 'w') as f:
                json.dump(initial_points_data, f, indent=4)

    def _load_difficulty_settings(self):
        """Load difficulty settings from settings.json"""
        try:
            with open("settings.json", 'r') as f:
                settings = json.load(f)
                self.difficulty_level = settings.get("difficulty_level", "chill")
        except (FileNotFoundError, json.JSONDecodeError):
            # If file doesn't exist or is invalid, create it with default settings
            self._save_difficulty_settings()

    def _save_difficulty_settings(self):
        """Save difficulty settings to settings.json"""
        settings = {
            "difficulty_level": self.difficulty_level
        }
        with open("settings.json", 'w') as f:
            json.dump(settings, f, indent=4)

    def create_settings_tab(self):
        """Create the settings tab with difficulty level options"""
        # Create main frame
        settings_frame = ctk.CTkFrame(self.settings_tab)
        settings_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Title
        title_label = ctk.CTkLabel(
            settings_frame,
            text="Difficulty Settings",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(20, 30))

        # Difficulty level selection
        difficulty_frame = ctk.CTkFrame(settings_frame)
        difficulty_frame.pack(padx=20, pady=10, fill="x")

        ctk.CTkLabel(
            difficulty_frame,
            text="Select Difficulty Level:",
            font=ctk.CTkFont(size=16)
        ).pack(pady=(10, 5))

        # Create radio buttons for difficulty levels
        self.difficulty_var = ctk.StringVar(value=self.difficulty_level)
        
        def on_difficulty_change():
            # Show confirmation popup
            confirm_window = ctk.CTkToplevel(self)
            confirm_window.title("Confirm Difficulty Change")
            confirm_window.geometry("400x200")
            confirm_window.transient(self)
            confirm_window.grab_set()
            
            # Make popup stay on top
            confirm_window.attributes('-topmost', True)
            
            # Add message
            message = ctk.CTkLabel(
                confirm_window,
                text=f"Are you sure you want to change the difficulty to {self.difficulty_var.get().title()}?\n\nThis will reset your current points to 0.",
                font=ctk.CTkFont(size=14),
                wraplength=350
            )
            message.pack(pady=20)
            
            # Add buttons
            button_frame = ctk.CTkFrame(confirm_window)
            button_frame.pack(pady=20)
            
            def apply_changes():
                self.difficulty_level = self.difficulty_var.get()
                self._save_difficulty_settings()
                # Reset points when changing difficulty
                self._dummy_current_points = 0
                with open("points.json", 'w') as file:
                    json.dump({"points": 0}, file, indent=4)
                self.points_label.configure(text="0")
                confirm_window.destroy()
            
            def cancel_changes():
                # Reset radio button to previous value
                self.difficulty_var.set(self.difficulty_level)
                confirm_window.destroy()
            
            cancel_button = ctk.CTkButton(
                button_frame,
                text="Cancel",
                command=cancel_changes,
                fg_color="#FF5555",
                hover_color="#FF3333"
            )
            cancel_button.pack(side="left", padx=10)
            
            confirm_button = ctk.CTkButton(
                button_frame,
                text="Confirm Change",
                command=apply_changes,
                fg_color="#55FF55",
                hover_color="#33FF33"
            )
            confirm_button.pack(side="left", padx=10)
            
            # Center the window
            confirm_window.update_idletasks()
            width = confirm_window.winfo_width()
            height = confirm_window.winfo_height()
            x = (confirm_window.winfo_screenwidth() // 2) - (width // 2)
            y = (confirm_window.winfo_screenheight() // 2) - (height // 2)
            confirm_window.geometry(f'{width}x{height}+{x}+{y}')

        difficulties = [
            ("Chill Mode", "chill", 
             "• 1 point per second on productive apps\n• No point deduction for entertainment apps\n• Perfect for beginners"),
            ("Medium Mode", "medium", 
             "• 1 point per 5 seconds on productive apps\n• -5 points per second on entertainment apps\n• Balanced challenge"),
            ("Productive Guru", "productive_guru", 
             "• 1 point per 10 seconds on productive apps\n• -10 points per second on entertainment apps\n• Strict monitoring with popup reminders")
        ]

        for text, value, description in difficulties:
            frame = ctk.CTkFrame(difficulty_frame)
            frame.pack(padx=20, pady=5, fill="x")
            
            radio = ctk.CTkRadioButton(
                frame,
                text=text,
                variable=self.difficulty_var,
                value=value,
                command=on_difficulty_change
            )
            radio.pack(side="left", padx=10)
            
            desc_label = ctk.CTkLabel(
                frame,
                text=description,
                font=ctk.CTkFont(size=12),
                text_color="gray",
                justify="left"
            )
            desc_label.pack(side="left", padx=10, fill="x", expand=True)

    def switch_tab_to_redeem_points(self):
        """Helper function to switch the tab to 'Point Redemption'."""
        self.tabview.set("Point Redemption")
        print("Switched to Point Redemption tab.")
        if hasattr(self, 'points_label'):
            self.points_label.configure(text=str(self.current_points))

    def create_dashboard_tab(self):
        """Populates the Dashboard tab with suggested GUI elements."""

        self.dashboard_tab.columnconfigure(0, weight=1)
        self.dashboard_tab.rowconfigure(1, weight=1)

        # Current Points Balance - Hero Section
        self.points_frame = ctk.CTkFrame(self.dashboard_tab, corner_radius=20, height=160)
        self.points_frame.grid(row=0, column=0, sticky="ew", padx=40, pady=(40, 25))
        self.points_frame.columnconfigure(0, weight=1)
        self.points_frame.grid_propagate(False)

        self.points_text_label = ctk.CTkLabel(self.points_frame, text="Current Focus Points", 
                                            font=ctk.CTkFont(size=28, weight="bold"),
                                            text_color=("gray10", "gray90"))
        self.points_text_label.grid(row=0, column=0, pady=(30, 5))
        
        self.points_label = ctk.CTkLabel(self.points_frame, text=str(self.current_points),
                                    font=ctk.CTkFont(size=56, weight="bold"),
                                    text_color=("#1f538d", "#4a9eff"))
        self.points_label.grid(row=1, column=0, pady=(0, 30))

        # App Detection Frame - Card Style
        self.detected_app_frame = ctk.CTkFrame(self.dashboard_tab, 
                                            fg_color=("gray92", "gray13"), 
                                            corner_radius=20,
                                            border_width=2,
                                            border_color=("gray80", "gray25"))
        self.detected_app_frame.grid(row=1, column=0, sticky="nsew", padx=40, pady=(0, 25))
        self.detected_app_frame.columnconfigure(0, weight=1)
        self.detected_app_frame.rowconfigure(1, weight=1)

        # Add a subtle header inside the frame
        self.app_header = ctk.CTkLabel(self.detected_app_frame, 
                                    text="🖥️ Active Application Monitor",
                                    font=ctk.CTkFont(size=20, weight="bold"),
                                    text_color=("gray20", "gray80"))
        self.app_header.grid(row=0, column=0, pady=(25, 15), padx=25, sticky="w")

        self.detected_apps_TB = ctk.CTkTextbox(self.detected_app_frame, 
                                            height=200, 
                                            width=400, 
                                            state="disabled",
                                            corner_radius=12,
                                            border_width=1,
                                            border_color=("gray75", "gray30"),
                                            font=ctk.CTkFont(size=13))
        self.detected_apps_TB.grid(row=1, column=0, padx=25, pady=(0, 20), sticky="nsew")

        # Category Label - Status Badge Style
        self.category_label = ctk.CTkLabel(self.dashboard_tab, 
                                        text="📊 Detected App Category: Unclassified",
                                        font=ctk.CTkFont(size=18, weight="bold"),
                                        fg_color=("orange", "darkorange"),
                                        corner_radius=25,
                                        height=50,
                                        text_color="white")
        self.category_label.grid(row=2, column=0, pady=(0, 40), padx=40, sticky="ew")

    def update_active_app_TB(self):
        """Updates the detected apps textbox with current active app."""
        while True:
            time.sleep(1)
            self.detected_app = tracker.get_active_app()
            if (self.detected_app) and (self.detected_app != "python.exe") and  (self.detected_app != "python3.12.exe") :
                self.detected_app_list.append(self.detected_app)
                # Update the textbox from the main thread
                self.after(0, self.update_active_app)
                self.category = tracker.check_app(self.detected_app)
                
                # Check if we should show popup based on difficulty level
                if self.difficulty_level == "productive_guru" and self.category == "Entertainment":
                    self.show_productivity_popup()
                
                with open("points.json", 'r') as file:
                    points_data = json.load(file)
                    self.current_points = points_data.get("points", "")
                    self.points_label.configure(text=self.current_points)
                

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

        if self.productivity_apps:
            for app_name in self.productivity_apps:
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

        if self.entertainment_apps:
            for app_name in self.entertainment_apps:
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

    def refresh_dropdown(self):
        self.all_app_list = tracker.get_all_app_list()
        self.choose_app_dropdown.configure(values=self.all_app_list)

    def add_app_gui(self):
        """Handles adding a new app from the GUI input fields using dummy data."""
        if self.app_name_entry.get().strip():
            app_name = self.app_name_entry.get().strip()
        else:
            app_name = self.choose_app_dropdown.get().strip()
        app_type = self.app_type_optionmenu.get().lower()

        if not app_name:
            messagebox.showwarning("Input Error", "Please enter an application name.")
            return

        if app_type == "productivity":
            if app_name not in self.productivity_apps:
                self.productivity_apps.append(app_name)
                save_app.save_app_to_productivity(app_name)
                self.refresh_app_lists()
                self.app_name_entry.delete(0, "end")
                messagebox.showinfo("Success", f"'{app_name}' added to Productivity apps (dummy).")
            else:
                messagebox.showwarning("Already Exists", f"'{app_name}' is already in the Productivity list (dummy).")
        elif app_type == "entertainment":
            if app_name not in self.entertainment_apps:
                self.entertainment_apps.append(app_name)
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
            if app_name in self.productivity_apps:
                self.productivity_apps.remove(app_name)
                save_app.remove_app_from_productivity(app_name)  # Simulate saving removal
                self.refresh_app_lists()
                messagebox.showinfo("Success", f"'{app_name}' removed from Productivity apps (dummy).")
                
            else:
                messagebox.showerror("Error", f"Could not remove '{app_name}'. It might not be in the list (dummy).")
        elif app_type == "entertainment":
            if app_name in self.entertainment_apps:
                self.entertainment_apps.remove(app_name)
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
        self.app_name_entry = ctk.CTkEntry(add_app_frame)
        self.app_name_entry.pack(pady=(0, 10), padx=20, fill="x")

        self.choose_app_dropdown = ctk.CTkComboBox(add_app_frame, values=self.all_app_list)
        self.choose_app_dropdown.pack(pady=(0, 10), padx=20, fill="x")

        self.refresh_dropdown = ctk.CTkButton(add_app_frame, text="Refresh", command=self.refresh_dropdown)
        self.refresh_dropdown.pack(pady=(0, 10), padx=20, fill="x")

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

    def create_mini_game_tab(self):
        frame = ctk.CTkFrame(self.mini_game_tab)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        label = ctk.CTkLabel(frame, text="Mini Game: Gamble Your Productivity Points!",
                             font=ctk.CTkFont(size=20, weight="bold"))
        label.pack(pady=20)

        launch_casino_button = ctk.CTkButton(
            frame, text="Launch Casino", command=self.open_casino_window,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#1ABC9C", hover_color="#16A085"
        )
        launch_casino_button.pack(pady=10)

    def open_casino_window(self):
        self.casino_window = ctk.CTkToplevel(self)
        self.casino_window.title("Gamble Your Points Casino")
        self.casino_window.geometry("400x500")
        self.casino_window.configure(bg="#2C3E50")
        self.casino_window.transient(self)
        self.casino_window.grab_set()

        self.casino_points_label = ctk.CTkLabel(self.casino_window,
                                                text=f"Current Points: {self.current_points}",
                                                text_color="white",
                                                font=ctk.CTkFont(size=18, weight="bold"))
        self.casino_points_label.pack(pady=20)

        self.slot_frame = ctk.CTkFrame(self.casino_window, fg_color="#2C3E50")
        self.slot_frame.pack(pady=20)

        self.slots = []
        for _ in range(3):
            slot = ctk.CTkLabel(self.slot_frame, text="?", font=ctk.CTkFont(size=32, weight="bold"),
                                width=50, text_color="white")
            slot.pack(side="left", padx=10)
            self.slots.append(slot)

        self.spin_button = ctk.CTkButton(
            self.casino_window, text="SPIN! (Costs 10 points)", command=self.spin,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#1ABC9C", hover_color="#16A085"
        )
        self.spin_button.pack(pady=20)

        self.result_label = ctk.CTkLabel(self.casino_window, text="", wraplength=350, justify="center",
                                        text_color="white", font=ctk.CTkFont(size=14))
        self.result_label.pack(pady=20)

        self.update_spin_button()

    def spin(self):
        if self.current_points >= 10:
            # Deduct points immediately
            self.deduct_points(10)
            self.update_points_display()

            # Disable spin button while spinning
            self.spin_button.configure(state='disabled')
            self.animate_slots()

    def animate_slots(self, iteration=0):
        if iteration < 20:
            for slot in self.slots:
                outcome = random.choice(self.outcomes)
                slot.configure(text=outcome[0])
            self.after(100, lambda: self.animate_slots(iteration + 1))
        else:
            # Select final outcome
            final_outcome = random.choice(self.outcomes)
            for slot in self.slots:
                slot.configure(text=final_outcome[0])
            self.result_label.configure(text=final_outcome[1])

            # Apply the outcome effect
            getattr(self, final_outcome[2])()

            # Update points display and spin button state after outcome is applied
            self.update_points_display()
            self.update_spin_button()

    def update_spin_button(self):
        if self.current_points < 10:
            self.spin_button.configure(state='disabled')
        else:
            self.spin_button.configure(state='normal')

    # Outcome handlers (cleaned, no button state management inside these)
    def give_points(self):
        points = random.randint(20, 50)
        self.add_points(points)
        self.result_label.configure(text=f"{self.result_label.cget('text')}\nYou won {points} points!")

    def show_tip(self):
        tip = random.choice(self.tips)
        self.result_label.configure(text=f"{self.result_label.cget('text')}\n\nProductivity Tip:\n{tip}")

    def show_dare(self):
        dare = random.choice(self.dares)
        self.result_label.configure(text=f"{self.result_label.cget('text')}\n\nYour Dare:\n{dare}")

    def lose_all_points(self):
        points_lost = self.current_points
        self.current_points = 0
        self.result_label.configure(text=f"{self.result_label.cget('text')}\n\nYou lost all {points_lost} points!")

    # Points utility functions
    def add_points(self, amount):
        self.current_points += amount


    def deduct_points(self, amount):
        self.current_points = max(0, self.current_points - amount)

    def update_points_display(self):
        self.points_label.configure(text=self.current_points)
        if hasattr(self, 'casino_points_label'):
            self.casino_points_label.configure(text=f"Current Points: {self.current_points}")
        new_data = {"points": self.current_points}
        with open("points.json", 'w') as file:
            json.dump(new_data, file, indent=4)

    def show_productivity_popup(self):
        """Show a productivity reminder popup"""
        popup = ctk.CTkToplevel(self)
        popup.title("Productivity Reminder")
        popup.geometry("400x200")
        
        # Make popup stay on top
        popup.attributes('-topmost', True)
        
        # Add message
        message = ctk.CTkLabel(
            popup,
            text="Are you sure you want to continue with this entertainment app?\n\nRemember your productivity goals!",
            font=ctk.CTkFont(size=14),
            wraplength=350
        )
        message.pack(pady=20)
        
        # Add buttons
        button_frame = ctk.CTkFrame(popup)
        button_frame.pack(pady=20)
        
        def close_popup():
            popup.destroy()
        
        continue_button = ctk.CTkButton(
            button_frame,
            text="Continue Anyway",
            command=close_popup,
            fg_color="#FF5555",
            hover_color="#FF3333"
        )
        continue_button.pack(side="left", padx=10)
        
        switch_button = ctk.CTkButton(
            button_frame,
            text="Switch to Productive App",
            command=close_popup,
            fg_color="#55FF55",
            hover_color="#33FF33"
        )
        switch_button.pack(side="left", padx=10)
        
        # Schedule popup to close after 10 seconds
        popup.after(10000, close_popup)

if __name__ == "__main__":
    app = App()
    app.mainloop()