import time
import threading
import queue
import numpy as np
import struct

from kivy.clock import Clock
from jnius import autoclass, cast

from SRC.Loger import _log

# Android API
AudioRecord = autoclass('android.media.AudioRecord')
AudioFormat = autoclass('android.media.AudioFormat')
AudioManager = autoclass('android.media.AudioManager')
AudioDeviceInfo = autoclass('android.media.AudioDeviceInfo')
Context = autoclass('android.content.Context')
PythonActivity = autoclass('org.kivy.android.PythonActivity')
BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
BluetoothProfile = autoclass('android.bluetooth.BluetoothProfile')
BluetoothHeadset = autoclass('android.bluetooth.BluetoothHeadset')

# permission
RECORD_AUDIO = "android.permission.RECORD_AUDIO"
BLUETOOTH_CONNECT = "android.permission.BLUETOOTH_CONNECT"

_SELECTED_DEVICE = None


class WakeWord:
    def __init__(self, screen, accuracy=5000, hold_time=0.10, cooldown=0.33, sco_wait=3.0):
        global _SELECTED_DEVICE

        self.screen = screen
        self.event_queue = queue.Queue()
        self.running = threading.Event()
        self.running.set()

        self.accuracy = accuracy
        self.hold_time = hold_time
        self.cooldown = cooldown
        self.sco_wait = sco_wait

        self.sample_rate = 16000
        self.frame_length = 512

        self._loud_start = None
        self._last_peak_time = 0
        self._peak_count = 0
        self._last_event_time = 0

        activity = PythonActivity.mActivity
        self.audio_manager = cast(AudioManager, activity.getSystemService(Context.AUDIO_SERVICE))

        # --- 1. Логируем все устройства ---
        try:
            devices = self.audio_manager.getDevices(AudioManager.GET_DEVICES_INPUTS)
            _log("Available input devices: " + ", ".join(
                [f"{d.getProductName()} (type {d.getType()})" for d in devices]
            ))
        except Exception as e:
            _log(f"Cannot list devices: {e}")

        # --- 2. Выбираем Bluetooth HFP (не A2DP!) ---
        if _SELECTED_DEVICE is None:
            try:
                devices = self.audio_manager.getDevices(AudioManager.GET_DEVICES_INPUTS)
                # Приоритет: HFP (18), SCO (7), потом встроенный
                preferred_types = [
                    AudioDeviceInfo.TYPE_BLUETOOTH_SCO,   # 7
                    AudioDeviceInfo.TYPE_BLUETOOTH_A2DP,  # 8 (но микрофон может не работать)
                    AudioDeviceInfo.TYPE_WIRED_HEADSET,
                    AudioDeviceInfo.TYPE_BUILTIN_MIC
                ]
                for dev in devices:
                    dev_type = dev.getType()
                    if dev_type in preferred_types:
                        _SELECTED_DEVICE = dev
                        _log(f"🎯 Выбрано устройство: {dev.getProductName()} (type {dev_type})")
                        break
                if not _SELECTED_DEVICE:
                    _log("⚠️ Нет подходящих устройств")
            except Exception as e:
                _log(f"Device selection error: {e}")

        # --- 3. ПРИНУДИТЕЛЬНЫЙ ЗАПУСК HFP через BluetoothHeadset ---
        self._force_hfp_mode()

        # --- 4. Режим IN_COMMUNICATION ---
        try:
            self.audio_manager.setMode(AudioManager.MODE_IN_COMMUNICATION)
            _log("✅ Audio mode: MODE_IN_COMMUNICATION")
        except Exception as e:
            _log(f"setMode failed: {e}")

        # --- 5. Ждём SCO (для HFP) ---
        sco_success = self._wait_for_sco()

        if sco_success:
            self.sample_rate = 8000
            _log("ℹ️ SCO активен → sample_rate = 8000")
        else:
            _log("⚠️ SCO не включился, пытаемся читать с A2DP (может не работать)")

        # --- 6. Создаём AudioRecord с VOICE_COMMUNICATION ---
        buffer_size = AudioRecord.getMinBufferSize(
            self.sample_rate,
            AudioFormat.CHANNEL_IN_MONO,
            AudioFormat.ENCODING_PCM_16BIT
        )
        if buffer_size <= 0:
            buffer_size = self.frame_length * 2 * 4  # fallback

        buffer_size = max(buffer_size, self.frame_length * 2 * 4)

        try:
            self._record = AudioRecord(
                7,  # VOICE_COMMUNICATION — критично для BT
                self.sample_rate,
                AudioFormat.CHANNEL_IN_MONO,
                AudioFormat.ENCODING_PCM_16BIT,
                buffer_size
            )
            _log("✅ AudioRecord создан с VOICE_COMMUNICATION")
        except Exception as e:
            _log(f"VOICE_COMMUNICATION failed: {e}, fallback to DEFAULT")
            self._record = AudioRecord(
                0,  # DEFAULT
                self.sample_rate,
                AudioFormat.CHANNEL_IN_MONO,
                AudioFormat.ENCODING_PCM_16BIT,
                buffer_size
            )

        # --- 7. Привязка устройства ---
        if _SELECTED_DEVICE:
            try:
                success = self._record.setPreferredDevice(_SELECTED_DEVICE)
                _log(f"setPreferredDevice({'OK' if success else 'FAILED'})")
            except Exception as e:
                _log(f"setPreferredDevice error: {e}")

        # --- 8. Старт записи ---
        try:
            self._record.startRecording()
            _log("🎤 Recording STARTED")
        except Exception as e:
            _log(f"startRecording FAILED: {e}")
            raise

        # --- 9. Поток ---
        self.audio_thread = threading.Thread(
            target=self._audio_loop,
            args=(accuracy, hold_time, cooldown),
            daemon=True
        )
        self.audio_thread.start()

    def _force_hfp_mode(self):
        """Принудительно переключает Bluetooth в HFP"""
        try:
            adapter = BluetoothAdapter.getDefaultAdapter()
            if not adapter.isEnabled():
                return

            # Получаем профиль Headset (HFP)
            headset_profile = None

            def on_service_connected(profile, proxy):
                nonlocal headset_profile
                headset_profile = proxy
                _log("BluetoothHeadset connected")

            # Слушаем подключение
            activity = PythonActivity.mActivity
            activity.registerReceiver(
                None,  # не нужен ресивер
                None
            )

            adapter.getProfileProxy(
                activity,
                on_service_connected,
                BluetoothProfile.HEADSET
            )

            # Ждём немного
            time.sleep(1.5)

            if headset_profile:
                connected_devices = headset_profile.getConnectedDevices()
                for device in connected_devices:
                    if device.getName() and "airpods" in device.getName().lower():
                        _log(f"Найдены AirPods: {device.getName()}")
                        # Принудительно включаем голосовой канал
                        try:
                            headset_profile.startVoiceRecognition(device)
                            _log("startVoiceRecognition вызван")
                        except:
                            pass
                        break

        except Exception as e:
            _log(f"_force_hfp_mode error: {e}")

    def _wait_for_sco(self):
        """Ждёт включения SCO"""
        try:
            self.audio_manager.startBluetoothSco()
            self.audio_manager.setBluetoothScoOn(True)
            _log("startBluetoothSco() вызван")

            start = time.time()
            while time.time() - start < self.sco_wait:
                if self.audio_manager.isBluetoothScoOn():
                    _log("SCO ВКЛЮЧЁН!")
                    return True
                time.sleep(0.2)
            _log("SCO НЕ включился за отведённое время")
            return False
        except Exception as e:
            _log(f"SCO error: {e}")
            return False

    def _audio_loop(self, accuracy, hold_time, cooldown):
        while self.running.is_set():
            try:
                buf = bytearray(self.frame_length * 2)
                read = self._record.read(buf, 0, len(buf), AudioRecord.READ_BLOCKING)
                if read <= 0:
                    time.sleep(0.01)
                    continue

                # Распаковка PCM
                pcm = struct.unpack_from("h" * self.frame_length, buf[:read])

                # Амплитуда
                amplitudes = np.abs(np.array(pcm, dtype=np.int16))
                amplitude = amplitudes.mean()
                max_ampl = amplitudes.max()

                # Обновление UI
                Clock.schedule_once(lambda dt, a=amplitude: setattr(self.screen.ids.amplitude, 'text', f"{a:.0f}"))
                Clock.schedule_once(lambda dt, m=max_ampl: setattr(self.screen.ids.max_amplitude, 'text', f"{m}"))

                now = time.time()

                # Логика "pip"
                if amplitude > accuracy:
                    if self._loud_start is None:
                        self._loud_start = now
                    elif now - self._loud_start > hold_time:
                        if now - self._last_peak_time > cooldown:
                            self._peak_count += 1
                            self._last_peak_time = now
                        self._loud_start = None
                else:
                    if self._peak_count > 0 and now - self._last_peak_time > cooldown:
                        self.event_queue.put(("pip", self._peak_count))
                        self._last_event_time = now
                        self._peak_count = 0
                    self._loud_start = None

            except Exception as e:
                _log(f"[AudioLoop] Error: {e}")
                time.sleep(0.1)

    def stop(self):
        self.running.clear()
        if hasattr(self, 'audio_thread'):
            self.audio_thread.join(timeout=2)

        try:
            if hasattr(self, '_record'):
                self._record.stop()
                self._record.release()
        except:
            pass

        try:
            self.audio_manager.setBluetoothScoOn(False)
            self.audio_manager.stopBluetoothSco()
            self.audio_manager.setMode(AudioManager.MODE_NORMAL)
        except:
            pass