from datetime import datetime

class TimeSkill:
    def __init__(self, engine):
        self.engine = engine

    def tell_time(self, text):
        now = datetime.now().strftime("%I:%M %p")
        self.engine.tts.speak(f"It's {now}")
