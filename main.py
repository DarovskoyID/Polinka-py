import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="ctranslate2")
import asyncio
from qasync import QEventLoop

from PySide6.QtWidgets import QApplication

from SRC.RecordMicro import record_seconds
from SRC.WakeWord import WakeWord
from SRC.Whisper import Whisper
from UI.Sources.MainWindow import MainWindow






WHISPER_MODEL_PATH = "./models/whisper-model"
WAKEWORD_POLINA_MODEL_PATH = "./models/Polina_en_windows_v3_0_0.ppn"
ANIMATION_PATH = "./UI/Raw/animation.gif"
LOG_FILE = "./log.txt"

def Recog(window, whisperASR, filelog):
    path, sr = record_seconds()
    result = whisperASR.Recognize(path)

    tmp = result + '\n'
    print(tmp)
    filelog.write(tmp)
    window.PushText(tmp)

def WakeWordDetected(window, filelog):
    infoText = "!++++++++++++ \n"
    filelog.write(infoText)
    window.PushText(infoText)

def main():
    app = QApplication([])
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    filelog = open(LOG_FILE, 'a+', encoding='utf-16')

    try:
        window = MainWindow(ANIMATION_PATH, LOG_FILE)
        window.show()

        whisperASR = Whisper(WHISPER_MODEL_PATH)
        wakeword = WakeWord(
            [], [WAKEWORD_POLINA_MODEL_PATH],
            [
                (WakeWordDetected, (window, filelog), {}),
                (Recog, (window, whisperASR, filelog), {}),
            ],
            window.ui.Animation
        )

        wakeword.StartListning()

        with loop:
            loop.run_forever()
    finally:
        filelog.close()


if __name__ == '__main__': main()


