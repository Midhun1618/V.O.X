import customtkinter as ctk
import speech_recognition as sr
import threading
import sys
import time
import pyttsx3

# Initialize customtkinter appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class VoxWidget(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.wm_attributes("-alpha", 0.7)  # 70% opacity

        self.overrideredirect(True)
        self.wm_attributes("-topmost", True)
        self.tts_engine = pyttsx3.init()

        # Bind mouse events for dragging the window
        self.bind("<Button-1>", self.start_move)
        self.bind("<B1-Motion>", self.move_window)

        self.geometry("80x90")
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = 80
        window_height = 90
        x = screen_width - window_width - 10
        y = (screen_height // 2) - (window_height // 2)
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.pack(fill="both", expand=True)

        # Add canvas for drawing the glow
        self.canvas = ctk.CTkCanvas(self.main_frame, width=60, height=60, bg="#2C2C2C", highlightthickness=0)
        self.canvas.pack(pady=(10, 5))

        self.draw_glow_circle()  # draw the glowing effect

        self.transcript_label = ctk.CTkLabel(self.main_frame, text="Listening", font=ctk.CTkFont(size=14, weight="bold"))
        self.transcript_label.pack(pady=(5, 0))

        self.bind("<Button-3>", lambda e: sys.exit())

        # Speech recognizer setup
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        # Animation state
        self.pulse_active = False
        self.pulse_direction = 1
        self.pulse_size = 5

        # Start listening thread
        self.listening = False
        self.listen_thread = threading.Thread(target=self.background_listen, daemon=True)
        self.listen_thread.start()

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def move_window(self, event):
        x = self.winfo_pointerx() - self.x
        y = self.winfo_pointery() - self.y
        self.geometry(f"+{x}+{y}")

    def draw_glow_circle(self):
        self.canvas.delete("all")  # Clear previous

        # Fake blur by drawing multiple ovals with increasing transparency
        glow_colors = [
            "#E7E875",  # Lighter yellow
            "#F0F150",
            "#F6F830",
            "#F9FF8E",  # Brightest
        ]

        radii = [30, 25, 20, 15]

        for radius, color in zip(radii, glow_colors):
            self.canvas.create_oval(
                30 - radius,
                30 - radius,
                30 + radius,
                30 + radius,
                fill=color,
                outline=""
            )

        # Actual center circle
        self.glow_circle = self.canvas.create_oval(
            5, 5, 55, 55, fill="#F9FF8E", outline=""
        )

    def glow_listen(self, active=True):
        color = "#F9FF8E" if active else "#CFCFCF"
        for i in range(3):  # Pulse 3 times
            self.canvas.itemconfig(self.glow_circle, fill=color)
            self.update_idletasks()
            time.sleep(0.4)
            self.canvas.itemconfig(self.glow_circle, fill="#F8FF33")
            self.update_idletasks()
            time.sleep(0.4)

    def pulse_glow(self):
        if not self.pulse_active:
            return

        self.pulse_size += self.pulse_direction

        if self.pulse_size >= 8 or self.pulse_size <= 5:
            self.pulse_direction *= -1

        self.canvas.delete(self.glow_circle)
        self.glow_circle = self.canvas.create_oval(
            self.pulse_size,
            self.pulse_size,
            60 - self.pulse_size,
            60 - self.pulse_size,
            fill="#F9FF8E"
        )

        self.after(50, self.pulse_glow)

    def background_listen(self):
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            self.recognizer.energy_threshold = 800  # You can tweak this

            while True:
                try:
                    print("[VOX] Listening...")
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)

                    try:
                        text = self.recognizer.recognize_google(audio)
                        self.after(0, self.update_transcript, text)
                        self.glow_listen(True)
                        time.sleep(0.3)
                        self.glow_listen(False)

                    except sr.UnknownValueError:
                        self.after(0, self.update_transcript, "Could not understand audio")
                        self.glow_listen(False)

                    except sr.RequestError:
                        self.after(0, self.update_transcript, "API Error")
                        self.glow_listen(False)

                except sr.WaitTimeoutError:
                    self.glow_listen(False)

    def update_transcript(self, text):
        if text!="Could not understand audio" and text!="API Error":
            self.tts_engine.say(f"{text}")
            print(f"{text}")
            self.tts_engine.runAndWait()
        else:
            print(f"{text}")

        


if __name__ == "__main__":
    app = VoxWidget()
    app.mainloop()
