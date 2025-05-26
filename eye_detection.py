import cv2
from config import haarcascadeEyePath

eye_cascade = cv2.CascadeClassifier(haarcascadeEyePath)

def draw_eyes(frame, gray, x, y, w, h):
    roi_gray = gray[y:y+h, x:x+w]
    roi_color = frame[y:y+h, x:x+w]
    eyes = eye_cascade.detectMultiScale(roi_gray)
    for (ex, ey, ew, eh) in eyes:
        cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (255, 255, 0), 2)