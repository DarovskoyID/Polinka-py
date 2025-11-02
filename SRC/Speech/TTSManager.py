import threading
import queue
import numpy as np
import sounddevice as sd
import piper

from SRC.Loger import _log

class TTSManager:
    def __init__(self, tts_model):
        try:
            self.voice = piper.PiperVoice.load(tts_model)
        except Exception as e:
            _log(e)
        self.queue = queue.Queue()
        self.lock = threading.Lock()
        self.speed = 1.0
        self.thread = threading.Thread(target=self._worker, daemon=True)
        self.thread.start()

    def _worker(self):
        while True:
            text = self.queue.get()
            if text is None:
                break
            try:
                with self.lock:
                    chunks = [c.audio_float_array for c in self.voice.synthesize(text)]
                    if chunks:
                        rate = int(self.voice.config.sample_rate * self.speed)
                        sd.play(np.concatenate(chunks), samplerate=rate)
                        sd.wait()
            except Exception as e:
                _log(f"[TTS] Error: {e}")

    def say(self, text):
        if text:
            self.queue.put(text)

    def clear(self):
        while not self.queue.empty():
            try:
                self.queue.get_nowait()
            except queue.Empty:
                break

    def stop(self):
        self.queue.put(None)
        self.thread.join(timeout=1)