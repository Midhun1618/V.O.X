import ctypes

class SystemSkill:
    def __init__(self, engine):
        self.engine = engine

    def volume_up(self, text):
        for _ in range(5):
            ctypes.windll.user32.keybd_event(0xAF, 0, 0, 0)
            ctypes.windll.user32.keybd_event(0xAF, 0, 2, 0)
        self.engine.tts.speak("Volume increased")

    def volume_down(self, text):
        for _ in range(5):
            ctypes.windll.user32.keybd_event(0xAE, 0, 0, 0)
            ctypes.windll.user32.keybd_event(0xAE, 0, 2, 0)
        self.engine.tts.speak("Volume decreased")

    def mute(self, text):
        ctypes.windll.user32.keybd_event(0xAD, 0, 0, 0)
        ctypes.windll.user32.keybd_event(0xAD, 0, 2, 0)
        self.engine.tts.speak("Muted")
