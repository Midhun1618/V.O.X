import speech_recognition as sr

class Listener:
    def __init__(self, device_index=None):
        self.recognizer = sr.Recognizer()
        self.device_index = device_index

    def listen(self, timeout=5, phrase_time_limit=5):
        try:
            with sr.Microphone(device_index=self.device_index) as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )

            text = self.recognizer.recognize_google(audio)
            return text

        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            print("[Listener] API error:", e)
            return None
