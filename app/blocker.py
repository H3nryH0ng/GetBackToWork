import tkinter as tk
import tkinter.font as tkFont
from PIL import Image, ImageTk
import os

CUSTOM_POPUP_IMAGE_PATH = "get-back-to-work.gif"

def show_popup(title, message):
    # Check if a root already exists, else create one
    if not tk._default_root:
        root = tk.Tk()
        root.withdraw()

    popup = tk.Toplevel()
    popup.title(title)
    popup.attributes('-topmost', True)
    popup.overrideredirect(True)
    popup.attributes('-alpha', 0.95)

    screen_width = popup.winfo_screenwidth()
    screen_height = popup.winfo_screenheight()

    popup_width = int(screen_width * 0.75)
    popup_height = int(screen_height * 0.75)

    min_width = 400
    min_height = 200
    popup_width = max(popup_width, min_width)
    popup_height = max(popup_height, min_height)

    x_pos = (screen_width // 2) - (popup_width // 2)
    y_pos = (screen_height // 2) - (popup_height // 2)
    popup.geometry(f"{popup_width}x{popup_height}+{x_pos}+{y_pos}")
    popup.config(bg="red")

    photo_image = None
    try:
        if not os.path.exists(CUSTOM_POPUP_IMAGE_PATH):
            raise FileNotFoundError(f"Image file not found: {CUSTOM_POPUP_IMAGE_PATH}")

        from PIL import Image, ImageTk
        original_image = Image.open(CUSTOM_POPUP_IMAGE_PATH)
        img_width, img_height = original_image.size
        max_img_width = popup_width - 80
        max_img_height = popup_height - 150

        width_scale = max_img_width / img_width
        height_scale = max_img_height / img_height
        scale_factor = min(width_scale, height_scale)

        new_img_width = int(img_width * scale_factor)
        new_img_height = int(img_height * scale_factor)

        resized_image = original_image.resize((new_img_width, new_img_height), Image.LANCZOS)
        photo_image = ImageTk.PhotoImage(resized_image)

    except Exception as e:
        print(f"Error loading image: {e}")
        fallback_label = tk.Label(
            popup,
            text=message,
            font=tkFont.Font(family="Helvetica", size=40, weight="bold"),
            fg="white",
            bg="red",
            wraplength=popup_width - 40
        )
        fallback_label.pack(expand=True, pady=(popup_height * 0.1, popup_height * 0.05))

    if photo_image:
        image_label = tk.Label(popup, image=photo_image, bg="red")
        image_label.image = photo_image
        image_label.pack(expand=True, pady=(popup_height * 0.05, popup_height * 0.02))

    button_font = tkFont.Font(family="Helvetica", size=18, weight="bold")
    close_button = tk.Button(
        popup,
        text="OK, I'll Get Back To Work!",
        font=button_font,
        command=popup.destroy,
        bg="white",
        fg="red",
        activebackground="lightgray",
        activeforeground="red",
        bd=5,
        relief="raised"
    )
    close_button.pack(pady=20)

    popup.grab_set()
    popup.wait_window()

# --- Main Execution Block ---
if __name__ == "__main__":
    pass