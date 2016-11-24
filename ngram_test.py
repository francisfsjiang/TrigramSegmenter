import sys

from pprint import pprint
from collections import defaultdict

from segmentor import Segmentor
from word_table import PUNTUATIONS

TOTAL_SEGS = 0
TOTAL_SEGS_GOLD = 0
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
        test_line = test_line.strip()

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
        acc = correct / len(result)
        recall = correct / len(gold_seq)
        f = 0
        try:
            f_value = acc * recall * 2 / (acc + recall)
        except ZeroDivisionError:
            pass
        ACC_PER_SEQ.append(
            acc
        )
        if acc > 0.8:
            count_line += 1
            TOTAL_SEGS += len(result)
            TOTAL_SEGS_GOLD += len(gold_seq)
            TOTAL_SEGS_CORRECT += correct

        line_no += 1
        print(gold_seq)
        print(result)
        print("%d: acc:%f %%  recall: %f %%  f: %f %%" % (line_no, acc * 100, recall * 100, f_value * 100))

    acc = TOTAL_SEGS_CORRECT / TOTAL_SEGS
    recall = TOTAL_SEGS_CORRECT / TOTAL_SEGS_GOLD
    f_value = acc * recall * 2 / (acc * recall)
    print("Total ACC: %f %%" % (acc, ))
    print("Total RECALL: %f %%" % (recall, ))
    print("Total F: %f %%" % (f, ))
    print(count_line)
