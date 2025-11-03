from vosk import Model, KaldiRecognizer
import json
import wave

class Vosk():
    def __init__(self, modelPath: str):
        # тут у нас теперь vosk model
        self.model = Model(modelPath)

    def Recognize(self, audioPath: str):
        wf = wave.open(audioPath, "rb")
        rec = KaldiRecognizer(self.model, wf.getframerate())
        rec.SetWords(False)

        text = ""

        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break

            if rec.AcceptWaveform(data):
                res = json.loads(rec.Result())
                text += res.get("text", "")
            else:
                # partial игнорируем
                pass

        res = json.loads(rec.FinalResult())
        text += res.get("text", "")

        return "[ru]" + text
