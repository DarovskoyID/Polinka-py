import sounddevice as sd
import soundfile as sf
import tempfile

def record_seconds(seconds=5, samplerate=16000, channels=1):
    print(f"Recording {seconds} seconds...")
    recording = sd.rec(int(seconds * samplerate), samplerate=samplerate, channels=channels, dtype='int16')
    sd.wait()
    tmpfile = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    sf.write(tmpfile.name, recording, samplerate)
    return tmpfile.name, samplerate