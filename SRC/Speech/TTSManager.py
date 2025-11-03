import threading
import queue
from jnius import autoclass
from SRC.Loger import _log

Locale = autoclass('java.util.Locale')
TextToSpeech = autoclass('android.speech.tts.TextToSpeech')
PythonActivity = autoclass('org.kivy.android.PythonActivity')


class TTSManager:
    def __init__(self):
        self.queue = queue.Queue()
        self.lock = threading.Lock()
        self.speed = 1.0

        self.tts = TextToSpeech(PythonActivity.mActivity, None)
        self.tts.setLanguage(Locale("ru","RU"))

        self.thread = threading.Thread(target=self._worker, daemon=True)
        self.thread.start()

    def _worker(self):
        while True:
            text = self.queue.get()
            if text is None:
                break
            try:
                with self.lock:
                    self.tts.setSpeechRate(self.speed)
                    self.tts.speak(text, TextToSpeech.QUEUE_ADD, None)
            except Exception as e:
                _log(f"[TTS] Error: {e}")

    def say(self, text: str):
        if text:
            self.queue.put(text)

    def clear(self):
        self.tts.stop()
        while not self.queue.empty():
            try: self.queue.get_nowait()
            except: break

    def stop(self):
        self.queue.put(None)
        self.thread.join(timeout=1)
        self.tts.shutdown()
