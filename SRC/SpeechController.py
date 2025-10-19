from SRC.RecordMicro import record_seconds
from SRC.WakeWord import WakeWord
from SRC.Whisper import Whisper

import numpy as np
import sounddevice as sd
import piper


class SpeechController:
    def __init__(self, WHISPER_MODEL_PATH,
                 WAKEWORD_POLINA_MODEL_PATH,
                 KOKORO_MODEL_PATH,
                 KOKORO_VOICES_MODEL_PATH,
                 TTS_MODEL_PATH,
                 ACCESS_KEY,
                 window,
                 filelog):

        self.result = ""        # <── обязательно
        self.answer = ""        # <── обязательно

        self.filelog = filelog
        self.window = window

        self.KOKORO_MODEL_PATH = KOKORO_MODEL_PATH
        self.KOKORO_VOICES_MODEL_PATH = KOKORO_VOICES_MODEL_PATH

        self.whisperASR = Whisper(WHISPER_MODEL_PATH)
        self.voice = piper.PiperVoice.load(TTS_MODEL_PATH)

        self.wakeword = WakeWord(
            window,
            filelog,
            [],
            [WAKEWORD_POLINA_MODEL_PATH],
            [
                (self.WakeWordDetected, (), {}),
                (self.Recog, (self.whisperASR,), {}),
                (self.ComputeSentence, (), {}),
                (self.ToSpeech, (), {}),
            ],
            ACCESS_KEY
        )

    # =============================================================
    # WakeWord
    # =============================================================
    def WakeWordDetected(self, stop_event=None, event_type=None):
        if stop_event and stop_event.is_set():
            return

        if event_type == "keyword_detected":
            infoText = "!++++++++++++ \n"
        elif event_type == "loud_sound":
            infoText = "!------ Пик! ------ \n"
        else:
            infoText = f"!??? event={event_type}\n"

        self.filelog.write(infoText)
        self.window.PushText(infoText)

    # =============================================================
    # Распознавание речи
    # =============================================================
    def Recog(self, whisperASR, stop_event=None, event_type=None):
        if stop_event and stop_event.is_set():
            return

        path, sr = record_seconds()
        if stop_event and stop_event.is_set():
            return

        self.result = whisperASR.Recognize(path)
        if not self.result:
            return

        tmp = self.result + '\n'
        self.filelog.write(tmp)
        self.window.PushText(tmp)

    # =============================================================
    # Обработка текста
    # =============================================================
    def ComputeSentence(self, stop_event=None, event_type=None):
        if stop_event and stop_event.is_set():
            return

        if not hasattr(self, "result") or not self.result:
            self.filelog.write("[ComputeSentence] Пропуск — нет текста")
            self.window.PushText("[ComputeSentence] Пропуск — нет текста")
            return

        if "привет" in self.result.lower():
            self.answer = "Здравствуйте, Иван!"
        else:
            self.answer = "Пользователь не распознан"

    # =============================================================
    # Озвучивание
    # =============================================================
    def ToSpeech(self, stop_event=None, event_type=None):
        if stop_event and stop_event.is_set():
            return

        if not hasattr(self, "answer") or not self.answer:
            self.filelog.write("[ToSpeech] Пропуск — нет ответа")
            self.window.PushText("[ToSpeech] Пропуск — нет ответа")
            return

        self.window.PushText("Полина: " + self.answer + "\n")

        chunks = []
        for audio_chunk in self.voice.synthesize(self.answer):
            if stop_event and stop_event.is_set():
                return
            chunks.append(audio_chunk.audio_float_array)

        if not chunks:
            return

        wav_array_float = np.concatenate(chunks)
        sd.play(wav_array_float, samplerate=self.voice.config.sample_rate)
        while sd.get_stream().active:
            if stop_event and stop_event.is_set():
                sd.stop()
                return

    # =============================================================
    # Запуск прослушивания
    # =============================================================
    def Start(self):
        self.wakeword.StartListning()
