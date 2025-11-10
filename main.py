from UI.Sources.main import JarvisApp
from android.permissions import request_permissions, Permission

from SRC.env import *

def main():
    request_permissions([Permission.RECORD_AUDIO])
    JarvisApp(
        animation_path=ANIMATION_PATH,
        log_file=LOG_FILE,
        json_file=JSON_PHRASES_FILE,
        title="Jarvis"
    ).run()

if __name__ == '__main__':
    main()
