import sys

from pprint import pprint

from kneser_ney import KneserNeyLM
from word_table import WORD_SET_LOADED, \
    WORD_SET, load_word_table, filter_by_word_table, START_SYMBOL, END_SYMBOL,\
    UNKNOWN_KEY, PUNTUATIONS,MAX_WORD_LEN


def find_best_state(state_list, current_idx, sequence, kn_model):

    min_segment_len = min(current_idx, MAX_WORD_LEN)

    max_prob = -float('Inf')
    max_pre_idx = 0
    max_item = None

    for i in range(min_segment_len - 2, 0, -1):
        for j in range(min_segment_len - i - 1, 0, -1):
            for k in range(min_segment_len - i - j, 0, -1):
                trigram = (
                    "".join(sequence[current_idx - i - j - k: current_idx - i - j]),
                    "".join(sequence[current_idx - i - j: current_idx - i]),
                    "".join(sequence[current_idx - i: current_idx]),
                )
                prob = kn_model.logprob(filter_by_word_table(trigram))
                pre_idx = current_idx - i - j - k
                prob += state_list[pre_idx]["prob"]
                if prob > max_prob:
                    max_prob = prob
                    max_pre_idx = pre_idx
                    max_item = trigram

    return max_prob, max_pre_idx, max_item


def segmenter(sequence, kn_model):
    sequence = [START_SYMBOL, START_SYMBOL] + sequence + [END_SYMBOL]
    print(sequence)

    state_list = []

    init_state = {}
    init_state["pre_state"] = -1
    init_state["item"] = ()
    init_state["prob"] = 0

    state_list += [init_state for i in range(3)]

    for idx in range(3, len(sequence) + 1):
        best_state = dict()

        best_state["prob"], best_state["pre_state"], best_state["item"] = find_best_state(
            state_list,
            idx,
            sequence,
            kn_model
        )
        state_list.append(best_state)

    pprint(state_list)

    best_path = []
    node = len(sequence) #最后一个点
    best_path.append(node)
    while True:
        pre_node = state_list[node]["pre_state"]
        if pre_node == -1:
            break
        node = pre_node
        best_path.append(node)
    best_path.reverse()

    word_list = []

    for idx in best_path:
        word_list += list(state_list[idx]["item"])

    pprint(word_list)
    print("\n\n")

if __name__ == "__main__":
    load_word_table(sys.argv[1])

    kn_model = KneserNeyLM(3)
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








