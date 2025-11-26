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

# 🎵 Initialize Pygame for sound playback
pygame.mixer.init()
click_sound_file = "click.mp3"

click_sound = None
if os.path.exists(click_sound_file):
    click_sound = pygame.mixer.Sound(click_sound_file)
else:
    print("⚠ click.mp3 not found!")

def play_click_sound():
    if click_sound:
        click_sound.play()

# 🔊 Setup for volume control
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume.iid, CLSCTX_ALL, None)
volume_control = cast(interface, POINTER(IAudioEndpointVolume))
vol_min, vol_max = volume_control.GetVolumeRange()[:2]

# 🖱 Setup
pyautogui.FAILSAFE = False
click_cooldown = 1
last_click_time = 0

# 🎥 Initialize webcam & MediaPipe
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

                if hand_label == "Right":
                    index_x, index_y = lm_list[8]
                    screen_x = np.interp(index_x, [0, img_w], [0, screen_w])
                    screen_y = np.interp(index_y, [0, img_h], [0, screen_h])
                    pyautogui.moveTo(screen_x, screen_y, duration=0.05)

                    # Left Click (Thumb + Ring Finger)
                    thumb, ring = lm_list[4], lm_list[16]
                    if np.hypot(thumb[0] - ring[0], thumb[1] - ring[1]) < 60:
                        if time.time() - last_click_time > click_cooldown:
                            pyautogui.click()
                            play_click_sound()
                            last_click_time = time.time()
                            time.sleep(0.2)

                    # Right Click (Thumb + Middle Finger)
                    middle = lm_list[12]
                    if np.hypot(thumb[0] - middle[0], thumb[1] - middle[1]) < 60:
                        if time.time() - last_click_time > click_cooldown:
                            pyautogui.rightClick()
                            play_click_sound()
                            last_click_time = time.time()
                            time.sleep(0.2)

                    # Scroll Gestures
                    if np.hypot(lm_list[8][0] - lm_list[12][0], lm_list[8][1] - lm_list[12][1]) < 50:
                        pyautogui.scroll(-30)
                    elif lm_list[8][1] < lm_list[5][1] and lm_list[12][1] > lm_list[9][1]:
                        pyautogui.scroll(30)

                elif hand_label == "Left":
                    # Volume Control using Left Hand (Thumb + Index distance)
                    thumb = lm_list[4]
                    index = lm_list[8]
                    distance = np.hypot(thumb[0] - index[0], thumb[1] - index[1])
                    vol = np.interp(distance, [20, 200], [vol_min, vol_max])
                    volume_control.SetMasterVolumeLevel(vol, None)

                    # Volume Bar UI
                    bar_y = int(np.interp(distance, [20, 200], [500, 300]))
                    cv2.rectangle(img, (40, 300), (60, 500), (200, 200, 200), 2)
                    cv2.rectangle(img, (40, bar_y), (60, 500), (100, 255, 100), -1)
                    cv2.putText(img, "Vol", (30, 280), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        else:
            cv2.putText(img, "🖐 Place hand in view", (200, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

    except Exception as e:
        print(f"Error: {e}")

    cv2.imshow("👑 Touchless Mouse + Volume Control", img)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()