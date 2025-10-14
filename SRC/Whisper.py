from faster_whisper import WhisperModel


class Whisper():
    def __init__(self, modelPath : str):
        self.modelPath = modelPath
        self.model = WhisperModel(modelPath, device="cuda", compute_type="int8_float16")

    def Recognize(self, audioPath : str):
        result = ""
        self.segments, self.info = self.model.transcribe(
            audioPath,
            task="transcribe",
            beam_size=5,
            vad_filter=True
        )
        result = f"[{self.info.language}]"
        for segment in self.segments:
            start = segment.start
            end = segment.end
            text = segment.text
            result += f"{text}"

        return result