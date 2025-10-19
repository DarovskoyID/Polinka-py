from SRC.RecordMicro import record_seconds
from SRC.WakeWord import WakeWord
from SRC.Whisper import Whisper

import numpy as np
import sounddevice as sd
import piper


class SpeechController:
    def __init__(self, WHISPER_MODEL_PATH,
                 WAKEWORD_POLINA_MODEL_PATH,
                 TTS_MODEL_PATH,
                 ACCESS_KEY,
                 window,
                 filelog,
                 fileTitles,
                 fileTickets
                 ):

        self.result = ""        # <── обязательно
        self.answer = ""        # <── обязательно
        self.ticket = None

        self.filelog = filelog
        self.window = window


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
                (self.ChooseTicket, (fileTitles,), {}),
                (self.SayTicket , (fileTickets,), {}),
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

        if event_type == "loud_sound":
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
    # Выбор билета
    # =============================================================
    def ChooseTicket(self, fileTitles, stop_event=None, event_type=None):
        if stop_event and stop_event.is_set():
            return
        if event_type == "loud_sound" and not self.ticket:
            with open(fileTitles, "r", encoding="utf-8") as f:
                i = 0
                for line in f:
                    i += 1
                    self.filelog.write(f"[ChooseTicket] ticket title said: {line}\n")
                    self.window.PushText(f"[ChooseTicket] ticket title said: {line}\n")
                    chunks = []
                    for audio_chunk in self.voice.synthesize(line):
                        if stop_event and stop_event.is_set():
                            return
                        chunks.append(audio_chunk.audio_float_array)

                    if not chunks:
                        return
                    wav_array_float = np.concatenate(chunks)
                    sd.play(wav_array_float, samplerate=self.voice.config.sample_rate)
                    while sd.get_stream().active:
                        if stop_event and stop_event.is_set():
                            self.ticket = i
                            self.filelog.write(f"[ChooseTicket] ticket chosen: {self.ticket}\n")
                            self.window.PushText(f"[ChooseTicket] ticket chosen: {self.ticket}\n")
                            sd.stop()
                            return

    # =============================================================
    # Диктовка билета
    # =============================================================
    def SayTicket(self, fileTickets, stop_event=None, event_type=None):
        if stop_event and stop_event.is_set():
            return

        if event_type != "loud_sound" or not self.ticket:
            return

        try:
            with open(fileTickets, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
                if self.ticket - 1 >= len(lines):
                    return
                line = lines[self.ticket - 1].strip()
                if not line:
                    return

            self.filelog.write(f"[SayTicket] ticket dictated: {self.ticket}\n")
            self.window.PushText(f"[SayTicket] ticket dictated: {self.ticket}\n")

            chunks = []
            for audio_chunk in self.voice.synthesize(line):
                if stop_event and stop_event.is_set():
                    self.ticket = None
                    return
                chunks.append(audio_chunk.audio_float_array)

            if not chunks:
                return

            wav_array_float = np.concatenate(chunks)
            sd.play(wav_array_float, samplerate=self.voice.config.sample_rate)

            while sd.get_stream().active:
                if stop_event and stop_event.is_set():
                    self.ticket = None
                    sd.stop()
                    return

            self.ticket = None

        except Exception as e:
            self.filelog.write(f"SayTicket error: {e}\n")
            self.window.PushText(f"SayTicket error: {e}\n")

    # =============================================================
    # Обработка текста
    # =============================================================
    def ComputeSentence(self, stop_event=None, event_type=None):
        if stop_event and stop_event.is_set():
            return

        if event_type == "loud_sound":
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

        if event_type == "loud_sound":
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
