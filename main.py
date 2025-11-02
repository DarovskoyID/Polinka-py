import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="ctranslate2")
import asyncio
import os
from UI.Sources.main import JarvisApp

from SRC.env import *

def main():
    JarvisApp(
        animation_path=os.path.join("UI", "Sources", "animation.gif"),
        log_file=LOG_FILE,
        json_file=JSON_PHRASES_FILE,
        title="Jarvis"
    ).run()

if __name__ == '__main__':
    main()
