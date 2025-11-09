# main.py (FIXED: prevent double KV loading)
import json
import os

from kivy.lang import Builder

from SRC.env import *
from SRC.Loger import _log
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import StringProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.button import Button
from kivy.utils import platform
from kivy.core.image import Image as CoreImage
# from SRC.Speech.Controller import SpeechController

# Path to kv — we will let MDApp load it exactly once by assigning self.kv_file
KV_FILE = os.path.join(os.path.dirname(__file__), "jarvis.kv")


class MainTab(Screen):
    log_text = StringProperty("")

    def on_enter(self):
        Clock.schedule_once(self.start_anim, 0)

    def start_anim(self, dt):
        app = App.get_running_app()
        self.frames = [CoreImage(f).texture for f in app.frames if f]
        self.anim_index = 0
        self.anim_image = self.ids.anim
        Clock.schedule_interval(self.next_frame, 0.03)

    def next_frame(self, dt):
        if not self.frames:
            return
        self.anim_image.texture = self.frames[self.anim_index]
        self.anim_index = (self.anim_index + 1) % len(self.frames)

class SettingsTab(Screen):
    ai_key = StringProperty("")
    base_phrases = StringProperty("")
    pv_key = StringProperty("")

class LogsTab(Screen):
    full_logs = StringProperty("")


class Root(ScreenManager):
    pass

class FileChooserPopup(Popup):
    def __init__(self, on_selection, **kwargs):
        super().__init__(**kwargs)
        self.title = "Выберите файл"
        self.size_hint = (0.8, 0.8)
        self.auto_dismiss = False
        self.on_selection = on_selection


        root = BoxLayout(orientation="vertical", spacing=5, padding=5)

        self.fc = FileChooserIconView()
        self.fc.multiselect = False

        if platform == "android":
            # путь к общей папке Downloads
            self.fc.path = "/"

        btns = BoxLayout(size_hint_y=None, height="48dp", spacing=5)
        btn_ok = Button(text="OK")
        btn_cancel = Button(text="Отмена")

        btn_ok.bind(on_release=self.do_select)
        btn_cancel.bind(on_release=lambda *a: self.dismiss())

        btns.add_widget(btn_ok)
        btns.add_widget(btn_cancel)

        root.add_widget(self.fc)
        root.add_widget(btns)
        self.add_widget(root)

    def do_select(self, *a):
        if self.fc.selection:
            self.on_selection(self, self.fc.selection)
        self.dismiss()

class JarvisApp(MDApp):
    def __init__(self, animation_path, log_file, json_file, **kwargs):
        # set kv_file so MDApp will load jarvis.kv automatically ONCE
        super().__init__(**kwargs)
        self.kv_file = KV_FILE
        self.animation_path = animation_path
        self.log_file = log_file
        self.json_file = json_file
        self.ignore_change = False
        self.asr_choice = "WHISPER"
        self.frames = [
            os.path.join(ANIMATION_PATH, f"out_%03d.png" % i)
            for i in range(1, 219)
        ]

    def build(self):
        # window size + ensure system chrome visible
        Window.clearcolor = (13/255., 13/255., 13/255., 1)
        # KivyMD theme
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "BlueGray"

        # self.speech = SpeechController(
        #     tts_model=TTS_MODEL_PATH,
        #     wakeword_model_path=WAKEWORD_POLINA_MODEL_PATH,
        #     access_key=ACCESS_KEY
        # )
        # root уже точно создан

        self.root = Root()
        self.root.current = "main"


        return self.root
    def on_start(self):
        print("I WAS STARTED")

        Clock.schedule_interval(self.read_logs, 2.0)
        Clock.schedule_once(self.load_json, 2.0)
        Clock.schedule_once(lambda dt: self.load_pv_key(), 2.0)

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
        print("TRY LOAD JSON:", self.json_file)
        if not os.path.exists(self.json_file):
            print("JSON FILE NOT FOUND!")
            return
        try:
            print("WWW", self.json_file)
            with open(self.json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.root.get_screen("settings").ids.pv_key.text = data.get("pv_key", "")
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
            data["pv_key"] = self.root.get_screen("settings").ids.pv_key.text
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

    def pick_titles(self):
        popup = FileChooserPopup(on_selection=self._titles_selected)
        popup.open()

    def _titles_selected(self, chooser, selection):
        if not selection:
            return
        src = selection[0]
        dst = BILETS_NAME_FILE

        try:
            with open(src, "r", encoding="utf-8") as fin, open(dst, "w", encoding="utf-8") as fout:
                fout.write(fin.read())
            _log(f"titles updated: {dst}")
        except Exception as e:
            _log(f"ERR copy titles: {e}")

    def pick_tickets(self):
        popup = FileChooserPopup(on_selection=self._tickets_selected)
        popup.open()

    def _tickets_selected(self, chooser, selection):
        if not selection:
            return
        src = selection[0]
        dst = BILETS_FILE

        try:
            with open(src, "r", encoding="utf-8") as fin, open(dst, "w", encoding="utf-8") as fout:
                fout.write(fin.read())
            _log(f"tickets updated: {dst} ")
        except Exception as e:
            _log(f"ERR copy tickets: {e}")

    def clear_logs(self):
        # очищаем файл
        try:
            with open(self.log_file, "w", encoding="utf-16") as f:
                f.write("")
        except Exception as e:
            print(f"ERR clearing log: {e}")

        # очищаем виджеты сразу
        try:
            main = self.root.get_screen("main")
            logs = self.root.get_screen("logs")
            if "small_logs" in main.ids:
                main.ids.small_logs.text = ""
            if "full_logs" in logs.ids:
                logs.ids.full_logs.text = ""
        except Exception:
            pass

    def load_pv_key(self):
        cfg_path = CONFIG_JSON
        if not os.path.exists(cfg_path):
            return
        try:
            with open(cfg_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            key = data.get("ACCESS_KEY_PV", "")
            settings = self.root.get_screen("settings")
            if "pv_key" in settings.ids:
                settings.ids.pv_key.text = key
                settings.pv_key = key  # если используешь свойство Screen
        except Exception as e:
            _log(f"ERR loading PV key: {e}")


    def save_pv_key(self):
        key = self.root.get_screen("settings").ids.pv_key.text
        cfg_path = CONFIG_JSON

        # загружаем существующий config
        data = {}
        if os.path.exists(cfg_path):
            try:
                with open(cfg_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = {}

        # записываем ключ
        data["ACCESS_KEY_PV"] = key

        try:
            with open(cfg_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            _log("Porcupine key saved!")
        except Exception as e:
            _log(f"ERR saving PV key: {e}")
