#!/usr/bin/env python3
import sys
import json
import socket
from datetime import datetime

import paho.mqtt.client as mqtt
import pytz
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QListWidgetItem, QMessageBox
)
from PySide6.QtCore import QTimer

from ui_form import Ui_MainWindow

# 한국 시간대 설정
korea_timezone = pytz.timezone("Asia/Seoul")

# MQTT 브로커 설정
BROKER_ADDR   = "172.20.10.6"
BROKER_PORT   = 1883
COMMAND_TOPIC = "AGV/command"
SENSING_TOPIC = "AGV/sensing"


def get_local_ip():
    # 로컬 IP 획득
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except:
        return ""
    finally:
        s.close()

LOCAL_IP = get_local_ip()

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # 초기 버튼 상태
        self.ui.stopButton.setEnabled(False)
        self.ui.stopButtonLeft.setEnabled(False)
        self.ui.midButton.hide()  # midButton 숨김

        # 시그널 연결
        self.ui.startButton.clicked.connect(self.on_start)
        self.ui.stopButton.clicked.connect(self.on_stop)
        self.ui.startButtonLeft.clicked.connect(self.on_all_start)
        self.ui.stopButtonLeft.clicked.connect(self.on_all_stop)

        # MQTT 초기화 및 구독
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(BROKER_ADDR, BROKER_PORT)
        self.client.loop_start()
        self.client.subscribe(SENSING_TOPIC, qos=1)

        # 수동 명령: 누를 때만 동작
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

        # 로그
        self.commandDataList = []
        self.sensorData      = []

        # UI 업데이트 타이머
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(500)

    def make_cmd(self, cmd_str, arg=0, finish=0):
        """공통 필드 생성 + sender_ip 자동 추가"""
        now = datetime.now(korea_timezone)
        return {
            "time": now.strftime("%Y-%m-%d %H:%M:%S"),
            "cmd_string": cmd_str,
            "arg_string": arg,
            "is_finish": finish,
            "sender_ip": LOCAL_IP
        }

    def send_cmd(self, name, arg, finish):
        """MQTT로 발행 (ip_range + sender_ip 포함)"""
        cmd = self.make_cmd(name, arg, finish)
        item = self.ui.ipListWidget.currentItem()
        if item:
            cmd["ip_range"] = item.text()
        self.client.publish(COMMAND_TOPIC, json.dumps(cmd), qos=1)
        self.commandDataList.append(cmd)
        print(f"[{name.upper()}] → {cmd}")

    def manual_start(self, name):
        # IP 검사
        if self.ui.ipListWidget.count() == 0:
            QMessageBox.warning(self, "Warning", "Enter IP!")
            return
        # 자동 버튼 비활성화
        for w in (self.ui.startButton, self.ui.stopButton,
                  self.ui.startButtonLeft, self.ui.stopButtonLeft):
            w.setEnabled(False)
        # 발행
        self.send_cmd(name, 100, 1)

    def manual_stop(self):
        # 자동 버튼 복구
        for w in (self.ui.startButton, self.ui.startButtonLeft):
            w.setEnabled(True)
        # 중지 명령 발행
        self.send_cmd("stop", 0, 1)

    def on_start(self):
        # IP 검사
        if self.ui.ipListWidget.count() == 0:
            QMessageBox.warning(self, "Warning", "Enter IP!")
            return
        # 확인창
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
        # UI toggle
        for w in (self.ui.startButton, self.ui.stopButton,
                  self.ui.goButton, self.ui.leftButton,
                  self.ui.rightButton, self.ui.backButton,
                  self.ui.startButtonLeft, self.ui.stopButtonLeft):
            w.setEnabled(False)
        self.ui.stopButton.setEnabled(True)
        # 발행
        cmd = self.make_cmd("auto_start")
        cmd["ip_range"] = self.ui.ipListWidget.currentItem().text()
        self.client.publish(COMMAND_TOPIC, json.dumps(cmd), qos=1)
        self.commandDataList.append(cmd)

    def on_stop(self):
        # IP 검사
        if self.ui.ipListWidget.count() == 0:
            QMessageBox.warning(self, "Warning", "Enter IP!")
            return
        # UI toggle
        for w in (self.ui.startButton, self.ui.stopButton,
                  self.ui.goButton, self.ui.leftButton,
                  self.ui.rightButton, self.ui.backButton,
                  self.ui.startButtonLeft, self.ui.stopButtonLeft):
            w.setEnabled(True)
        self.ui.stopButton.setEnabled(False)
        self.ui.stopButtonLeft.setEnabled(False)
        # 발행
        cmd = self.make_cmd("auto_stop")
        cmd["ip_range"] = self.ui.ipListWidget.currentItem().text()
        self.client.publish(COMMAND_TOPIC, json.dumps(cmd), qos=1)
        self.commandDataList.append(cmd)

    def on_all_start(self):
        # IP 검사
        if self.ui.ipListWidget.count() == 0:
            QMessageBox.warning(self, "Warning", "Enter IP!")
            return
        # 확인창
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Confirm")
        dlg.setText("All AGV will start moving! Proceed???")
        dlg.setIcon(QMessageBox.Question)
        dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        dlg.button(QMessageBox.Yes).setText("Yes")
        dlg.button(QMessageBox.No).setText("No")
        dlg.setDefaultButton(QMessageBox.No)
        if dlg.exec() != QMessageBox.Yes:
            return
        # UI toggle
        for w in (self.ui.startButtonLeft, self.ui.stopButtonLeft,
                  self.ui.startButton, self.ui.stopButton,
                  self.ui.goButton, self.ui.leftButton,
                  self.ui.rightButton, self.ui.backButton):
            w.setEnabled(False)
        self.ui.stopButtonLeft.setEnabled(True)
        # 발행
        cmd = self.make_cmd("auto_start")
        cmd["ip_range"] = "All"
        self.client.publish(COMMAND_TOPIC, json.dumps(cmd), qos=1)
        self.commandDataList.append(cmd)

    def on_all_stop(self):
        # UI toggle
        for w in (self.ui.startButtonLeft, self.ui.stopButtonLeft,
                  self.ui.startButton, self.ui.stopButton,
                  self.ui.goButton, self.ui.leftButton,
                  self.ui.rightButton, self.ui.backButton):
            w.setEnabled(True)
        self.ui.stopButton.setEnabled(False)
        self.ui.stopButtonLeft.setEnabled(False)
        # 발행
        cmd = self.make_cmd("auto_stop")
        cmd["ip_range"] = "All"
        self.client.publish(COMMAND_TOPIC, json.dumps(cmd), qos=1)
        self.commandDataList.append(cmd)

    def add_ip_range(self):
        ip_text = self.ui.ipRangeInput.text().strip()
        if ip_text:
            self.ui.ipListWidget.addItem(QListWidgetItem(ip_text))
            self.ui.ipRangeInput.clear()

    def remove_ip_item(self, item):
        row = self.ui.ipListWidget.row(item)
        self.ui.ipListWidget.takeItem(row)

    def send_chat(self):
        msg = self.ui.chatInput.text().strip()
        if msg:
            self.ui.chatLog.append(msg)
            self.ui.chatInput.clear()

    def update_ui(self):
        self.ui.logText.clear()
        for i, c in enumerate(self.commandDataList, 1):
            self.ui.logText.appendPlainText(
                f"{i:2d} | {c['time']} | {c['cmd_string']} | {c.get('ip_range','')} | {c['sender_ip']}"
            )
        self.ui.sensingText.clear()
        for i, s in enumerate(self.sensorData[-15:], 1):
            time_str = s.get("time", "")
            self.ui.sensingText.appendPlainText(f"{i:2d} | {time_str}")

    def on_connect(self, client, userdata, flags, rc):
        print("MQTT connected" if rc == 0 else f"Connect failed: {rc}")

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
    window.show()
    sys.exit(app.exec())
