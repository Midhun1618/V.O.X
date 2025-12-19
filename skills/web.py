import webbrowser

class WebSkill:
    def __init__(self, engine):
        self.engine = engine

    def open_youtube(self, text):
        webbrowser.open("https://www.youtube.com")
        self.engine.tts.speak("Opening YouTube")

    def open_google(self, text):
        webbrowser.open("https://www.google.com")
        self.engine.tts.speak("Opening Google")
