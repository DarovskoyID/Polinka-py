import sounddevice as sd
import soundfile as sf
import tempfile

import sounddevice as sd
import numpy as np
import soundfile as sf
import tempfile

def record_seconds(
    samplerate=16000,
    channels=1,
    silence_threshold=0.01,  # Порог громкости (0..1)
    silence_duration=1.0,    # Сколько секунд тишины нужно для остановки
    chunk_duration=0.2       # Размер буфера для анализа (сек)
):

    chunk_size = int(samplerate * chunk_duration)
    silence_chunks_needed = int(silence_duration / chunk_duration)
    silence_counter = 0
    recording = []

    with sd.InputStream(samplerate=samplerate, channels=channels, dtype='float32') as stream:
        while True:
            data, _ = stream.read(chunk_size)
            recording.append(data.copy())

            # Рассчитываем RMS (средний уровень громкости)
            rms = np.sqrt(np.mean(data**2))

            # Проверяем, ниже ли уровень порога
            if rms < silence_threshold:
                silence_counter += 1
            else:
                silence_counter = 0  # сброс при звуке

            # Останавливаем после нескольких "тихих" чанков подряд
            if silence_counter > silence_chunks_needed:
                break

    # Склеиваем все чанки в один массив
    recording = np.concatenate(recording, axis=0)

    # Сохраняем во временный файл
    tmpfile = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    sf.write(tmpfile.name, recording, samplerate)

    return tmpfile.name, samplerate
