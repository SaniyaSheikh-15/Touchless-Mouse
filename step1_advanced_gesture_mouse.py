import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time
from playsound import playsound
import os

# ===================== CONFIG =====================
pyautogui.FAILSAFE = False
click_cooldown = 1  # seconds
last_click_time = 0
click_sound_file = "click.mp3"

# ===================== FUNCTIONS =====================
def play_click_sound():
    try:
        if os.path.exists(click_sound_file):
            playsound(click_sound_file, block=False)
        else:
            print("⚠ click.mp3 not found.")
    except Exception as e:
        print(f"🔇 Error playing sound: {e}")

# ===================== INIT =====================
cap = cv2.VideoCapture(0)
hands = mp.solutions.hands.Hands(max_num_hands=2, min_detection_confidence=0.7)
draw = mp.solutions.drawing_utils
screen_w, screen_h = pyautogui.size()

# ===================== MAIN LOOP =====================
while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    img_h, img_w, _ = img.shape
    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_img)

    if results.multi_hand_landmarks and results.multi_handedness:
        for hand_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
            # Get hand label (Left or Right)
            hand_label = results.multi_handedness[hand_idx].classification[0].label

            draw.draw_landmarks(img, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS)

            # Landmark list
            lm_list = []
            for id, lm in enumerate(hand_landmarks.landmark):
                x, y = int(lm.x * img_w), int(lm.y * img_h)
                lm_list.append((x, y))

            if hand_label == "Right":
                # Cursor control - Index finger
                index_x, index_y = lm_list[8]
                screen_x = np.interp(index_x, [0, img_w], [0, screen_w])
                screen_y = np.interp(index_y, [0, img_h], [0, screen_h])
                pyautogui.moveTo(screen_x, screen_y, duration=0.05)

                # Click detection - Thumb + Ring finger
                thumb_x, thumb_y = lm_list[4]
                ring_x, ring_y = lm_list[16]
                distance = np.hypot(thumb_x - ring_x, thumb_y - ring_y)

                if distance < 40:
                    if time.time() - last_click_time > click_cooldown:
                        pyautogui.click()
                        play_click_sound()
                        last_click_time = time.time()
                        time.sleep(0.2)  # prevent re-trigger
                        cv2.putText(img, "Left Click", (index_x + 20, index_y - 20),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

    cv2.imshow("🖱 Touchless Mouse - Step 1", img)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()