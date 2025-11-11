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
AudioSource = autoclass("android.media.MediaRecorder$AudioSource")

# ===========================================================
# WakeWordListener: ловит пики (ANDROID), без pvporcupine
# ===========================================================
class WakeWord:
    def __init__(self, accuracy=5000, hold_time=0.10, cooldown=0.33):
        self.event_queue = queue.Queue()
        self.running = threading.Event()
        self.running.set()

        # === ANDROID INPUT ===
        # no pyaudio, using AudioRecord
        self.sample_rate = 16000  # стандартная частота для микрофона
        self.frame_length = 512   # произвольная длина буфера
        buffer_size = self.frame_length * 2

        self._record = AudioRecord(
            AudioSource.MIC,
            self.sample_rate,
            AudioFormat.CHANNEL_IN_MONO,
            AudioFormat.ENCODING_PCM_16BIT,
            buffer_size
        )
        self._record.startRecording()

        self.audio_thread = threading.Thread(
            target=self._audio_loop,
            args=(accuracy, hold_time, cooldown),
            daemon=True
        )
        self.audio_thread.start()


    def _audio_loop(self, accuracy, hold_time, cooldown):
        while self.running.is_set():
            try:
                # read raw pcm from android
                buf = bytearray(self.frame_length * 2)
                read = self._record.read(buf, 0, len(buf))
                if read <= 0:
                    continue

                pcm = struct.unpack_from("h" * self.frame_length, buf)

                # Loud sound detection (pip)
                amplitude = np.abs(np.array(pcm, dtype=np.int16)).mean()
                #_log(str(amplitude))
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
