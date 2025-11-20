import customtkinter as ctk
import speech_recognition as sr
import threading
import sys
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
import sounddevice as sd
import ctypes
import pyperclip
import pyautogui
import spacy
from dotenv import load_dotenv
import torch.nn as nn
import numpy as np
import asyncio
import edge_tts

class EdgeTTS:
    def __init__(self, voice="en-US-AriaNeural"):
        self.voice = voice

    async def _generate(self, text, output_path):
        tts = edge_tts.Communicate(text, self.voice)
        await tts.save(output_path)

    def speak(self, text):
        try:
            output_path = "output.mp3"
            asyncio.run(self._generate(text, output_path))
            pygame.mixer.music.load(output_path)
            pygame.mixer.music.play()
        except Exception as e:
            print("TTS Error:", e)


try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
sd.default.device = (1, None)

load_dotenv()
ACCESS_KEY = "l4YcMaXwFVLjkElTdruR5vz2fjZ3Vwd0CuGnfDR/lg0ifYd/iQzgmA=="
GCS_API_KEY = os.getenv("GCS_API_KEY")
GCS_CX = os.getenv("GCS_CX")

class VoxWidget(tk.Tk):
    def __init__(self):
        super().__init__()

        pygame.mixer.init()
        self.update_idletasks()

        self.iconbitmap("vox_icon.ico")
        self.title("VOX")

        self.nlp = spacy.load("en_core_web_sm")

        self.tts = EdgeTTS(voice="en-US-AriaNeural")

        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-transparentcolor", "black")
        self.configure(bg="black")
        self.attributes("-alpha", 1.0)

        self.bind("<Button-1>", self.start_move)
        self.bind("<B1-Motion>", self.move_window)

        window_size = 65
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = screen_width - window_size - 10
        y = screen_height - window_size - 70
        self.geometry(f"{window_size}x{window_size}+{x}+{y}")

        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="black")
        self.main_frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(self.main_frame, width=window_size, height=window_size, bg="black", highlightthickness=0)
        self.canvas.pack(pady=(8, 8))

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
        self.speak("Hi, i am vox, your own personal assistant")
        
    def speak(self, text):
        self.tts.speak(text)

    def clean_query(self, command):
        command = command.lower()

        fillers = [
            "transcript:", "transcript", 
            "what is", "who is", "define", 
            "explain", "tell me about", 
            "describe", "what are", "where is"
        ]

        for f in fillers:
            if f in command:
                command = command.replace(f, "")

        command = command.strip().replace("?", "").replace(".", "")
        print(command)
        
        return command.title()


    def wiki_search(self, query):
        url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + query.replace(" ", "_")
        print("url:", url)

        headers = {
            "User-Agent": "VoxAssistant/1.0 (https://github.com/Midhun1618)"
        }
        res = requests.get(url,headers=headers)
        print("status:", res.status_code)

        if res.status_code == 200:
            data = res.json()
            return data.get("extract")
        else:
            return None


    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def open_control_panel(self):
        os.system("control")

    def get_current_time(self):
        now = datetime.now()
        print(now)
        self.speak(now.strftime("It's %I:%M %p"))
    
    def greet_check(self):
        now = datetime.now()
        print(now)
        hour = int(now.strftime("%I"))
        m = now.strftime("%p")
        print(hour)
        print(m)
        if(m=="AM")and(hour<=11):
            return ("morning")
        if(m=="PM")and((hour<=4)or(hour==12)):
            return ("noon")
        if(m=="PM")and((hour>=5)and(hour<=8)):
            return ("evening")
        if(m=="PM")and((hour>8)and(hour<12)):
            return ("night")


    def get_weather(self):
        try:
            response = requests.get("https://wttr.in/Kochi?format=3")
            w_info = response.text
            temp = w_info[11:14]
            self.speak(f"It's around {temp} degree Celsius now.")  
        except Exception as e:
            print("Error:", e)

    def load_tasks(self):
        if os.path.exists("tasks.json"):
            with open("tasks.json", "r") as file:
                return json.load(file)
        return {"tasks": [], "reminders": []}

    def save_tasks(self, data):
        with open("tasks.json", "w") as file:
            json.dump(data, file, indent=4)


    def draw_glow_circle(self, active=False):
        self.canvas.delete("all")

        image_path = self.resource_path("assets/vox_icon_active.png") if active else self.resource_path("assets/vox_icon_inactive.png")
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
            keyword_path = self.resource_path("assets/vox.ppn")
            self.porcupine = pvporcupine.create(access_key=ACCESS_KEY, keyword_paths=[keyword_path])
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
                    waketone_path = self.resource_path("assets/waketone.wav")
                    pygame.mixer.music.load(waketone_path)
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
        try:
            with sr.Microphone() as source: 
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)

                text = self.recognizer.recognize_google(audio)
                self.after(0, self.update_transcript, text)
                command = text.lower()
                doc = self.nlp(command)

                QUESTION_WORDS = ["what", "who", "when", "where", "why", "how","tell me about"]

                if any(token.lemma_ == "open" for token in doc):
                    
                    if "notepad" in command:
                        subprocess.Popen("notepad.exe")
                        self.success_sfx()
                        self.speak("Opening Notepad")
                    elif "settings" in command:
                        os.system("start ms-settings:")
                        self.speak("Opening Windows system settings")
                    elif "control panel" in command:
                        self.open_control_panel()
                        self.success_sfx()
                        self.speak("Opening control panel")
                    elif "settings" in command:
                        os.system("start ms-settings:")
                        self.speak("Opening Windows system settings")
                        self.success_sfx()
                    elif "mail" in command:
                        webbrowser.open("https://mail.google.com/mail/u/0/#inbox")
                        self.success_sfx()
                        self.speak("Opening Gmail")
                    elif "youtube" in command:
                        webbrowser.open("https://www.youtube.com")
                        self.success_sfx()
                        self.speak("Opening YouTube")
                    elif "github" in command:
                        webbrowser.open("https://www.github.com")
                        self.success_sfx()
                        self.speak("Opening Github")
                    elif "spotify" in command:
                        webbrowser.open("https://www.spotify.com")
                        self.success_sfx()
                        self.speak("Opening spotify")
                    elif "google" in command:
                        webbrowser.open("https://www.google.com")
                        self.success_sfx()
                        self.speak("Opening Google")
                    else:
                        self.speak("What do you want to open.")
                elif "search" in command:
                    doc = self.nlp(command)
                    search_terms = []

                    for token in doc:
                        if token.dep_ in ["dobj", "pobj", "attr", "conj", "nsubj", "nmod"] or token.pos_ == "NOUN":
                            search_terms.append(token.text)

                    if not search_terms:
                        parts = command.split()
                        if "search" in parts:
                            pos = parts.index("search")
                            search_terms = parts[pos + 1:]

                    search_query = " ".join(search_terms).lower()

                    if "youtube" in command:
                        for suffix in ["in youtube", "on youtube", "youtube","search"]:
                            search_query = search_query.replace(suffix, "")
                        search_query = search_query.strip()

                        if search_query:
                            encoded_query = urllib.parse.quote(search_query)
                            url = f"https://www.youtube.com/results?search_query={encoded_query}"
                            webbrowser.open(url)
                            self.success_sfx()
                            self.speak(f"Searching {search_query} on YouTube")
                        else:
                            self.failure_sfx()
                            self.speak("I couldn't figure out what to search for on YouTube.")
                    else:
                        search_query = search_query.strip()
                        if not search_query:
                            search_query = command.replace("search", "").strip()

                        if search_query:
                            encoded_query = urllib.parse.quote(search_query)
                            url = f"https://www.google.com/search?q={encoded_query}"
                            webbrowser.open(url)
                            self.success_sfx()
                            self.speak(f"Searching for {search_query}")
                        else:
                            self.speak("What would you like me to search for?")
                elif "your creator" in command or "who are you" in command:
                    self.success_sfx()
                    self.speak("I'm Vox")
                    self.speak("A virtual assistant developed by Midhun")
                elif "buddy" in command or "what's up" in command:
                    self.success_sfx()
                    self.speak("How're you Boss? I am always here to assist you")
                elif "sleep" in command or "hide" in command:
                    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
                    self.success_sfx()
                    self.speak("Going to sleep mode")
                
                    self.success_sfx()
                elif "what's the weather" in command or "weather" in command:
                    self.get_weather()
                    self.success_sfx()
                elif "what's the time" in command or "current time" in command:
                    self.success_sfx()
                    self.get_current_time()
                    
                elif "good morning" in command:
                    time_current = self.greet_check()
                    if time_current=="morning":
                       self.success_sfx()
                       self.speak("hey Boss ,Good morning")
                        
                    else :
                        self.success_sfx()
                        self.speak(f"Sorry its not morning,its {time_current},So Good{time_current}")
                        
                elif "good afternoon" in command:
                    time_current = self.greet_check()
                    if time_current=="afternoon":
                       self.success_sfx()
                       self.speak("hey Boss ,Good afternoon")
                       
                    else :
                        self.success_sfx()
                        self.speak(f"Sorry its not afternoon,its {time_current},So Good{time_current}")
                        
                elif "good evening" in command:
                    time_current = self.greet_check()
                    if time_current=="evening":
                       self.success_sfx()
                       self.speak("hey Boss ,Good evening")
                       
                    else :
                        self.success_sfx()
                        self.speak(f"Sorry its not evening,its {time_current},So Good{time_current}")
                        
                elif "good night" in command:
                    time_current = self.greet_check()
                    if time_current=="night":
                       self.success_sfx()
                       self.speak("hey Boss ,Good night")
                       
                    else :
                        self.success_sfx()
                        self.speak(f"Sorry its not night,its {time_current},So Good{time_current}")
                        
                elif "paste previous" in command :
                    pyautogui.hotkey("ctrl","v")
                    self.success_sfx()
                        
                elif "paste" in command:
                    copy_content = command.replace("paste", "").strip()
                    pyperclip.copy(copy_content)
                    def perform_paste():
                        try:
                            pyautogui.hotkey('ctrl', 'v')
                             
                            self.after(0, self.success_sfx)
                        except Exception as e:
                            print("Paste error:", e)
                            self.after(0, self.failure_sfx)
                    threading.Thread(target=perform_paste, daemon=True).start()

                elif "reload" in command:
                    pyautogui.hotkey("ctrl","r")
                    self.success_sfx()
                elif ("copy all" or "select all and copy") in command:
                    pyautogui.hotkey("ctrl","a")
                    pyautogui.hotkey("ctrl","c")
                    self.success_sfx()
                elif "save"in command:
                    pyautogui.hotkey('ctrl', 's')
                    self.success_sfx()
                    self.speak("Saved")
                    
                elif "exit" in command or "quit" in command:
                    self.speak("Goodbye Boss!")
                    sys.exit()
                elif any(word in command.lower() for word in QUESTION_WORDS):
                    for ent in doc.ents:
                        if ent.label_ == "GPE": 
                            location = ent.text
                    query = self.clean_query(command)
                    summary = self.wiki_search(query)
                    if summary is not None:
                        self.success_sfx()
                        sentences = summary.split(". ")
                        for sentence in sentences:
                            self.speak(sentence)
                    else:
                        self.speak("I could not find any information on that.")
                    
                elif "need assistance" in command or "open chat gpt" in command:
                    webbrowser.open("https://chatgpt.com")
                    self.success_sfx()
                    self.speak("Opening chat GPT for assistance.")
                elif "mute" in command:
                    VK_VOLUME_MUTE = 0xAD
                    ctypes.windll.user32.keybd_event(VK_VOLUME_MUTE, 0, 0, 0)
                    ctypes.windll.user32.keybd_event(VK_VOLUME_MUTE, 0, 2, 0) 
                    self.success_sfx()
                elif "full volume" in command or ("maximum volume" or "max volume") in command:
                    VK_VOLUME_UP = 0xAF 
                    for _ in range(100): 
                        ctypes.windll.user32.keybd_event(VK_VOLUME_UP, 0, 0, 0)
                        ctypes.windll.user32.keybd_event(VK_VOLUME_UP, 0, 2, 0)
                        time.sleep(0.01)
                    self.success_sfx()
                elif "increase volume" in command or "volume up" in command:
                    VK_VOLUME_UP = 0xAF 
                    for _ in range(10): 
                        ctypes.windll.user32.keybd_event(VK_VOLUME_UP, 0, 0, 0)
                        ctypes.windll.user32.keybd_event(VK_VOLUME_UP, 0, 2, 0)
                        time.sleep(0.01)
                    self.success_sfx()
                elif ("volume" in command) and ("decrease" in command or "down" in command):
                    VK_VOLUME_DOWN = 0xAE 
                    for _ in range(10): 
                        ctypes.windll.user32.keybd_event(VK_VOLUME_DOWN, 0, 0, 0)
                        ctypes.windll.user32.keybd_event(VK_VOLUME_DOWN, 0, 2, 0)
                        time.sleep(0.1)
                    self.success_sfx()
                elif "activate coding mode" in command:
                    webbrowser.open("https://youtu.be/LVbUNRwpXzw?si=dp_7ajWR_qgWqf3S")
                    webbrowser.open("https://www.github.com/")
                    webbrowser.open("https://chatgpt.com")
                    pyautogui.hotkey("win")
                    pyperclip.copy("visual studio code")
                    pyautogui.hotkey("ctrl","v")
                    pyautogui.press('enter')
                    self.success_sfx()
                    self.speak("Activating programming mode, initializing chat GPT,Git hub and Youtube")

                elif "add task" in command:
                    task_text = command.replace("add task", "").strip()
                    data = self.load_tasks()
                    data["tasks"].append(task_text)
                    self.save_tasks(data)
                    self.speak(f"Task added: {task_text}")
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
                        
                        self.speak(f"Marking task '{task_keyword}' as done.")
                        self.success_sfx()
                    else:
                        self.speak(f"Can't find '{task_keyword}' in tasks")
                        self.failure_sfx()

                elif "read my task" in command or "read my tasks" in command:
                    data = self.load_tasks()
                    tasks = data.get("tasks", [])
                    if tasks:
                        self.speak("Here are your tasks:")
                        for task in tasks:
                             self.speak(task)
                    else:
                         self.speak("You don't have any tasks right now.")
                elif "help me" in command or "can you help" in command:
                    self.speak("Ofcourse, how can i help you?")
                    self.listening_for_command = True
                    self.after(0, self.update_transcript, "Help: Listening for command")
                    self.glow_listen(True)
                    self.listen_for_command()
                    self.listening_for_command = False
                    self.after(0, self.update_transcript, "Waiting for wake word 'VOX'...")
                    self.glow_listen(False)

                else:
                    no_response_phrases = [
                        "Sorry, I didn't catch that.",
                        "Can you say that again?",
                        "Didn't get that clearly, could you repeat?",
                        "Please repeat that.",
                        "Hmm, not sure what you meant."
                    ]
                    self.speak(random.choice(no_response_phrases))

        except sr.WaitTimeoutError:
            self.after(0, self.update_transcript, "Listening timed out, try again.")
            self.failure_sfx()
        except sr.UnknownValueError:
            self.after(0, self.update_transcript, "Sorry, I did not understand that.")
            self.failure_sfx()
        except sr.RequestError as e:
            self.after(0, self.update_transcript, f"Could not request results; {e}")
            self.failure_sfx()
        except Exception as e:
            print(f"Unexpected error while listening: {e}")

    def success_sfx(self):
        try:
            sfx_path = self.resource_path("assets/ontrue.wav")
            pygame.mixer.music.load(sfx_path)
            pygame.mixer.music.play()
        except Exception as e:
            print("Error playing sound effects:", e)
    def failure_sfx(self):
        try:
            sfx_path = self.resource_path("assets/onfalse.wav")
            pygame.mixer.music.load(sfx_path)
            pygame.mixer.music.play()
        except Exception as e:
            print("Error playing sound effects:", e)

    def update_transcript(self, text):
        print("Transcript:", text)

if __name__ == "__main__":
    app = VoxWidget()
    app.mainloop()