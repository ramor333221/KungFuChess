import tkinter as tk
from tkinter import messagebox
from config import constants

def show_gui_home_screen() -> tuple[str, str, str, str, str]:
    """Display the Tkinter room portal window using constants with automatic authentication."""
    root = tk.Tk()
    root.title("Chess Room Portal")
    root.geometry(f"{constants.PORTAL_WINDOW_WIDTH}x{constants.PORTAL_WINDOW_HEIGHT}")
    root.resizable(False, False)

    action = {
        "type": constants.ACTION_CANCEL,
        "username": "",
        "room_name": "",
        "room_password": "",
        "user_password": ""
    }

    tk.Label(
        root,
        text=constants.WELCOME_TITLE_TEXT,
        font=(constants.UI_FONT_FAMILY, constants.UI_TITLE_FONT_SIZE, "bold")
    ).pack(pady=constants.UI_TITLE_PADY)


    tk.Label(root, text="Username:").pack()
    user_entry = tk.Entry(root, width=constants.DEFAULT_ENTRY_WIDTH)
    user_entry.pack(pady=3)
    user_entry.insert(0, getattr(constants, "DEFAULT_USERNAME", ""))

    tk.Label(root, text="Password:").pack()
    pass_entry = tk.Entry(root, width=constants.DEFAULT_ENTRY_WIDTH, show="*")
    pass_entry.pack(pady=3)

    tk.Label(root, text="Room Name:").pack()
    room_entry = tk.Entry(root, width=constants.DEFAULT_ENTRY_WIDTH)
    room_entry.pack(pady=3)

    tk.Label(root, text="Room Password (Optional):").pack()
    room_pass_entry = tk.Entry(root, width=constants.DEFAULT_ENTRY_WIDTH, show="*")
    room_pass_entry.pack(pady=3)

    def validate_inputs() -> tuple[str, str, str, str] | None:
        username = user_entry.get().strip()
        user_password = pass_entry.get().strip()
        room_name = room_entry.get().strip()
        room_password = room_pass_entry.get().strip()

        if not username:
            messagebox.showwarning("Input Error", "Please enter a Username!")
            return None
        if not user_password:
            messagebox.showwarning("Input Error", "Please enter a Password!")
            return None
        if not room_name:
            messagebox.showwarning("Input Error", "Please enter a Room Name!")
            return None
        return username, user_password, room_name, room_password

    def on_create():
        inputs = validate_inputs()
        if inputs:
            action["type"] = constants.ACTION_CREATE
            action["username"], action["user_password"], action["room_name"], action["room_password"] = inputs
            root.destroy()

    def on_join():
        inputs = validate_inputs()
        if inputs:
            action["type"] = constants.ACTION_JOIN
            action["username"], action["user_password"], action["room_name"], action["room_password"] = inputs
            root.destroy()

    def on_cancel():
        action["type"] = constants.ACTION_CANCEL
        root.destroy()

    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=12)

    tk.Button(btn_frame, text="Create", width=constants.DEFAULT_BUTTON_WIDTH, command=on_create).grid(row=0, column=0, padx=4)
    tk.Button(btn_frame, text="Join", width=constants.DEFAULT_BUTTON_WIDTH, command=on_join).grid(row=0, column=1, padx=4)
    tk.Button(btn_frame, text="Cancel", width=constants.DEFAULT_BUTTON_WIDTH, command=on_cancel).grid(row=0, column=2, padx=4)

    root.mainloop()
    return action["type"], action["username"], action["room_name"], action["room_password"], action["user_password"]