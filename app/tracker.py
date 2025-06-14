import win32gui
import win32process
import psutil
import time
import app_classifier

def get_active_app():
    handle = win32gui.GetForegroundWindow()
    _,pid = win32process.GetWindowThreadProcessId(handle)

    for process in psutil.process_iter(['pid', 'name']):
        if process.info['pid'] == pid:
            process_name = process.info['name']
            return process_name
        
def check_app(app_name):
    category = app_classifier.classify_app_or_website(app_name)
    return category

if __name__ == "__main__":
    x = input("Enter the name of the app you want to check: ")
    check_app(x)