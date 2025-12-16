<h1>VOX – Desktop Voice Assistant</h1>
VOX is a Python-based desktop voice assistant that enables hands-free system interaction using a custom wake word. It supports real-time voice commands, system automation, and natural voice responses through a lightweight floating widget interface.

<h2>Features</h2>
Wake-word detection using Picovoice Porcupine (“Hey Vox”)\n
Real-time speech recognition
Hybrid text-to-speech
Online: Edge TTS
Offline fallback: pyttsx3
Floating, draggable widget UI using CustomTkinter
System automation
Open apps and system settings
Volume control, mute, sleep mode
Clipboard actions (copy, paste, save, reload)
Voice-based Google and YouTube search
Task management via voice commands (JSON storage)
Contextual responses (time, weather, greetings)
Audio feedback for command success/failure
Multithreaded and async execution for smooth performance

<h2>Tech Stack</h2>
Language: Python
UI: CustomTkinter, Tkinter
Wake Word: Picovoice Porcupine
Speech Recognition: SpeechRecognition
Text-to-Speech: Edge TTS, pyttsx3
Audio: PyAudio, Pygame
Automation: PyAutoGUI, ctypes
Storage: JSON

<h2>Installation</h2>
git clone https://github.com/Midhun1618/VOX.git
cd VOX
pip install -r requirements.txt


Note: PyAudio may require a pre-built wheel on Windows.

Run
python main.py

<h2>Example Commands :</h2>
“Hey Vox, open YouTube”
“Hey Vox, search Python multithreading”
“Hey Vox, add task buy groceries”
“Hey Vox, read my tasks”
“Hey Vox, mute volume”

<h2>Project Structure</h2>
VOX/
├── assets/
├── main.py
├── tasks.json
└── README.md

Author:
Midhun KP
GitHub: https://github.com/Midhun1618
LinkedIn: https://www.linkedin.com/in/midhun-kp
