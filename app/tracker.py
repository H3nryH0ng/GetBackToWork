import win32gui
import win32process
import psutil
import app_classifier
import json
import blocker
import tkinter as tk
import pywinauto.application
import time

def get_active_app():
    handle = win32gui.GetForegroundWindow()
    _,pid = win32process.GetWindowThreadProcessId(handle)

    for process in psutil.process_iter(['pid', 'name']):
        if process.info['pid'] == pid:
            process_name = process.info['name']
            if process_name == "chrome.exe":
                return get_current_tab_name()
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

def get_current_tab_name():

    try:
        foregroundApp = win32gui.GetForegroundWindow()
        TID, PID = win32process.GetWindowThreadProcessId(foregroundApp)
        chromeApp = pywinauto.application.Application(backend = "uia").connect(process = PID) # Connects to active Chrome
        topWindow = chromeApp.top_window() 
        url = topWindow.child_window(title = "Address and search bar", control_type = "Edit").get_value() # URL is here

        tabName = url.split("/")[0].split(".")[-2].capitalize()

    except Exception:
        tabName = "URL not detected"

    return tabName

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
    while True:
        x = get_active_app()
        
        print(x) 
        time.sleep(1) # Check every second
