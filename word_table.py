import pickle

START_SYMBOL = "<S>"
END_SYMBOL = "<E>"
UNKNOWN_KEY = "<U>"

PUNTUATIONS = "，。【】{}《》、`‘ ’ ()（）；：''“”-『』？！-—\n"

WORD_SET = set()
WORD_SET_LOADED = False
MAX_WORD_LEN = 14


# def load_word_table(file_name):
#     global WORD_SET, WORD_SET_LOADED
#
#     try:
#         f = open(file_name, "rb")
#     except FileNotFoundError:
#         print("word_table not load")
#         WORD_SET_LOADED = False
#         WORD_SET = None
#         return
#
#     WORD_SET = pickle.load(f)
#     print("word_table loaded")
#     WORD_SET_LOADED = True
#     f.close()
#
#
# def filter_by_word_table(item):
#     if not WORD_SET:
#         return item
#     tmp = []
#     for i in item:
#         if i in WORD_SET or i == START_SYMBOL or i == END_SYMBOL:
#             tmp.append(i)
#         else:
#             tmp.append(UNKNOWN_KEY)
#     return tuple(tmp)
