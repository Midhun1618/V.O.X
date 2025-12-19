from skills.web import WebSkill 

class Router:
    def __init__(self):
        self.intents = []

    def register(self, intent, keywords, handler):

        self.intents.append({
            "intent": intent,
            "keywords": keywords,
            "handler": handler
        })

    def route(self, text):
        text = text.lower()

        for item in self.intents:
            if any(keyword in text for keyword in item["keywords"]):
                return item["handler"], text

        return None, text
