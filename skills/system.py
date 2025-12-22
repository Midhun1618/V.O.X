import os
import subprocess
import ctypes
import time

class SystemSkill:
    def __init__(self, engine):
        self.engine = engine

    def open_notepad(self, text):
        subprocess.Popen("notepad.exe")
        self.engine.tts.speak("Opening Notepad")

    def open_settings(self, text):
        os.system("start ms-settings:")
        self.engine.tts.speak("Opening system settings")

    def open_control_panel(self, text):
        os.system("control")
        self.engine.tts.speak("Opening control panel")

    def sleep_system(self, text):
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

    def volume_up(self, text):
        for _ in range(10):
            ctypes.windll.user32.keybd_event(0xAF, 0, 0, 0)
            ctypes.windll.user32.keybd_event(0xAF, 0, 2, 0)

    def volume_down(self, text):
        for _ in range(10):
            ctypes.windll.user32.keybd_event(0xAE, 0, 0, 0)
            ctypes.windll.user32.keybd_event(0xAE, 0, 2, 0)

    def full_volume(self, text):
        for _ in range(100):
            ctypes.windll.user32.keybd_event(0xAF, 0, 0, 0)
            ctypes.windll.user32.keybd_event(0xAF, 0, 2, 0)
            time.sleep(0.01)

    def mute(self, text):
        ctypes.windll.user32.keybd_event(0xAD, 0, 0, 0)
        ctypes.windll.user32.keybd_event(0xAD, 0, 2, 0)

    def exit_app(self, text):
        self.engine.tts.speak("Goodbye Boss")
        os._exit(0)
