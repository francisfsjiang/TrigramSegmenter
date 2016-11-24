import sys

from segmentor import Segmentor


if __name__ == "__main__":
    seger = Segmentor.load_from_file(sys.argv[1])

    # sequence = "人类社会前进的航船就要驶入21世纪的新航程"
    sequence = "工信处女干事每月经过下属科室都要亲口交代24口交换机等技术性器件的安装工作"
    seg_sequence = seger.mp_seg(list(sequence))
    print("original sequence: " + sequence)
    print("segment result: " + seg_sequence)

    exit(0)
    # lines = []
    # with open(sys.argv[2], "r", encoding="utf-8") as f:
    #     lines = list(f.readlines())
    #
    # for line in lines[:4]:
    #     sequence = []
    #     for w in line:
    #         if w not in PUNTUATIONS:
    #             sequence.append(w)
    #         elif sequence:
    #             segmenter(sequence, kn_model)
    #             sequence = []
    #         else:
    #             continue
    #     if sequence:
    #         segmenter(sequence, kn_model)
    #         sequence = []
    #
