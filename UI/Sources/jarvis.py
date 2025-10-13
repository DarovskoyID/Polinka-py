# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'jarvis.ui'
##
## Created by: Qt User Interface Compiler version 6.10.0
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
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QHBoxLayout,
    QLabel, QLineEdit, QMainWindow, QPlainTextEdit,
    QPushButton, QSizePolicy, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(500, 800)
        self.Main = QWidget(MainWindow)
        self.Main.setObjectName(u"Main")
        self.verticalLayout_3 = QVBoxLayout(self.Main)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.Tabs = QWidget(self.Main)
        self.Tabs.setObjectName(u"Tabs")
        self.Tabs.setStyleSheet(u"#Tabs{\n"
"background-color: rgb(13, 13, 13);\n"
"}\n"
"QPushButton {\n"
"    background-color: #0f0f1a;\n"
"    color: #00f0ff;\n"
"    border: 2px solid #00f0ff;\n"
"    border-radius: 12px;\n"
"    padding: 8px 16px;\n"
"    font-family: \"Segoe UI\", \"Roboto\", sans-serif;\n"
"    font-size: 14px;\n"
"    font-weight: bold;\n"
"    letter-spacing: 1px;\n"
"    text-transform: uppercase;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #1a1a2e;\n"
"    border: 2px solid #00ffee;\n"
"    color: #ffffff;\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: #00f0ff;\n"
"    color: #0f0f1a;\n"
"    border: 2px solid #00f0ff;\n"
"}\n"
"")
        self.horizontalLayout_2 = QHBoxLayout(self.Tabs)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.Home = QPushButton(self.Tabs)
        self.Home.setObjectName(u"Home")

        self.horizontalLayout_2.addWidget(self.Home)

        self.Settings = QPushButton(self.Tabs)
        self.Settings.setObjectName(u"Settings")

        self.horizontalLayout_2.addWidget(self.Settings)

        self.Logs = QPushButton(self.Tabs)
        self.Logs.setObjectName(u"Logs")

        self.horizontalLayout_2.addWidget(self.Logs)


        self.verticalLayout_3.addWidget(self.Tabs)

        self.SettingsTab = QWidget(self.Main)
        self.SettingsTab.setObjectName(u"SettingsTab")
        self.SettingsTab.setStyleSheet(u"#SettingsTab{\n"
"	background-color: rgb(30, 37, 47);\n"
"}\n"
"QLabel {\n"
"color: rgb(255, 255, 255);\n"
"}")
        self.verticalLayout = QVBoxLayout(self.SettingsTab)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.labelOpenAi = QLabel(self.SettingsTab)
        self.labelOpenAi.setObjectName(u"labelOpenAi")
        self.labelOpenAi.setMinimumSize(QSize(0, 30))
        self.labelOpenAi.setStyleSheet(u" font: 14pt \"Segoe UI\";  ")
        self.labelOpenAi.setLineWidth(1)

        self.verticalLayout.addWidget(self.labelOpenAi)

        self.AIKeyOpenAi = QLineEdit(self.SettingsTab)
        self.AIKeyOpenAi.setObjectName(u"AIKeyOpenAi")
        self.AIKeyOpenAi.setStyleSheet(u"QLineEdit {\n"
"    background-color: rgba(0, 30, 60, 180); /* \u0442\u0451\u043c\u043d\u043e-\u0441\u0438\u043d\u0438\u0439 \u0444\u043e\u043d \u0441 \u043f\u0440\u043e\u0437\u0440\u0430\u0447\u043d\u043e\u0441\u0442\u044c\u044e */\n"
"    color: #00ffff;                         /* \u044f\u0440\u043a\u043e-\u0433\u043e\u043b\u0443\u0431\u043e\u0439 \u0442\u0435\u043a\u0441\u0442 */\n"
"    border: 2px solid #00bfff;              /* \u044f\u0440\u043a\u0438\u0439 \u0441\u0438\u043d\u0438\u0439 \u043a\u043e\u043d\u0442\u0443\u0440 */\n"
"    border-radius: 10px;                     /* \u0441\u043a\u0440\u0443\u0433\u043b\u0451\u043d\u043d\u044b\u0435 \u0443\u0433\u043b\u044b */\n"
"    padding: 5px 10px;                       /* \u0432\u043d\u0443\u0442\u0440\u0435\u043d\u043d\u0438\u0435 \u043e\u0442\u0441\u0442\u0443\u043f\u044b */\n"
"    font: 14pt \"Segoe UI\";                   /* \u0441\u043e\u0432\u0440\u0435\u043c\u0435\u043d\u043d\u044b\u0439 \u0448\u0440\u0438\u0444\u0442 */\n"
"}\n"
"\n"
"QLineEdit:"
                        "focus {\n"
"    border: 2px solid #00ffff;              /* \u043f\u043e\u0434\u0441\u0432\u0435\u0442\u043a\u0430 \u043f\u0440\u0438 \u0444\u043e\u043a\u0443\u0441\u0435 */\n"
"    background-color: rgba(0, 50, 100, 200); /* \u0447\u0443\u0442\u044c \u044f\u0440\u0447\u0435 \u0444\u043e\u043d */\n"
"    color: #ffffff;                          /* \u0442\u0435\u043a\u0441\u0442 \u0441\u0442\u0430\u043d\u043e\u0432\u0438\u0442\u0441\u044f \u0431\u0435\u043b\u044b\u043c \u043f\u0440\u0438 \u0444\u043e\u043a\u0443\u0441\u0435 */\n"
"}\n"
"\n"
"QLineEdit::placeholder {\n"
"    color: #00bfff;                          /* \u0446\u0432\u0435\u0442 \u043f\u043b\u0435\u0439\u0441\u0445\u043e\u043b\u0434\u0435\u0440\u0430 */\n"
"    font-style: italic;\n"
"}\n"
"")

        self.verticalLayout.addWidget(self.AIKeyOpenAi)

        self.label_choose = QLabel(self.SettingsTab)
        self.label_choose.setObjectName(u"label_choose")
        self.label_choose.setStyleSheet(u" font: 14pt \"Segoe UI\";  ")

        self.verticalLayout.addWidget(self.label_choose)

        self.widget = QWidget(self.SettingsTab)
        self.widget.setObjectName(u"widget")
        self.widget.setStyleSheet(u"QPushButton {\n"
"    background-color: #111111;        /* \u043f\u043e\u0447\u0442\u0438 \u0447\u0451\u0440\u043d\u044b\u0439 \u0444\u043e\u043d */\n"
"    color: #ffffff;                   /* \u0431\u0435\u043b\u044b\u0439 \u0442\u0435\u043a\u0441\u0442 */\n"
"    border: 2px solid #1E90FF;        /* \u0441\u0438\u043d\u0438\u0435 \u0430\u043a\u0446\u0435\u043d\u0442\u044b */\n"
"    border-radius: 8px;\n"
"    padding: 8px 16px;\n"
"    font-size: 14px;\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"/* \u041d\u0430\u0432\u0435\u0434\u0435\u043d\u0438\u0435 */\n"
"QPushButton:hover {\n"
"    background-color: #1E90FF;        /* \u043f\u043e\u0434\u0441\u0432\u0435\u0442\u043a\u0430 \u0441\u0438\u043d\u0438\u043c */\n"
"    color: #ffffff;                   /* \u0431\u0435\u043b\u044b\u0439 \u0442\u0435\u043a\u0441\u0442 */\n"
"    border: 2px solid #1E90FF;\n"
"}\n"
"\n"
"/* \u041d\u0430\u0436\u0430\u0442\u0438\u0435 */\n"
"QPushButton:pressed {\n"
"    background-color: #0f65b5;        /* \u0431\u043e\u043b\u0435"
                        "\u0435 \u0442\u0451\u043c\u043d\u044b\u0439 \u0441\u0438\u043d\u0438\u0439 */\n"
"    border: 2px solid #0f65b5;\n"
"}\n"
"\n"
"/* \u041d\u0435\u0430\u043a\u0442\u0438\u0432\u043d\u0430\u044f \u043a\u043d\u043e\u043f\u043a\u0430 */\n"
"QPushButton:disabled {\n"
"    background-color: #1a1a1a;        /* \u0442\u0451\u043c\u043d\u043e-\u0441\u0435\u0440\u044b\u0439 */\n"
"    border: 2px solid #333333;        /* \u0442\u0443\u0441\u043a\u043b\u0430\u044f \u0440\u0430\u043c\u043a\u0430 */\n"
"    color: #777777;                   /* \u0441\u0435\u0440\u044b\u0439 \u0442\u0435\u043a\u0441\u0442 */\n"
"}\n"
"")
        self.horizontalLayout = QHBoxLayout(self.widget)
        self.horizontalLayout.setSpacing(5)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(5, 0, 5, 0)
        self.vosk_choose = QPushButton(self.widget)
        self.vosk_choose.setObjectName(u"vosk_choose")
        self.vosk_choose.setEnabled(False)

        self.horizontalLayout.addWidget(self.vosk_choose)

        self.whisper_choose = QPushButton(self.widget)
        self.whisper_choose.setObjectName(u"whisper_choose")
        self.whisper_choose.setEnabled(True)
        self.whisper_choose.setCheckable(False)

        self.horizontalLayout.addWidget(self.whisper_choose)


        self.verticalLayout.addWidget(self.widget)

        self.label_basePhrase = QLabel(self.SettingsTab)
        self.label_basePhrase.setObjectName(u"label_basePhrase")
        self.label_basePhrase.setMinimumSize(QSize(0, 30))
        self.label_basePhrase.setStyleSheet(u" font: 14pt \"Segoe UI\";  ")

        self.verticalLayout.addWidget(self.label_basePhrase)

        self.BaseFrases = QPlainTextEdit(self.SettingsTab)
        self.BaseFrases.setObjectName(u"BaseFrases")
        self.BaseFrases.setStyleSheet(u"background-color: rgb(0, 0, 0);\n"
"color: rgb(255, 255, 255);")

        self.verticalLayout.addWidget(self.BaseFrases)


        self.verticalLayout_3.addWidget(self.SettingsTab)

        self.LogsTab = QWidget(self.Main)
        self.LogsTab.setObjectName(u"LogsTab")
        self.gridLayout_3 = QGridLayout(self.LogsTab)
        self.gridLayout_3.setSpacing(0)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.FullLogs = QPlainTextEdit(self.LogsTab)
        self.FullLogs.setObjectName(u"FullLogs")
        self.FullLogs.setStyleSheet(u"background-color: rgb(0, 0, 0);\n"
"color: rgb(255, 255, 255);")

        self.gridLayout_3.addWidget(self.FullLogs, 0, 0, 1, 1)


        self.verticalLayout_3.addWidget(self.LogsTab)

        self.MainTab = QWidget(self.Main)
        self.MainTab.setObjectName(u"MainTab")
        self.MainTab.setEnabled(True)
        self.verticalLayout_2 = QVBoxLayout(self.MainTab)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.line = QFrame(self.MainTab)
        self.line.setObjectName(u"line")
        self.line.setStyleSheet(u"background-color: rgb(58, 58, 58);")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_2.addWidget(self.line)

        self.Animation = QWidget(self.MainTab)
        self.Animation.setObjectName(u"Animation")
        self.Animation.setStyleSheet(u"background-color: rgb(30, 37, 47);")
        self.gridLayout_2 = QGridLayout(self.Animation)
        self.gridLayout_2.setObjectName(u"gridLayout_2")

        self.verticalLayout_2.addWidget(self.Animation)

        self.line_2 = QFrame(self.MainTab)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setStyleSheet(u"background-color: rgb(58, 58, 58);")
        self.line_2.setFrameShape(QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_2.addWidget(self.line_2)

        self.logs = QWidget(self.MainTab)
        self.logs.setObjectName(u"logs")
        self.gridLayout = QGridLayout(self.logs)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.SmallLogs = QPlainTextEdit(self.logs)
        self.SmallLogs.setObjectName(u"SmallLogs")
        self.SmallLogs.setStyleSheet(u"background-color: rgb(0, 0, 0);\n"
"color: rgb(255, 255, 255);")

        self.gridLayout.addWidget(self.SmallLogs, 0, 0, 1, 1)


        self.verticalLayout_2.addWidget(self.logs)

        self.verticalLayout_2.setStretch(1, 10)
        self.verticalLayout_2.setStretch(3, 3)

        self.verticalLayout_3.addWidget(self.MainTab)

        MainWindow.setCentralWidget(self.Main)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.Home.setText(QCoreApplication.translate("MainWindow", u"\u0413\u043b\u0430\u0432\u043d\u0430\u044f", None))
        self.Settings.setText(QCoreApplication.translate("MainWindow", u"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438", None))
        self.Logs.setText(QCoreApplication.translate("MainWindow", u"\u041b\u041e\u0413\u0418", None))
        self.labelOpenAi.setText(QCoreApplication.translate("MainWindow", u"\u041a\u043b\u044e\u0447 AI", None))
        self.AIKeyOpenAi.setText("")
        self.label_choose.setText(QCoreApplication.translate("MainWindow", u"ASR(automatic speech recognition) AI", None))
        self.vosk_choose.setText(QCoreApplication.translate("MainWindow", u"VOSK", None))
        self.whisper_choose.setText(QCoreApplication.translate("MainWindow", u"WHISPER", None))
        self.label_basePhrase.setText(QCoreApplication.translate("MainWindow", u"\u0411\u0430\u0437\u043e\u0432\u044b\u0435 \u0444\u0440\u0430\u0437\u044b", None))
        self.BaseFrases.setPlainText(QCoreApplication.translate("MainWindow", u"{\n"
"lddld:fddd\n"
"}", None))
        self.FullLogs.setPlainText(QCoreApplication.translate("MainWindow", u"gfhfhfhfhfhfhdfjdsjd", None))
        self.SmallLogs.setPlainText(QCoreApplication.translate("MainWindow", u"not initilize", None))
    # retranslateUi

