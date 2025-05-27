# %%
import torchvision
import torch
import torchvision.transforms as transforms
import torch.nn.functional as F

from IPython.display import display
import ipywidgets
import ipywidgets.widgets as widgets
import traitlets
from jetbot import Robot, Camera, bgr8_to_jpeg
from SCSCtrl import TTLServo

import threading
import time
import cv2
import PIL.Image
import numpy as np
from pick_drop import *
from box_color import *

# %%
MODEL_PATH = "/home/jetbot/Notebooks/road_following/523_1100.pth"

areaA = 'green'
areaB = 'orange'
robot = None
camera = None
model = None
mean = None
std = None

lbl1 = ipywidgets.Label(value="areaA :")
areaAlbl = ipywidgets.Label(value="None")
hbox1 = widgets.HBox([lbl1, areaAlbl])

lbl2 = ipywidgets.Label(value="areaB :")
areaBlbl = ipywidgets.Label(value="None")
hbox2 = widgets.HBox([lbl2, areaBlbl])

lbl3 = ipywidgets.Label(value="self.flag :")
flaglbl = ipywidgets.Label(value="None")
hbox3 = widgets.HBox([lbl3, flaglbl])
vbox1 = widgets.VBox([hbox1, hbox2, hbox3])

image_widget = ipywidgets.Image(format='jpeg', width=224, height=224)
x_slider = ipywidgets.FloatSlider(min=-1.0, max=1.0, description='x')
y_slider = ipywidgets.FloatSlider(min=0, max=1.0, orientation='vertical', description='y')
steering_slider = ipywidgets.FloatSlider(min=-1.0, max=1.0, description='steering')
speed_slider = ipywidgets.FloatSlider(min=0, max=1.0, orientation='vertical', description='speed')
vbox2 = widgets.VBox([image_widget, x_slider, steering_slider], layout=widgets.Layout(align_self='center'))
hbox4 = widgets.HBox([vbox2, y_slider, speed_slider], layout=widgets.Layout(align_self='center'))

startBtn = widgets.Button(description="Start", button_style='info')
lbl41 = ipywidgets.Label(value="Find Area : ")
goallbl = ipywidgets.Label(value="None")
hbox5 = widgets.HBox([startBtn, lbl41, goallbl])

lbl50 = ipywidgets.Label(value="Manual Controller")
button_layout = widgets.Layout(width='100px', height='80px', align_self='center')
stop_button = widgets.Button(description='stop', button_style='danger', layout=button_layout)
forward_button = widgets.Button(description='forward', layout=button_layout)
backward_button = widgets.Button(description='backward', layout=button_layout)
left_button = widgets.Button(description='left', layout=button_layout)
right_button = widgets.Button(description='right', layout=button_layout)
middle_box = widgets.HBox([left_button, stop_button, right_button], layout=widgets.Layout(align_self='center'))
controls_box = widgets.VBox([lbl50, forward_button, middle_box, backward_button])

lbl51 = ipywidgets.Label(value="Auto Controller")
speed_gain_slider = ipywidgets.FloatSlider(min=0.0, max=1.0, step=0.01, value=0.25, description='speed gain')
steering_gain_slider = ipywidgets.FloatSlider(min=0.0, max=1.0, step=0.01, value=0.2, description='steering gain')
steering_dgain_slider = ipywidgets.FloatSlider(min=0.0, max=0.5, step=0.001, value=0.0, description='steering kd')
steering_bias_slider = ipywidgets.FloatSlider(min=-0.3, max=0.3, step=0.01, value=0.0, description='steering bias')
vbox3 = widgets.VBox([lbl51, speed_gain_slider, steering_gain_slider, steering_dgain_slider, steering_bias_slider])
hbox6 = widgets.HBox([controls_box, vbox3], layout=widgets.Layout(align_self='center'))

display(vbox1, hbox4, hbox5, hbox6)

manual_btnlst = [stop_button, forward_button, backward_button, left_button, right_button]

# %%
def stop(change):
    robot.stop()

def step_forward(change):
    robot.forward(0.4)

def step_backward(change):
    robot.backward(0.4)

def step_left(change):
    robot.left(0.3)
    time.sleep(0.5)
    robot.stop()

def step_right(change):
    robot.right(0.3)
    time.sleep(0.5)
    robot.stop()

stop_button.on_click(stop)
forward_button.on_click(step_forward)
backward_button.on_click(step_backward)
left_button.on_click(step_left)
right_button.on_click(step_right)

# %%
colors = [
    {'name': 'red', 'lower': np.array([0, 140, 50]),  'upper': np.array([25, 160, 255])},
    {'name': 'green', 'lower': np.array([50, 130, 70]),  'upper': np.array([89, 150, 255])},
    {'name': 'blue', 'lower': np.array([90, 190, 70]),  'upper': np.array([120, 215, 255])},
    {'name': 'purple', 'lower': np.array([125, 50, 70]), 'upper': np.array([158, 255, 255])},
    {'name': 'yellow', 'lower': np.array([20, 120, 100]), 'upper': np.array([30, 139, 255])},
    {'name': 'orange', 'lower': np.array([10, 170, 20]), 'upper': np.array([19, 210, 255])}
]

areaA_color = next((color for color in colors if color['name'] == areaA), None)
areaB_color = next((color for color in colors if color['name'] == areaB), None)

areaAlbl.value = areaA_color['name']
areaBlbl.value = areaB_color['name']

findArea = areaA
goallbl.value = findArea

frame_width = 224
frame_height = 224
camera_center_X = int(frame_width / 2)
camera_center_Y = int(frame_height / 2)

colorHSVvalueList = []
max_len = 20

roadFinding = None
goalFinding = None
device = None

# %%
def load_model():
    global model, device, mean, std
    model = torchvision.models.resnet18(pretrained=False)
    model.fc = torch.nn.Linear(512, 2)
    model.load_state_dict(torch.load(MODEL_PATH))
    device = torch.device('cuda')
    model = model.to(device)
    model = model.eval().half()
    mean = torch.Tensor([0.485, 0.456, 0.406]).cuda().half()
    std = torch.Tensor([0.229, 0.224, 0.225]).cuda().half()
    print('===== model load success =====')

# %%
def init():
    global robot, camera, camera_link
    robot = Robot()
    camera = Camera()
    motor_init()
    camera_link = traitlets.dlink((camera, 'value'), (image_widget, 'value'), transform=bgr8_to_jpeg)
    load_model()
    print("===== initialization success =====")

# %%
class WorkingAreaFind(threading.Thread):
    def __init__(self):
        super().__init__()
        self.th_flag = True
        self.imageInput = 0
        self.flag = 1
        flaglbl.value = str(self.flag)

    def run(self):
        while self.th_flag:
            self.imageInput = camera.value
            hsv = cv2.cvtColor(self.imageInput, cv2.COLOR_BGR2HSV)
            hsv = cv2.blur(hsv, (15, 15))

            areaA_mask = cv2.inRange(hsv, areaA_color['lower'], areaA_color['upper'])
            areaA_mask = cv2.erode(areaA_mask, None, iterations=2)
            areaA_mask = cv2.dilate(areaA_mask, None, iterations=2)

            areaB_mask = cv2.inRange(hsv, areaB_color['lower'], areaB_color['upper'])
            areaB_mask = cv2.erode(areaB_mask, None, iterations=2)
            areaB_mask = cv2.dilate(areaB_mask, None, iterations=2)

            AContours, _ = cv2.findContours(areaA_mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            BContours, _ = cv2.findContours(areaB_mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if AContours and self.flag == 1:
                self.findCenter(areaA, AContours)
            elif BContours and self.flag == 2:
                self.findCenter(areaB, BContours)
            else:
                cv2.putText(self.imageInput, "Finding...", (0, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
                image_widget.value = bgr8_to_jpeg(self.imageInput)

            time.sleep(0.1)

    def findCenter(self, name, Contours):
        global roadFinding, findArea, areaA
        c = max(Contours, key=cv2.contourArea)
        ((box_x, box_y), radius) = cv2.minEnclosingCircle(c)

        X = int(box_x)
        Y = int(box_y)

        error_Y = abs(camera_center_Y - Y)
        error_X = abs(camera_center_X - X)

        if error_Y < 15 and error_X < 15:
            if name == areaA and self.flag == 1:
                self.flag = 2
                findArea = areaB
                goallbl.value = findArea
                areaAlbl.value = areaA + " Goal!"
                flaglbl.value = str(self.flag)
                roadFinding.halt()
                look_right()
                drop()
                roadFinding.resume()

            elif name == areaB and self.flag == 2:
                self.flag = 1
                findArea = areaB
                goallbl.value = findArea
                areaBlbl.value = areaB + " Goal!"
                flaglbl.value = str(self.flag)
                roadFinding.stop()
                time.sleep(0.5)
                self.flag = 1
                look_right()
                areaA = get_center_color(camera)
                areaAlbl.value = areaA
                pick()
                roadFinding = RobotMoving()
                roadFinding.start()

        image_widget.value = bgr8_to_jpeg(self.imageInput)

    def stop(self):
        self.th_flag = False
        robot.stop()

# %%
class RobotMoving(threading.Thread):
    def __init__(self):
        super().__init__()
        self.th_flag = True
        self.angle = 0.0
        self.angle_last = 0.0
        self.halt_flag = False

    def run(self):
        while self.th_flag:
            if self.halt_flag:
                robot.left_motor.value = 0
                robot.right_motor.value = 0
                time.sleep(5)
                continue
                
            image = camera.value
            xy = model(self.preprocess(image)).detach().float().cpu().numpy().flatten()
            x = xy[0]
            y = (0.5 - xy[1]) / 2.0
            x_slider.value = x
            y_slider.value = y
            speed_slider.value = speed_gain_slider.value
            image_widget.value = bgr8_to_jpeg(image)

            self.angle = np.arctan2(x, y)

            if not self.th_flag:
                break

            pid = self.angle * steering_gain_slider.value + (self.angle - self.angle_last) * steering_dgain_slider.value
            self.angle_last = self.angle

            steering_slider.value = pid + steering_bias_slider.value

            robot.left_motor.value = max(min(speed_slider.value + steering_slider.value, 1.0), 0.0)
            robot.right_motor.value = max(min(speed_slider.value - steering_slider.value, 1.0), 0.0)
            time.sleep(0.1)
        robot.stop()

    def preprocess(self, image):
        image = PIL.Image.fromarray(image)
        image = transforms.functional.to_tensor(image).to(device).half()
        image.sub_(mean[:, None, None]).div_(std[:, None, None])
        return image[None, ...]
    
    def halt(self):
        self.halt_flag = True
        
    def resume(self):
        self.halt_flag = False

    def stop(self):
        self.th_flag = False
        robot.stop()

# %%
def start(_=None):
    global camera_link, goalFinding, roadFinding, areaA
    if startBtn.description == "Start":
        camera_link.unlink()
        look_right()
        areaA = get_center_color(camera)
        time.sleep(3)
        pick()
        goalFinding = WorkingAreaFind()
        goalFinding.start()
        roadFinding = RobotMoving()
        roadFinding.start()
        startBtn.button_style = "warning"
        startBtn.description = "Stop"
    elif startBtn.description == "Stop":
        roadFinding.stop()
        goalFinding.stop()
        camera_link = traitlets.dlink((camera, 'value'), (image_widget, 'value'), transform=bgr8_to_jpeg)
        startBtn.button_style = "info"
        startBtn.description = "Start"

# %%
init()

# %%
startBtn.on_click(start)

# %%
if __name__ == "__main__":
    init()
    # startBtn.on_click(start)
    start()

# %%
# time.sleep(0.1)
# robot.stop()
# camera.stop()

# print('End')


