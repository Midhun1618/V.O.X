import pvporcupine
import pyaudio
import struct
import threading
import os

class WakeWord:
    def __init__(self, access_key, keyword_path, on_detected):
        self.access_key = access_key
        self.keyword_path = keyword_path
        self.on_detected = on_detected

        self.porcupine = None
        self.pa = None
        self.stream = None
        self.running = False

    def start(self):
        self.running = True
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        self.porcupine = pvporcupine.create(
            access_key=self.access_key,
            keyword_paths=[self.keyword_path]
        )

        self.pa = pyaudio.PyAudio()
        self.stream = self.pa.open(
            rate=self.porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self.porcupine.frame_length
        )

        print("[WakeWord] Listening...")

        while self.running:
            pcm = self.stream.read(
                self.porcupine.frame_length,
                exception_on_overflow=False
            )
            pcm = struct.unpack_from(
                "h" * self.porcupine.frame_length, pcm
            )

            result = self.porcupine.process(pcm)
            if result >= 0:
                print("[WakeWord] Detected!")
                self.on_detected()
