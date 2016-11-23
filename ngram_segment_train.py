import sys
from ngram_segment import DNASegment
from word_table import load_word_table


if __name__ == "__main__":
    load_word_table(sys.argv[1])

    seg = DNASegment()
    seg.train(sys.argv[2], sys.argv[3])
    seg.dump_to_file(sys.argv[4])
