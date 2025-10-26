import time
import threading
import queue
import numpy as np
import struct
import pyaudio
import pvporcupine
from SRC.Loger import _log

# ===========================================================
# WakeWordListener: ловит "полина" и пики
# ===========================================================
class WakeWord:
    def __init__(self, window, wakeword_model_path, access_key, accuracy = 8000, hold_time = 0.01, cooldown = 0.1):
        self.window = window
        self.event_queue = queue.Queue()
        self.running = threading.Event()
        self.running.set()

        self.porcupine = pvporcupine.create(keyword_paths=[wakeword_model_path], access_key=access_key)
        self.pa = pyaudio.PyAudio()
        self.stream = self.pa.open(
            rate=self.porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self.porcupine.frame_length
        )

        self.audio_thread = threading.Thread(target=self._audio_loop, args={accuracy, hold_time, cooldown}, daemon=True)
        self.audio_thread.start()


    def _audio_loop(self, accuracy, hold_time, cooldown):
        loud_start = None
        while self.running.is_set():
            try:
                pcm_bytes = self.stream.read(self.porcupine.frame_length, exception_on_overflow=False)
                if len(pcm_bytes) != self.porcupine.frame_length * 2:
                    continue
                pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm_bytes)

                # WakeWord detection
                keyword_index = self.porcupine.process(pcm)
                if keyword_index >= 0:
                    self.event_queue.put(("wakeword", time.time()))

                # Loud sound detection (pip)
                amplitude = np.abs(np.array(pcm, dtype=np.int16)).mean()
                now = time.time()

                if not hasattr(self, "_loud_start"):
                    self._loud_start = None
                if not hasattr(self, "_last_peak_time"):
                    self._last_peak_time = 0
                if not hasattr(self, "_peak_count"):
                    self._peak_count = 0
                if not hasattr(self, "_last_event_time"):
                    self._last_event_time = 0

                if amplitude > accuracy:
                    if self._loud_start is None:
                        self._loud_start = now
                    elif now - self._loud_start > hold_time:
                        # если прошло достаточно времени от прошлого пика
                        if now - self._last_peak_time > cooldown:
                            self._peak_count += 1
                            self._last_peak_time = now
                        # сбрасываем начало громкости, чтобы не ловить один и тот же пик
                        self._loud_start = None
                else:
                    # если была тишина дольше cooldown — значит серия пиков закончилась
                    if self._peak_count > 0 and now - self._last_peak_time > cooldown:
                        self.event_queue.put(("pip", self._peak_count))
                        self._last_event_time = now
                        self._peak_count = 0
                    self._loud_start = None
            except Exception as e:
                _log(f"[WakeWordListener] Audio error: {e}")

    def stop(self):
        self.running.clear()
        self.audio_thread.join(timeout=1)
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.pa:
            self.pa.terminate()
        if self.porcupine:
            self.porcupine.delete()

