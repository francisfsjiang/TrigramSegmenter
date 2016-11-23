

START_SYMBOL = "🐸"
END_SYMBOL = "➿"
UNKNOWN_KEY = "❓"

WORD_SET = set()
WORD_SET_LOADED = False


def load_word_table(file_name):
    global WORD_SET, WORD_SET_LOADED

    try:
        f = open(file_name, "r", encoding="utf-8")
    except FileNotFoundError:
        print("word_table not load")
        WORD_SET_LOADED = False
        WORD_SET = None
        return

    for line in f.readlines():
        WORD_SET.add(
            line.split()[0]
        )
    print("word_table loaded")
    WORD_SET_LOADED = True
    f.close()
