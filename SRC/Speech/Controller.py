import threading
import queue
import time

from SRC.Loger import _log
from SRC.Speech.EventRouter import EventRouter
from SRC.Speech.TTSManager import TTSManager
from SRC.WakeWord.WakeWord import WakeWord


class SpeechController:
    def __init__(self, file_titles, file_tickets, window, tts_model, wakeword_model_path, access_key):
        # --- подсистемы ---
        self.window = window
        self.tts = TTSManager(tts_model)
        self.router = EventRouter()
        self.wake_listener = WakeWord(window, wakeword_model_path, access_key)

        # --- состояния ---
        self._state = "IDLE"
        self._adjusting_speed = False
        self.current_sentence_index = None
        self.current_sentences = None
        self.reading_titles = False
        self.reading_ticket = False
        self.ticket_texts = None
        self.current_stop_event = threading.Event()
        self.read_lock = threading.Lock()

        # --- параметры скорости ---
        self.speed_config = {
            "step": 0.1,
            "min": 0.5,
            "max": 2.0,
            "default": 1.0
        }
        self.read_speed = self.speed_config["default"]
        self.delay = 5  # базовая пауза между предложениями

        # --- файлы ---
        self.file_titles = file_titles
        self.file_tickets = file_tickets

        # --- события ---
        self._register_event_handlers()

        # --- поток событий ---
        self.event_thread = threading.Thread(target=self._event_loop, daemon=True)
        self.event_thread.start()

    # =======================================================
    # Регистрация событий
    # =======================================================
    def _register_event_handlers(self):
        self.router.on("wakeword", self._on_wakeword)
        self.router.on("pip:1", self._on_pip_1)
        self.router.on("pip:2", self._on_pip_2)
        self.router.on("pip:3", self._on_pip_3)
        self.router.on("pip:4", self._on_pip_4)
        self.router.on("pip", self._on_pip_generic)  # fallback

    # =======================================================
    # Цикл событий
    # =======================================================
    def _event_loop(self):
        while True:
            try:
                ev = self.wake_listener.event_queue.get(timeout=0.5)
                etype = ev[0]
                data = ev[1] if len(ev) > 1 else None

                if etype == "pip":
                    self.router.emit(f"pip:{data}", data)
                self.router.emit(etype, data)

            except queue.Empty:
                continue

    # =======================================================
    # Обработчики событий
    # =======================================================
    def _on_wakeword(self, *_):
        _log("[WakeWord] 'Полина' обнаружена")
        self._stop_all_readings()
        self.tts.say("Слушаю")

    def _on_pip_generic(self, count_pip):
        _log(f"[PIP] Detected {count_pip} (generic handler)")

    # =======================================================
    # pip:1 → короткий сигнал
    # =======================================================
    def _on_pip_1(self, *_):
        if self._adjusting_speed:
            self._enter_speed_mode(1)
            return

        if self._state == "READ_TITLES":
            self._state = "CONFIRM_TITLE"

        elif self._state == "CONFIRM_TITLE":
            self._state = "READ_TICKET"
            self.current_sentence_index = 0
            self.tts.clear()
            self.read_ticket()

        elif self._state == "READ_TICKET":
            self._repeat_or_restart_sentence()

    # =======================================================
    # pip:2 → двойной сигнал
    # =======================================================
    def _on_pip_2(self, *_):
        if self._adjusting_speed:
            self._enter_speed_mode(2)
            return

        if self._state == "IDLE":
            _log("[FSM] Запуск чтения заголовков")
            self._state = "READ_TITLES"
            threading.Thread(target=self._read_titles, daemon=True).start()

        elif self._state == "CONFIRM_TITLE":
            self._state = "READ_TITLES"
            threading.Thread(target=self._read_titles, daemon=True).start()

        elif self._state == "READ_TICKET":
            _log("[READ_TICKET] Возврат к заголовкам")
            self._state = "READ_TITLES"
            self.current_sentence_index = 0
            self.tts.clear()
            threading.Thread(target=self._read_titles, daemon=True).start()

    # =======================================================
    # pip:3 → тройной сигнал
    # =======================================================
    def _on_pip_3(self, *_):
        if self._adjusting_speed:
            self._enter_speed_mode(3)
            return

        _log("[PIP] Остановка всех чтений")
        self._stop_all_readings()

    # =======================================================
    # pip:4 → вход в режим настройки скорости
    # =======================================================
    def _on_pip_4(self, *_):
        self._adjusting_speed = True
        _log(f"[Speed] Настройка скорости активирована (текущая = {self.read_speed:.2f})")
        self.tts.say(f"Настройка скорости. Текущая {self.read_speed:.1f}")

    # =======================================================
    # Управление скоростью (🔒 защищено мьютексом)
    # =======================================================
    def _enter_speed_mode(self, count_pip):
        step = self.speed_config["step"]
        min_speed = self.speed_config["min"]
        max_speed = self.speed_config["max"]

        with self.read_lock:  # 🔒 защищаем доступ к read_speed
            if count_pip == 1:
                self.read_speed = max(min_speed, self.read_speed - step)
                _log(f"[Speed] ↓ {self.read_speed:.2f}")
                self.tts.say(f"Скорость {self.read_speed:.1f}")

            elif count_pip == 2:
                self.read_speed = min(max_speed, self.read_speed + step)
                _log(f"[Speed] ↑ {self.read_speed:.2f}")
                self.tts.say(f"Скорость {self.read_speed:.1f}")

            elif count_pip == 3:
                self._adjusting_speed = False
                self._state = "IDLE"
                _log("[Speed] Режим настройки завершён")
                self.tts.say("Настройка скорости завершена")

            # 🔄 применяем скорость к TTS (потокобезопасно)
            with self.tts.lock:
                self.tts.speed = self.read_speed

    # =======================================================
    # Повтор предложения в билете
    # =======================================================
    def _repeat_or_restart_sentence(self):
        if hasattr(self, "current_sentence_index") and self.current_sentence_index > 0:
            self.current_sentence_index -= 1
            _log(f"[READ_TICKET] Повтор предложения {self.current_sentence_index}")
            self.tts.clear()
            for i in range(self.current_sentence_index, len(self.current_sentences)):
                self.tts.say(self.current_sentences[i])
        else:
            _log("[READ_TICKET] Уже в начале билета")

    # =======================================================
    # Чтение названий билетов
    # =======================================================
    def _read_titles(self):
        with self.read_lock:
            if self.reading_titles or self.reading_ticket:
                return
            self.reading_titles = True

        try:
            with open(self.file_titles, encoding="utf-8") as f:
                self.ticket_titles = [line.strip() for line in f if line.strip()]
        except Exception as e:
            _log(f"[ReadTitles] {e}")
            self.reading_titles = False
            self._state = "IDLE"
            return

        for i, title in enumerate(self.ticket_titles):
            if self.current_stop_event.is_set() or self._state not in ["READ_TITLES", "CONFIRM_TITLE"]:
                break

            self.last_title_index = i
            _log(f"[ReadTitles] Читаем заголовок {i + 1}: {title}")
            self.tts.say(title)

            t0 = time.time()
            while time.time() - t0 < self.delay:
                if self.current_stop_event.is_set() or self._state not in ["READ_TITLES", "CONFIRM_TITLE"]:
                    break
                time.sleep(0.05)

            if self._state == "CONFIRM_TITLE":
                _log(f"[ReadTitles] Подтверждаем билет {i + 1}: {title}")
                self.tts.say(f"{title}. Подтверждаете билет?")
                t0_confirm = time.time()
                while time.time() - t0_confirm < self.delay:
                    if self.current_stop_event.is_set() or self._state in ["READ_TICKET", "IDLE"]:
                        break
                    time.sleep(0.05)

            if self._state == "CONFIRM_TITLE":
                self._state = "READ_TITLES"

        self.reading_titles = False
        if self._state != "READ_TICKET":
            self._state = "IDLE"

    # =======================================================
    # Чтение билета (потоковое)
    # =======================================================
    def read_ticket(self):
        with self.read_lock:
            if self.reading_ticket:
                return
            self.reading_ticket = True

        try:
            with open(self.file_tickets, encoding="utf-8") as f:
                self.ticket_texts = [line.strip() for line in f if line.strip()]
        except Exception as e:
            _log(f"[ReadTickets] {e}")
            self.reading_ticket = False
            return

        index = self.last_title_index
        if index >= len(self.ticket_texts):
            _log(f"[ReadTicket] Нет билета для заголовка {index + 1}")
            self.reading_ticket = False
            return

        text = self.ticket_texts[index]
        words = text.split()
        self.current_sentences = [" ".join(words[i:i + 10]) for i in range(0, len(words), 10)]
        self.current_sentence_index = 0

        _log(f"[ReadTicket] Чтение билета {index + 1}")
        threading.Thread(target=self._read_ticket_sentences, daemon=True).start()

    def _read_ticket_sentences(self):
        while (
            self._state == "READ_TICKET"
            and not self.current_stop_event.is_set()
            and self.current_sentence_index < len(self.current_sentences)
        ):
            sentence = self.current_sentences[self.current_sentence_index]
            _log(f"[ReadTicket] [{self.current_sentence_index + 1}/{len(self.current_sentences)}] {sentence}")
            self.tts.say(sentence)

            # задержка между предложениями с учётом скорости
            time.sleep(self.delay / self.read_speed)

            self.current_sentence_index += 1

        _log("[ReadTicket] Чтение билета завершено")
        self.reading_ticket = False
        if self._state == "READ_TICKET":
            self._state = "IDLE"

    # =======================================================
    # Управление состоянием
    # =======================================================
    def _stop_all_readings(self):
        self.current_stop_event.set()
        self.tts.clear()
        self.tts.say("Чтение остановлено")
        self._state = "IDLE"
        self._adjusting_speed = False
        self.current_stop_event.clear()

    def stop(self):
        self._stop_all_readings()
        self.tts.stop()
        self.wake_listener.stop()
