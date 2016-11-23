import sys
import os

from collections import defaultdict
from pprint import pprint

from word_table import WORD_SET, WORD_SET_LOADED, load_word_table

START_SYMBOL = "🐸"
END_SYMBOL = "➿"
UNKNOWN_KEY = "❓"


t_counter   = defaultdict(int)
t_counter_2 = defaultdict(int)
b_counter   = defaultdict(int)
b_counter_2 = defaultdict(int)
u_counter   = defaultdict(int)

u_set       = defaultdict(set)
b_set       = defaultdict(set)
t_set       = defaultdict(set)


def add_counter(item, dict):
    dict[item] += 1
    # dict[item] = dict.get(item, 0) + 1


def add_set(item, item2, dict):
    dict[item].add(item2)
    # if item in dict:
    #     dict[item].add(item2)
    # else:
    #     dict[item] = {item2}


def filter_by_word_table(item):
    if not WORD_SET:
        return item
    tmp = []
    for i in item:
        if i in WORD_SET:
            tmp.append(i)
        else:
            tmp.append(UNKNOWN_KEY)
    return tuple(tmp)


def t_count(item):
    item = filter_by_word_table(item)
    add_counter(item, t_counter)
    add_counter(item[:2], t_counter_2)
    add_set(item[:2], item[2], t_set)


def b_count(item):
    item = filter_by_word_table(item)
    add_counter(item, b_counter)
    add_counter(item[:1], b_counter_2)
    add_set(item[:1], item[1], b_set)

    add_set(item[1:2], item[0], u_set)


def u_count(item):
    item = filter_by_word_table(item)
    add_counter(item, u_counter)


def save_counter(c, file_name):
    f = open(os.path.join("records/", file_name), "w", encoding="utf-8")
    for key, value in c.items():
        f.write(
            "%s %d\n" % (" ".join(key), value)
        )
    f.close()


def save_set(s, file_name):
    f = open(os.path.join("records/", file_name), "w", encoding="utf-8")
    for key, value in s.items():
        f.write(
            "%s %d\n" % (" ".join(key), len(value))
        )
    f.close()


def save_word_table(d, file_name):
    f = open(os.path.join("data/", file_name), "w", encoding="utf-8")
    for key, value in d.items():
        if value > 1:
            f.write(
                "%s\n" % (key[0], )
            )
    f.close()


def save():
    save_counter(t_counter, "trigram_counter.record")
    save_counter(t_counter_2, "trigram_counter_c.record")

    save_counter(b_counter, "bigram_counter.record")
    save_counter(b_counter_2, "bigram_counter_c.record")

    save_counter(u_counter, "unigram_counter.record")

    save_set(t_set, "trigram_set.record")
    save_set(b_set, "bigram_set.record")
    save_set(u_set, "unigram_set.record")

    if not WORD_SET_LOADED:
        save_word_table(u_counter, "word_table.utf8")


def process_file(file_name):
    file = open(file_name, "r", encoding="utf-8")

    last_word = last_last_word = START_SYMBOL
    line_num = 0
    for line in file.readlines():
        for word in line.split():
            if word in "，。【】{}《》、`‘ ’ ()（）；：''“”-『』？！":
                if last_word != START_SYMBOL:
                    t_count((last_last_word, last_word, END_SYMBOL))
                    b_count((last_word, END_SYMBOL))
                    # pprint(t_counter)
                    # pprint(b_counter)
                    # pprint(u_counter)
                    # exit(-1)
                last_word = last_last_word = START_SYMBOL
                continue

            t_count((last_last_word, last_word, word))
            b_count((last_word, word, ))
            u_count((word, ))

            last_last_word = last_word
            last_word = word
        line_num += 1
        if line_num % 1000 == 0:
            print(file_name, " ", line_num)
    file.close()

if __name__ == "__main__":
    load_word_table(sys.argv[1])

    for i in range(len(sys.argv) - 2):
        process_file(sys.argv[i + 2])

    save()
    print(len(t_counter))
    print(len(b_counter))
    print(len(u_counter))



