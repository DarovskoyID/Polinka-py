from jnius import autoclass, PythonJavaClass, java_method
from threading import Event
from android.runnable import run_on_ui_thread
from kivy.clock import Clock

# Android классы
SpeechRecognizer = autoclass('android.speech.SpeechRecognizer')
RecognizerIntent = autoclass('android.speech.RecognizerIntent')
Intent = autoclass('android.content.Intent')
PythonActivity = autoclass('org.kivy.android.PythonActivity')

class Vosk():
    def __init__(self):
        """
        Встроенный Android SpeechRecognizer вместо Vosk.
        modelPath игнорируется, оставлено для совместимости.
        """
        self.activity = PythonActivity.mActivity
        self.result_text = ""
        self.finished = Event()



        # Создаем listener
        class Listener(PythonJavaClass):
            __implements__ = ['android.speech.RecognitionListener']

            def __init__(self, outer):
                super().__init__()
                self.outer = outer

            @java_method('(Ljava/util/List;)V')
            def onResults(self, results):
                n = results.size()
                text = ""
                for i in range(n):
                    text += str(results.get(i)) + " "
                self.outer.result_text = "[ru]" + text.strip()
                self.outer.finished.set()

            # Обязательные методы интерфейса
            @java_method('()V')
            def onReadyForSpeech(self): pass
            @java_method('(I)V')
            def onBeginningOfSpeech(self, i): pass
            @java_method('(F)V')
            def onRmsChanged(self, v): pass
            @java_method('([B)V')
            def onBufferReceived(self, buffer): pass
            @java_method('()V')
            def onEndOfSpeech(self): pass
            @java_method('(I)V')
            def onError(self, error):
                self.outer.result_text = f"[ru][ERROR {error}]"
                self.outer.finished.set()
            @java_method('(Ljava/lang/String;)V')
            def onEvent(self, event): pass
            @java_method('(Ljava/util/Bundle;)V')
            def onPartialResults(self, partial): pass

        self._init_real()

    @run_on_ui_thread
    def _init_real(self):
        self.recognizer = SpeechRecognizer.createSpeechRecognizer(self.activity)
        self.recognizer.setRecognitionListener(self.listener)

    def Recognize(self, audioPath: str = None):
        """
        Запускает распознавание речи через микрофон.
        Параметр audioPath игнорируется для совместимости.
        """
        self.result_text = ""
        self.finished.clear()

        intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
        intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL,
                        RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
        intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, 'ru-RU')

        self.recognizer.startListening(intent)

        # Ждем окончания распознавания
        self.finished.wait()

        return self.result_text
