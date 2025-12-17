import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk
import sys

class VoxWidget(ctk.CTk):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine

        self._setup_window()
        self._setup_ui()
        self._bind_events()


    def _draw_icon(self, path):
        self.canvas.delete("all")

        img = Image.open(path).resize((40, 40), Image.Resampling.LANCZOS)
        self._icon_img = ImageTk.PhotoImage(img)

        self.canvas.create_image(
            32, 32,
            image=self._icon_img
        )

    def _setup_window(self):
        icon_path = ("assets/vox_icon.ico")
        self.iconbitmap(icon_path)

        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(bg="black")
        
        size = 50
        x = self.winfo_screenwidth() - size - 10
        y = self.winfo_screenheight() - size - 70
        self.geometry(f"{size}x{size}+{x}+{y}")

    def _setup_ui(self):
        self.frame = ctk.CTkFrame(self,corner_radius=10, fg_color="black")
        self.frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(
            self.frame,
            width=50,
            height=50,
            bg="black",
            highlightthickness=0,
        )
        self.canvas.pack()

        self.show_idle()

    def _bind_events(self):
        self.bind("<Button-1>", self._start_move)
        self.bind("<B1-Motion>", self._move)
        self.bind("<Button-3>", lambda e: sys.exit())

    def show_idle(self):
        self._draw_icon("assets/vox_icon_inactive.png")

    def show_listening(self):
        self._draw_icon("assets/vox_icon_active.png")

    def _start_move(self, event):
        self._x = event.x
        self._y = event.y

    def _move(self, event):
        x = self.winfo_pointerx() - self._x
        y = self.winfo_pointery() - self._y
        self.geometry(f"+{x}+{y}")
