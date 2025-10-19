import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="ctranslate2")

import asyncio
from qasync import QEventLoop
from SRC.SpeechController import SpeechController
from PySide6.QtWidgets import QApplication


from UI.Sources.MainWindow import MainWindow


ACCESS_KEY = "uHmVJfEIx6ynqIPc4DeQAiLClCio/4FtDwkqUu3p2yehntyj3USUYQ=="

TTS_MODEL_PATH = "./models/piper-model/ru_RU-irina-medium.onnx"
WHISPER_MODEL_PATH = "./models/whisper-model/"
WAKEWORD_POLINA_MODEL_PATH = "./models/Polina_en_windows_v3_0_0.ppn"
KOKORO_MODEL_PATH = "./models/kokoro-model/kokoro-v1.0.int8.onnx"
KOKORO_VOICES_MODEL_PATH = "./models/kokoro-model/voices-v1.0.bin"
ANIMATION_PATH = "./UI/Raw/animation.gif"
LOG_FILE = "./log.txt"
JSON_PHRASES_FILE = "./commands.json"
BILETS_NAME_FILE = "./billetsTitles.txt"
BILETS_FILE = "./bilets.txt"

def main():

    app = QApplication([])
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    filelog = open(LOG_FILE, 'a+', encoding='utf-16')

    try:
        window = MainWindow(ANIMATION_PATH, LOG_FILE, JSON_PHRASES_FILE)
        window.show()
        spechController = SpeechController(
            WHISPER_MODEL_PATH,
            WAKEWORD_POLINA_MODEL_PATH,
            TTS_MODEL_PATH,
            ACCESS_KEY,
            window,
            filelog,
            # JSON_PHRASES_FILE,
            BILETS_NAME_FILE,
            BILETS_FILE,
        )

        spechController.Start()
        with loop:
            loop.run_forever()
    finally:
        filelog.close()


if __name__ == '__main__': main()


