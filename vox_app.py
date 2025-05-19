import cv2
import mediapipe as mp
import math

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
hands = mp_hands.Hands(max_num_hands=1)

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

def volume_function(fingers):
    return fingers[0] == 1 and fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0 and fingers[4] == 0

while True:
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks:
        for handLms in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)
            finger_status = fingers_up(handLms)

            
            if finger_status[1] == 1 and finger_status[2] == 1 and sum(finger_status) == 2:
                cv2.putText(frame, "Two Fingers Up - Open App!", (10, 70),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 3)
                print("Open App function triggered . no target apps found C:/no data available")

            if volume_function(finger_status):
                cv2.putText(frame, "volume controll accessed", (10, 110),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3)
                print("System volume controll function activated!")

            # Volume control with thumb and index finger distance
            thumb_tip = handLms.landmark[4]
            index_tip = handLms.landmark[8]

            h, w, _ = frame.shape
            thumb_x, thumb_y = int(thumb_tip.x * w), int(thumb_tip.y * h)
            index_x, index_y = int(index_tip.x * w), int(index_tip.y * h)

            # Draw circles and line between thumb and index
            cv2.circle(frame, (thumb_x, thumb_y), 10, (255, 0, 255), cv2.FILLED)
            cv2.circle(frame, (index_x, index_y), 10, (255, 0, 255), cv2.FILLED)
            cv2.line(frame, (thumb_x, thumb_y), (index_x, index_y), (255, 0, 255), 3)

            # Calculate distance
            length = math.hypot(index_x - thumb_x, index_y - thumb_y)

            # Map length to volume (example: 30 to 200 pixels → 0 to 100%)
            vol = int((length - 30) / (200 - 30) * 100)
            vol = max(0, min(100, vol))  # Clamp between 0 and 100

            cv2.putText(frame, f'Volume: {vol}%', (10, 150),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)

            # You can add real volume control code here later!

    cv2.imshow("VOX", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
