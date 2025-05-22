import pvporcupine
import pyaudio
import struct
import os
import sys

ACCESS_KEY = "l4YcMaXwFVLjkElTdruR5vz2fjZ3Vwd0CuGnfDR/lg0ifYd/iQzgmA=="  # Replace with your actual access key
KEYWORD_PATH = os.path.join("assets", "vox.ppn")  # Path to your .ppn file

def main():
    porcupine = None
    pa = None
    audio_stream = None

    try:
        # Initialize Porcupine with your keyword file and access key
        porcupine = pvporcupine.create(
            access_key=ACCESS_KEY,
            keyword_paths=[KEYWORD_PATH]
        )

        pa = pyaudio.PyAudio()

        audio_stream = pa.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length
        )

        print("Listening for wake word 'VOX'...")

        while True:
            # Read audio frame from mic (exactly porcupine.frame_length samples)
            pcm = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
            # Unpack audio bytes to int16 array
            pcm_unpacked = struct.unpack_from("h" * porcupine.frame_length, pcm)

            # Process frame with Porcupine
            result = porcupine.process(pcm_unpacked)

            if result >= 0:
                print("Wake word detected! Launching VOX assistant...")
                # Here you can call your main.py or trigger your assistant start
                # For example:
                # os.system("python main.py")
                # or handle however you want

    except KeyboardInterrupt:
        print("\nStopping...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if audio_stream is not None:
            audio_stream.close()
        if pa is not None:
            pa.terminate()
        if porcupine is not None:
            porcupine.delete()

if __name__ == "__main__":
    main()
