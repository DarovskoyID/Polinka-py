import asyncio
from time import sleep

from PySide6.QtCore import QEasingCurve, QVariantAnimation, QPropertyAnimation, QSequentialAnimationGroup, QTimer
from PySide6.QtGui import QColor
from qasync import QEventLoop

from PySide6.QtWidgets import QApplication

from SRC.RecordMicro import record_seconds
from SRC.WakeWord import WakeWord
from SRC.Whisper import Whisper
from UI.Sources.MainWindow import MainWindow

WHISPER_MODEL_PATH = "./models/whisper-model"
ANIMATION_PATH = "./UI/Raw/animation.gif"

def Recog(window, whisperASR):
    path, sr = record_seconds()
    result = whisperASR.Recognize(path)

    tmp = result + '\n'
    print(tmp)

    window.PushText(tmp)

def main():
    app = QApplication([])
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = MainWindow(ANIMATION_PATH)
    window.show()
    whisperASR = Whisper(WHISPER_MODEL_PATH)
    wakeword = WakeWord(["jarvis"],
                        [
                            (Recog, (window, whisperASR, ), {}),

                        ],
                        window.ui.Animation)

    wakeword.StartListning()

    with loop:
        loop.run_forever()



if __name__ == '__main__': main()


