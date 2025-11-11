

# -------------------------
# Логирование
# -------------------------
def _log(msg: str):
    try:
        from SRC.env import LOG_FILE
        filelog = open(LOG_FILE, 'a+', encoding='utf-16')
        filelog.write(msg + "\n")
        filelog.close()
        print(LOG_FILE, msg)
    except Exception as e:
        print("Problem log.txt", e)