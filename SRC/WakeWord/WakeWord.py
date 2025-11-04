import time
import threading
import queue
import numpy as np
import struct
from SRC.Loger import _log

from jnius import autoclass

AudioRecord = autoclass('android.media.AudioRecord')
AudioFormat = autoclass('android.media.AudioFormat')
MediaRecorder = autoclass('android.media.MediaRecorder')


# ===========================================================
# WakeWordListener: ловит "Polina" (через простой метод)
# ===========================================================
class WakeWord:
    def __init__(self, accuracy=5000, hold_time=0.10, cooldown=0.33):
        self.event_queue = queue.Queue()
        self.running = threading.Event()
        self.running.set()

        # === ANDROID INPUT ===
        self.samplerate = 16000
        self.chunk_duration = 0.2
        self.chunk_size = int(self.samplerate * self.chunk_duration)
        buffer_size = self.chunk_size * 2  # 16bit PCM

        self._record = AudioRecord(
            MediaRecorder.AudioSource.MIC,
            self.samplerate,
            AudioFormat.CHANNEL_IN_MONO,
            AudioFormat.ENCODING_PCM_16BIT,
            buffer_size
        )
        self._record.startRecording()

        # переменные для пиков
        self._loud_start = None
        self._last_peak_time = 0
        self._peak_count = 0
        self._last_event_time = 0

        # слово Polina
        self.wakeword = "polina"
        self.audio_thread = threading.Thread(target=self._audio_loop, args=(accuracy, hold_time, cooldown), daemon=True)
        self.audio_thread.start()


    def _detect_wakeword(self, pcm):
        """
        Простая имитация wakeword: проверка амплитуды и структуры,
        чтобы не ломать event_queue. Тут можно вставить ML/ASR позже.
        """
        # Т.к. готового offline ASR на Android через Python нет,
        # ловим "Polina" условно: например, если rms > threshold
        rms = np.sqrt(np.mean(pcm ** 2))
        if rms > 0.1:  # условный порог, просто пример
            return True
        return False


    def _audio_loop(self, accuracy, hold_time, cooldown):
        buf = bytearray(self.chunk_size * 2)

        while self.running.is_set():
            try:
                read = self._record.read(buf, 0, len(buf))
                if read <= 0:
                    continue

                pcm = np.frombuffer(buf, dtype=np.int16).astype(np.float32) / 32768.0

                # --- WakeWord detection ---
                if self._detect_wakeword(pcm):
                    self.event_queue.put(("wakeword", time.time()))

                # --- Loud sound detection (pip) ---
                amplitude = np.abs(pcm).mean()
                now = time.time()

                if amplitude > accuracy:
                    if self._loud_start is None:
                        self._loud_start = now
                    elif now - self._loud_start > hold_time:
                        if now - self._last_peak_time > cooldown:
                            self._peak_count += 1
                            self._last_peak_time = now
                        self._loud_start = None
                else:
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
        try:
            self._record.stop()
            self._record.release()
        except:
            pass
