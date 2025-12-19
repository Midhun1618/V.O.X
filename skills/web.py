import webbrowser
import urllib.parse

class WebSkill:
    def __init__(self, engine):
        self.engine = engine

    def open_gmail(self, text):
        webbrowser.open("https://mail.google.com/mail/u/0/#inbox")
        self.engine.tts.speak("Opening Gmail")

    def open_youtube(self, text):
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

    def search_google(self, text):
        query = text.replace("search", "").strip()

        if not query:
            self.engine.tts.speak("What would you like me to search for?")
            return

        url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
        webbrowser.open(url)
        self.engine.tts.speak(f"Searching for {query}")

    def search_youtube(self, text):
        query = text

        for suffix in ["search", "youtube", "on youtube", "in youtube"]:
            query = query.replace(suffix, "")

        query = query.strip()

        if not query:
            self.engine.tts.speak("What should I search on YouTube?")
            return

        url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
        webbrowser.open(url)
        self.engine.tts.speak(f"Searching {query} on YouTube")
