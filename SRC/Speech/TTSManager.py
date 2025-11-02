import threading
import queue
import numpy as np
import piper

from SRC.Loger import _log

from jnius import autoclass

AudioTrack = autoclass('android.media.AudioTrack')
AudioFormat = autoclass('android.media.AudioFormat')
AudioManager = autoclass('android.media.AudioManager')


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

    def _play_android(self, pcm_f32, rate):
        # convert float32 → int16 PCM
        pcm16 = np.int16(np.clip(pcm_f32, -1, 1) * 32767).tobytes()

        track = AudioTrack(
            AudioManager.STREAM_MUSIC,
            rate,
            AudioFormat.CHANNEL_OUT_MONO,
            AudioFormat.ENCODING_PCM_16BIT,
            len(pcm16),
            AudioTrack.MODE_STATIC
        )
        track.write(pcm16, 0, len(pcm16))
        track.play()

        # ждём окончания
        while track.getPlaybackHeadPosition() < len(pcm16) // 2:
            pass

        track.stop()
        track.release()

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
                        pcm = np.concatenate(chunks)
                        self._play_android(pcm, rate)
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
