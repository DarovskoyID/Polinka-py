import time
import numpy as np
import pvporcupine
import pyaudio
import struct
import threading
import queue


class WakeWord:
    def __init__(self, window, filelog, wakeWords=["jarvis"], keywordPaths=[], callBacks=None, key=""):
        self.window = window
        self.filelog = filelog
        self.wakeWords = wakeWords
        self.keywordPaths = keywordPaths
        self.callBacks = callBacks or []  # список [(func, args, kwargs)]

        self.porcupine = pvporcupine.create(
            keywords=wakeWords,
            keyword_paths=keywordPaths,
            access_key=key
        )

        self.flagListing = True
        self.pa = None
        self.stream = None

        self.thread_audio = None
        self.worker_thread = None

        self.event_queue = queue.Queue()

        # Для сброса цепочек
        self.session_id = 0
        self.stop_event = threading.Event()

    def __del__(self):
        try:
            self.flagListing = False
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
            if self.pa:
                self.pa.terminate()
            if self.porcupine:
                self.porcupine.delete()
        except Exception as e:
            self.filelog.write(f"Destructor error: {e}\n")
            self.window.PushText(f"Destructor error: {e}\n")

    # ===================================================================
    # Основной цикл чтения аудио
    # ===================================================================
    def _audio_reader_loop(self, volume_threshold=10000, min_duration=0.5):
        loud_start = None
        while self.flagListing:
            try:
                pcm_bytes = self.stream.read(self.porcupine.frame_length, exception_on_overflow=False)
                pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm_bytes)

                # --- Wake word detection ---
                keyword_index = self.porcupine.process(pcm)
                if keyword_index >= 0:
                    self.event_queue.put(("keyword_detected", time.time()))

                # --- Loud sound detection ---
                amplitude = np.abs(np.array(pcm, dtype=np.int16)).mean()
                if amplitude > volume_threshold:
                    if loud_start is None:
                        loud_start = time.time()
                    elif time.time() - loud_start >= min_duration:
                        self.event_queue.put(("loud_sound", time.time()))
                        loud_start = None
                else:
                    loud_start = None

            except Exception as e:
                self.filelog.write(f"Audio reader loop error: {e}\n")

    # ===================================================================
    # Безопасный вызов callback
    # ===================================================================
    def _safe_callback(self, func, args, kwargs, stop_event):
        try:
            func(*args, **kwargs, stop_event=stop_event)
        except TypeError:
            # если функция не принимает stop_event
            func(*args, **kwargs)
        except Exception as e:
            self.filelog.write(f"Callback error: {e}\n")
            self.window.PushText(f"Callback error: {e}\n")

    # ===================================================================
    # Основной цикл обработки событий
    # ===================================================================
    def _worker_loop(self):
        while self.flagListing:
            try:
                event, ts = self.event_queue.get(timeout=0.5)
            except queue.Empty:
                continue

            if event in ["keyword_detected", "loud_sound"]:
                # каждый wakeword / loud sound = новая сессия
                self.session_id += 1
                current_session = self.session_id

                # останавливаем все старые цепочки
                self.stop_event.set()
                self.stop_event = threading.Event()

                self.filelog.write(f"[WakeWord] New session {current_session} ({event})\n")
                self.window.PushText(f"[WakeWord] New session {current_session} ({event})\n")

                # запускаем новую цепочку выполнения
                threading.Thread(
                    target=self._execute_callback_chain,
                    args=(current_session, event),
                    daemon=True
                ).start()

    # ===================================================================
    # Выполнение последовательной цепочки коллбэков
    # ===================================================================
    def _execute_callback_chain(self, session_id, event_type):
        for func, args, kwargs in self.callBacks:
            if not self.flagListing:
                return
            if session_id != self.session_id:
                self.filelog.write(f"[WakeWord] Session {session_id} cancelled\n")
                self.window.PushText(f"[WakeWord] Session {session_id} cancelled\n")
                return

            # добавляем тип события в kwargs
            kwargs = dict(kwargs)
            kwargs["event_type"] = event_type

            self._safe_callback(func, args, kwargs, self.stop_event)

    # ===================================================================
    # Запуск и остановка
    # ===================================================================
    def StartListning(self):
        if not self.pa:
            self.pa = pyaudio.PyAudio()
            self.stream = self.pa.open(
                rate=self.porcupine.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=self.porcupine.frame_length
            )

        if not self.thread_audio or not self.thread_audio.is_alive():
            self.thread_audio = threading.Thread(target=self._audio_reader_loop, daemon=True)
            self.thread_audio.start()

        if not self.worker_thread or not self.worker_thread.is_alive():
            self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
            self.worker_thread.start()

    def StopListning(self):
        self.flagListing = False
        self.stop_event.set()
        if self.thread_audio:
            self.thread_audio.join()
        if self.worker_thread:
            self.worker_thread.join()
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.pa:
            self.pa.terminate()
