import time

import numpy as np
import pvporcupine
import pyaudio
import struct
import threading


class WakeWord:
    def __init__(self, window, filelog, wakeWords=["jarvis"], keywordPaths = [], callBacks=None, key = ""):
        self.porcupine = pvporcupine.create(
            keywords=wakeWords,
            keyword_paths=keywordPaths,
            access_key=key
        )
        self.keywordPaths = keywordPaths
        self.wakeWords = wakeWords
        self.callBacks = callBacks or []  # список [(func, args, kwargs)]
        self.flagListing = True
        self.thread = None
        self.window = window
        self.filelog = filelog

    def __del__(self):
        try:
            self.flagListing = False
            if hasattr(self, "stream"):
                self.stream.stop_stream()
                self.stream.close()
            if hasattr(self, "pa"):
                self.pa.terminate()
            if hasattr(self, "porcupine"):
                self.porcupine.delete()
        except Exception as e:
            self.filelog.write(f"Destructor error: {e} \n")
            self.window.PushText(f"Destructor error: {e} \n",)

    def _callFunctions(self):
        for func, args, kwargs in self.callBacks:
            try:
                func(*args, **kwargs)
            except Exception as e:
                self.filelog.write(f"Callback error: {e} \n")
                self.window.PushText(f"Callback error: {e} \n")

    def _listen_loop(self, volume_threshold = 10000, min_duration = 0.5):
        self.pa = pyaudio.PyAudio()
        self.stream = self.pa.open(
            rate=self.porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self.porcupine.frame_length
        )


        loud_start = None

        while self.flagListing:
            pcm = self.stream.read(self.porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)
            keyword_index = self.porcupine.process(pcm)
            if keyword_index >= 0:
                self._callFunctions()
                continue

            np_pcm = np.array(pcm, dtype=np.int16)
            amplitude = np.abs(np_pcm).mean()

            if amplitude > volume_threshold:
                if loud_start is None:
                    loud_start = time.time()
                elif time.time() - loud_start >= min_duration:
                    self._callFunctions()
                    loud_start = None
            else:
                loud_start = None


    def StartListning(self):
        if not self.thread or not self.thread.is_alive():
            self.thread = threading.Thread(target=self._listen_loop, daemon=True)
            self.thread.start()

    def StopListning(self):
        self.flagListing = False