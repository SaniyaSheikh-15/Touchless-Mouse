import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time
import pygame
import os
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from screen_brightness_control import set_brightness

# 🎵 Sound setup
pygame.mixer.init()
click_sound_file = "click.mp3"
click_sound = pygame.mixer.Sound(click_sound_file) if os.path.exists(click_sound_file) else None

def play_click_sound():
    if click_sound:
        click_sound.play()

# 🔊 Volume Control
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume_control = cast(interface, POINTER(IAudioEndpointVolume))
vol_min, vol_max = volume_control.GetVolumeRange()[:2]

# 🖱 PyAutoGUI setup
pyautogui.FAILSAFE = False
click_cooldown = 1
last_click_time = 0

# 🎥 Camera & MediaPipe
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

    try:
        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                hand_label = results.multi_handedness[hand_idx].classification[0].label
                draw.draw_landmarks(img, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS)

                lm_list = []
                for id, lm in enumerate(hand_landmarks.landmark):
                    x, y = int(lm.x * img_w), int(lm.y * img_h)
                    lm_list.append((x, y))

                # 👉 Right Hand – Mouse + Click + Scroll
                if hand_label == "Right":
                    index_x, index_y = lm_list[8]
                    screen_x = np.interp(index_x, [50, img_w - 50], [0, screen_w])
                    screen_y = np.interp(index_y, [50, img_h - 50], [0, screen_h])
                    pyautogui.moveTo(screen_x, screen_y, duration=0.05)

                    thumb, ring, middle = lm_list[4], lm_list[16], lm_list[12]

                    # Left Click
                    if np.hypot(thumb[0] - ring[0], thumb[1] - ring[1]) < 60:
                        if time.time() - last_click_time > click_cooldown:
                            pyautogui.click()
                            play_click_sound()
                            last_click_time = time.time()
                            time.sleep(0.2)

                    # Right Click
                    if np.hypot(thumb[0] - middle[0], thumb[1] - middle[1]) < 60:
                        if time.time() - last_click_time > click_cooldown:
                            pyautogui.rightClick()
                            play_click_sound()
                            last_click_time = time.time()
                            time.sleep(0.2)

                    # Scroll Down
                    if np.hypot(lm_list[8][0] - lm_list[12][0], lm_list[8][1] - lm_list[12][1]) < 50:
                        pyautogui.scroll(-30)

                    # Scroll Up
                    elif lm_list[8][1] < lm_list[5][1] and lm_list[12][1] > lm_list[9][1]:
                        pyautogui.scroll(30)

                # 👉 Left Hand – Volume + Brightness
                elif hand_label == "Left":
                    thumb = lm_list[4]
                    index = lm_list[8]
                    middle = lm_list[12]

                    # 🎚 Volume Control (Thumb + Index)
                    vol_dist = np.hypot(thumb[0] - index[0], thumb[1] - index[1])
                    if vol_dist < 200:
                        vol = np.interp(vol_dist, [20, 200], [vol_min, vol_max])
                        volume_control.SetMasterVolumeLevel(vol, None)
                        volume_val = int(np.interp(vol_dist, [20, 200], [0, 100]))

                        bar_y = int(np.interp(vol_dist, [20, 200], [500, 300]))
                        cv2.rectangle(img, (40, 300), (60, 500), (200, 200, 200), 2)
                        cv2.rectangle(img, (40, bar_y), (60, 500), (100, 255, 100), -1)
                        cv2.putText(img, f"Vol: {volume_val}%", (30, 280), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

                    # 💡 Brightness Control (Index + Middle)
                    bri_dist = np.hypot(index[0] - middle[0], index[1] - middle[1])
                    if bri_dist < 150:
                        brightness_val = int(np.interp(bri_dist, [20, 150], [0, 100]))
                        set_brightness(brightness_val)
                        cv2.putText(img, f"Bri: {brightness_val}%", (30, 260), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        else:
            cv2.putText(img, "🖐 Place hand in view", (200, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

    except Exception as e:
        print(f"Error: {e}")

    cv2.imshow("🖐 Touchless System Control", img)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()