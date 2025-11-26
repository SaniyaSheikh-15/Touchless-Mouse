import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time
from playsound import playsound
import os

pyautogui.FAILSAFE = False
click_cooldown = 1
last_click_time = 0
click_sound_file = "click.mp3"

def play_click_sound():
    try:
        if os.path.exists(click_sound_file):
            playsound(click_sound_file, block=False)
        else:
            print("⚠ click.mp3 not found.")
    except Exception as e:
        print(f"🔇 Sound Error: {e}")

cap = cv2.VideoCapture(0)
hands = mp.solutions.hands.Hands(max_num_hands=2, min_detection_confidence=0.7)
draw = mp.solutions.drawing_utils
screen_w, screen_h = pyautogui.size()

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    img_h, img_w, _ = img.shape
    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_img)

    if results.multi_hand_landmarks and results.multi_handedness:
        for hand_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
            hand_label = results.multi_handedness[hand_idx].classification[0].label
            draw.draw_landmarks(img, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS)

            lm_list = []
            for id, lm in enumerate(hand_landmarks.landmark):
                x, y = int(lm.x * img_w), int(lm.y * img_h)
                lm_list.append((x, y))

            if hand_label == "Right":
                index_x, index_y = lm_list[8]
                screen_x = np.interp(index_x, [0, img_w], [0, screen_w])
                screen_y = np.interp(index_y, [0, img_h], [0, screen_h])
                pyautogui.moveTo(screen_x, screen_y, duration=0.05)

                # Left Click: Thumb + Ring
                thumb = lm_list[4]
                ring = lm_list[16]
                dist_ring = np.hypot(thumb[0] - ring[0], thumb[1] - ring[1])

                if dist_ring < 40 and time.time() - last_click_time > click_cooldown:
                    pyautogui.click()
                    play_click_sound()
                    last_click_time = time.time()
                    time.sleep(0.2)
                    cv2.putText(img, "Left Click", (index_x + 20, index_y - 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

                # Right Click: Thumb + Middle
                middle = lm_list[12]
                dist_middle = np.hypot(thumb[0] - middle[0], thumb[1] - middle[1])

                if dist_middle < 40 and time.time() - last_click_time > click_cooldown:
                    pyautogui.rightClick()
                    play_click_sound()
                    last_click_time = time.time()
                    time.sleep(0.2)
                    cv2.putText(img, "Right Click", (index_x + 20, index_y + 40),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

                # Scroll down: Index + Middle close
                dist_scroll = np.hypot(lm_list[8][0] - lm_list[12][0], lm_list[8][1] - lm_list[12][1])
                if dist_scroll < 40:
                    pyautogui.scroll(-40)
                    cv2.putText(img, "Scroll Down", (index_x + 20, index_y + 80),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                # Scroll up: Only index lifted, middle bent
                index_tip = lm_list[8]
                middle_tip = lm_list[12]
                index_mcp = lm_list[5]
                middle_mcp = lm_list[9]

                if index_tip[1] < index_mcp[1] and middle_tip[1] > middle_mcp[1]:
                    pyautogui.scroll(40)
                    cv2.putText(img, "Scroll Up", (index_x + 20, index_y + 110),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 0), 2)

            elif hand_label == "Left":
                cv2.putText(img, "👋 Left hand detected", (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 100, 100), 2)
                # We'll add brightness + volume in Step 3 & 4

    cv2.imshow("🖱 Step 2: Right Click + Scroll + Left Hand Base", img)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()