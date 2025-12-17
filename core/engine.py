from core.tts import TTS
from core.wakeword import WakeWord
import os

ACCESS_KEY = "l4YcMaXwFVLjkElTdruR5vz2fjZ3Vwd0CuGnfDR/lg0ifYd/iQzgmA=="

class VoxEngine:
    def __init__(self):
        self.tts = TTS()

        keyword_path = os.path.join("assets", "vox.ppn")

        self.wakeword = WakeWord(
            access_key=ACCESS_KEY,
            keyword_path=keyword_path,
            on_detected=self.on_wake_word
        )
    
    def start(self):
        self.wakeword.start()

    def on_wake_word(self):
        print("[Engine] Wake word received")

        if self.ui:
            self.ui.after(0, self.ui.show_listening)

        self.tts.speak("Yes?")

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
