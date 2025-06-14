import customtkinter as ctk

import tracker
import time

detected_app = ""
detected_app_list = []

import threading

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("CustomTkinter Tab View Example")
        self.geometry("1280x720")  # Set a default size for the window

        # Configure grid layout (1x1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

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

        # Current Points Balance
        self.points_frame = ctk.CTkFrame(self.dashboard_tab)
        self.points_frame.pack(pady=(20, 10), padx=20, fill="x")
        self.points_frame.columnconfigure(0, weight=1)

        self.points_label = ctk.CTkLabel(self.points_frame, text="Current Focus Points: 0", font=ctk.CTkFont(size=16, weight="bold"))
        self.points_label.grid(row=0, column=0, pady=(10, 0), padx=20, sticky="w")

        self.detected_apps_TB = ctk.CTkTextbox(self.dashboard_tab, width=400, height=200, state="normal")
        self.detected_apps_TB.pack()

         

        # Start background thread
        threading.Thread(target=self.update_active_app_TB, daemon=True).start()

    def update_active_app_TB(self):
        while True:
            time.sleep(1)
            detected_app = tracker.get_active_app()
            if detected_app:
                detected_app_list.append(detected_app)
                self.detected_apps_TB.delete("1.0", "end")  # Clear the textbox
                self.detected_apps_TB.insert("1.0", "\n".join(detected_app_list))  # Insert updated text

if __name__ == "__main__":
    app = App()
    app.mainloop()