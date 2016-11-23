import sys
import os
import pickle

from collections import defaultdict

from word_table import WORD_SET, WORD_SET_LOADED,\
    START_SYMBOL, END_SYMBOL, UNKNOWN_KEY, PUNTUATIONS, MAX_WORD_LEN


u_counter = defaultdict(int)


def add_counter(item, dict):
    dict[item] += 1


def u_count(item):
    add_counter(item, u_counter)


def save_counter(c, file_name):
    f = open(os.path.join("records/", file_name), "wb")
    pickle.dump(c, f)
    f.close()


def save():
    save_counter(u_counter, "unigram_counter.record")


def process_file(file_name):
    file = open(file_name, "r", encoding="utf-8")

    line_num = 0
    for line in file.readlines():
        for word in line.split():
            if word in PUNTUATIONS:
                continue

            u_count(word)

        line_num += 1
        if line_num % 1000 == 0:
            print(file_name, " ", line_num)
    file.close()

if __name__ == "__main__":
    for i in range(1, len(sys.argv)):
        process_file(sys.argv[i])

    u_counter[START_SYMBOL] = 1
    u_counter[UNKNOWN_KEY] = 1
    u_counter[END_SYMBOL] = 1

    #add pangu dict
    f = open(os.path.join("data/pangu_word_table.utf8"), "r")
    for w in f.readlines():
        w = w.strip()
        u_count(w)
    f.close()

    save()

    print(len(u_counter))



