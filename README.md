<h1>VOX – Desktop Voice Assistant</h1>
VOX is a Python-based desktop voice assistant that enables hands-free system interaction using a custom wake word. It supports real-time voice commands, system automation, and natural voice responses through a lightweight floating widget interface.

Features
Wake-word detection using Picovoice Porcupine (“Hey Vox”)
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

<b>Tech Stack</b>
Language: Python
UI: CustomTkinter, Tkinter
Wake Word: Picovoice Porcupine
Speech Recognition: SpeechRecognition
Text-to-Speech: Edge TTS, pyttsx3
Audio: PyAudio, Pygame
Automation: PyAutoGUI, ctypes
Storage: JSON

Installation
git clone https://github.com/Midhun1618/VOX.git
cd VOX
pip install -r requirements.txt


Note: PyAudio may require a pre-built wheel on Windows.

Run
python main.py

Example Commands :
“Hey Vox, open YouTube”
“Hey Vox, search Python multithreading”
“Hey Vox, add task buy groceries”
“Hey Vox, read my tasks”
“Hey Vox, mute volume”

Project Structure
VOX/
├── assets/
├── main.py
├── tasks.json
└── README.md

Author:
Midhun KP
GitHub: https://github.com/Midhun1618
LinkedIn: https://www.linkedin.com/in/midhun-kp
