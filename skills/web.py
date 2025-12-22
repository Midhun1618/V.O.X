import webbrowser
import urllib.parse

class WebSkill:
    def __init__(self, engine):
        self.engine = engine

    def open_gmail(self, text):
        webbrowser.open("https://mail.google.com/mail/u/0/#inbox")
        self.engine.tts.speak("Opening Gmail")

    def open_youtube(self, text):
        if "search" in text :
            query = text
            for w in ["search", "youtube", "on youtube", "in youtube"]:
                query = query.replace(w, "")
            query = query.strip()

            url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
            webbrowser.open(url)
        else:
            webbrowser.open("https://www.youtube.com")
        self.engine.tts.speak("Opening YouTube")

    def open_github(self, text):
        webbrowser.open("https://www.github.com")
        self.engine.tts.speak("Opening GitHub")

    def open_spotify(self, text):
        webbrowser.open("https://www.spotify.com")
        self.engine.tts.speak("Opening Spotify")

    def open_google(self, text):
        webbrowser.open("https://www.google.com")
        self.engine.tts.speak("Opening Google")

    def open_chatgpt(self, text):
        webbrowser.open("https://chatgpt.com")
        self.engine.tts.speak("Opening ChatGPT")

    def search_google(self, text):
        self.engine.tts.speak(f"Searching for")

    def search_youtube(self, text):
        self.engine.tts.speak(f"Searching on YouTube")
