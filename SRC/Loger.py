from SRC.env import *

# -------------------------
# Логирование
# -------------------------
def _log(msg: str):
    try:
        filelog = open(LOG_FILE, 'a+', encoding='utf-16')
        filelog.write(msg + "\n")
        filelog.close()
    except Exception:
        pass