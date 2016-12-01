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
        "人类社会前进的航船就要驶入21世纪的新航程",
        "结婚的和尚未结婚的",
        "他说的确实在理",
        "这事的确定不下来",
        "费孝通向人大常委会提交书面报告",
        "工信处女干事每月经过下属科室都要亲口交代24口交换机等技术性器件的安装工作",
        "你认为学生会听老师的吗",
        "他是研究生物化学的",
        "人的一生是有限的",
        "而为人民服务是无限的",
        "邓颖超生前使用过的物品",
        "有意见分歧"
    ]
    for sequence in seqs:
        seg_sequence = seger.cut(list(sequence))
        print("original sequence: " + sequence)
        print("segment result: %s" % seg_sequence)
        print("test file: %s" % sys.argv[2])
        print("gold file: %s" % sys.argv[3])
