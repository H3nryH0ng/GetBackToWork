import customtkinter as ctk

def create_gui():
    # Initialize the main window
    app = ctk.CTk()
    app.title("FocusSwap")
    app.geometry("1280x720")

    # Create the TabView widget
    tabview = ctk.CTkTabview(app)
    tabview.pack(expand=True, fill="both", padx=20, pady=20)

    # Add tabs to the TabView
    tabview.add("Tab 1")
    tabview.add("Tab 2")

    # Start the app window loop
    app.mainloop()

if __name__ == "__main__":
    create_gui()
