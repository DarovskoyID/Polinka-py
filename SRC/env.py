import json
import os
from SRC.Loger import _log

TTS_MODEL_PATH = "./models/piper-model/ru_RU-irina-medium.onnx"
WHISPER_MODEL_PATH = "./models/whisper-model/"
WAKEWORD_POLINA_MODEL_PATH = "./models/Polina_en_windows_v3_0_0.ppn"
ANIMATION_PATH = "./UI/Raw/animation.gif"
LOG_FILE = "./assets/log.txt"
JSON_PHRASES_FILE = "./assets/commands.json"
BILETS_NAME_FILE = "./assets/billetsTitles.txt"
BILETS_FILE = "./assets/bilets.txt"
CONFIG_JSON = "./assets/config.json"

ACCESS_KEY = None
try:
    ACCESS_KEY = json.load(open(CONFIG_JSON, "r", encoding="utf-8"))["ACCESS_KEY_PV"]
except Exception as e:
    _log(f"Config error: {e}")
