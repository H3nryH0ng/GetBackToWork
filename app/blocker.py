import os
import json
import time # For a small delay for user to read messages
import tkinter as tk # For creating GUI elements
from tkinter import messagebox # For showing message boxes

# --- Helper functions for JSON file handling (from previous versions) ---

def _create_initial_json_file(file_path):
    """
    Helper function to create an initial, empty JSON file with the expected structure.
    """
    initial_data = {
        "productivity_app": [],
        "entertainment_app": []
    }
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(initial_data, f, indent=4, ensure_ascii=False)
        print(f"Info: '{file_path}' not found. Created an empty file with initial structure.")
    except IOError as e:
        print(f"Error: Could not create '{file_path}'. Reason: {e}")

def classify_app_or_website(app_name, categories_file_path="productivity.json"):
    """
    Classifies an application or website name as 'Productive' or 'Entertainment'
    based on keywords found in a specified JSON file (e.g., productivity.json).
    If the file does not exist, it will be created with an empty structure.
    """
    productive_keywords = []
    entertainment_keywords = []

    if not os.path.exists(categories_file_path):
        _create_initial_json_file(categories_file_path)
    elif os.path.getsize(categories_file_path) == 0:
        print(f"Warning: '{categories_file_path}' is empty. Initializing its content.")
        _create_initial_json_file(categories_file_path)

    try:
        with open(categories_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            productive_keywords = [kw.lower() for kw in data.get('productivity_app', []) if isinstance(kw, str)]
            entertainment_keywords = [kw.lower() for kw in data.get('entertainment_app', []) if isinstance(kw, str)]
    except json.JSONDecodeError:
        print(f"Error: '{categories_file_path}' is not a valid JSON. Attempting to re-create.")
        _create_initial_json_file(categories_file_path)
        return classify_app_or_website(app_name, categories_file_path) # Retry after fix
    except Exception as e:
        print(f"An error occurred reading '{categories_file_path}': {e}")
        return "Error"

    app_name_lower = app_name.lower()

    for keyword in productive_keywords:
        if keyword in app_name_lower:
            return "Productive"

    for keyword in entertainment_keywords:
        if keyword in app_name_lower:
            return "Entertainment"

    return "Unclassified"

# --- New function to show a popup ---
def show_popup(title: str, message: str):
    """
    Displays a simple pop-up message box.
    """
    # Create a Tkinter root window, but keep it hidden
    root = tk.Tk()
    root.withdraw() # Hide the main window

    # Show the message box
    messagebox.showinfo(title, message)

    # Destroy the root window after the message box is closed
    root.destroy()

def manage_app_usage(app_name_input: str):
    """
    Classifies an app/website and, if it's entertainment, displays a pop-up warning.

    Args:
        app_name_input (str): The user-friendly name of the app/website (e.g., "Netflix", "YouTube").
    """
    print(f"\n--- Analyzing: {app_name_input} ---")
    classification = classify_app_or_website(app_name_input)
    print(f"Classification: {classification}")

    if classification == "Entertainment":
        print(f"'{app_name_input}' is classified as an entertainment app/website. Displaying warning.")
        show_popup("Warning!", "Get Back To Workk!!")
    elif classification == "Productive":
        print(f"'{app_name_input}' is a productive app/website. No action taken.")
    else: # Unclassified or Error
        print(f"'{app_name_input}' could not be classified. No action taken.")

# --- Example Usage ---
if __name__ == "__main__":
    # Ensure 'productivity.json' is set up with your categories.
    # Example content for productivity.json:
    # {
    #     "productivity_app": ["word", "jira", "slack", "code"],
    #     "entertainment_app": ["netflix", "youtube", "game", "spotify", "discord"]
    # }

    print("Welcome to the App Usage Manager!")
    print("\n--- Disclaimer ---")
    print("This program identifies entertainment apps and displays a warning pop-up.")
    print("It does NOT terminate or block applications from running in the background.")
    print("------------------")

    # Example 1: Entertainment App (should trigger popup)
    manage_app_usage("Netflix binge-watching")
    time.sleep(1) # Small delay

    # Example 2: Another entertainment app (should trigger popup)
    manage_app_usage("YouTube Videos")
    time.sleep(1)

    # Example 3: Productive App (no popup)
    manage_app_usage("Microsoft Word Document")
    time.sleep(1)

    # Example 4: Unclassified App (no popup)
    manage_app_usage("My New Project App")
    time.sleep(1)

    input("\nPress Enter to exit.")
