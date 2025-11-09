from kivy.resources import resource_find
import shutil
import json
import os
from SRC.Loger import _log
from kivy.app import App

# Получаем путь к папке приложения на Android
APP_DIR = App.get_running_app().user_data_dir if hasattr(App.get_running_app(), "user_data_dir") else os.getcwd()

TTS_MODEL_PATH = os.path.join(APP_DIR, "models/piper-model/ru_RU-irina-medium.onnx")
VOSK_MODEL_PATH = os.path.join(APP_DIR, "models/vosk-model-small-ru-0.22")
WAKEWORD_POLINA_MODEL_PATH = os.path.join(APP_DIR, "models/Polina_en_windows_v3_0_0.ppn")
ANIMATION_PATH = os.path.join(APP_DIR, "assets/anim/")
LOG_FILE = os.path.join(APP_DIR, "assets/log.txt")
JSON_PHRASES_FILE = os.path.join(APP_DIR, "assets/commands.json")
BILETS_NAME_FILE = os.path.join(APP_DIR, "assets/billetsTitles.txt")
BILETS_FILE = os.path.join(APP_DIR, "assets/bilets.txt")
CONFIG_JSON = os.path.join(APP_DIR, "assets/config.json")
ACCESS_KEY = None

try:
    with open(CONFIG_JSON, "r", encoding="utf-8") as f:
        ACCESS_KEY = json.load(f).get("ACCESS_KEY_PV")
except Exception as e:
    _log(f"Config error: {e}")
