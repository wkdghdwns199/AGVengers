#!/usr/bin/env python3
# mqtt_subscriber.py

import json
import time
import threading
import pytz
import socket
import paho.mqtt.client as mqtt
from datetime import datetime
from jetbot import Robot        # 로봇 제어 모듈
from SCSCtrl import TTLServo    # 서보 제어 모듈

# --- 로컬 IP 획득 함수 ---
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return None
    finally:
        s.close()

LOCAL_IP = get_local_ip()

# --- 전역 변수 설정 ---
korea_tz      = pytz.timezone("Asia/Seoul")
BROKER_ADDR   = "172.20.10.6"
BROKER_PORT   = 1883
COMMAND_TOPIC = "AGV/command"
SENSING_TOPIC = "AGV/sensing"

robot = Robot()

# 제어 이벤트 및 현재 컨트롤러 IP 저장
auto_event    = threading.Event()
manual_event  = threading.Event()
exit_event    = threading.Event()
manual_cmd    = None
controller_ip = None    # 초기값: None


def motion_loop():
    """
    auto_event 또는 manual_event에 따라
    100ms 간격으로 연속 제어를 수행.
    """
    while not exit_event.is_set():
        if auto_event.is_set():
            ### 여기다가 자동 동작 로직 구현
            
            
            robot.forward(0.8)
            
            
            
            ### 여기다가 자동 동작 로직 구현
            
        elif manual_event.is_set():
            if manual_cmd == "go":
                robot.forward(0.8)
            elif manual_cmd == "left":
                robot.left(0.6)
            elif manual_cmd == "right":
                robot.right(0.6)
            elif manual_cmd == "back":
                robot.backward(0.8)
        else:
            robot.stop()
        time.sleep(0.1)
    robot.stop()

# --- MQTT 콜백 함수 ---
def on_connect(client, userdata, flags, rc):
    print(f"[{datetime.now(korea_tz)}] MQTT 연결 {'성공' if rc==0 else '실패 코드='+str(rc)}")
    if rc == 0:
        client.subscribe(COMMAND_TOPIC, qos=1)
        print(f"[{datetime.now(korea_tz)}] 구독 시작 → {COMMAND_TOPIC}")


def on_publish(client, userdata, mid):
    print(f"[{datetime.now(korea_tz)}] publish 완료, mid={mid}")


def on_message(client, userdata, msg):
    global manual_cmd, controller_ip
    try:
        message = json.loads(msg.payload.decode("utf-8"))
    except json.JSONDecodeError:
        print("Invalid JSON:", msg.payload)
        return

    cmd       = message.get("cmd_string", "")
    ip_range  = message.get("ip_range")
    sender_ip = message.get("sender_ip")

    # 최초 컨트롤러 IP 저장
    if controller_ip is None and sender_ip:
        controller_ip = sender_ip
        print(f"Controller set to {controller_ip}")

    # 컨트롤러가 아니면 무시 + 알림 전송
    if sender_ip != controller_ip:
        print(f"Sender IP mismatch ({sender_ip}) → 무시")
        ignored = {
            "time": datetime.now(korea_tz).strftime("%Y-%m-%d %H:%M:%S"),
            "status": "ignored",
            "cmd_string": cmd,
            "sender_ip": sender_ip
        }
        client.publish(SENSING_TOPIC, json.dumps(ignored), qos=1)
        return

    # auto_start/auto_stop 처리
    if cmd == "auto_start":
        auto_event.set()
        print(f"[{datetime.now(korea_tz)}] → 자동 START (controller={controller_ip})")
        return
    if cmd == "auto_stop":
        auto_event.clear()
        print(f"[{datetime.now(korea_tz)}] → 자동 STOP (controller={controller_ip})")
        controller_ip = None
        print("Controller cleared")
        return

    # 수동 제어
    if cmd in ("go", "left", "right", "back"):
        manual_cmd = cmd
        manual_event.set()
        print(f"[{datetime.now(korea_tz)}] 수동 명령 → {cmd} (controller={controller_ip})")
    elif cmd in ("stop", "mid"):
        manual_event.clear()
        print(f"[{datetime.now(korea_tz)}] 수동 정지 (controller cleared)")
        controller_ip = None
        print("Controller cleared")
    elif cmd == "exit":
        auto_event.clear(); manual_event.clear();
        exit_event.set()
        client.unsubscribe(COMMAND_TOPIC)
        client.loop_stop()
        client.disconnect()
        print("Exit received, shutdown")
        
        print(f"[DEBUG] sender_ip={sender_ip}, controller_ip={controller_ip}")



def main():
    threading.Thread(target=motion_loop, daemon=True).start()

    client = mqtt.Client()
    client.on_connect  = on_connect
    client.on_message  = on_message
    client.on_publish  = on_publish

    try:
        client.connect(BROKER_ADDR, BROKER_PORT)
    except Exception as e:
        print(f"[{datetime.now(korea_tz)}] 초기 연결 실패: {e}")
        return

    client.loop_start()

    try:
        while not exit_event.is_set():
            time.sleep(0.5)
    except KeyboardInterrupt:
        exit_event.set()
        client.unsubscribe(COMMAND_TOPIC)
        client.loop_stop()
        client.disconnect()
        print("KeyboardInterrupt! 종료")

if __name__ == "__main__":
    print(f"Local IP: {LOCAL_IP}")
    main()
