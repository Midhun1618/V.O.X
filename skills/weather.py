import requests

class WeatherSkill:
    def __init__(self, engine):
        self.engine = engine

    def get_weather(self, text):
        try:
            response = requests.get("https://wttr.in/?format=3", timeout=5)
            self.engine.tts.speak(response.text)
        except Exception:
            self.engine.tts.speak("Sorry, I couldn't get the weather right now")
