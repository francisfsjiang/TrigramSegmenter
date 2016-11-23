import sys

from kneser_ney import KneserNeyLM
from word_table import WORD_SET_LOADED, WORD_SET, load_word_table


if __name__ == "__main__":
    load_word_table(sys.argv[1])

    kn_model = KneserNeyLM(3)
    kn_model.load_from_file("records/kneser_nay.model")





