from core.tts import TTS
from core.wakeword import WakeWord
from core.listener import Listener
import os
import threading
import pygame

ACCESS_KEY = "l4YcMaXwFVLjkElTdruR5vz2fjZ3Vwd0CuGnfDR/lg0ifYd/iQzgmA=="

class VoxEngine:
    def __init__(self):
        keyword_path = os.path.join("assets", "vox.ppn")

        self.tts = TTS()
        self.listener = Listener()
        self.wakeword = WakeWord(
            access_key=ACCESS_KEY,
            keyword_path=keyword_path,
            on_detected=self.on_wake_word
        )
    
    def start(self):
        self.wakeword.start()

    def on_wake_word(self):
        print("[Engine] Wake word received")

        pygame.mixer.init()
        self.wake_sound = pygame.mixer.Sound(
            os.path.join("assets", "waketone.wav")
        )
        self.wake_sound.play()

        if self.ui:
            self.ui.after(0, self.ui.show_listening)        

        self.listen_for_command()

    def listen_for_command(self):
        def run():
            text = self.listener.listen()

            if self.ui:
                self.ui.after(0, self.ui.show_idle)

            if text:
                print("[User said]:", text)
                self.tts.speak(f"You said {text}")
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
