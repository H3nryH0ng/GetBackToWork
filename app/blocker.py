import time
import tkinter as tk
from tkinter import messagebox
import tkinter.font as tkFont
from PIL import Image, ImageTk # Import Pillow components for image handling
import io # Import io to handle image data if needed, but not for file path
import os # Import os for file path checking


# --- IMPORTANT: Configure your image file path here ---
# The path has been updated to your specified GIF image file.
# Make sure 'get-back-to-work.gif' is in the same directory as this Python script.
CUSTOM_POPUP_IMAGE_PATH = "get-back-to-work.gif" # <--- THIS LINE HAS BEEN CHANGED


# --- Pop-up function ---
def show_popup(parent_root: tk.Tk, title: str, message: str):
    """
    Displays a custom pop-up window that is at least half the screen size,
    displaying an image from a specified file.
    """
    popup = tk.Toplevel(parent_root)
    popup.title(title)
    popup.attributes('-topmost', True)
    popup.overrideredirect(True)
    popup.attributes('-alpha', 0.95)

    screen_width = parent_root.winfo_screenwidth()
    screen_height = parent_root.winfo_screenheight()

    popup_width = int(screen_width * 0.75) # Let's aim for 75% width
    popup_height = int(screen_height * 0.75) # Let's aim for 75% height

    min_width = 400
    min_height = 200
    popup_width = max(popup_width, min_width)
    popup_height = max(popup_height, min_height)

    # Calculate position to center the popup
    x_pos = (screen_width // 2) - (popup_width // 2)
    y_pos = (screen_height // 2) - (popup_height // 2)

    # Set window geometry (WxH+X+Y)
    popup.geometry(f"{popup_width}x{popup_height}+{x_pos}+{y_pos}")
    popup.config(bg="red")

    photo_image = None
    # --- Image Loading from File ---
    try:
        if not os.path.exists(CUSTOM_POPUP_IMAGE_PATH):
            raise FileNotFoundError(f"Image file not found: {CUSTOM_POPUP_IMAGE_PATH}")

        original_image = Image.open(CUSTOM_POPUP_IMAGE_PATH)

        # Handle GIF animations if desired (optional: display only first frame or iterate)
        # For a simple static display, using Image.open() directly is fine as it loads the first frame.
        # If you need animation, a more complex Tkinter animation loop would be required.

        img_width, img_height = original_image.size
        max_img_width = popup_width - 80
        max_img_height = popup_height - 150

        width_scale = max_img_width / img_width
        height_scale = max_img_height / img_height
        scale_factor = min(width_scale, height_scale)

        new_img_width = int(img_width * scale_factor)
        new_img_height = int(img_height * scale_factor)

        # Use Image.LANCZOS for high-quality downsampling
        resized_image = original_image.resize((new_img_width, new_img_height), Image.LANCZOS)
        photo_image = ImageTk.PhotoImage(resized_image)

    except Exception as e:
        print(f"Error loading or processing image from '{CUSTOM_POPUP_IMAGE_PATH}': {e}")
        # Fallback to text message if image fails
        fallback_label = tk.Label(popup, text=message, font=tkFont.Font(family="Helvetica", size=40, weight="bold"),
                                   fg="white", bg="red", wraplength=popup_width - 40)
        fallback_label.pack(expand=True, pady=(popup_height * 0.1, popup_height * 0.05))

    if photo_image:
        image_label = tk.Label(popup, image=photo_image, bg="red")
        image_label.image = photo_image # Keep reference
        image_label.pack(expand=True, pady=(popup_height * 0.05, popup_height * 0.02)) # Padding

    button_font = tkFont.Font(family="Helvetica", size=18, weight="bold")
    close_button = tk.Button(popup, text="OK, I'll Get Back To Work!", font=button_font, command=popup.destroy,
                             bg="white", fg="red", activebackground="lightgray", activeforeground="red",
                             bd=5, relief="raised")
    close_button.pack(pady=20)

    popup.grab_set()
    parent_root.wait_window(popup)


def run_continuous_popup_monitor(parent_root: tk.Tk, interval_seconds: int):
    """
    Continuously displays a popup at a specified interval using root.after().
    """
    print(f"Scheduling popup to appear in {interval_seconds} seconds.")

    parent_root.after(interval_seconds * 1000, lambda: _show_and_reschedule(parent_root, interval_seconds))

def _show_and_reschedule(parent_root: tk.Tk, interval_seconds: int):
    """
    Internal helper to show the popup and then reschedule the next one.
    """
    try:
        # The 'message' parameter here is only used for fallback if image loading fails
        show_popup(parent_root, "Reminder!", "GET BACK TO WORKK!!")
    except Exception as e:
        print(f"An error occurred during popup display: {e}")
    finally:
        parent_root.after(interval_seconds * 1000, lambda: _show_and_reschedule(parent_root, interval_seconds))


# --- Main Execution Block ---
if __name__ == "__main__":

    root = tk.Tk()
    root.withdraw() # Popup every 2 seconds
    show_popup(root, "Reminder!", "GET BACK TO WORKK!!")


    root.mainloop()
