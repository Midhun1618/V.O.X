import cv2
import mediapipe as mp
import math
import speech_recognition as sr
import threading

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
hands = mp_hands.Hands(max_num_hands=1)

volume_control_active = False
confirmed_volume = 0

def fingers_up(hand_landmarks):
    tips = [4, 8, 12, 16, 20]
    pip_joints = [3, 6, 10, 14, 18]

    fingers = []
    if hand_landmarks.landmark[tips[0]].x < hand_landmarks.landmark[pip_joints[0]].x:
        fingers.append(1)
    else:
        fingers.append(0)

    for i in range(1, 5):
        if hand_landmarks.landmark[tips[i]].y < hand_landmarks.landmark[pip_joints[i]].y:
            fingers.append(1)
        else:
            fingers.append(0)
    return fingers

def is_thumb_index_middle_up(fingers):
    return fingers[0] == 1 and fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0 and fingers[4] == 0

def listen_for_commands():
    global volume_control_active, confirmed_volume
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        recognizer.adjust_for_ambient_noise(source)

    while True:
        with mic as source:
            print("🎤 VOX Listening for Command...")
            audio = recognizer.listen(source)

        try:
            command = recognizer.recognize_google(audio).lower()
            print(f"🗣️ You said: {command}")

            if "vox access volume control" in command:
                print("🔊 Volume control activated")
                volume_control_active = True

            elif "vox confirm volume level" in command:
                print("🔒 Volume level confirmed!")
                volume_control_active = False
                print(f"✅ Final Volume: {confirmed_volume}%")

        except sr.UnknownValueError:
            print("🤔 VOX didn’t catch that.")
        except sr.RequestError as e:
            print(f"Speech recognition error: {e}")

# Start voice recognition in the background
voice_thread = threading.Thread(target=listen_for_commands)
voice_thread.daemon = True
voice_thread.start()

while True:
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks:
        for handLms in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)
            finger_status = fingers_up(handLms)

            # ABCD gesture
            if is_thumb_index_middle_up(finger_status):
                cv2.putText(frame, "ABCD Triggered!", (10, 110),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3)
                print("ABCD")

            # Volume control only when activated by voice
            if volume_control_active:
                thumb_tip = handLms.landmark[4]
                index_tip = handLms.landmark[8]

                h, w, _ = frame.shape
                thumb_x, thumb_y = int(thumb_tip.x * w), int(thumb_tip.y * h)
                index_x, index_y = int(index_tip.x * w), int(index_tip.y * h)

                cv2.circle(frame, (thumb_x, thumb_y), 10, (255, 0, 255), cv2.FILLED)
                cv2.circle(frame, (index_x, index_y), 10, (255, 0, 255), cv2.FILLED)
                cv2.line(frame, (thumb_x, thumb_y), (index_x, index_y), (255, 0, 255), 3)

                length = math.hypot(index_x - thumb_x, index_y - thumb_y)
                vol = int((length - 30) / (200 - 30) * 100)
                vol = max(0, min(100, vol))
                confirmed_volume = vol  # Store this for confirmation

                cv2.putText(frame, f'Live Volume: {vol}%', (10, 150),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)

    cv2.imshow("VOX Assistant", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
