from UI.Sources.main import JarvisApp

from SRC.env import *

def main():
    JarvisApp(
        animation_path=ANIMATION_PATH,
        log_file=LOG_FILE,
        json_file=JSON_PHRASES_FILE,
        title="Jarvis"
    ).run()

if __name__ == '__main__':
    main()
