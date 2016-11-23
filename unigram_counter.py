import sys
import os
import pickle

from collections import defaultdict

from word_table import WORD_SET, WORD_SET_LOADED,\
    START_SYMBOL, END_SYMBOL, UNKNOWN_KEY, PUNTUATIONS, MAX_WORD_LEN


u_counter = defaultdict(int)


def add_counter(item, dict):
    dict[item] += 1
    # dict[item] = dict.get(item, 0) + 1


def b_count(item):
    item = filter_by_word_table(item)
    add_counter(item, b_counter)


def u_count(item):
    add_counter(item, u_counter)


def save_counter(c, file_name):
    f = open(os.path.join("records/", file_name), "w", encoding="utf-8")
    for key, value in c.items():
        f.write(
            "%s %d\n" % (" ".join(key), value)
        )
    f.close()


def save():

    save_counter(b_counter, "bigram_counter.record")

    save_counter(u_counter, "unigram_counter.record")

    if not WORD_SET_LOADED:
        save_word_table(u_counter, "word_table.utf8")


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
            u_count((word, ))

            last_word = word
        line_num += 1
        if line_num % 1000 == 0:
            print(file_name, " ", line_num)
    file.close()

if __name__ == "__main__":
    for i in range(1, len(sys.argv)):
        process_file(sys.argv[i])

    u_counter[START_SYMBOL] = 1
    u_counter[UNKNOWN_KEY] = 1

    #add pangu dict

    f = open(os.path.join("data/word_table.utf8.pangu"), "r")
    for w in f.readlines():
        w = w.strip()
        u_count((w, ))
    f.close()

    save()

    print(len(b_counter))
    print(len(u_counter))



