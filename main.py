# main.py
from app.gui import GetBack2WorkGUI

def main():
    # Create the GUI application instance
    app = GetBack2WorkGUI()
    
    # Start the main event loop
    app.root.mainloop()

if __name__ == "__main__":
    main()