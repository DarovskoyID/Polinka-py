import json
import os

from PySide6.QtWidgets import QMainWindow, QLabel, QStackedWidget
from PySide6.QtGui import QMovie
from PySide6.QtCore import QFileSystemWatcher, QTimer

from UI.Sources.jarvis import Ui_MainWindow


class MainWindow(QMainWindow):
    def activateTab(self, n):
        for i in range(len(self.stackTabs)):
            self.stackTabs[i].hide()
        self.stackTabs[n].show()

    def __init__(self, animationPath: str, log_file: str, json_file: str):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.json_path = json_file
        self.ui.setupUi(self)

        # --- табы ---
        self.stack = QStackedWidget(self)
        self.stackTabs = [self.ui.MainTab, self.ui.SettingsTab, self.ui.LogsTab]
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

        self.ui.SmallLogs.setPlainText("")
        self.ui.FullLogs.setPlainText("")

        # watcher для логов
        self.log_watcher = QFileSystemWatcher([self.log_file])
        self.log_watcher.fileChanged.connect(self.read_logs)

        # таймер на случай пропуска событий
        self.timer = QTimer()
        self.timer.setInterval(2000)
        self.timer.timeout.connect(self.read_logs)
        self.timer.start()

        # начальное чтение логов
        self.read_logs()

        # --- JSON ---
        self.text = self.ui.BaseFrases
        self.json_watcher = QFileSystemWatcher([self.json_path])
        self.json_watcher.fileChanged.connect(self.reload_json)

        self.text.textChanged.connect(self.on_text_changed)
        self.ignore_change = False
        self.reload_json()

    # ------------------------- ЛОГИ -------------------------

    def read_logs(self):
        """Полностью перечитывает лог-файл и обновляет виджеты"""
        try:
            with open(self.log_file, 'r', encoding='utf-16') as f:
                text = f.read()
        except FileNotFoundError:
            text = ""
        except Exception:
            return  # на случай ошибки чтения — просто пропускаем

        for widget in [self.ui.SmallLogs, self.ui.FullLogs]:
            widget.setPlainText(text)
            widget.verticalScrollBar().setValue(widget.verticalScrollBar().maximum())

    # ------------------------- JSON -------------------------

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
        except Exception:
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

    # ------------------------- ПРОЧЕЕ -------------------------

    def GetAnimationLabel(self):
        return self.label
