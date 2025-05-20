import cv2
import mediapipe as mp
import sounddevice as sd
import pyttsx3
import numpy as np
import speech_recognition as sr
import time
import threading

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

engine = pyttsx3.init()
recognizer = sr.Recognizer()

volume_mode = False
confirming = False
last_y = None
idle_start = None

# Dummy volume setter (replace with actual system volume control)
def set_volume(level):
    print(f"Setting volume to {level}%")

# Record and recognize speech

def recognize_speech():
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            print("You said:", text)
            return text.lower()
        except sr.UnknownValueError:
            print("Could not understand audio")
            return ""
        except sr.RequestError:
            print("Request error")
            return ""

# Gesture: Pointing + Middle fingers up (tip_y < pip_y for both)
def wake_gesture(hand_landmarks):
    index_up = hand_landmarks.landmark[8].y < hand_landmarks.landmark[6].y
    middle_up = hand_landmarks.landmark[12].y < hand_landmarks.landmark[10].y
    return index_up and middle_up

# Gesture: Only Index finger up

def index_gesture(hand_landmarks):
    index_up = hand_landmarks.landmark[8].y < hand_landmarks.landmark[6].y
    other_down = hand_landmarks.landmark[12].y > hand_landmarks.landmark[10].y  # Middle
    return index_up and other_down

def record_audio(duration=5, fs=16000):
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    return recording

def main():
    global volume_mode, confirming, last_y, idle_start

    cap = cv2.VideoCapture(0)
    with mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7) as hands:
        print("Waiting for wake gesture (Index + Middle finger up)...")

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = hands.process(rgb_frame)

            if result.multi_hand_landmarks:
                for hand_landmarks in result.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                    if not volume_mode and wake_gesture(hand_landmarks):
                        print("Wake gesture detected!")
                        engine.say("Vox here")
                        engine.runAndWait()
                        record_audio()
                        command = recognize_speech()

                        if "control the volume" in command:
                            print("Volume control mode ON")
                            volume_mode = True
                            engine.say("Show index finger to set volume")
                            engine.runAndWait()

                    if volume_mode and index_gesture(hand_landmarks):
                        y = hand_landmarks.landmark[8].y
                        height, _ = frame.shape[:2]
                        volume_level = int((1 - y) * 100)
                        print(f"Volume Level: {volume_level}%")

                        if last_y is not None and abs(y - last_y) < 0.01:
                            if idle_start is None:
                                idle_start = time.time()
                            elif time.time() - idle_start > 1.5 and not confirming:
                                engine.say("Can I confirm this level?")
                                engine.runAndWait()
                                confirming = True
                                threading.Thread(target=confirm_volume, args=(volume_level,)).start()
                        else:
                            idle_start = None
                            confirming = False

                        last_y = y
                    else:
                        idle_start = None
                        last_y = None

            cv2.imshow("VOX - Hand Gesture Volume Control", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break

    cap.release()
    cv2.destroyAllWindows()

def confirm_volume(level):
    global volume_mode, confirming
    response = recognize_speech()
    if "yes" in response:
        engine.say("Volume confirmed")
        engine.runAndWait()
        set_volume(level)
        volume_mode = False
    else:
        engine.say("Okay, adjust again")
        engine.runAndWait()
        confirming = False

if __name__ == "__main__":
    main()
