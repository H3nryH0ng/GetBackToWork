import win32gui
import win32process
import psutil
import app_classifier
import json
import blocker
import tkinter as tk

def get_active_app():
    handle = win32gui.GetForegroundWindow()
    _,pid = win32process.GetWindowThreadProcessId(handle)

    for process in psutil.process_iter(['pid', 'name']):
        if process.info['pid'] == pid:
            process_name = process.info['name']
            return process_name
        
def check_app(app_name):
    category = app_classifier.classify_app(app_name)
    with open('points.json', 'r') as file:
        data = json.load(file)

    if category == "Productive":
        data['points'] += 1  # Add 1 point
    elif category == "Entertainment":
        if data['points'] <= 0:
            blocker.show_popup("Reminder!", "GET BACK TO WORKK!!")
        else:
            data['points'] -= 1
    with open('points.json', 'w') as file:
        json.dump(data, file, indent=2)
        return category

def get_all_app_list():
    app_list = []
    ignored_list = ["TextInputHost.exe", "explorer.exe"]
    for process in psutil.process_iter(['pid', 'name']):
        pid = process.info['pid']

        def enumWindowsArguments(handle, __):
            _, foundPID = win32process.GetWindowThreadProcessId(handle)

            if foundPID == pid and win32gui.IsWindowVisible(handle):
                process_name = process.info["name"]
                if process_name and (process_name not in ignored_list):
                    app_name = process_name # Get all active app name
                    if app_name not in app_list:
                        app_list.append(app_name)

        win32gui.EnumWindows(enumWindowsArguments, None)
    return app_list

if __name__ == "__main__":
    check_app("steamwebhelper.exe")