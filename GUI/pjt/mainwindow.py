#!/usr/bin/env python3
import sys
import json
import socket
from datetime import datetime

import paho.mqtt.client as mqtt
import pytz
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QListWidgetItem, QMessageBox, QLineEdit
)
from PySide6.QtCore import QTimer, QThread, Signal

from ui_form import Ui_MainWindow
from openai import OpenAI

import subprocess

# 한국 시간대 설정
korea_timezone = pytz.timezone("Asia/Seoul")

# MQTT 브로커 설정
BROKER_ADDR   = "172.20.10.6"
BROKER_PORT   = 1883
COMMAND_TOPIC = "AGV/command"
SENSING_TOPIC = "AGV/sensing"

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime
import time
import random as rd

# 서비스 계정 키 파일 경로를 설정
# key 이름은 각 팀마다 생성한 키 이름으로 변경한다.
cred = credentials.Certificate('firebase.json')

# Firebase Admin SDK 초기화
firebase_admin.initialize_app(cred)

# Firestore 클라이언트 초기화
db = firestore.client()

# 한국 시간대 (Asia/Seoul)로 설정
korea_timezone = pytz.timezone("Asia/Seoul")

# 특정 컬렉션에 데이터 추가 예제
def write_data(collection_name, data):
    doc_ref = db.collection(collection_name).document()
    doc_ref.set(data)
    print(f'Data written to {collection_name}/')

# 특정 컬렉션의 모든 문서 데이터 조회 예제
def read_data(collection_name):
    collection_ref = db.collection(collection_name)
    docs = collection_ref.stream()
    data = {doc.id: doc.to_dict() for doc in docs}
    return data

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except:
        return ""
    finally:
        s.close()

LOCAL_IP = get_local_ip()


def get_response(sentense):

    # api_key =
    # warehouse manager 역할 부여, GO/LEFT/... 규칙 정의
    content = (
        "You are an warehouse manager. I will input a specific sentence about the current situation, "
        "and you need to interpret the sentence and respond with either 'GO' , 'LEFT', 'RIGHT', 'BACK', "
        "'STOP', 'AUTO' with numbers or a word 'All' in the back. Do not provide any explanation, "
        "only respond with the specific word. "
        "ex1) I need to buy some groceries after work. -> 'IGNORE' , "
        "ex2) go number 7. -> 'GO 7', ex3) move number 10 to left -> 'LEFT 10', "
        "ex4) number 3 to back -> 'BACK 3' ex5) See today's amount and start the work -> 'AUTO 60' "
        "ex6) move number 11 to front -> 'GO 11' ex7) move number 13 and 50 -> 'GO 13 50' "
        "ex8) stop all -> 'STOP All' ex9) 14 is too fast -> 'STOP 14'"
    )

    bot = OpenAI(api_key=api_key)
    response = bot.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": content},
            {"role": "user",   "content": sentense}
        ],
        max_tokens=256,
        temperature=1,
        top_p=1.0,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response.choices[0].message.content.strip()


class ChatWorker(QThread):
    result_ready = Signal(str)

    def __init__(self, msg: str):
        super().__init__()
        self.msg = msg

    def run(self):
        resp = get_response(self.msg)
        # 앞에 붙는 " >> " 를 포함해서 전달
        self.result_ready.emit(" >> " + resp)


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # print(read_data('IP_addresses'))

        IP_ADDRESS_LIST = read_data('IP_addresses')

        for info in IP_ADDRESS_LIST.values():
            self.ui.ipListWidget.addItem(QListWidgetItem(info['IP'] + " - " + info['name']))


        # 온스크린 키보드 토글
        self.ui.chatInput.mousePressEvent = lambda event: (
            subprocess.Popen(["onboard"]),
            QLineEdit.mousePressEvent(self.ui.chatInput, event)
        )

        # 초기 버튼 상태 설정
        self.ui.stopButton.setEnabled(False)
        self.ui.stopButtonLeft.setEnabled(False)
        self.ui.midButton.hide()

        # 버튼 시그널 연결
        self.ui.startButton.clicked.connect(self.on_start)
        self.ui.stopButton.clicked.connect(self.on_stop)
        self.ui.startButtonLeft.clicked.connect(self.on_all_start)
        self.ui.stopButtonLeft.clicked.connect(self.on_all_stop)

        # 수동 명령: 눌렀을 때만 발행
        for btn, cmd in ((self.ui.goButton, "go"),
                         (self.ui.leftButton, "left"),
                         (self.ui.rightButton, "right"),
                         (self.ui.backButton, "back")):
            btn.pressed.connect(lambda c=cmd: self.manual_start(c))
            btn.released.connect(self.manual_stop)

        # IP 추가/삭제
        self.ui.addIpButton.clicked.connect(self.add_ip_range)
        self.ui.ipListWidget.itemDoubleClicked.connect(self.remove_ip_item)

        # 채팅
        self.ui.sendChatButton.clicked.connect(self.send_chat)

        # 로그 및 센싱 데이터 저장소
        self.commandDataList = []
        self.sensorData      = []

        # UI 업데이트 타이머
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(500)

        # MQTT 클라이언트 초기화 (연결은 비동기로)
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.loop_start()

        # 화면 표시 후 MQTT 연결 시도
        QTimer.singleShot(0, self.start_mqtt)

    def start_mqtt(self):
        """앱 로드 직후 한 번만 호출되어야 하는 연결 시도"""
        try:
            self.client.connect_async(BROKER_ADDR, BROKER_PORT)
            self.client.subscribe(SENSING_TOPIC, qos=1)
        except Exception as e:
            QMessageBox.warning(self, "MQTT 연결 오류", f"브로커에 연결할 수 없습니다:\n{e}")

    def make_cmd(self, cmd_str, arg=0, finish=0):
        now = datetime.now(korea_timezone)
        return {
            "time": now.strftime("%Y-%m-%d %H:%M:%S"),
            "cmd_string": cmd_str,
            "arg_string": arg,
            "is_finish": finish,
            "sender_ip": LOCAL_IP
        }

    def send_cmd(self, name, arg, finish, ip_range):
        cmd = self.make_cmd(name, arg, finish)
        cmd["ip_range"] = ip_range.split(' ')[0]
        self.client.publish(COMMAND_TOPIC, json.dumps(cmd), qos=1)
        self.commandDataList.append(cmd)

        sendingData = {'command' : cmd["cmd_string"], 'receive_IP' : cmd["ip_range"], 'send_IP' : cmd["sender_ip"], 'time' : cmd["time"]}

        write_data('manual_activities', sendingData)

        print(f"[{name.upper()}] → {cmd}")

    def manual_start(self, name):
        if self.ui.ipListWidget.count() == 0:
            QMessageBox.warning(self, "Warning", "Enter IP!")
            return
        for w in (self.ui.startButton, self.ui.stopButton,
                  self.ui.startButtonLeft, self.ui.stopButtonLeft):
            w.setEnabled(False)
        # 좌표 없이 호출된 기존 수동은 arg=100, finish=1, ip_range=현재 선택된 항목
        item = self.ui.ipListWidget.currentItem()
        ipr = item.text() if item else ""
        self.send_cmd(name, 100, 1, ipr)

    def manual_stop(self):
        for w in (self.ui.startButton, self.ui.startButtonLeft):
            w.setEnabled(True)
        # stop도 ip_list 기반
        item = self.ui.ipListWidget.currentItem()
        ipr = item.text() if item else ""
        self.send_cmd("stop", 0, 1, ipr)

    def on_start(self):
        if self.ui.ipListWidget.count() == 0:
            QMessageBox.warning(self, "Warning", "Enter IP!")
            return
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Confirm")
        dlg.setText("Selected AGV will start moving! Proceed??")
        dlg.setIcon(QMessageBox.Question)
        dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        dlg.button(QMessageBox.Yes).setText("Yes")
        dlg.button(QMessageBox.No).setText("No")
        dlg.setDefaultButton(QMessageBox.No)
        if dlg.exec() != QMessageBox.Yes:
            return
        for w in (self.ui.goButton, self.ui.leftButton,
                  self.ui.rightButton, self.ui.backButton,
                  self.ui.startButton, self.ui.startButtonLeft,
                  self.ui.stopButtonLeft):
            w.setEnabled(False)
        self.ui.stopButton.setEnabled(True)
        ipr = self.ui.ipListWidget.currentItem().text()
        self.send_cmd("auto_start", 0, 0, ipr)

    def on_stop(self):
        if self.ui.ipListWidget.count() == 0:
            QMessageBox.warning(self, "Warning", "Enter IP!")
            return
        for w in (self.ui.goButton, self.ui.leftButton,
                  self.ui.rightButton, self.ui.backButton,
                  self.ui.startButton, self.ui.startButtonLeft,
                  self.ui.stopButtonLeft, self.ui.stopButton):
            w.setEnabled(True)
        self.ui.stopButton.setEnabled(False)
        self.ui.stopButtonLeft.setEnabled(False)
        ipr = self.ui.ipListWidget.currentItem().text()
        self.send_cmd("auto_stop", 0, 0, ipr)

    def on_all_start(self):
        if self.ui.ipListWidget.count() == 0:
            QMessageBox.warning(self, "Warning", "Enter IP!")
            return
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Confirm")
        dlg.setText("All AGV will start moving! Proceed??")
        dlg.setIcon(QMessageBox.Question)
        dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        dlg.button(QMessageBox.Yes).setText("Yes")
        dlg.button(QMessageBox.No).setText("No")
        dlg.setDefaultButton(QMessageBox.No)
        if dlg.exec() != QMessageBox.Yes:
            return
        for w in (self.ui.goButton, self.ui.leftButton,
                  self.ui.rightButton, self.ui.backButton,
                  self.ui.startButton, self.ui.stopButton,
                  self.ui.stopButtonLeft):
            w.setEnabled(False)
        self.ui.startButtonLeft.setEnabled(False)
        self.ui.stopButtonLeft.setEnabled(True)
        self.send_cmd("auto_start", 0, 0, "All")

    def on_all_stop(self):
        for w in (self.ui.goButton, self.ui.leftButton,
                  self.ui.rightButton, self.ui.backButton,
                  self.ui.startButton, self.ui.stopButton,
                  self.ui.startButtonLeft, self.ui.stopButtonLeft):
            w.setEnabled(True)
        self.ui.stopButton.setEnabled(False)
        self.ui.stopButtonLeft.setEnabled(False)
        self.send_cmd("auto_stop", 0, 0, "All")

    def add_ip_range(self):
        ip_text = self.ui.ipRangeInput.text().strip()
        if ip_text:
            self.ui.ipListWidget.addItem(QListWidgetItem(ip_text))
            self.ui.ipRangeInput.clear()

    def remove_ip_item(self, item):
        row = self.ui.ipListWidget.row(item)
        self.ui.ipListWidget.takeItem(row)

    def display_bot_response(self, response: str):
        # UI에 출력
        self.ui.chatLog.append(response)
        # " >> GO 7" 같은 prefix 제거하고 실제 명령 파싱
        cmd = response.lstrip(" >")
        self.process_bot_command(cmd.strip())

    def process_bot_command(self, cmd: str):

        if cmd[0]=="\'":
            temp = cmd[1:len(cmd)-1]
            cmd = temp

        parts = cmd.split()
        if not parts:
            return

        action = parts[0].upper()
        args   = parts[1:]


        print(action)
        print(args)


        # GO/BACK/LEFT/RIGHT
        if action in ("GO","BACK","LEFT","RIGHT"):
            for arg in args:
                if arg.isdigit():
                    ipr = f"172.20.10.{int(arg)}"
                    self.send_cmd(action.lower(), 0, 1, ipr)

        # STOP
        elif action == "STOP":
            for arg in args:
                if arg.upper() == "ALL":
                    self.on_all_stop()
                elif arg.isdigit():
                    ipr = f"172.20.10.{int(arg)}"
                    self.send_cmd("stop", 0, 1, ipr)

        # AUTO (단일 IP)
        elif action == "AUTO":
            for arg in args:
                if arg.isdigit():
                    ipr = f"172.20.10.{int(arg)}"
                    self.send_cmd("auto_start", 0, 0, ipr)

        # AUTO_ALL (전체 반복)
        elif action == "AUTO_ALL" and args:
            count = int(args[0]) if args[0].isdigit() else 1
            for _ in range(count):
                self.send_cmd("auto_start", 0, 0, "All")

    def send_chat(self):
        msg = self.ui.chatInput.text().strip()
        if msg:
            self.ui.chatLog.append(msg)
            self.ui.chatInput.clear()
            self.chat_thread = ChatWorker(msg)
            self.chat_thread.result_ready.connect(self.display_bot_response)
            self.chat_thread.start()

    def update_ui(self):
        self.ui.logText.clear()
        for i, c in enumerate(self.commandDataList, 1):
            self.ui.logText.appendPlainText(
                f"{i:2d} | {c['time']} | {c['cmd_string']} | "
                f"{c.get('ip_range','')} | {c['sender_ip']}"
            )
        self.ui.sensingText.clear()
        for i, s in enumerate(self.sensorData[-15:], 1):
            if s.get("status") == "ignored":
                self.ui.sensingText.appendPlainText(
                    f"{i:2d} | {s['time']} | IGNORED {s.get('cmd_string')} "
                    f"from {s.get('sender_ip')}"
                )
            else:
                self.ui.sensingText.appendPlainText(f"{i:2d} | {s.get('time','')}")

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("MQTT connected")
        else:
            print(f"MQTT 연결 실패, 코드={rc}")

    def on_message(self, client, userdata, msg):
        data = json.loads(msg.payload.decode())
        self.sensorData.append(data)

    def closeEvent(self, event):
        self.client.loop_stop()
        self.client.disconnect()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(800, 480)
    window.show()
    sys.exit(app.exec())
