import torchvision
import torch
import torchvision.transforms as transforms
import torch.nn.functional as F

from jetbot import Robot, Camera, bgr8_to_jpeg
from SCSCtrl import TTLServo

import threading
import time
import cv2
import PIL.Image
import numpy as np

from pick_drop import *

import requests
import socket
from datetime import datetime, timezone

# Firebase 프로젝트와 컬렉션 정보 (본인의 프로젝트 ID로 변경)
PROJECT_ID = 'embedded-finalpjt-9b5d0'    # <-- 여기에 실제 프로젝트 아이디 넣으세요
COLLECTION = 'auto_activities'

# Firestore REST API URL 템플릿
firestore_url = f'https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/{COLLECTION}'

# 현재 로봇 IP 가져오는 함수
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # 외부 DNS 접속 시도용 용도 (실제로 연결 안 함)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = 'unknown'
    finally:
        s.close()
    return ip

robot_ip = get_ip()

# --- 전역 하드웨어 객체 ---
robot = Robot()
camera = Camera()

# --- 모델 로드 및 초기화 ---
model = torchvision.models.resnet18(pretrained=False)
model.fc = torch.nn.Linear(512, 2)
model.load_state_dict(torch.load("./final_movement.pth"))
device = torch.device('cuda')
model = model.to(device).eval().half()

mean = torch.Tensor([0.485, 0.456, 0.406]).cuda().half()
std = torch.Tensor([0.229, 0.224, 0.225]).cuda().half()

# --- 기본값으로 변환된 이전 위젯 변수 ---
speed_gain = 0.25              # speed_gain_slider 초기값
steering_gain = 0.2            # steering_gain_slider 초기값
steering_dgain = 0.0           # steering_dgain_slider 초기값
steering_bias = 0.0            # steering_bias_slider 초기값

# --- 컨트롤 변수 ---
frame_width = 224
frame_height = 224
camera_center_X = frame_width // 2
camera_center_Y = frame_height // 2

# Working Area 지정 (원하는 색상 이름으로 변경 가능)
areaA = 'purple'
areaB = 'red'

colors = [
     {'name': 'red', 'lower': np.array([3, 30, 181]),  'upper': np.array([50, 255, 255])},
    {'name': 'green', 'lower': np.array([50, 130, 70]),  'upper': np.array([89, 150, 255])},
    {'name': 'blue', 'lower': np.array([75, 145, 70]),  'upper': np.array([90, 150, 255])},
    {'name': 'purple', 'lower': np.array([125, 50, 70]), 'upper': np.array([158, 255, 255])},
    {'name': 'yellow', 'lower': np.array([44, 145, 100]), 'upper': np.array([50, 150, 255])},
    {'name': 'orange', 'lower': np.array([35, 140, 20]), 'upper': np.array([40, 150, 255])}
]

areaA_color = next((color for color in colors if color['name'] == areaA), None)
areaB_color = next((color for color in colors if color['name'] == areaB), None)

# --- 스레드 객체 전역 참조용 ---
roadFinding = None
goalFinding = None

# --- WorkingAreaFind 클래스 ---
class WorkingAreaFind(threading.Thread):
    """
    Working Area 찾는 스레드
    flag 상태:
        1: areaA 탐색
        2: areaB 탐색
    """
    def __init__(self, camera, areaA_color, areaB_color, areaA_name, areaB_name):
        super().__init__()
        self.th_flag = True
        self.camera = camera

        self.flag = 1  # 시작은 areaA 찾기
        self.areaA_color = areaA_color
        self.areaB_color = areaB_color
        self.areaA_name = areaA_name
        self.areaB_name = areaB_name

        self.find_area = areaA_name
        
    def run(self):
        while self.th_flag:
            frame = self.camera.value
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            hsv = cv2.blur(hsv, (15, 15))
            
            areaA_mask = cv2.inRange(hsv, self.areaA_color['lower'], self.areaA_color['upper'])
            areaA_mask = cv2.erode(areaA_mask, None, iterations=2)
            areaA_mask = cv2.dilate(areaA_mask, None, iterations=2)
            
            areaB_mask = cv2.inRange(hsv, self.areaB_color['lower'], self.areaB_color['upper'])
            areaB_mask = cv2.erode(areaB_mask, None, iterations=2)
            areaB_mask = cv2.dilate(areaB_mask, None, iterations=2)
            
            AContours, _ = cv2.findContours(areaA_mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            BContours, _ = cv2.findContours(areaB_mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if AContours and self.flag == 1:
                self.findCenter(frame, self.areaA_name, AContours)
            elif BContours and self.flag == 2:
                self.findCenter(frame, self.areaB_name, BContours)
            else:
                # 단순히 반복하면서 대기
                time.sleep(0.1)
    
    def findCenter(self, frame, name, contours):
        c = max(contours, key=cv2.contourArea)
        ((box_x, box_y), radius) = cv2.minEnclosingCircle(c)
        X = int(box_x)
        Y = int(box_y)

        error_Y = Y - camera_center_Y
        error_X = abs(camera_center_X - X)
        
        if 5 < error_Y and error_X < 15:  # 도착 조건(임계값)
            if name == self.areaA_name and self.flag == 1:
                # areaA 도착 -> areaB 탐색으로 변경
                self.flag = 2
                self.find_area = self.areaB_name
                print(f"[WorkingAreaFind] {self.areaA_name} 찾음, {self.areaB_name} 탐색 시작")
                roadFinding.halt()
                look_right()
                pick()
                log_activity_rest('pick', "green")
                roadFinding.resume()
                
            elif name == self.areaB_name and self.flag == 2:
                # areaB 도착 -> areaA 탐색을 다시 시작
                self.flag = 1
                self.find_area = self.areaA_name
                print(f"[WorkingAreaFind] {self.areaB_name} 찾음, {self.areaA_name} 탐색 시작")
                roadFinding.halt()
                look_right()
                drop()
                log_activity_rest('drop', "blue")
                roadFinding.resume()
    
    def stop(self):
        self.th_flag = False
        robot.stop()

# --- RobotMoving 클래스 ---
class RobotMoving(threading.Thread):
    """
    Road Following 스레드
    """
    def __init__(self, camera, model, device):
        super().__init__()
        self.th_flag = True
        self.camera = camera
        self.model = model
        self.device = device
        
        self.angle = 0.0
        self.angle_last = 0.0
        
        self.halt_flag = False
        
    def run(self):
        global speed_gain, steering_gain, steering_dgain, steering_bias
        
        while self.th_flag:
            if self.halt_flag:
                robot.left_motor.value = 0
                robot.right_motor.value = 0
                time.sleep(5)
                continue

            image = self.camera.value
            xy = self.model(self.preprocess(image)).detach().float().cpu().numpy().flatten()
            x = xy[0]
            y = (0.5 - xy[1]) / 2.0
            
            self.angle = np.arctan2(x, y)
            
            if not self.th_flag:
                break
            
            pid = self.angle * steering_gain + (self.angle - self.angle_last) * steering_dgain
            self.angle_last = self.angle
            
            steering = pid + steering_bias
            
            left_speed = max(min(speed_gain + steering, 1.0), 0.0)
            right_speed = max(min(speed_gain - steering, 1.0), 0.0)
            
            robot.left_motor.value = left_speed
            robot.right_motor.value = right_speed
            
            time.sleep(0.1)
        robot.stop()
    
    def preprocess(self, image):
        image = PIL.Image.fromarray(image)
        image = transforms.functional.to_tensor(image).to(self.device).half()
        image.sub_(mean[:, None, None]).div_(std[:, None, None])
        return image[None, ...]
    
    def stop(self):
        self.th_flag = False
        robot.stop()
        
    def halt(self):
        self.halt_flag = True
        
    def resume(self):
        self.halt_flag = False

# --- 수동 제어 함수 (원본에서 motor_init(), pick(), drop(), look_right() 등은 pick_drop 모듈에서 로드됨) ---
def stop_robot():
    robot.stop()
    
def step_forward():
    robot.forward(0.4)

def step_backward():
    robot.backward(0.4)

def step_left():
    robot.left(0.3)
    time.sleep(0.5)
    robot.stop()

def step_right():
    robot.right(0.3)
    time.sleep(0.5)
    robot.stop()

# --- 모듈 시작 명령 ---
def start_all():
    """
    RoadFollowing과 WorkingAreaRecognition 스레드 시작
    """
    global roadFinding, goalFinding
    roadFinding = RobotMoving(camera, model, device)
    roadFinding.start()
    goalFinding = WorkingAreaFind(camera, areaA_color, areaB_color, areaA, areaB)
    goalFinding.start()
    
        

def stop_all():
    """
    RoadFollowing과 WorkingAreaRecognition 스레드 종료 및 정지
    """
    global roadFinding, goalFinding
    if roadFinding is not None:
        roadFinding.stop()
        roadFinding.join()
        roadFinding = None
    if goalFinding is not None:
        goalFinding.stop()
        goalFinding.join()
        goalFinding = None
    robot.stop()

# --- 모듈 종료 함수 ---
def shutdown():
    stop_all()
    camera.stop()
    robot.stop()
    print('End')

# --- 로그 기록 함수 --- dest_color로 바꾸기
def log_activity_rest(command, dest_color):
    """
    인증 없이 Firestore REST API로 데이터 추가 (보안 규칙이 공개 쓰기 허용 상태여야 함)
    """
    timestamp = datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')
    
    # Firestore에 넣을 포맷 JSON
    # https://firebase.google.com/docs/firestore/reference/rest/v1/Value
    data = {
        "fields": {
            "command": {"stringValue": command},
            "receive_IP": {"stringValue": robot_ip},
            "dest_color": {"stringValue": dest_color},
            "time": {"timestampValue": timestamp}
        }
    }

    try:
        res = requests.post(firestore_url, json=data, verify=False)
        if res.status_code == 200:
            print(f'[Firestore REST] Logged {command} command for {dest_color}')
        else:
            print(f'[Firestore REST] Failed to log: {res.status_code} {res.text}')
    except Exception as e:
        print(f'[Firestore REST] Exception: {e}')

# --- motor 초기화 호출 (원래 motor_init()가 pick_drop에서 import 되어있음) ---
motor_init()

if __name__ == '__main__':
    #try:
        print("자동 주행과 작업 인식 시작")
        start_all()
        
        # 원하는 시간만큼 작동시키기 (예: 60초)
        #time.sleep(60)
        
#     finally:
#         print("종료 중...")
#         shutdown()
#         print("종료 완료")