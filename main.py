import asyncio
from qasync import QEventLoop

from PySide6.QtWidgets import QApplication

from SRC.RecordMicro import record_seconds
from SRC.Whisper import Whisper
from UI.Sources.MainWindow import MainWindow

WHISPER_MODEL_PATH = "./models/whisper-model"
ANIMATION_PATH = "./UI/Raw/animation.gif"

async def Recog(window, whisperASR):
    loop = asyncio.get_event_loop()

    # Тяжёлая синхронная работа выполняется в отдельном потоке
    path, sr = await loop.run_in_executor(None, record_seconds)
    result = await loop.run_in_executor(None, whisperASR.Recognize, path)

    tmp = result + '\n'
    print(tmp)

    # Обновляем GUI (если PushText обычная функция PyQt)
    window.PushText(tmp)

def main():
    app = QApplication([])
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = MainWindow(ANIMATION_PATH)
    window.show()
    whisperASR = Whisper(WHISPER_MODEL_PATH)

    # Запуск Recog в фоне
    asyncio.ensure_future(Recog(window, whisperASR))

    with loop:
        loop.run_forever()



if __name__ == '__main__': main()


