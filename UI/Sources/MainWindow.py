import json
import os

from PySide6.QtWidgets import QMainWindow, QLabel, QStackedWidget
from PySide6.QtGui import QMovie, QTextCursor
from PySide6.QtCore import QFileSystemWatcher, QTimer

from UI.Sources.jarvis import Ui_MainWindow


class MainWindow(QMainWindow):
    def activateTab(self, n):
        for i in range(len(self.stackTabs)):
            self.stackTabs[i].hide()
        self.stackTabs[n].show()

    def __init__(self, animationPath: str, log_file: str, json_file : str):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.json_path = json_file
        self.ui.setupUi(self)
        # --- табы ---
        self.stack = QStackedWidget(self)
        self.stackTabs = []
        self.stackTabs.append(self.ui.MainTab)
        self.stackTabs.append(self.ui.SettingsTab)
        self.stackTabs.append(self.ui.LogsTab)
        self.activateTab(0)
        self.ui.Home.clicked.connect(lambda: self.activateTab(0))
        self.ui.Settings.clicked.connect(lambda: self.activateTab(1))
        self.ui.Logs.clicked.connect(lambda: self.activateTab(2))

        # --- анимация ---
        self.label = QLabel()
        self.ui.Animation.layout().addWidget(self.label)
        self.movie = QMovie(animationPath)
        self.label.setMovie(self.movie)
        self.movie.start()

        # --- лог ---
        self.log_file = log_file
        self.log_pos = 0

        self.ui.SmallLogs.setPlainText("")
        self.ui.FullLogs.setPlainText("")

        # watcher для файла
        self.watcher = QFileSystemWatcher([self.log_file])
        self.watcher.fileChanged.connect(self.read_new_lines)

        # таймер на случай пропуска событий
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.read_new_lines)
        self.timer.start()

        # начальное чтение
        self.read_new_lines()

        #json
        self.text = self.ui.BaseFrases
        self.watcher = QFileSystemWatcher([self.json_path])
        self.watcher.fileChanged.connect(self.reload_json)

        self.text.textChanged.connect(self.on_text_changed)
        self.ignore_change = False
        self.reload_json()

    def read_new_lines(self):
        """Читает только новые строки и добавляет в оба виджета"""
        try:
            with open(self.log_file, 'r', encoding='utf-16') as f:
                f.seek(self.log_pos)
                new_text = f.read()
                if new_text:
                    for widget in [self.ui.SmallLogs, self.ui.FullLogs]:
                        widget.moveCursor(QTextCursor.End)  # <-- здесь исправлено
                        widget.insertPlainText(new_text)
                        widget.verticalScrollBar().setValue(widget.verticalScrollBar().maximum())
                self.log_pos = f.tell()
        except FileNotFoundError:
            pass

    def reload_json(self):
        if not os.path.exists(self.json_path):
            return
        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            text = json.dumps(data, indent=4, ensure_ascii=False)
            self.ignore_change = True
            self.text.setPlainText(text)
            self.ignore_change = False
        except Exception as e:
            pass

    def on_text_changed(self):
        if self.ignore_change:
            return
        QTimer.singleShot(500, self.save_json)

    def save_json(self):
        if self.ignore_change:
            return
        try:
            data = json.loads(self.text.toPlainText())
            with open(self.json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception:
            # Игнорируем, если текст еще невалидный JSON
            pass

    def PushText(self, text):
        for widget in [self.ui.SmallLogs, self.ui.FullLogs]:
            widget.moveCursor(QTextCursor.End)
            widget.insertPlainText(text)
            widget.verticalScrollBar().setValue(widget.verticalScrollBar().maximum())

    def GetAnimationLabel(self):
        return self.label
