# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QGridLayout, QHBoxLayout,
    QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QMainWindow, QPlainTextEdit, QPushButton, QSizePolicy,
    QTextEdit, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(900, 600)
        MainWindow.setStyleSheet(u"QMainWindow { background-color: black; }")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setStyleSheet(u"background-color: black;")
        self.mainLayout = QVBoxLayout(self.centralwidget)
        self.mainLayout.setObjectName(u"mainLayout")
        self.topLayout = QHBoxLayout()
        self.topLayout.setObjectName(u"topLayout")
        self.ipSection = QVBoxLayout()
        self.ipSection.setObjectName(u"ipSection")
        self.ipListWidget = QListWidget(self.centralwidget)
        self.ipListWidget.setObjectName(u"ipListWidget")
        self.ipListWidget.setSelectionMode(QAbstractItemView.SingleSelection)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ipListWidget.sizePolicy().hasHeightForWidth())
        self.ipListWidget.setSizePolicy(sizePolicy)
        self.ipListWidget.setStyleSheet(u"QListWidget { background-color: #111111; color: white; border: 1px solid white; border-radius: 5px; font-size: 14px; padding: 4px; } QListWidget::item:selected { background-color: white; color: black; }")

        self.ipSection.addWidget(self.ipListWidget)

        self.ipRegisterLayout = QHBoxLayout()
        self.ipRegisterLayout.setObjectName(u"ipRegisterLayout")
        self.ipLabel = QLabel(self.centralwidget)
        self.ipLabel.setObjectName(u"ipLabel")
        self.ipLabel.setStyleSheet(u"color: white; font-size: 14px;")

        self.ipRegisterLayout.addWidget(self.ipLabel)

        self.ipRangeInput = QLineEdit(self.centralwidget)
        self.ipRangeInput.setObjectName(u"ipRangeInput")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(1)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.ipRangeInput.sizePolicy().hasHeightForWidth())
        self.ipRangeInput.setSizePolicy(sizePolicy1)
        self.ipRangeInput.setStyleSheet(u"background-color: #111111; color: white; border: 1px solid white; border-radius: 5px; padding: 4px;")

        self.ipRegisterLayout.addWidget(self.ipRangeInput)

        self.addIpButton = QPushButton(self.centralwidget)
        self.addIpButton.setObjectName(u"addIpButton")
        self.addIpButton.setStyleSheet(u"background-color: #444444; color: white; border: 1px solid white; border-radius: 5px; padding: 6px 12px; font-size: 14px;")

        self.ipRegisterLayout.addWidget(self.addIpButton)


        self.ipSection.addLayout(self.ipRegisterLayout)


        self.topLayout.addLayout(self.ipSection)

        self.chatSection = QVBoxLayout()
        self.chatSection.setObjectName(u"chatSection")
        self.chatLog = QTextEdit(self.centralwidget)
        self.chatLog.setObjectName(u"chatLog")
        self.chatLog.setReadOnly(True)
        self.chatLog.setStyleSheet(u"background-color: #111111; color: white; border: 1px solid white; border-radius: 5px; font-size: 14px; padding: 8px;")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy2.setHorizontalStretch(1)
        sizePolicy2.setVerticalStretch(1)
        sizePolicy2.setHeightForWidth(self.chatLog.sizePolicy().hasHeightForWidth())
        self.chatLog.setSizePolicy(sizePolicy2)

        self.chatSection.addWidget(self.chatLog)

        self.chatInputLayout = QHBoxLayout()
        self.chatInputLayout.setObjectName(u"chatInputLayout")
        self.ipLabel1 = QLabel(self.centralwidget)
        self.ipLabel1.setObjectName(u"ipLabel1")
        self.ipLabel1.setStyleSheet(u"color: white; font-size: 14px;")

        self.chatInputLayout.addWidget(self.ipLabel1)

        self.chatInput = QLineEdit(self.centralwidget)
        self.chatInput.setObjectName(u"chatInput")
        self.chatInput.setStyleSheet(u"background-color: #111111; color: white; border: 1px solid white; border-radius: 5px; padding: 4px;")
        sizePolicy1.setHeightForWidth(self.chatInput.sizePolicy().hasHeightForWidth())
        self.chatInput.setSizePolicy(sizePolicy1)

        self.chatInputLayout.addWidget(self.chatInput)

        self.sendChatButton = QPushButton(self.centralwidget)
        self.sendChatButton.setObjectName(u"sendChatButton")
        self.sendChatButton.setStyleSheet(u"background-color: #444444; color: white; border: 1px solid white; border-radius: 5px; padding: 6px 12px; font-size: 14px;")

        self.chatInputLayout.addWidget(self.sendChatButton)


        self.chatSection.addLayout(self.chatInputLayout)


        self.topLayout.addLayout(self.chatSection)


        self.mainLayout.addLayout(self.topLayout)

        self.textLayout = QHBoxLayout()
        self.textLayout.setObjectName(u"textLayout")
        self.logText = QPlainTextEdit(self.centralwidget)
        self.logText.setObjectName(u"logText")
        self.logText.setStyleSheet(u"background-color: #111111; color: white; border: 1px solid white; border-radius: 10px; font-size: 14px; padding: 8px;")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.logText.sizePolicy().hasHeightForWidth())
        self.logText.setSizePolicy(sizePolicy3)

        self.textLayout.addWidget(self.logText)

        self.sensingText = QPlainTextEdit(self.centralwidget)
        self.sensingText.setObjectName(u"sensingText")
        self.sensingText.setStyleSheet(u"background-color: #111111; color: white; border: 1px solid white; border-radius: 10px; font-size: 14px; padding: 8px;")
        sizePolicy3.setHeightForWidth(self.sensingText.sizePolicy().hasHeightForWidth())
        self.sensingText.setSizePolicy(sizePolicy3)

        self.textLayout.addWidget(self.sensingText)


        self.mainLayout.addLayout(self.textLayout)

        self.buttonSection = QHBoxLayout()
        self.buttonSection.setObjectName(u"buttonSection")
        self.allControlsLeft = QVBoxLayout()
        self.allControlsLeft.setObjectName(u"allControlsLeft")
        self.startButtonLeft = QPushButton(self.centralwidget)
        self.startButtonLeft.setObjectName(u"startButtonLeft")
        self.startButtonLeft.setStyleSheet(u"QPushButton { background-color: green; color: white; border: 2px solid white; border-radius: 10px; padding: 12px 24px; font-size: 16px; font-weight: bold; } QPushButton:disabled { background-color: #444444; color: #aaaaaa; border: 2px solid #666666; }")

        self.allControlsLeft.addWidget(self.startButtonLeft)

        self.stopButtonLeft = QPushButton(self.centralwidget)
        self.stopButtonLeft.setObjectName(u"stopButtonLeft")
        self.stopButtonLeft.setStyleSheet(u"QPushButton { background-color: red; color: white; border: 2px solid white; border-radius: 10px; padding: 12px 24px; font-size: 16px; font-weight: bold; } QPushButton:disabled { background-color: #444444; color: #aaaaaa; border: 2px solid #666666; }")

        self.allControlsLeft.addWidget(self.stopButtonLeft)


        self.buttonSection.addLayout(self.allControlsLeft)

        self.gridButtons = QGridLayout()
        self.gridButtons.setObjectName(u"gridButtons")
        self.goButton = QPushButton(self.centralwidget)
        self.goButton.setObjectName(u"goButton")
        self.goButton.setStyleSheet(u"QPushButton { background-color: black; color: white; border: 2px solid white; border-radius: 10px; padding: 12px 24px; font-size: 16px; font-weight: bold; } QPushButton:disabled { background-color: #444444; color: #aaaaaa; border: 2px solid #666666; } QPushButton:pressed { background-color: yellow; color: black; }")

        self.gridButtons.addWidget(self.goButton, 0, 1, 1, 1)

        self.leftButton = QPushButton(self.centralwidget)
        self.leftButton.setObjectName(u"leftButton")
        self.leftButton.setStyleSheet(u"QPushButton { background-color: black; color: white; border: 2px solid white; border-radius: 10px; padding: 12px 24px; font-size: 16px; font-weight: bold; } QPushButton:disabled { background-color: #444444; color: #aaaaaa; border: 2px solid #666666; } QPushButton:pressed { background-color: yellow; color: black; }")

        self.gridButtons.addWidget(self.leftButton, 1, 0, 1, 1)

        self.midButton = QPushButton(self.centralwidget)
        self.midButton.setObjectName(u"midButton")
        self.midButton.setStyleSheet(u"QPushButton { background-color: black; color: white; border: 2px solid white; border-radius: 10px; padding: 12px 24px; font-size: 16px; font-weight: bold; } QPushButton:disabled { background-color: #444444; color: #aaaaaa; border: 2px solid #666666; }")

        self.gridButtons.addWidget(self.midButton, 1, 1, 1, 1)

        self.rightButton = QPushButton(self.centralwidget)
        self.rightButton.setObjectName(u"rightButton")
        self.rightButton.setStyleSheet(u"QPushButton { background-color: black; color: white; border: 2px solid white; border-radius: 10px; padding: 12px 24px; font-size: 16px; font-weight: bold; } QPushButton:disabled { background-color: #444444; color: #aaaaaa; border: 2px solid #666666; } QPushButton:pressed { background-color: yellow; color: black; }")

        self.gridButtons.addWidget(self.rightButton, 1, 2, 1, 1)

        self.backButton = QPushButton(self.centralwidget)
        self.backButton.setObjectName(u"backButton")
        self.backButton.setStyleSheet(u"QPushButton { background-color: black; color: white; border: 2px solid white; border-radius: 10px; padding: 12px 24px; font-size: 16px; font-weight: bold; } QPushButton:disabled { background-color: #444444; color: #aaaaaa; border: 2px solid #666666; } QPushButton:pressed { background-color: yellow; color: black; }")

        self.gridButtons.addWidget(self.backButton, 2, 1, 1, 1)


        self.buttonSection.addLayout(self.gridButtons)

        self.allControlsRight = QVBoxLayout()
        self.allControlsRight.setObjectName(u"allControlsRight")
        self.startButton = QPushButton(self.centralwidget)
        self.startButton.setObjectName(u"startButton")
        self.startButton.setStyleSheet(u"QPushButton { background-color: green; color: white; border: 2px solid white; border-radius: 10px; padding: 12px 24px; font-size: 16px; font-weight: bold; } QPushButton:disabled { background-color: #444444; color: #aaaaaa; border: 2px solid #666666; }")

        self.allControlsRight.addWidget(self.startButton)

        self.stopButton = QPushButton(self.centralwidget)
        self.stopButton.setObjectName(u"stopButton")
        self.stopButton.setEnabled(False)
        self.stopButton.setStyleSheet(u"QPushButton { background-color: red; color: white; border: 2px solid white; border-radius: 10px; padding: 12px 24px; font-size: 16px; font-weight: bold; } QPushButton:disabled { background-color: #444444; color: #aaaaaa; border: 2px solid #666666; }")

        self.allControlsRight.addWidget(self.stopButton)


        self.buttonSection.addLayout(self.allControlsRight)


        self.mainLayout.addLayout(self.buttonSection)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"AGV Controller", None))
        self.ipLabel.setText(QCoreApplication.translate("MainWindow", u"IP Range:", None))
        self.ipRangeInput.setPlaceholderText(QCoreApplication.translate("MainWindow", u"e.g. 192.168.0.0/24", None))
        self.addIpButton.setText(QCoreApplication.translate("MainWindow", u"Add", None))
        self.ipLabel1.setText(QCoreApplication.translate("MainWindow", u"AI Command : ", None))
        self.chatInput.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Type message", None))
        self.sendChatButton.setText(QCoreApplication.translate("MainWindow", u"Send", None))
        self.startButtonLeft.setText(QCoreApplication.translate("MainWindow", u"All Start", None))
        self.stopButtonLeft.setText(QCoreApplication.translate("MainWindow", u"All Stop", None))
        self.goButton.setText(QCoreApplication.translate("MainWindow", u"Go", None))
        self.leftButton.setText(QCoreApplication.translate("MainWindow", u"Left", None))
        self.midButton.setText(QCoreApplication.translate("MainWindow", u"Mid", None))
        self.rightButton.setText(QCoreApplication.translate("MainWindow", u"Right", None))
        self.backButton.setText(QCoreApplication.translate("MainWindow", u"Back", None))
        self.startButton.setText(QCoreApplication.translate("MainWindow", u"Start", None))
        self.stopButton.setText(QCoreApplication.translate("MainWindow", u"Stop", None))
    # retranslateUi

