from UI.Sources.main import JarvisApp
from android.permissions import Permission
from jnius import autoclass, cast
from SRC.env import *
from kivy.utils import platform
from kivy.clock import Clock

PythonActivity = autoclass('org.kivy.android.PythonActivity')
Manifest = autoclass('android.Manifest')

activity = PythonActivity.mActivity
PERMISSION_GRANTED = 0

# Список нужных разрешений
REQUIRED_PERMISSIONS = [
    Permission.RECORD_AUDIO,
    Permission.BLUETOOTH,
    Permission.BLUETOOTH_ADMIN,
    Permission.BLUETOOTH_CONNECT,
    Permission.READ_EXTERNAL_STORAGE,
    Permission.WRITE_EXTERNAL_STORAGE
]

# Функция для запроса полного доступа к файлам на Android 11+
def request_all_files_access():
    if platform != "android":
        return

    Environment = autoclass('android.os.Environment')
    Settings = autoclass('android.provider.Settings')
    Uri = autoclass('android.net.Uri')
    Intent = autoclass('android.content.Intent')

    if not Environment.isExternalStorageManager():
        intent = Intent(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION)
        uri = Uri.fromParts("package", activity.getPackageName(), None)
        intent.setData(uri)
        activity.startActivity(intent)

# Проверка, даны ли все разрешения
def check_permissions():
    for perm in REQUIRED_PERMISSIONS:
        if activity.checkSelfPermission(perm) != PERMISSION_GRANTED:
            return False
    return True

# Запрос разрешений через стандартный Android API
def request_permissions(callback=None):
    missing = [perm for perm in REQUIRED_PERMISSIONS if activity.checkSelfPermission(perm) != PERMISSION_GRANTED]
    if not missing:
        if callback:
            callback(True)
        return

    # Запрашиваем недостающие разрешения
    activity.requestPermissions(missing, 0)

    # Ожидаем несколько секунд, потом проверяем снова
    # Можно использовать Kivy Clock для отложенной проверки
    def _check(dt):
        if check_permissions():
            if callback:
                callback(True)
        else:
            if callback:
                callback(False)
    Clock.schedule_once(_check, 1)  # Проверка через 1 сек

def main():
    # 1. Запрос полного доступа к файлам
    request_all_files_access()

    # 2. Запуск приложения только после разрешений
    def start_app(permissions_granted):
        if not permissions_granted:
            print("Не все разрешения даны. Приложение не запущено.")
            return

        JarvisApp(
            animation_path=ANIMATION_PATH,
            log_file=LOG_FILE,
            json_file=JSON_PHRASES_FILE,
            title="Jarvis"
        ).run()

    # 3. Запрашиваем разрешения с callback
    request_permissions(callback=start_app)


if __name__ == "__main__":
    main()
