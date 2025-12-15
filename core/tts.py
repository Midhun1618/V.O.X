import asyncio
import threading
import uuid
import os
import pygame
import edge_tts
import pyttsx3

class TTS:
    def __init__(self, voice="en-US-AriaNeural"):
        self.voice = voice

        if not pygame.mixer.get_init():
            pygame.mixer.init()

        self.fallback = pyttsx3.init()
        self.fallback.setProperty("rate", 175)
        self.fallback.setProperty("volume", 1.0)

    async def _generate(self, text, path):
        tts = edge_tts.Communicate(text, self.voice)
        await tts.save(path)

    def _fallback_speak(self, text):
        print("⚠ Using fallback TTS")
        self.fallback.say(text)
        self.fallback.runAndWait()

    def speak(self, text):
        if not text.strip():
            return

        file_path = f"tts_{uuid.uuid4().hex}.mp3"

        def run():
            success = False
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self._generate(text, file_path))
                loop.close()
            except:
                pass

            if os.path.exists(file_path) and os.path.getsize(file_path) > 200:
                success = True

            if success:
                try:
                    pygame.mixer.music.load(file_path)
                    pygame.mixer.music.play()
                except:
                    self._fallback_speak(text)
            else:
                self._fallback_speak(text)

        threading.Thread(target=run, daemon=True).start()
