import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="ctranslate2")
import asyncio
import os
from UI.Sources.main import JarvisApp

from SRC.env import *

def main():
    JarvisApp(
        animation_path=os.path.join("UI", "Sources", "animation.gif"),
        log_file=os.path.join("log.txt"),
        json_file=os.path.join("commands.json"),
        title="Jarvis"
    ).run()

if __name__ == '__main__':
    main()
