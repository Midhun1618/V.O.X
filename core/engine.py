from core.tts import TTS
from core.wakeword import WakeWord
from core.router import Router
from core.listener import Listener
from skills.web import WebSkill
from skills.system import SystemSkill
from skills.time import TimeSkill
from skills.weather import WeatherSkill

import os
import threading
import pygame

ACCESS_KEY = "l4YcMaXwFVLjkElTdruR5vz2fjZ3Vwd0CuGnfDR/lg0ifYd/iQzgmA=="

class VoxEngine:
    def __init__(self):
        keyword_path = os.path.join("assets", "vox.ppn")
        
        self.router = Router()
        self.web_skill = WebSkill(self)
        self.system_skill = SystemSkill(self)
        self.time_skill = TimeSkill(self)
        self.weather_skill = WeatherSkill(self)

        self.tts = TTS()
        self.listener = Listener()
        self.wakeword = WakeWord(
            access_key=ACCESS_KEY,
            keyword_path=keyword_path,
            on_detected=self.on_wake_word
        )
        pygame.mixer.init()
        self.wake_sound = pygame.mixer.Sound(
            os.path.join("assets", "waketone.wav")
        )
        self.ontrue = pygame.mixer.Sound(
            os.path.join("assets", "ontrue.wav")
        )
        self.onfalse = pygame.mixer.Sound(
            os.path.join("assets", "onfalse.wav")
        )

        web_intents = [
            ("OPEN_GMAIL",   ["mail", "gmail", "open mail"], self.web_skill.open_gmail),
            ("OPEN_YOUTUBE", ["youtube", "open youtube"], self.web_skill.open_youtube),
            ("OPEN_GITHUB",  ["github", "open github"], self.web_skill.open_github),
            ("OPEN_SPOTIFY", ["spotify", "open spotify"], self.web_skill.open_spotify),
            ("OPEN_GOOGLE",  ["google", "open google"], self.web_skill.open_google),
            ("OPEN_CHATGPT", ["chat gpt", "open chat gpt", "need assistance"], self.web_skill.open_chatgpt),

            ("SEARCH_GOOGLE", ["search"], self.web_skill.search_google),
            ("SEARCH_YOUTUBE", ["search youtube", "youtube search"], self.web_skill.search_youtube),
        ]

        system_intents = [
            ("OPEN_NOTEPAD", ["notepad", "open notepad"], self.system_skill.open_notepad),
            ("OPEN_SETTINGS", ["settings", "open settings"], self.system_skill.open_settings),
            ("OPEN_CONTROL_PANEL", ["control panel"], self.system_skill.open_control_panel),

            ("VOLUME_UP", ["volume up", "increase volume"], self.system_skill.volume_up),
            ("VOLUME_DOWN", ["volume down", "decrease volume"], self.system_skill.volume_down),
            ("FULL_VOLUME", ["full volume", "max volume", "maximum volume"], self.system_skill.full_volume),
            ("MUTE", ["mute"], self.system_skill.mute),

            ("SLEEP", ["sleep", "hide"], self.system_skill.sleep_system),
            ("EXIT", ["exit", "quit"], self.system_skill.exit_app),
        ]
        time_weather_intents = [
            ("TIME_NOW",["time","time right now"],self.time_skill.tell_time)
            ("WEATHER",["weather","weather today"],self.weather_skill.get_weather)
        ]

        for intent, keywords, handler in web_intents + system_intents + time_weather_intents:
            self.router.register(intent, keywords, handler)
    
    def start(self):
        self.wakeword.start()

    def on_wake_word(self):
        self.wake_sound.play()
        print("[Engine] Wake word received")
        
        if self.ui:
            self.ui.after(0, self.ui.show_listening)        
        self.listen_for_command()

    def listen_for_command(self):
        def run():
            text = self.listener.listen()
            print("[User]",text)
            if self.ui:
                self.ui.after(0, self.ui.show_idle)

            if not text:
                print("[Engine] No speech detected")
                self.onfalse.play()
                return

            handler,cleaned_text = self.router.route(text)
            if handler:
                handler(cleaned_text)
            else:
                self.tts.speak("I didn't catch that")

        threading.Thread(target=run, daemon=True).start()


    def speak(self, text):
        self.tts.speak(text)

    def startup(self):
        self.speak("Hi, I am Vox. Engine initialized successfully.")

    def attach_ui(self, ui):
        self.ui = ui
        
    def on_listening(self):
        if self.ui:
            self.ui.show_listening()

    def on_idle(self):
        if self.ui:
            self.ui.show_idle()
