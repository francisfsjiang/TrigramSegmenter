import sys

from segmentor import Segmentor


if __name__ == "__main__":
    myseg = Segmentor()
    myseg.load_from_file(sys.argv[1])

    sequence = "人类社会前进的航船就要驶入21世纪的新航程"
    seg_sequence = myseg.mp_seg(sequence)
    print("original sequence: " + sequence)
    print("segment result: " + seg_sequence)

    exit(0)
    lines = []
    with open(sys.argv[2], "r", encoding="utf-8") as f:
        lines = list(f.readlines())

    for line in lines[:4]:
        sequence = []
        for w in line:
            if w not in PUNTUATIONS:
                sequence.append(w)
            elif sequence:
                segmenter(sequence, kn_model)
                sequence = []
            else:
                continue
        if sequence:
            segmenter(sequence, kn_model)
            sequence = []








