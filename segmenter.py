import sys

from pprint import pprint

from kneser_ney import KneserNeyLM
from word_table import WORD_SET_LOADED, \
    WORD_SET, load_word_table, filter_by_word_table, START_SYMBOL, END_SYMBOL,\
    UNKNOWN_KEY, PUNTUATIONS,MAX_WORD_LEN


def get_best_pre_node(sequence, node, node_state_list, kn_model):
    #如果node比最大词长小，取的片段长度以node的长度为限
    max_seg_length = min([node, MAX_WORD_LEN])
    pre_node_list = [] #前驱节点列表

    #获得所有的前驱片段，并记录累加概率
    for segment_length in range(1,max_seg_length+1):
        segment_start_node = node-segment_length
        segment = "".join(sequence[segment_start_node:node]) #获取片段

        pre_node = segment_start_node  #取该片段，则记录对应的前驱节点

        if pre_node == 0:
            #如果前驱片段开始节点是序列的开始节点，
            #则概率为<S>转移到当前词的概率
            #segment_prob = self.get_word_prob(segment)
            segment_prob = \
                kn_model.logprob((START_SYMBOL, segment))
        else: #如果不是序列开始节点，按照二元概率计算
            #获得前驱片段的前一个词
            pre_pre_node = node_state_list[pre_node]["pre_node"]
            pre_pre_word = "".join(sequence[pre_pre_node:pre_node])
            segment_prob = \
                kn_model.logprob((pre_pre_word, segment))


        pre_node_prob_sum = node_state_list[pre_node]["prob_sum"] #前驱节点的概率的累加值

        #当前node一个候选的累加概率值
        candidate_prob_sum = pre_node_prob_sum + segment_prob

        pre_node_list.append((pre_node, candidate_prob_sum))

    #找到最大的候选概率值
    (best_pre_node, best_prob_sum) = \
        max(pre_node_list, key=lambda d:d[1])
    return (best_pre_node, best_prob_sum)

    #最大概率分词
def segmenter(sequence, kn_model):

    #初始化
    node_state_list = [] #记录节点的最佳前驱，index就是位置信息
    #初始节点，也就是0节点信息
    ini_state = {}
    ini_state["pre_node"] = -1 #前一个节点
    ini_state["prob_sum"] = 0 #当前的概率总和
    node_state_list.append( ini_state )
    #字符串概率为2元概率
    #P(a b c) = P(a|<S>)P(b|a)P(c|b)

    #逐个节点寻找最佳前驱节点
    for node in range(1,len(sequence) + 1):
        #寻找最佳前驱，并记录当前最大的概率累加值
        (best_pre_node, best_prob_sum) = \
            get_best_pre_node(sequence, node, node_state_list, kn_model)

        #添加到队列
        cur_node = {}
        cur_node["pre_node"] = best_pre_node
        cur_node["prob_sum"] = best_prob_sum
        node_state_list.append(cur_node)
        #print "cur node list",node_state_list

    # step 2, 获得最优路径,从后到前
    best_path = []
    node = len(sequence) #最后一个点
    best_path.append(node)
    while True:
        pre_node = node_state_list[node]["pre_node"]
        if pre_node == -1:
            break
        node = pre_node
        best_path.append(node)
    best_path.reverse()

    # step 3, 构建切分
    word_list = []
    for i in range(len(best_path)-1):
        left = best_path[i]
        right = best_path[i + 1]
        word = "".join(sequence[left:right])
        word_list.append(word)

    seg_sequence = " - ".join(word_list)
    print(seg_sequence)
    return seg_sequence

# def find_best_state(state_list, current_idx, sequence, kn_model):
#
#     min_segment_len = min(current_idx, MAX_WORD_LEN)
#
#     max_prob = -float('Inf')
#     max_pre_idx = 0
#     max_item = None
#
#     for i in range(min_segment_len - 2, 0, -1):
#         for j in range(min_segment_len - i - 1, 0, -1):
#             for k in range(min_segment_len - i - j, 0, -1):
#                 trigram = (
#                     "".join(sequence[current_idx - i - j - k: current_idx - i - j]),
#                     "".join(sequence[current_idx - i - j: current_idx - i]),
#                     "".join(sequence[current_idx - i: current_idx]),
#                 )
#                 prob = kn_model.logprob(filter_by_word_table(trigram))
#                 pre_idx = current_idx - i - j - k
#                 prob += state_list[pre_idx]["prob"]
#                 if prob > max_prob:
#                     max_prob = prob
#                     max_pre_idx = pre_idx
#                     max_item = trigram
#
#     return max_prob, max_pre_idx, max_item
#
#
# def segmenter(sequence, kn_model):
#     sequence = [START_SYMBOL] + sequence + [END_SYMBOL]
#     print(sequence)
#
#     state_list = []
#
#     init_state = {}
#     init_state["pre_state"] = -1
#     init_state["item"] = ()
#     init_state["prob"] = 0
#
#     state_list += [init_state for i in range(3)]
#
#     for idx in range(3, len(sequence) + 1):
#         best_state = dict()
#
#         best_state["prob"], best_state["pre_state"], best_state["item"] = find_best_state(
#             state_list,
#             idx,
#             sequence,
#             kn_model
#         )
#         state_list.append(best_state)
#
#     pprint(state_list)
#
#     best_path = []
#     node = len(sequence) #最后一个点
#     best_path.append(node)
#     while True:
#         pre_node = state_list[node]["pre_state"]
#         if pre_node == -1:
#             break
#         node = pre_node
#         best_path.append(node)
#     best_path.reverse()
#
#     word_list = []
#
#     for idx in best_path:
#         word_list += list(state_list[idx]["item"])
#
#     pprint(word_list)
#     print("\n\n")

if __name__ == "__main__":
    load_word_table(sys.argv[1])

    kn_model = KneserNeyLM(2)
    kn_model.load_from_file("records/kneser_nay.model")

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








