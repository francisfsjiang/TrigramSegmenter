import sys
import math
import pickle

from pprint import pprint
from collections import defaultdict

from word_table import UNKNOWN_KEY, START_SYMBOL, END_SYMBOL
#global parameter
DELIMITER = " - " #分词之后的分隔符


class Segmentor:
    def __init__(self):
        self.word_set = defaultdict(bool)
        self.bigram_count = defaultdict(int)
        self.gmax_word_length = 0

        self.V = 0
        self.T = defaultdict(int)
        self.N = defaultdict(int)

        self.debug = False

    @property
    def word_num(self):
        return len(self.word_set)

    def dprint(self, msg, end="\n"):
        if self.debug:
            print(msg, end=end)
            # pprint(msg)
            # print(end, end='')

    #获得两个词的转移概率
    def get_word_trans_prob(self, first_word, second_word):
        punishment = 0
        key_word = []
        if first_word not in self.word_set:
            key_word.append(UNKNOWN_KEY)
            punishment -= 100 * len(first_word)
        else:
            key_word.append(first_word)

        if second_word not in self.word_set:
            key_word.append(UNKNOWN_KEY)
            punishment -= 300 * len(second_word)
        else:
            key_word.append(second_word)

        key_word = tuple(key_word)
        index_word = key_word[0]
        # if key_word == ('工信处', '女'):
        #     self.dprint("break")
        #     pass

        if key_word in self.bigram_count:
            numerator = self.bigram_count[key_word] * self.N[index_word]
            denominator = (self.N[index_word] + self.T[index_word]) * self.N[index_word]
        elif index_word in self.T:
            numerator = self.T[index_word] * self.N[index_word]
            denominator = (self.word_num - self.T[index_word]) * \
                          (self.N[index_word] + self.T[index_word]) * self.N[index_word]
        else:
            numerator = math.e
            denominator = 1
            punishment -= 10

        self.dprint("%s %s    %s" % (first_word, second_word, str(key_word)))
        if index_word in self.T:
            self.dprint("%d %d " % (self.T[index_word], self.N[index_word],))
        self.dprint("%f %f " % (numerator, denominator, ), end="")

        prob = -float('inf')
        try:
            prob = math.log(
                numerator / denominator
            )
            prob += punishment
        except ZeroDivisionError as e:
            pass

        self.dprint(" %f" % (prob, ))
        return prob


    #寻找node的最佳前驱节点
    #方法为寻找所有可能的前驱片段
    def get_best_pre_node(self, sequence, node, node_state_list):
        #如果node比最大词长小，取的片段长度以node的长度为限
        max_seg_length = min([node, self.gmax_word_length])

        max_prob = -float('inf')
        max_pre_node = 0
        max_segment = 0

        candidates = []

        #获得所有的前驱片段，并记录累加概率
        for segment_length in range(1, max_seg_length+1):
            for pre_segment_length in range(1, max_seg_length + 1 - segment_length):
                segment_start_node = node-segment_length
                segment = "".join(sequence[segment_start_node:node]) #获取片段

                pre_segment_start_node = node - segment_length - pre_segment_length
                if pre_segment_start_node == 0 and pre_segment_length != 1:
                    continue
                pre_segment = "".join(sequence[pre_segment_start_node:pre_segment_length + pre_segment_start_node])

                candidate_prob_sum = 0

                segment_prob = \
                    self.get_word_trans_prob(pre_segment, segment)
                candidate_prob_sum += segment_prob

                if pre_segment_start_node > 2:
                    pre_pre_segment = node_state_list[pre_segment_start_node]["segment"][1]
                    pre_segment_prob = \
                        self.get_word_trans_prob(pre_pre_segment, pre_segment)
                    candidate_prob_sum += pre_segment_prob

                pre_node_prob_sum = node_state_list[pre_segment_start_node]["prob_sum"]  #前驱节点的概率的累加值
                candidate_prob_sum += pre_node_prob_sum

                self.dprint(pre_node_prob_sum)
                self.dprint(candidate_prob_sum)

                #当前node一个候选的累加概率值
                # candidate_prob_sum = segment_prob

                candidates.append({
                    "prob_sum": candidate_prob_sum,
                    "pre_node": pre_segment_start_node,
                    "segment": (pre_segment, segment)
                })

                # if candidate_prob_sum > max_prob:
                #     max_prob = candidate_prob_sum
                #     max_pre_node = pre_segment_start_node
                #     max_segment = (pre_segment, segment)

                self.dprint("-"*10)

        candidates.sort(key=lambda x: x["prob_sum"], reverse=True)
        candidates_max_prob = candidates[0]["prob_sum"]
        candidates_max_prob += candidates_max_prob * 0.07
        self.dprint(candidates)
        max_len = 0
        max_node = candidates[0]
        self.dprint(candidates_max_prob)
        for cand in candidates:
            l = len("".join(cand["segment"]))
            if l > max_len and cand["prob_sum"] > candidates_max_prob:
                max_len = l
                max_node = cand

        self.dprint("Max: ")
        self.dprint("%f %d %s" % (
            max_node["prob_sum"],
            max_node["pre_node"],
            max_node["segment"]
        ))

        return max_node

    #最大概率分词
    def mp_seg(self, sequence):
        sequence = [START_SYMBOL] + sequence

        #初始化
        node_state_list = [] #记录节点的最佳前驱，index就是位置信息
        #初始节点，也就是0节点信息
        ini_state = {}
        ini_state["pre_node"] = -1 #前一个节点
        ini_state["prob_sum"] = 0 #当前的概率总和
        ini_state["segment"] = None
        node_state_list.append(ini_state)
        node_state_list.append(ini_state)
        #字符串概率为2元概率
        #P(a b c) = P(a|<S>)P(b|a)P(c|b)

        #逐个节点寻找最佳前驱节点
        for node in range(2, len(sequence) + 1):
            # if node > 5:
            #     exit(-1)
            self.dprint("Node: %d" % node)
            #寻找最佳前驱，并记录当前最大的概率累加值

            #添加到队列
            cur_node = self.get_best_pre_node(sequence, node, node_state_list)

            node_state_list.append(
                cur_node
            )

            self.dprint("\n")

        for i in enumerate(node_state_list):
            self.dprint(i)

        # step 2, 获得最优路径,从后到前
        best_path = []
        node = len(sequence) #最后一个点
        while True:
            pre_node = node_state_list[node]["pre_node"]
            if pre_node == -1:
                break

            best_path.append(node_state_list[node]["segment"])
            node = pre_node
        best_path.reverse()

        # step 3, 构建切分
        word_list = []
        for i in best_path:
            word_list.append(i[0])
            word_list.append(i[1])
        if word_list[0] == START_SYMBOL:
            word_list = word_list[1:]
        return word_list

    #加载词典，为词\t词频的格式
    def train(self, bigram_file, word_table):

        f = open(word_table, "r", encoding="utf-8")
        for line in f.readlines():
            line = line.strip()
            self.word_set[line] = True
            if len(line) > self.gmax_word_length:
                self.gmax_word_length = len(line)

        self.word_set[START_SYMBOL] = True
        self.word_set[UNKNOWN_KEY] = True

        self.V = self.word_num

        self.bigram_count = pickle.load(open(bigram_file, "rb"))

        self.bigram_count[(UNKNOWN_KEY, UNKNOWN_KEY)] = 1

        for key, value in self.bigram_count.items():
            first_key, second_key = key
            if first_key == UNKNOWN_KEY or second_key == UNKNOWN_KEY:
                self.bigram_count[key] = 1
            #     self.dprint(key, " ", value)
            self.T[first_key] += 1
            self.N[first_key] += value

    def dump_to_file(self, file_name):
        f = open(file_name, "wb")
        # pickle.dump((
        #     self.word1_dict,
        #     self.word1_dict_count,
        #     self.word2_dict,
        #     self.word2_dict_count,
        #     self.all_freq,
        #     self.gmax_word_length
        # ), f)
        pickle.dump(self, f)
        f.close()

    @staticmethod
    def load_from_file(file_name):
        f = open(file_name, "rb")

        # self.word1_dict, \
        # self.word1_dict_count, \
        # self.word2_dict, \
        # self.word2_dict_count, \
        # self.all_freq, \
        # self.gmax_word_length = pickle.load(f)
        obj = pickle.load(f)
        f.close()
        return obj

if __name__ == "__main__":

    seger = Segmentor()
    seger.train(sys.argv[1], sys.argv[2])
    seger.dump_to_file(sys.argv[3])
