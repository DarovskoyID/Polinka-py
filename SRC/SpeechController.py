import threading
import queue
import time
import numpy as np
import piper
import sounddevice as sd
from SRC.Loger import _log
from SRC.WakeWord import WakeWord

# ===========================================================
# SpeechController: обработка билетов и TTS
# ===========================================================
class SpeechController:
    def __init__(self, fileTitles, fileTickets, window, tts_model, wakeword_model_path, access_key):
        self.window = window
        self.fileTitles = fileTitles
        self.fileTickets = fileTickets
        self.tts_voice = piper.PiperVoice.load(tts_model)

        # TTS
        self.tts_queue = queue.Queue()
        self.tts_lock = threading.Lock()
        self.tts_thread = threading.Thread(target=self._tts_worker, daemon=True)
        self.tts_thread.start()

        # WakeWord listener
        self.wake_listener = WakeWord(window, wakeword_model_path, access_key)

        # Состояния
        self.read_lock = threading.Lock()
        self.current_stop_event = threading.Event()
        self.reading_titles = False
        self.reading_ticket = False
        self.ticket_titles = []
        self.ticket_texts = []
        self.last_title_index = 0
        self.ticket_index = None
        self.pip_counter = 0

        # Запускаем обработку событий
        self.event_thread = threading.Thread(target=self._event_loop, daemon=True)
        self.event_thread.start()

    # ==========================
    # TTS
    # ==========================
    def _tts_worker(self):
        while True:
            text = self.tts_queue.get()
            if text is None:
                break
            try:
                with self.tts_lock:
                    chunks = [c.audio_float_array for c in self.tts_voice.synthesize(text)]
                    if chunks:
                        sd.play(np.concatenate(chunks), samplerate=self.tts_voice.config.sample_rate)
                        sd.wait()
            except Exception as e:
                _log(f"[TTS] Error: {e}")

    def queue_tts(self, text):
        if text:
            self.tts_queue.put(text)

    # ==========================
    # Обработка событий WakeWord и пиков
    # ==========================
    def _event_loop(self):
        while True:
            try:
                ev = self.wake_listener.event_queue.get(timeout=0.5)
            except queue.Empty:
                continue
            if ev[0] == "wakeword":
                self._handle_wakeword()
            elif ev[0] == "pip":
                self._handle_pip(ev[1])

    # ==========================
    # WakeWord
    # ==========================
    def _handle_wakeword(self):
        _log("[WakeWord] Detected 'полина', прерываем все чтения")
        self._stop_all_readings()
        self._compute_answer()

    def _compute_answer(self):
        _log("[ComputeAnswer] Stub answer computation")

    # ==========================
    # PIP controller
    # ==========================
    def _handle_pip(self, event):
        count_pip = event
        _log(f"[PIP] Detected pip {count_pip}")
        if count_pip == 1:
            if self.reading_titles:
                title = self.ticket_titles[self.last_title_index]
                self.queue_tts(title)
            elif self.reading_ticket and self.ticket_index is not None:
                line = self.ticket_texts[self.ticket_index]
                self.queue_tts(line)
        elif count_pip == 2:
            if not self.reading_titles and not self.reading_ticket:
                threading.Thread(target=self._read_titles, daemon=True).start()
            elif self.reading_titles and self.last_title_index > 0:
                self.last_title_index -= 1
                title = self.ticket_titles[self.last_title_index]
                self.queue_tts(title)
        elif count_pip >= 3:
            _log("[PIP3] Stop all readings")
            self._stop_all_readings()

    # ==========================
    # Прерывание всех чтений
    # ==========================
    def _stop_all_readings(self):
        self.current_stop_event.set()
        self.reading_titles = False
        self.reading_ticket = False
        self.ticket_index = None
        self.last_title_index = 0
        self.current_stop_event = threading.Event()

        while not self.tts_queue.empty():
            try:
                self.tts_queue.get_nowait()
            except queue.Empty:
                break
        _log("[TTS] Queue cleared")
        _log("[Stop] All readings stopped")

    # ==========================
    # Чтение названий билетов
    # ==========================
    def _read_titles(self, delay=3):
        with self.read_lock:
            if self.reading_titles or self.reading_ticket:
                return
            self.reading_titles = True

        try:
            with open(self.fileTitles, "r", encoding="utf-8") as f:
                self.ticket_titles = [line.strip() for line in f if line.strip()]
        except Exception as e:
            _log(f"[ReadTitles] {e}")
            self.reading_titles = False
            return

        for i, title in enumerate(self.ticket_titles):
            if self.current_stop_event.is_set():
                break
            self.last_title_index = i
            self.queue_tts(title)
            t0 = time.time()
            while time.time() - t0 < delay:
                if self.current_stop_event.is_set():
                    break
                time.sleep(0.05)
        self.reading_titles = False

    # ==========================
    # Чтение билета
    # ==========================
    def read_ticket(self):
        with self.read_lock:
            if self.reading_ticket or self.ticket_index is not None:
                return
            self.reading_ticket = True

        try:
            with open(self.fileTickets, "r", encoding="utf-8") as f:
                self.ticket_texts = [line.strip() for line in f if line.strip()]
        except Exception as e:
            _log(f"[ReadTickets] {e}")
            self.reading_ticket = False
            return

        if self.ticket_index is None:
            self.ticket_index = 0
        if self.ticket_index >= len(self.ticket_texts):
            self.reading_ticket = False
            return

        line = self.ticket_texts[self.ticket_index]
        self.queue_tts(line)
        self.reading_ticket = False
        self.ticket_index = None

    # ==========================
    # Завершение
    # ==========================
    def stop(self):
        self._stop_all_readings()
        self.tts_queue.put(None)
        self.tts_thread.join(timeout=1)
        self.wake_listener.stop()
