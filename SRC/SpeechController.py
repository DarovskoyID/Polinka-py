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
        self.answer = None
        self.KOKORO_MODEL_PATH = KOKORO_MODEL_PATH
        self.KOKORO_VOICES_MODEL_PATH = KOKORO_VOICES_MODEL_PATH
        self.whisperASR = Whisper(WHISPER_MODEL_PATH)
        self.wakeword = WakeWord(window, filelog,
            [], [WAKEWORD_POLINA_MODEL_PATH],
            [
                (self.WakeWordDetected, (window, filelog), {}),
                (self.Recog, (window, self.whisperASR, filelog), {}),
                (self.ComputeSentence, (), {}),
                (self.ToSpeech, (window,), {}),
            ],
            ACCESS_KEY
        )
        self.voice = piper.PiperVoice.load(TTS_MODEL_PATH)

    def ToSpeech(self, window):
        window.PushText("Полина: " + self.answer + "\n")
        chunks = []
        for audio_chunk in self.voice.synthesize(self.answer):
            chunks.append(audio_chunk.audio_float_array)
        wav_array_float = np.concatenate(chunks)
        sd.play(wav_array_float, samplerate=self.voice.config.sample_rate)
        sd.wait()


    def ComputeSentence(self):
        if "привет" in self.result.lower():
            self.answer = "Здравствуйте, Иван!"
        else:
            self.answer = "Пользователь не распознан"



    def Recog(self, window, whisperASR, filelog):
        path, sr = record_seconds()
        self.result = whisperASR.Recognize(path)

        tmp = self.result + '\n'
        filelog.write(tmp)
        window.PushText(tmp)

    def WakeWordDetected(self, window, filelog):
        infoText = "!++++++++++++ \n"
        filelog.write(infoText)
        window.PushText(infoText)

    def Start(self):
        self.wakeword.StartListning()