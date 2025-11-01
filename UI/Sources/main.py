# main.py (FIXED: prevent double KV loading)
import json
import os
from SRC.env import *
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import StringProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from SRC.Speech.Controller import SpeechController

# Path to kv — we will let MDApp load it exactly once by assigning self.kv_file
KV_FILE = os.path.join(os.path.dirname(__file__), "jarvis.kv")


class MainTab(Screen):
    log_text = StringProperty("")


class SettingsTab(Screen):
    ai_key = StringProperty("")
    base_phrases = StringProperty("")


class LogsTab(Screen):
    full_logs = StringProperty("")


class Root(ScreenManager):
    pass


class JarvisApp(MDApp):
    def __init__(self, animation_path, log_file, json_file, **kwargs):
        # set kv_file so MDApp will load jarvis.kv automatically ONCE
        super().__init__(**kwargs)
        self.kv_file = KV_FILE    # <-- IMPORTANT: let MDApp load this file once
        self.animation_path = animation_path
        self.log_file = log_file
        self.json_file = json_file
        self.ignore_change = False
        self.asr_choice = "WHISPER"

    def build(self):
        # window size + ensure system chrome visible
        Window.size = (500, 750)
        Window.borderless = False
        Window.clearcolor = (13/255., 13/255., 13/255., 1)

        # KivyMD theme
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "BlueGray"

        # create root AFTER kv is loaded by MDApp (MDApp already loaded kv_file)
        # Note: do NOT call Builder.load_file(KV_FILE) anywhere else
        self.root = Root()
        self.root.current = "main"

        # schedule polling of logs and load json
        Clock.schedule_interval(self.read_logs, 2.0)
        Clock.schedule_once(self.load_json, 0.3)

        self.speech = SpeechController(
            file_titles=BILETS_NAME_FILE,
            file_tickets=BILETS_FILE,
            tts_model=TTS_MODEL_PATH,
            wakeword_model_path=WAKEWORD_POLINA_MODEL_PATH,
            access_key=ACCESS_KEY
        )

        return self.root

    # --- LOGS ---
    def read_logs(self, *_):
        text = ""
        try:
            with open(self.log_file, "r", encoding="utf-16") as f:
                text = f.read()
        except FileNotFoundError:
            text = ""
        except Exception:
            return

        try:
            main = self.root.get_screen("main")
            logs = self.root.get_screen("logs")
            if "small_logs" in main.ids:
                main.ids.small_logs.text = text
            if "full_logs" in logs.ids:
                logs.ids.full_logs.text = text
        except Exception:
            pass

    # --- JSON load/save ---
    def load_json(self, *_):
        if not os.path.exists(self.json_file):
            return
        try:
            with open(self.json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            txt = json.dumps(data, indent=4, ensure_ascii=False)
            self.ignore_change = True
            if "base_phrases" in self.root.get_screen("settings").ids:
                self.root.get_screen("settings").ids.base_phrases.text = txt
            self.ignore_change = False
        except Exception:
            pass

    def save_json(self, *_):
        if self.ignore_change:
            return
        try:
            txt = self.root.get_screen("settings").ids.base_phrases.text
            data = json.loads(txt)
            with open(self.json_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception:
            pass

    def on_base_phrases_change(self, instance, value):
        if self.ignore_change:
            return
        Clock.unschedule(self.save_json)
        Clock.schedule_once(self.save_json, 0.6)

    # navigation called from top menu buttons
    def switch_screen(self, name):
        if name in ("main", "settings", "logs"):
            self.root.current = name

    # ASR choice visual
    def set_asr(self, name):
        self.asr_choice = name
        try:
            settings = self.root.get_screen("settings")
            for btn_id, val in (("btn_vosk", "VOSK"), ("btn_whisper", "WHISPER")):
                btn = settings.ids.get(btn_id)
                if btn:
                    btn.disabled = (val != name)
        except Exception:
            pass



if __name__ == "__main__":
    JarvisApp(
        animation_path=os.path.join("UI", "Sources", "animation.gif"),
        log_file=os.path.join("assets", "log.txt"),
        json_file=os.path.join("assets", "data.json"),
        title="Jarvis"
    ).run()
