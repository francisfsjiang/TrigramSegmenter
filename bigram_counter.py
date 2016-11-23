import sys
import os
import pickle

from collections import defaultdict

from word_table import WORD_SET, WORD_SET_LOADED,\
    START_SYMBOL, END_SYMBOL, UNKNOWN_KEY, PUNTUATIONS, MAX_WORD_LEN


b_counter   = defaultdict(int)
u_counter   = None


def filter_by_word_table(item):
    if not u_counter:
        return item
    tmp = []
    for i in item:
        if i in u_counter:
            tmp.append(i)
        else:
            tmp.append(UNKNOWN_KEY)
    return tuple(tmp)


def add_counter(item, dict):
    dict[item] += 1
    # dict[item] = dict.get(item, 0) + 1


def b_count(item):
    item = filter_by_word_table(item)
    add_counter(item, b_counter)


def save_counter(c, file_name):
    f = open(os.path.join("records/", file_name), "wb")
    pickle.dump(c, f)
    f.close()


def save():
    save_counter(b_counter, "bigram_counter.record")


def process_file(file_name):
    file = open(file_name, "r", encoding="utf-8")

    last_word = START_SYMBOL
    line_num = 0
    for line in file.readlines():
        for word in line.split():
            if word in PUNTUATIONS:
                if last_word != START_SYMBOL:
                    b_count((last_word, END_SYMBOL))
                last_word = START_SYMBOL
                continue

            b_count((last_word, word, ))

            last_word = word
        line_num += 1
        if line_num % 1000 == 0:
            print(file_name, " ", line_num)
    file.close()


if __name__ == "__main__":
    f = open("records/unigram_counter.record", "rb")
    u_counter = pickle.load(f)
    f.close()

    for i in range(1, len(sys.argv)):
        process_file(sys.argv[i])

    save()

    print(len(b_counter))
    print(len(u_counter))



