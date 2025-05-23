import customtkinter as ctk
import speech_recognition as sr
import threading
import sys
import pyttsx3
import pvporcupine
import pyaudio
import struct
import os
import pygame
import webbrowser
import urllib.parse
import subprocess
import random
import tkinter as tk
from PIL import Image, ImageTk
import json
import datetime
import time
import requests
from datetime import datetime


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


ACCESS_KEY = "l4YcMaXwFVLjkElTdruR5vz2fjZ3Vwd0CuGnfDR/lg0ifYd/iQzgmA=="
KEYWORD_PATH = os.path.join("assets", "vox.ppn")

class VoxWidget(tk.Tk):
    def __init__(self):
        super().__init__()

        pygame.mixer.init()
        self.update_idletasks()



        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-transparentcolor", "white")
        self.configure(bg="white")
        self.attributes("-alpha", 0.7)



        self.tts_engine = pyttsx3.init()

        self.bind("<Button-1>", self.start_move)
        self.bind("<B1-Motion>", self.move_window)


        window_size = 65
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = screen_width - window_size - 10
        y = screen_height - window_size - 70
        self.geometry(f"{window_size}x{window_size}+{x}+{y}")

        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(self.main_frame, width=window_size, height=window_size,bg="#1E1E1E", highlightthickness=0)
        self.canvas.pack(pady=(8, 8))

        self.draw_rounded_background()
        self.draw_glow_circle(active=False)

        self.bind("<Button-3>", lambda e: sys.exit())

        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        self.porcupine = None
        self.pa = None
        self.stream = None
        self.listening_for_command = False

        self.porcupine_thread = threading.Thread(target=self.wake_word_listener, daemon=True)
        self.porcupine_thread.start()

    def open_control_panel(self):
        os.system("control")

    def get_current_time(self):
        now = datetime.now()
        return now.strftime("It's %I:%M %p")
    
    def get_weather(self): 
        try:
            response = requests.get("https://wttr.in/Kochi?format=3")
            w_info=response.text
            print(w_info[11:13] )
            self.tts_engine.say(f"its around {w_info[11:13]} degree celcius now.")
        except Exception as e:
            print("Error:", e)
    def load_tasks(self):
        if os.path.exists("tasks.json"):
            with open("tasks.json", "r") as file:
                return json.load(file)
        return {"tasks": [], "reminders": []}

    def save_tasks(self,data):
        with open("tasks.json", "w") as file:
            json.dump(data, file, indent=4)


    def draw_rounded_background(self):
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        radius = 25
        bg_color = "#1E1E1E"

        self.canvas.create_rectangle(0, 0, width, height, fill=bg_color, outline=bg_color)

        self.canvas.create_oval(0, 0, radius*2, radius*2, fill=bg_color, outline=bg_color)
        self.canvas.create_oval(width-radius*2, 0, width, radius*2, fill=bg_color, outline=bg_color)
        self.canvas.create_oval(0, height-radius*2, radius*2, height, fill=bg_color, outline=bg_color)
        self.canvas.create_oval(width-radius*2, height-radius*2, width, height, fill=bg_color, outline=bg_color)

        # Optional: draw center rect to complete the middle part
        self.canvas.create_rectangle(radius, 0, width - radius, height, fill=bg_color, outline=bg_color)
        self.canvas.create_rectangle(0, radius, width, height - radius, fill=bg_color, outline=bg_color)

    def draw_glow_circle(self, active=False):
        self.canvas.delete("all")
        self.draw_rounded_background()
        
        image_path = "assets/vox_icon_inactive.png" if not active else "assets/vox_icon_active.png"
        image = Image.open(image_path)
        image = image.resize((60, 60), Image.Resampling.LANCZOS)
        self.icon_image = ImageTk.PhotoImage(image)


        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if canvas_width <= 1 or canvas_height <= 1:
            canvas_width = 65
            canvas_height = 65

        self.canvas.create_image(
            canvas_width // 2,
            canvas_height // 2,
            image=self.icon_image
        )


    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def move_window(self, event):
        x = self.winfo_pointerx() - self.x
        y = self.winfo_pointery() - self.y
        self.geometry(f"+{x}+{y}")

    def glow_listen(self, active=True):
        self.draw_glow_circle(active)
        self.update_idletasks()

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
                    pygame.mixer.music.load("waketone.wav")
                    pygame.mixer.music.play()
                    self.listening_for_command = True
                    self.after(0, self.update_transcript, "Wake word detected! Listening for command...")
                    self.glow_listen(True)
                    self.listen_for_command()
                    self.listening_for_command = False
                    self.after(0, self.update_transcript, "Waiting for wake word 'VOX'...")
                    self.glow_listen(False)
        except Exception as e:
            print(f"Wake word error: {e}")

    def listen_for_command(self):
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                text = self.recognizer.recognize_google(audio)
                self.after(0, self.update_transcript, text)
                command = text.lower()
                search_context = ""


                if "open notepad" in command:
                    subprocess.Popen("notepad.exe")
                    self.success_sfx()
                    self.tts_engine.say("opening notepad")
                elif "open control panel" in command or "control panel" in command:
                    self.open_control_panel()
                    self.success_sfx()
                    self.tts_engine.say("opening control panel")
                elif "your creator" in command or "who are you" in command:
                    self.success_sfx()
                    self.tts_engine.say("I'm Vox")
                    self.tts_engine.say("A virtual assistant developed by mithun")
                elif "buddy" in command or "what's up" in command:
                    self.success_sfx()
                    self.tts_engine.say("How're you Boss? I am is alway here to assist you")
                elif "sleep" in command or "hide" in command:
                    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
                    self.success_sfx()
                    self.tts_engine.say("opening control panel")
                elif "open settings" in command:
                    os.system("start ms-settings:")
                    self.tts_engine.say("Opening Windows system settings")
                    self.success_sfx()
                elif "what's the weather" in command or "weather" in command:
                    weather_report = self.get_weather() 
                    self.tts_engine.say(weather_report)
                    self.success_sfx()

                elif "what's the time" in command or "current time" in command:
                    time_now = self.get_current_time()
                    self.tts_engine.say(time_now)
                    self.success_sfx()

                elif "open youtube" in command and "search" in command:
                    parts = command.split()
                    if "search" in parts:
                        pos = parts.index("search")
                        search_context = " ".join(parts[pos + 1:])
                        encoded_query = urllib.parse.quote(search_context)
                        url = f"https://www.youtube.com/results?search_query={encoded_query}"
                        webbrowser.open(url)
                        self.success_sfx()
                        self.tts_engine.say(f"Searching {search_context} in Youtube")
                    else:
                        webbrowser.open("https://youtu.be/")
                        self.success_sfx()
                elif "open youtube" in command:
                    webbrowser.open("https://youtu.be/")
                    self.success_sfx()
                    self.tts_engine.say("Opening Youtube")
                elif "blush mode" in command:
                    rom = [
                        'https://youtu.be/4q5o3Tiwcmc?si=PKMgk9gBWgZ1YV3-',
                        'https://youtu.be/2NrpwkyoTrI?si=44LmN2OoKUJpNZx_',
                        'https://youtu.be/LRHSq0tTLB0?si=4DeYQfS_29sU-Un6',
                        'https://youtu.be/SS4QdqgvFl0?si=PBB0DeCfyb6KgUQT'
                    ]
                    webbrowser.open(random.choice(rom))
                    self.success_sfx()
                elif "open spotify" in command:
                    webbrowser.open("https://open.spotify.com/")
                    self.success_sfx()
                    self.tts_engine.say("Starting Spotify")
                elif "open mail" in command:
                    webbrowser.open("https://mail.google.com/mail/u/0/#inbox")
                    self.success_sfx()
                    self.tts_engine.say("Opening gmail right now")
                elif "need assistance" in command:
                    webbrowser.open("https://chatgpt.com")
                    self.success_sfx()
                    self.tts_engine.say("Opening chat GPT for assistance.")
                elif "activate coding mode" in command:
                    webbrowser.open("https://youtu.be/LVbUNRwpXzw?si=dp_7ajWR_qgWqf3S")
                    webbrowser.open("https://www.github.com/")
                    webbrowser.open("https://chatgpt.com")
                    self.success_sfx()
                    self.tts_engine.say("Activating programming mode, initializing chat GPT,Git hub and Youtube")

                elif "add task" in command:
                    task_text = command.replace("add task", "").strip()
                    data = self.load_tasks()
                    data["tasks"].append(task_text)
                    self.save_tasks(data)
                    self.tts_engine.say(f"Task added: {task_text}")
                    self.tts_engine.runAndWait()
                    self.success_sfx()
                elif "task is done" in command:
                    data = self.load_tasks()
                    tasks = data.get("tasks", [])
                    
                    task_keyword = command.split("task is done")[0].strip()
                    print(f"Task keyword detected: {task_keyword}")
                    
                    if task_keyword in tasks:
                        tasks.remove(task_keyword)
                        data["tasks"] = tasks
                        
                        self.save_tasks(data)
                        
                        self.tts_engine.say(f"Marking task '{task_keyword}' as done.")
                        self.success_sfx()
                    else:
                        self.tts_engine.say(f"Can't find '{task_keyword}' in tasks")
                        self.failure_sfx()

                elif "read my task" in command or "read my tasks" in command:
                    data = self.load_tasks()
                    tasks = data.get("tasks", [])
                    if tasks:
                        self.tts_engine.say("Here are your tasks:")
                        for task in tasks:
                             self.tts_engine.say(task)
                    else:
                         self.tts_engine.say("You don't have any tasks right now.")

                else:
                    print("Command not recognized!")
                    self.failure_sfx()

        
                self.tts_engine.runAndWait()

            except sr.UnknownValueError:
                self.after(0, self.update_transcript, "Could not understand audio")
                self.failure_sfx()
            except sr.RequestError:
                self.after(0, self.update_transcript, "API Error")
                self.failure_sfx()
            except sr.WaitTimeoutError:
                self.after(0, self.update_transcript, "Listening timed out")
                self.failure_sfx()

    def success_sfx(self):
        pygame.mixer.music.load("ontrue.wav")
        pygame.mixer.music.play()

    def failure_sfx(self):
        pygame.mixer.music.load("onfalse.wav")
        pygame.mixer.music.play()

    def alert_sfx(self):
        pygame.mixer.music.load("onalert.wav")
        pygame.mixer.music.play()

    def update_transcript(self, text):
        print(text)


if __name__ == "__main__":
    app = VoxWidget()
    app.mainloop()
