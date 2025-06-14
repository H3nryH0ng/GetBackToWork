import win32gui
import win32process
import psutil
import time

def get_active_app():
    handle = win32gui.GetForegroundWindow()
    _,pid = win32process.GetWindowThreadProcessId(handle)

    for process in psutil.process_iter(['pid', 'name']):
        if process.info['pid'] == pid:
            process_name = process.info['name']
            return process_name

if __name__ == "__main__":
    while True:
        name = get_active_app()
        print(name)
        time.sleep(1)