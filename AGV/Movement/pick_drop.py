from SCSCtrl import TTLServo
import time

def motor_init():
  TTLServo.servoAngleCtrl(1, 0, 1, 150)
  TTLServo.servoAngleCtrl(2, 0, 1, 150)
  TTLServo.servoAngleCtrl(3, 0, 1, 150)
  TTLServo.servoAngleCtrl(4, 0, 1, 150)
  TTLServo.servoAngleCtrl(5, 30, 1, 150)

def look_right():
  TTLServo.servoAngleCtrl(1, 90, 1, 500)
  time.sleep(1)

  TTLServo.servoAngleCtrl(2, 75, 1, 500)
  time.sleep(1)

def pick():
  TTLServo.servoAngleCtrl(4, 0, 1, 500)
  servoPos_4 = -40 
  TTLServo.servoAngleCtrl(4, servoPos_4, 1, 500)
  time.sleep(1)

  TTLServo.servoAngleCtrl(2, 0, 1, 500)
  time.sleep(1)

  TTLServo.servoAngleCtrl(1, 0, 1, 500)
  time.sleep(1)

  TTLServo.servoStop(1)

def drop():
  servoPos_4 = 0 
  TTLServo.servoAngleCtrl(4, servoPos_4, 1, 500)
  time.sleep(1)

  TTLServo.servoAngleCtrl(2, 0, 1, 500)
  time.sleep(1)

  TTLServo.servoAngleCtrl(1, 0, 1, 500)
  time.sleep(1)

  TTLServo.servoStop(1)