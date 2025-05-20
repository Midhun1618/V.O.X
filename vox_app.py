import speech_recognition as sr
import pyttsx3

# Initialize the recognizer and TTS engine
recognizer = sr.Recognizer()
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen():
    with sr.Microphone() as source:
        print("🎤 Listening...")
        audio = recognizer.listen(source)

        try:
            command = recognizer.recognize_google(audio)
            print(f"🗣️ You said: {command}")
            return command
        except sr.UnknownValueError:
            speak("Sorry, I didn't catch that.")
            return ""
        except sr.RequestError:
            speak("Sorry, speech service is down.")
            return ""

# Main Loop
speak("Hello Midhun! I am Vox.")
while True:
    command = listen().lower()

    if "hello" in command:
        speak("Hi there! How can I help you?")
    elif "stop" in command or "exit" in command:
        speak("Goodbye!")
        break
    elif command:
        speak(f"You said {command}")
