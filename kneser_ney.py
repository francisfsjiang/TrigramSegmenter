import math
import pickle
import sys

from collections import Counter, defaultdict
from pprint import pprint

from word_table import WORD_SET, WORD_SET_LOADED, \
    load_word_table, filter_by_word_table, START_SYMBOL, END_SYMBOL, UNKNOWN_KEY


class KneserNeyLM:

    def __init__(self, highest_order):
        """
        Constructor for KneserNeyLM.

        Params:
            highest_order [int] The order of the language model.
            ngrams [list->tuple->string] Ngrams of the highest_order specified.
                Ngrams at beginning / end of sentences should be padded.
            start_pad_symbol [string] The symbol used to pad the beginning of
                sentences.
            end_pad_symbol [string] The symbol used to pad the beginning of
                sentences.
        """
        self.highest_order = highest_order
        self.lm = None

    def train(self, ngrams):
        """
        Train the language model on the given ngrams.

        Params:
            ngrams [list->tuple->string] Ngrams of the highest_order specified.
        """
        kgram_counts = self._calc_adj_counts(Counter(ngrams))
        self.lm = probs = self._calc_probs(kgram_counts)

        #未知key惩罚
        for order in self.lm:
            for key, value in order.items():
                if UNKNOWN_KEY in key:
                    order[key] -= 20
        return probs

    def load_from_file(self, file_name):
        f = open(file_name, "rb")
        self.lm = pickle.load(f)
        f.close()

    def dump_to_file(self, file_name):
        f = open(file_name, "wb")
        pickle.dump(self.lm, f)
        f.close()

    def highest_order_probs(self):
        return self.lm[0]

    def _calc_adj_counts(self, highest_order_counts):
        """
        Calculates the adjusted counts for all ngrams up to the highest order.

        Params:
            highest_order_counts [dict{tuple->string, int}] Counts of the highest
                order ngrams.

        Returns:
            kgrams_counts [list->dict] List of dict from kgram to counts
                where k is in descending order from highest_order to 0.
        """
        kgrams_counts = [highest_order_counts]
        for i in range(1, self.highest_order):
            last_order = kgrams_counts[-1]
            new_order = defaultdict(int)
            for ngram in last_order.keys():
                suffix = ngram[1:]
                new_order[suffix] += 1
            kgrams_counts.append(new_order)
        return kgrams_counts

    def _calc_probs(self, orders):
        """
        Calculates interpolated probabilities of kgrams for all orders.
        """
        backoffs = []
        for order in orders[:-1]:
            backoff = self._calc_order_backoff_probs(order)
            backoffs.append(backoff)
        orders[-1] = self._calc_unigram_probs(orders[-1])
        backoffs.append(defaultdict(int))
        self._interpolate(orders, backoffs)
        return orders

    def _calc_unigram_probs(self, unigrams):
        sum_vals = sum(v for v in unigrams.values())
        unigrams = dict((k, math.log(v/sum_vals)) for k, v in unigrams.items())
        return unigrams

    def _calc_order_backoff_probs(self, order):
        num_kgrams_with_count = Counter(
            value for value in order.values() if value <= 4)
        discounts = self._calc_discounts(num_kgrams_with_count)
        prefix_sums = defaultdict(int)
        backoffs = defaultdict(int)
        for key in order.keys():
            prefix = key[:-1]
            count = order[key]
            prefix_sums[prefix] += count
            discount = self._get_discount(discounts, count)
            order[key] -= discount
            backoffs[prefix] += discount
        for key in order.keys():
            prefix = key[:-1]
            if order[key] <= 1e-9:
                order[key] = 0
            else:
                order[key] = math.log(order[key]/prefix_sums[prefix])
        for prefix in backoffs.keys():
            backoffs[prefix] = math.log(backoffs[prefix]/prefix_sums[prefix])
        return backoffs

    def _get_discount(self, discounts, count):
        if count > 3:
            return discounts[3]
        return discounts[count]

    def _calc_discounts(self, num_with_count):
        """
        Calculate the optimal discount values for kgrams with counts 1, 2, & 3+.
        """
        common = num_with_count[1]/(num_with_count[1] + 2 * num_with_count[2])
        # Init discounts[0] to 0 so that discounts[i] is for counts of i
        discounts = [0]
        for i in range(1, 4):
            if num_with_count[i] == 0:
                discount = 0
            else:
                discount = (i - (i + 1) * common
                        * num_with_count[i + 1] / num_with_count[i])
            discounts.append(discount)
        if any(d for d in discounts[1:] if d <= 0):
            raise Exception(
                '***Warning*** Non-positive discounts detected. '
                'Your dataset is probably too small.')
        return discounts

    def _interpolate(self, orders, backoffs):
        """
        """
        for last_order, order, backoff in zip(
                reversed(orders), reversed(orders[:-1]), reversed(backoffs[:-1])):
            for kgram in order.keys():
                prefix, suffix = kgram[:-1], kgram[1:]
                order[kgram] += last_order[suffix] + backoff[prefix]

    def logprob(self, ngram):
        for i, order in enumerate(self.lm):
            if ngram[i:] in order:
                return order[ngram[i:]]
        return -30


t_gram = []


def t_count(item):
    item = filter_by_word_table(item)
    t_gram.append(item)


def process_file(file_name):
    file = open(file_name, "r", encoding="utf-8")

    last_word = last_last_word = START_SYMBOL
    line_num = 0
    for line in file.readlines():
        for word in line.split():
            if word in "，。【】{}《》、`‘ ’ ()（）；：''“”-『』？！":
                if last_word != START_SYMBOL:
                    t_count((last_last_word, last_word, END_SYMBOL))
                last_word = last_last_word = START_SYMBOL
                continue

            t_count((last_last_word, last_word, word))

            last_last_word = last_word
            last_word = word
        line_num += 1
        if line_num % 1000 == 0:
            print(file_name, " ", line_num)
    file.close()


if __name__ == "__main__":

    load_word_table(sys.argv[1])

    for i in range(len(sys.argv) - 2):
        process_file(sys.argv[i + 2])

    lm = KneserNeyLM(
        highest_order=3,
    )
    lm.train(t_gram)

    lm.dump_to_file("records/kneser_nay.model")
