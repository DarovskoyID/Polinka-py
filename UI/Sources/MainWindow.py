from PySide6.QtGui import QMovie
from PySide6.QtWidgets import QMainWindow, QStackedWidget, QLabel

from UI.Sources.jarvis import Ui_MainWindow


class MainWindow(QMainWindow):
    def activateTab(self, n):
        for i in range(len(self.stackTabs)):
            self.stackTabs[i].hide()
        self.stackTabs[n].show()
    def __init__(self, animationPath : str):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.stack = QStackedWidget(self)
        self.stackTabs = []
        self.stackTabs.append(self.ui.MainTab)
        self.stackTabs.append(self.ui.SettingsTab)
        self.stackTabs.append(self.ui.LogsTab)
        self.activateTab(0)
        self.ui.Home.clicked.connect(lambda: self.activateTab(0))
        self.ui.Settings.clicked.connect(lambda: self.activateTab(1))
        self.ui.Logs.clicked.connect(lambda: self.activateTab(2))

        self.label = QLabel()
        self.ui.Animation.layout().addWidget(self.label)
        self.movie = QMovie(animationPath)
        self.label.setMovie(self.movie)
        self.movie.start()

        self.ui.SmallLogs.setPlainText("")

    def PushText(self, text):
        self.ui.SmallLogs.insertPlainText(text)
