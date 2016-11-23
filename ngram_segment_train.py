import sys

from segmentor import Segmentor

if __name__ == "__main__":

    seger = Segmentor()
    seger.train(sys.argv[1], sys.argv[2])
    seger.dump_to_file(sys.argv[3])
