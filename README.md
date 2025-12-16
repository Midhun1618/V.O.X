<h1>VOX – Desktop Voice Assistant</h1>

<p>
VOX is a Python-based desktop voice assistant that enables hands-free system interaction using a custom wake word.
It supports real-time voice commands, system automation, and natural voice responses through a lightweight
floating widget interface.
</p>

<h2>Features</h2>
<ul>
  <li>Wake-word detection using Picovoice Porcupine (“Hey Vox”)</li>
  <li>Real-time speech recognition</li>
  <li>Hybrid text-to-speech (Edge TTS with pyttsx3 offline fallback)</li>
  <li>Floating, draggable widget UI using CustomTkinter</li>
  <li>System automation (open apps, system settings, volume control, sleep mode)</li>
  <li>Clipboard actions (copy, paste, save, reload)</li>
  <li>Voice-based Google and YouTube search</li>
  <li>Task management using voice commands with JSON storage</li>
  <li>Contextual responses such as time, weather, and greetings</li>
  <li>Audio feedback for command success and failure</li>
  <li>Multithreaded and asynchronous execution for smooth performance</li>
</ul>

<h2>Tech Stack</h2>
<ul>
  <li><b>Language:</b> Python</li>
  <li><b>UI:</b> CustomTkinter, Tkinter</li>
  <li><b>Wake Word:</b> Picovoice Porcupine</li>
  <li><b>Speech Recognition:</b> SpeechRecognition</li>
  <li><b>Text-to-Speech:</b> Edge TTS, pyttsx3</li>
  <li><b>Audio:</b> PyAudio, Pygame</li>
  <li><b>Automation:</b> PyAutoGUI, ctypes</li>
  <li><b>Storage:</b> JSON</li>
</ul>

<h2>Installation</h2>
<pre>
git clone https://github.com/Midhun1618/VOX.git
cd VOX
pip install -r requirements.txt
</pre>

<p>
<b>Note:</b> PyAudio may require a pre-built wheel on Windows.
</p>

<h2>Run</h2>
<pre>
python main.py
</pre>

<h2>Example Commands</h2>
<ul>
  <li>Hey Vox, open YouTube</li>
  <li>Hey Vox, search Python multithreading</li>
  <li>Hey Vox, add task buy groceries</li>
  <li>Hey Vox, read my tasks</li>
  <li>Hey Vox, mute volume</li>
</ul>

<h2>Project Structure</h2>
<pre>
VOX/
├── assets/
├── main.py
├── tasks.json
└── README.md
</pre>

<h2>Author</h2>
<p>
<b>Midhun KP</b><br>
GitHub: <a href="https://github.com/Midhun1618">https://github.com/Midhun1618</a><br>
LinkedIn: <a href="https://www.linkedin.com/in/midhun-kp">https://www.linkedin.com/in/midhun-kp</a>
</p>
