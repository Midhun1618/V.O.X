from core.tts import TTS
from core.wakeword import WakeWord
from core.router import Router
from core.listener import Listener
from skills.web import WebSkill
import os
import threading
import pygame

ACCESS_KEY = "l4YcMaXwFVLjkElTdruR5vz2fjZ3Vwd0CuGnfDR/lg0ifYd/iQzgmA=="

class VoxEngine:
    def __init__(self):
        keyword_path = os.path.join("assets", "vox.ppn")
        
        self.router = Router()
        self.web_skill = WebSkill(self)

        self.router.register(
            intent="OPEN_YOUTUBE",
            keywords=["open youtube", "youtube"],
            handler=self.web_skill.open_youtube
        )
        
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
