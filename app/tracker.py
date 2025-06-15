import win32gui
import win32process
import psutil
import app_classifier
import json
import blocker
import tkinter as tk
import time

def get_active_app():
    handle = win32gui.GetForegroundWindow()
    _,pid = win32process.GetWindowThreadProcessId(handle)

    for process in psutil.process_iter(['pid', 'name']):
        if process.info['pid'] == pid:
            process_name = process.info['name']
            return process_name
        
def check_app(app_name):
    category = app_classifier.classify_app(app_name)
    
    # Load current difficulty level
    try:
        with open('settings.json', 'r') as f:
            settings = json.load(f)
            difficulty = settings.get('difficulty_level', 'chill')
    except (FileNotFoundError, json.JSONDecodeError):
        difficulty = 'chill'  # Default to chill mode if settings not found
    
    # Load current points
    with open('points.json', 'r') as file:
        data = json.load(file)
        current_points = data.get('points', 0)

    # Calculate points based on difficulty level
    if category == "Productive":
        if difficulty == "chill":
            points_change = 1  # 1 point per second
        elif difficulty == "medium":
            # Add 1 point every 5 seconds
            if time.time() % 5 < 1:  # Check if we're in the first second of each 5-second interval
                points_change = 1
            else:
                points_change = 0
        else:  # productive_guru
            # Add 1 point every 10 seconds
            if time.time() % 10 < 1:  # Check if we're in the first second of each 10-second interval
                points_change = 1
            else:
                points_change = 0
        current_points += points_change
    elif category == "Entertainment":
        if difficulty == "chill":
            points_change = 0  # No point deduction in chill mode
        elif difficulty == "medium":
            points_change = -5  # -5 points per second
        else:  # productive_guru
            points_change = -10  # -10 points per second
        current_points = max(0, current_points + points_change)  # Ensure points don't go below 0

    # Save updated points
    with open('points.json', 'w') as file:
        json.dump({"points": current_points}, file, indent=2)
    
    return category

if __name__ == "__main__":
    check_app("steamwebhelper.exe")