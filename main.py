import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="ctranslate2")

import asyncio
from qasync import QEventLoop
from PySide6.QtWidgets import QApplication

from SRC.SpeechController import SpeechController
from UI.Sources.MainWindow import MainWindow

from SRC.env import *

def main():
    app = QApplication([])
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)



    try:
        window = MainWindow(ANIMATION_PATH, LOG_FILE, JSON_PHRASES_FILE)
        window.show()

        # создаём SpeechController
        speechController = SpeechController(
            fileTitles=BILETS_NAME_FILE,
            fileTickets=BILETS_FILE,
            window=window,
            tts_model=TTS_MODEL_PATH,
            wakeword_model_path=WAKEWORD_POLINA_MODEL_PATH,
            access_key=ACCESS_KEY
        )

        # запускаем прослушивание wakeword и поток TTS
        # чтение названий стартует только по второму пику
        with loop:
            loop.run_forever()

    finally:
        pass

if __name__ == '__main__':
    main()
