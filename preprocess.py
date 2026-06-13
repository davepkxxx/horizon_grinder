import cv2
import numpy as np


def preprocess(frame: np.ndarray, roi: dict) -> np.ndarray:
    h, w = frame.shape[:2]
    x1 = int(roi["x"] * w)
    y1 = int(roi["y"] * h)
    x2 = x1 + int(roi["w"] * w)
    y2 = y1 + int(roi["h"] * h)
    cropped = frame[y1:y2, x1:x2]

    gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    _, thresh = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh
