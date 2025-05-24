#!/usr/bin/env python3
import sys
import json
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

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # --- 초기 버튼 상태 ---
        self.ui.stopButton.setEnabled(False)        # 일반 Stop
        self.ui.stopButtonLeft.setEnabled(False)    # All Stop
        # midButton 사용하지 않음
        self.ui.midButton.hide()

        # --- 시그널 연결 ---
        self.ui.startButton.clicked.connect(self.on_start)
        self.ui.stopButton.clicked.connect(self.on_stop)
        self.ui.startButtonLeft.clicked.connect(self.on_all_start)
        self.ui.stopButtonLeft.clicked.connect(self.on_all_stop)

        # MQTT 초기화 및 연결
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(BROKER_ADDR, BROKER_PORT)
        self.client.loop_start()
        self.client.subscribe(SENSING_TOPIC, qos=1)

        # 수동 명령 버튼: 누르고 있는 동안 동작, 떼면 중지
        self.ui.goButton.pressed.connect(lambda: self.send_cmd("go", 100, 1))
        self.ui.goButton.released.connect(lambda: self.send_cmd("stop", 0, 1))
        self.ui.leftButton.pressed.connect(lambda: self.send_cmd("left", 100, 1))
        self.ui.leftButton.released.connect(lambda: self.send_cmd("stop", 0, 1))
        self.ui.rightButton.pressed.connect(lambda: self.send_cmd("right", 100, 1))
        self.ui.rightButton.released.connect(lambda: self.send_cmd("stop", 0, 1))
        self.ui.backButton.pressed.connect(lambda: self.send_cmd("back", 100, 1))
        self.ui.backButton.released.connect(lambda: self.send_cmd("stop", 0, 1))

        # IP 추가/삭제
        self.ui.addIpButton.clicked.connect(self.add_ip_range)
        self.ui.ipListWidget.itemDoubleClicked.connect(self.remove_ip_item)

        # 채팅
        self.ui.sendChatButton.clicked.connect(self.send_chat)

        # 데이터 리스트
        self.commandDataList = []
        self.sensorData      = []

        # UI 업데이트 타이머
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(500)

    def make_cmd(self, cmd_str, arg=0, finish=0):
        now = datetime.now(korea_timezone)
        return {
            "time": now.strftime("%Y-%m-%d %H:%M:%S"),
            "cmd_string": cmd_str,
            "arg_string": arg,
            "is_finish": finish
        }

    def send_cmd(self, name, arg, finish):
        cmd = self.make_cmd(name, arg, finish)
        item = self.ui.ipListWidget.currentItem()
        if item:
            cmd["ip_range"] = item.text()
        self.client.publish(COMMAND_TOPIC, json.dumps(cmd), qos=1)
        self.commandDataList.append(cmd)
        print(f"[{name.upper()}] → {cmd}")

    # --- 일반 Start/Stop 핸들러 ---
    def on_start(self):
        # IP 리스트 확인
        if self.ui.ipListWidget.count() == 0:
            QMessageBox.warning(self, "알림", "IP를 입력하세요")
            return

        # UI 토글
        widgets = (
            self.ui.startButton, self.ui.stopButton,
            self.ui.goButton, self.ui.leftButton, self.ui.rightButton, self.ui.backButton,
            self.ui.startButtonLeft, self.ui.stopButtonLeft
        )
        for w in widgets:
            w.setEnabled(False)
            self.ui.stopButton.setEnabled(True)        # 일반 Stop

        # MQTT 발행: 선택된 IP
        cmd = self.make_cmd("auto_start")
        item = self.ui.ipListWidget.currentItem()
        cmd["ip_range"] = item.text()
        self.client.publish(COMMAND_TOPIC, json.dumps(cmd), qos=1)
        self.commandDataList.append(cmd)

    def on_stop(self):
        # IP 리스트 확인
        if self.ui.ipListWidget.count() == 0:
            QMessageBox.warning(self, "알림", "IP를 입력하세요")
            return

        # UI 토글
        widgets = (
            self.ui.startButton, self.ui.stopButton,
            self.ui.goButton, self.ui.leftButton, self.ui.rightButton, self.ui.backButton,
            self.ui.startButtonLeft, self.ui.stopButtonLeft
        )
        for w in widgets:
            w.setEnabled(True)
        self.ui.stopButton.setEnabled(False)
        self.ui.stopButtonLeft.setEnabled(False)

        # MQTT 발행: 선택된 IP
        cmd = self.make_cmd("auto_stop")
        item = self.ui.ipListWidget.currentItem()
        cmd["ip_range"] = item.text()
        self.client.publish(COMMAND_TOPIC, json.dumps(cmd), qos=1)
        self.commandDataList.append(cmd)

    # --- All Start/Stop 핸들러 ---
    def on_all_start(self):
        # 확인 대화상자
        dlg = QMessageBox(self)
        dlg.setWindowTitle("경고")
        dlg.setText("모든 AGV 가 동작합니다! 실행하시겠습니까?")
        dlg.setIcon(QMessageBox.Warning)
        dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        dlg.button(QMessageBox.Yes).setText("확인")
        dlg.button(QMessageBox.No).setText("취소")
        dlg.setDefaultButton(QMessageBox.No)

        if dlg.exec() == QMessageBox.Yes:
            # IP 리스트 확인
            if self.ui.ipListWidget.count() == 0:
                QMessageBox.warning(self, "알림", "IP를 입력하세요")
                return

            # UI 토글
            widgets = (
                self.ui.startButtonLeft, self.ui.stopButtonLeft,
                self.ui.startButton, self.ui.stopButton,
                self.ui.goButton, self.ui.leftButton, self.ui.rightButton, self.ui.backButton
            )
            for w in widgets:
                w.setEnabled(False)
            self.ui.stopButtonLeft.setEnabled(True)

            # MQTT 발행: All
            cmd = self.make_cmd("auto_start")
            cmd["ip_range"] = "All"
            self.client.publish(COMMAND_TOPIC, json.dumps(cmd), qos=1)
            self.commandDataList.append(cmd)

    def on_all_stop(self):
        # UI 토글
        widgets = (
            self.ui.startButtonLeft, self.ui.stopButtonLeft,
            self.ui.startButton, self.ui.stopButton,
            self.ui.goButton, self.ui.leftButton, self.ui.rightButton, self.ui.backButton
        )
        for w in widgets:
            w.setEnabled(True)
        self.ui.stopButton.setEnabled(False)
        self.ui.stopButtonLeft.setEnabled(False)

        # MQTT 발행: All
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
                f"{i:2d} | {c['time']} | {c['cmd_string']} | {c.get('ip_range', '')}"
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
