import win32gui
import win32process
import psutil
import time
import app_classifier
import json

def get_active_app():
    handle = win32gui.GetForegroundWindow()
    _,pid = win32process.GetWindowThreadProcessId(handle)

    for process in psutil.process_iter(['pid', 'name']):
        if process.info['pid'] == pid:
            process_name = process.info['name']
            return process_name
        
def check_app(app_name):
    category = app_classifier.classify_app_or_website(app_name)
    with open('points.json', 'r') as file:
        data = json.load(file)

    if category == "You are using a productive app/website.":
        data['points'] += 1  # Add 1 point
    elif category == "You are using an entertainment app/website.":
        data['points'] -= 1
    with open('points.json', 'w') as file:
        json.dump(data, file, indent=2)
        return category

if __name__ == "__main__":
    x = input("Enter the name of the app you want to check: ")
    check_app(x)