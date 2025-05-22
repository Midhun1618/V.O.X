import customtkinter as ctk
import speech_recognition as sr
import threading
import sys
import time
import pyttsx3
import pvporcupine
import pyaudio
import struct
import os

# Initialize customtkinter appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

ACCESS_KEY = "l4YcMaXwFVLjkElTdruR5vz2fjZ3Vwd0CuGnfDR/lg0ifYd/iQzgmA=="  # Replace this with your actual Porcupine access key
KEYWORD_PATH = os.path.join("assets", "vox.ppn")  # Your wake word model path

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

        self.canvas = ctk.CTkCanvas(self.main_frame, width=60, height=60, bg="#2C2C2C", highlightthickness=0)
        self.canvas.pack(pady=(10, 5))
        self.draw_glow_circle()

        self.transcript_label = ctk.CTkLabel(self.main_frame, text="Waiting for wake word 'VOX'...", font=ctk.CTkFont(size=14, weight="bold"))
        self.transcript_label.pack(pady=(5, 0))

        self.bind("<Button-3>", lambda e: sys.exit())

        # Speech recognizer setup
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        # Porcupine wake word stuff
        self.porcupine = None
        self.pa = None
        self.stream = None
        self.porcupine_thread = threading.Thread(target=self.wake_word_listener, daemon=True)
        self.listening_for_command = False  # Flag to manage state

        # Start wake word detection thread
        self.porcupine_thread.start()

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def move_window(self, event):
        x = self.winfo_pointerx() - self.x
        y = self.winfo_pointery() - self.y
        self.geometry(f"+{x}+{y}")

    def draw_glow_circle(self):
        self.canvas.delete("all")
        glow_colors = ["#E7E875", "#F0F150", "#F6F830", "#F9FF8E"]
        radii = [30, 25, 20, 15]
        for radius, color in zip(radii, glow_colors):
            self.canvas.create_oval(30 - radius, 30 - radius, 30 + radius, 30 + radius, fill=color, outline="")
        self.glow_circle = self.canvas.create_oval(5, 5, 55, 55, fill="#F9FF8E", outline="")

    def glow_listen(self, active=True):
        color = "#F9FF8E" if active else "#CFCFCF"
        for _ in range(3):
            self.canvas.itemconfig(self.glow_circle, fill=color)
            self.update_idletasks()
            time.sleep(0.4)
            self.canvas.itemconfig(self.glow_circle, fill="#F8FF33")
            self.update_idletasks()
            time.sleep(0.4)

    def wake_word_listener(self):
        try:
            self.porcupine = pvporcupine.create(access_key=ACCESS_KEY, keyword_paths=[KEYWORD_PATH])
            self.pa = pyaudio.PyAudio()
            self.stream = self.pa.open(
                rate=self.porcupine.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=self.porcupine.frame_length
            )

            while True:
                pcm = self.stream.read(self.porcupine.frame_length, exception_on_overflow=False)
                pcm_unpacked = struct.unpack_from("h" * self.porcupine.frame_length, pcm)
                result = self.porcupine.process(pcm_unpacked)
                if result >= 0 and not self.listening_for_command:
                    # Wake word detected
                    self.listening_for_command = True
                    self.after(0, self.update_transcript, "Wake word detected! Listening for command...")
                    self.glow_listen(True)
                    self.listen_for_command()  # blocking call but okay in thread
                    self.listening_for_command = False
                    self.after(0, self.update_transcript, "Waiting for wake word 'VOX'...")
        except Exception as e:
            print(f"Wake word error: {e}")

    def listen_for_command(self):
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                text = self.recognizer.recognize_google(audio)
                self.after(0, self.update_transcript, text)
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except sr.UnknownValueError:
                self.after(0, self.update_transcript, "Could not understand audio")
            except sr.RequestError:
                self.after(0, self.update_transcript, "API Error")
            except sr.WaitTimeoutError:
                self.after(0, self.update_transcript, "Listening timed out")

    def update_transcript(self, text):
        print(text)
        self.transcript_label.configure(text=text)

if __name__ == "__main__":
    app = VoxWidget()
    app.mainloop()
