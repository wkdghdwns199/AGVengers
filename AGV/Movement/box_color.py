import cv2
import numpy as np


colors = [
    {'name': 'red', 'lower': np.array([0, 140, 50]),  'upper': np.array([25, 160, 255]) },
    {'name': 'green', 'lower': np.array([50, 130, 70]),  'upper': np.array([89, 150, 255]) },
    {'name': 'blue', 'lower': np.array([90, 190, 70]),  'upper': np.array([120, 215, 255]) },
    {'name': 'purple', 'lower': np.array([125, 50, 70]), 'upper': np.array([158, 255, 255]) },
    {'name': 'yellow', 'lower': np.array([20, 120, 100]), 'upper': np.array([30, 139, 255]) },
    {'name': 'orange', 'lower': np.array([10, 180, 20]), 'upper': np.array([19, 210, 255]) }
]

def get_center_color(camera, frame_width=224, frame_height=224):
    frame = camera.value
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    center_x = frame_width // 2
    center_y = frame_height // 2
    center_pixel = hsv[center_y, center_x]
    
    for color in colors:
        if all(color['lower'] <= center_pixel) and all(center_pixel <= color['upper']):
            return color['name']
    
    return "red"
