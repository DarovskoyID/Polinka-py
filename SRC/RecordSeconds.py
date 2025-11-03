from jnius import autoclass
import numpy as np
import soundfile as sf
import tempfile
import time

# java classes
AudioRecord = autoclass('android.media.AudioRecord')
MediaRecorder = autoclass('android.media.MediaRecorder')
AudioFormat = autoclass('android.media.AudioFormat')


def record_seconds(
    samplerate=16000,
    channels=1,
    silence_threshold=0.01,
    silence_duration=1.0,
    chunk_duration=0.2
):
    # android constants
    channel_config = AudioFormat.CHANNEL_IN_MONO
    audio_format = AudioFormat.ENCODING_PCM_16BIT

    buf_size = AudioRecord.getMinBufferSize(samplerate, channel_config, audio_format)

    recorder = AudioRecord(
        MediaRecorder.AudioSource.MIC,
        samplerate,
        channel_config,
        audio_format,
        buf_size
    )

    recorder.startRecording()

    chunk_size = int(samplerate * chunk_duration)
    bytes_per_sample = 2  # 16bit
    byte_chunk = bytearray(chunk_size * bytes_per_sample)

    silence_chunks_needed = int(silence_duration / chunk_duration)
    silence_counter = 0
    frames = []

    while True:
        read = recorder.read(byte_chunk, 0, len(byte_chunk))
        if read <= 0:
            continue

        # convert to numpy float32 normalized -1..1
        pcm16 = np.frombuffer(byte_chunk, dtype=np.int16)[:chunk_size]
        float32 = pcm16.astype(np.float32) / 32768.0
        frames.append(float32.copy())

        rms = np.sqrt(np.mean(float32 ** 2))

        if rms < silence_threshold:
            silence_counter += 1
        else:
            silence_counter = 0

        if silence_counter > silence_chunks_needed:
            break

    recorder.stop()
    recorder.release()

    audio = np.concatenate(frames)

    tmpfile = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    sf.write(tmpfile.name, audio, samplerate)

    return tmpfile.name, samplerate
