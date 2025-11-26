# 🖐 Touchless Mouse & System Controller
A fully touchless mouse + system controller built with **OpenCV**, **MediaPipe**, **PyAutoGUI**, **Pycaw**, and **Screen Brightness Control**.
Control your **cursor, clicks, scrolling, system volume, and screen brightness** using nothing but **hand gestures** in front of your webcam. No physical mouse needed.

## ✨ Features
This project is built step-by-step and then combined into a complete system:

### 🧩 Step 1 – Basic Touchless Mouse
File: `step1_advanced_gesture_mouse.py` :contentReference[oaicite:1]{index=1}  
- Track right-hand index finger to move the mouse cursor.
- Perform **left click** using a custom gesture: **thumb + ring finger pinch**.
- Smooth cursor movement using coordinate interpolation.
- Click sound feedback using `click.mp3`.

### 🧩 Step 2 – Right Click + Scrolling
File: `step2_advanced_mouse_right_click_scroll.py` :contentReference[oaicite:2]{index=2}  
Builds on Step 1 and adds:
- **Right click**: thumb + middle finger pinch.
- **Scroll down**: index + middle fingers close together.
- **Scroll up**: index raised + middle bent (gesture-based scroll detection).
- Left-hand detection placeholder for system control in later steps.

### 🧩 Step 3 – Volume Control (Left Hand)
File: `step3_advanced_volume_control.py` :contentReference[oaicite:3]{index=3}  
Adds:
- **Left hand → System Volume Control** using **Pycaw**.
- Volume is mapped to the distance between **thumb and index finger** (left hand).
- On-screen **volume bar UI** that reflects current gesture-based volume.
- Click sound feedback using `click.mp3`.

### 👑 Final – Full Touchless System Control
File: touchless_system.py

# ✋ Gesture Guide

**Right Hand – Mouse Control**
- **Cursor movement with right-hand index finger.**
- **Left click**: thumb + ring finger pinch.
- **Right click**: thumb + middle finger pinch.
- **Scroll down**: index + middle fingers close.
- **Scroll up**: index up, middle bent down.

**Left Hand – System Control**
- **Volume control**: thumb + index distance → maps to system volume (0–100%).
- **Brightness control**: index + middle distance → maps to screen brightness (0–100%).
- On-screen HUD for volume and brightness levels.
- Click sound feedback using `click.mp3` where configured.
- Tip: Try to keep your hand roughly in the middle of the webcam frame for best tracking.

## 🛠 Tech Stack

- **Language**: Python
- **Computer Vision**: OpenCV (`cv2`)
- **Hand Tracking**: MediaPipe Hands
- **Mouse & Scroll Control**: PyAutoGUI
- **System Volume Control**: Pycaw
- **Screen Brightness Control**: `screen_brightness_control`
- **Audio Feedback**: `pygame` / `playsound`
- **Math & Helpers**: NumPy, time, os

# ✅ Requirements
Make sure you have Python 3.8+ installed.
Install the required libraries:
pip install opencv-python mediapipe pyautogui numpy pygame playsound pycaw screen-brightness-control comtypes
On Windows, you may also need:
pip install pywin32

⚠️ Note:
Pycaw and screen_brightness_control are primarily Windows-focused.
Some functionality may not work the same way on Linux/macOS.

# 🚀 How to Run
Clone the repo or download the files.
Place click.mp3 in the same folder as the .py files (optional but recommended).
Run any step script or the final version:
python touchless_system.py

A window will open showing your webcam feed.
Make sure your face and hands are visible and use the gestures below.
Press q anytime to exit.

# If you like this project → leave a ⭐ on GitHub, it’ll make my whole day ✨
