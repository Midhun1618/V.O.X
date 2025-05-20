import cv2
import mediapipe as mp
import sounddevice as sd
import pyttsx3
import numpy as np
import speech_recognition as sr
import time

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

engine = pyttsx3.init()
r = sr.Recognizer()

volume_mode = False
idle_start = None
current_volume = 0.5  # Start with 50% volume


def speak(text):
    print("Vox:", text)
    engine.say(text)
    engine.runAndWait()


def record_audio(duration=5, fs=16000):
    print("Recording...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    return recording


def recognize_speech():
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)
        try:
            command = r.recognize_google(audio)
            print("Recognized:", command)
            return command.lower()
        except sr.UnknownValueError:
            print("Could not understand.")
        except sr.RequestError:
            print("Could not request results.")
    return ""


def fingers_touching(hand1, hand2):
    x1, y1 = hand1.landmark[8].x, hand1.landmark[8].y
    x2, y2 = hand2.landmark[8].x, hand2.landmark[8].y
    distance = np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
    return distance < 0.05


def draw_finger_connection(frame, hand1, hand2):
    h, w, _ = frame.shape
    x1, y1 = int(hand1.landmark[8].x * w), int(hand1.landmark[8].y * h)
    x2, y2 = int(hand2.landmark[8].x * w), int(hand2.landmark[8].y * h)
    cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 255), 3)


def volume_gesture_condition(hand_landmarks):
    return True


def draw_volume_circle(frame, x, y, volume):
    cv2.circle(frame, (x, y), 15, (0, 255, 0), -1)
    cv2.putText(frame, f"Volume: {int(volume * 100)}%", (x + 20, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)


def main():
    global volume_mode, idle_start, current_volume

    cap = cv2.VideoCapture(0)
    with mp_hands.Hands(
        max_num_hands=2,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7) as hands:

        print("Touch both index fingertips to wake up Vox.")

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = hands.process(rgb_frame)

            if result.multi_hand_landmarks and len(result.multi_hand_landmarks) == 2:
                hand1, hand2 = result.multi_hand_landmarks
                mp_drawing.draw_landmarks(frame, hand1, mp_hands.HAND_CONNECTIONS)
                mp_drawing.draw_landmarks(frame, hand2, mp_hands.HAND_CONNECTIONS)

                draw_finger_connection(frame, hand1, hand2)

                h, w, _ = frame.shape
                x = int(hand1.landmark[8].x * w)
                y = int(hand1.landmark[8].y * h)

       
            cv2.imshow("VOX Assistant", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
