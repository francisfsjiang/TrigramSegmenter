import sys

from pprint import pprint
from collections import defaultdict

from segmentor import Segmentor
from word_table import PUNTUATIONS

TOTAL_SEGS = 0
TOTAL_SEGS_CORRECT = 0
ACC_PER_SEQ = []


def lcs(x_list, y_list):
    dp = {
        0: defaultdict(int)
    }
    for i in range(1, len(x_list) + 1):
        dp[i] = defaultdict(int)
        for j in range(1, len(y_list) + 1):
            if x_list[i - 1] == y_list[j - 1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    return dp[len(x_list)][len(y_list)]


if __name__ == "__main__":
    seger = Segmentor.load_from_file(sys.argv[1])
    seger.debug = False

    seqs = [
        # "人类社会前进的航船就要驶入21世纪的新航程",
        # "结婚的和尚未结婚的",
        # "他说的确实在理",
        # "这事的确定不下来",
        "费孝通向人大常委会提交书面报告",
        # "工信处女干事每月经过下属科室都要亲口交代24口交换机等技术性器件的安装工作",
        # "你认为学生会听老师的吗",
        # "他是研究生物化学的",
        # "人的一生是有限的",
        # "而为人民服务是无限的",
    ]
    for sequence in seqs:
        seg_sequence = seger.mp_seg(list(sequence))
        print("original sequence: " + sequence)
        print("segment result: %s" % seg_sequence)
        print("test file: %s" % sys.argv[2])
        print("gold file: %s" % sys.argv[3])
    exit(-1)

    test_f = open(sys.argv[2], "r", encoding="utf-8")
    gold_f = open(sys.argv[3], "r", encoding="utf-8")
    line_no = 0
    count_line = 0
    test_lines = list(test_f.readlines())
    gold_lines = list(gold_f.readlines())
    for test_line, gold_line in zip(test_lines, gold_lines):
        # test_line = test_f.readline().strip()
        # gold_line = gold_f.readline().strip()
        if not test_line or not gold_line:
            break
        gold_seq = gold_line.split()
        # print(gold_seq)

        result = []
        sequence = []
        for w in test_line:
            if w not in PUNTUATIONS:
                sequence.append(w)
            elif sequence:
                result += \
                    seger.mp_seg(sequence)
                result += [w]
                sequence = []
            else:
                result += [w]
                continue
        if sequence:
            result += seger.mp_seg(sequence)
            sequence = []

        correct = lcs(gold_seq, result)
        acc = correct / len(gold_seq)
        ACC_PER_SEQ.append(
            acc
        )
        if acc > 0.8:
            count_line += 1
            TOTAL_SEGS += len(gold_seq)
            TOTAL_SEGS_CORRECT += correct

        line_no += 1
        print("%d: %f %%" % (line_no, acc * 100))
        # print(result)

    print("Total ACC: %f %%" % (TOTAL_SEGS_CORRECT / TOTAL_SEGS * 100, ))
    print(count_line)
