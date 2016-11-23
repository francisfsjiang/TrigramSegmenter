#!/usr/bin/env python
#coding=utf-8
#############################################################
#function: max probility segment
#          a dynamic programming method
#
#input: dict file
#output: segmented words, divide by delimiter "\ "
#author: wangliang.f@gmail.com
##############################################################
import sys
import math
import pickle

from pprint import pprint

from word_table import UNKNOWN_KEY, START_SYMBOL, END_SYMBOL
#global parameter
DELIMITER = " - " #分词之后的分隔符


class DNASegment:
    def __init__(self):
        self.word1_dict = {}  #记录概率,1-gram
        self.word1_dict_count = {}  #记录词频,1-gram
        self.word1_dict_count["<S>"] = 8310575403 #开始的<S>的个数 

        self.word2_dict = {} #记录概率,2-gram
        self.word2_dict_count = {} #记录词频,2-gram


        self.gmax_word_length = 0
        self.all_freq = 0 #所有词的词频总和,1-gram的

    #估算未出现的词的概率,根据beautiful data里面的方法估算
    def get_unkonw_word_prob(self, word):
        return math.log(10./(self.all_freq*10**len(word))) - 20 * len(word)

    #获得片段的概率
    def get_word_prob(self, word):
        if word in self.word1_dict:  #如果字典包含这个词
            prob = self.word1_dict[word]
        else:
            prob = self.get_unkonw_word_prob(word)
        return prob

    
    #获得两个词的转移概率
    """
    def get_word_trans_prob(self, first_word, second_word):
        trans_word =  first_word + " " + second_word
        if self.word2_dict.has_key(trans_word):
            trans_prob = self.word2_dict[trans_word]
        else:
            trans_prob = self.get_word_prob(second_word)

        return trans_prob
    """
    def get_word_trans_prob(self, first_word, second_word):
        trans_word = first_word + " " + second_word
        #print trans_word
        if trans_word in self.word2_dict_count:
            trans_prob = \
    math.log(self.word2_dict_count[trans_word]/self.word1_dict_count[first_word])
        else:
            trans_prob = self.get_word_prob(second_word)

        print("%s %s %f " % (first_word, second_word, trans_prob))
        return trans_prob


    #寻找node的最佳前驱节点
    #方法为寻找所有可能的前驱片段
    def get_best_pre_node(self, sequence, node, node_state_list):
        #如果node比最大词长小，取的片段长度以node的长度为限
        max_seg_length = min([node, self.gmax_word_length])
        pre_node_list = [] #前驱节点列表

        max_prob = -float('inf')
        max_pre_node = 0
        max_segment = 0
        
        #获得所有的前驱片段，并记录累加概率
        for segment_length in range(1, max_seg_length+1):
            for pre_segment_length in range(1, max_seg_length + 1 - segment_length):
                segment_start_node = node-segment_length
                segment = sequence[segment_start_node:node] #获取片段

                pre_segment_start_node = node - segment_length - pre_segment_length
                pre_segment = sequence[pre_segment_start_node:pre_segment_length]

                pre_node = pre_segment_start_node  #取该片段，则记录对应的前驱节点
                print(pre_segment, " ", segment)

                if pre_node == 0:
                    #如果前驱片段开始节点是序列的开始节点，
                    #则概率为<S>转移到当前词的概率
                    #segment_prob = self.get_word_prob(segment)
                    segment_prob = \
                            self.get_word_trans_prob(START_SYMBOL, segment)
                else: #如果不是序列开始节点，按照二元概率计算
                    #获得前驱片段的前一个词
                    pre_pre_node = node_state_list[pre_node]["pre_node"]
                    pre_pre_word = sequence[pre_pre_node:pre_node]
                    segment_prob = \
                            self.get_word_trans_prob(pre_pre_word, segment)

                pre_node_prob_sum = node_state_list[pre_node]["prob_sum"]  #前驱节点的概率的累加值

                #当前node一个候选的累加概率值
                candidate_prob_sum = pre_node_prob_sum + segment_prob

                if candidate_prob_sum > max_prob:
                    max_prob = candidate_prob_sum
                    max_pre_node = pre_node
                    max_segment = segment

        print("Max: %d" % node)
        print("%f %d %s" % (max_prob, max_pre_node, max_segment))

        return (max_pre_node, max_prob)

    #最大概率分词
    def mp_seg(self, sequence):
        sequence = sequence.strip()
        sequence = START_SYMBOL + sequence

        #初始化
        node_state_list = [] #记录节点的最佳前驱，index就是位置信息
        #初始节点，也就是0节点信息
        ini_state = {}
        ini_state["pre_node"] = 0 #前一个节点
        ini_state["prob_sum"] = 0 #当前的概率总和
        node_state_list.append(ini_state)
        node_state_list.append(ini_state)
        #字符串概率为2元概率
        #P(a b c) = P(a|<S>)P(b|a)P(c|b)

        #逐个节点寻找最佳前驱节点
        for node in range(2, len(sequence) + 1):
            pprint("Node: %d" % node)
            #寻找最佳前驱，并记录当前最大的概率累加值
            (best_pre_node, best_prob_sum) = \
                    self.get_best_pre_node(sequence, node, node_state_list)
            
            #添加到队列
            cur_node = {}
            cur_node["pre_node"] = best_pre_node
            cur_node["prob_sum"] = best_prob_sum
            node_state_list.append(cur_node)
            #print "cur node list",node_state_list

            print("\n")

        pprint(node_state_list)

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
            word = sequence[left:right]
            word_list.append(word)

        seg_sequence = DELIMITER.join(word_list)
        return seg_sequence

    #加载词典，为词\t词频的格式
    def train(self, gram1_file, gram2_file):
        #读取1_gram文件
        dict_file = open(gram1_file, "r", encoding="utf-8")
        for line in dict_file:
            sequence = line.strip()
            key, value = sequence.split()
            value = float(value)
            self.word1_dict_count[key] = value
        #计算频率
        self.all_freq = sum(self.word1_dict_count.values()) #所有词的词频
        self.gmax_word_length = max(len(key) for key in self.word1_dict_count.keys())
        # self.gmax_word_length = 20
        # self.all_freq = 1024908267229.0
        #计算1gram词的概率
        for key in self.word1_dict_count:
            self.word1_dict[key] = math.log(self.word1_dict_count[key]/self.all_freq)
        
        #读取2_gram_file，同时计算转移概率
        dict_file = open(gram2_file, "r", encoding="utf-8")
        for line in dict_file:
            sequence = line.strip()
            first_word, second_word, value = sequence.split()
            value = float(value)
            key = "%s %s" % (first_word, second_word)
            self.word2_dict_count[key] = float(value)
            if first_word in self.word1_dict_count:
                self.word2_dict[key] = \
                    math.log(value/self.word1_dict_count[first_word])  #取自然对数
            else:
                self.word2_dict[key] = self.word1_dict[second_word]

    def dump_to_file(self, file_name):
        f = open(file_name, "wb")
        pickle.dump((
            self.word1_dict,
            self.word1_dict_count,
            self.word2_dict,
            self.word2_dict_count,
            self.all_freq,
            self.gmax_word_length
        ), f)
        f.close()

    def load_from_file(self, file_name):
        f = open(file_name, "rb")

        self.word1_dict, \
        self.word1_dict_count, \
        self.word2_dict, \
        self.word2_dict_count, \
        self.all_freq, \
        self.gmax_word_length = pickle.load(f)
        f.close()


#test
if __name__=='__main__':

    myseg = DNASegment()
    myseg.train(sys.argv[1], sys.argv[2])
    sequence = "人类社会前进的航船就要驶入21世纪的新航程"
    seg_sequence = myseg.mp_seg(sequence)
    print("original sequence: " + sequence)
    print("segment result: " + seg_sequence)

    sequence = "tositdown"
    seg_sequence = myseg.mp_seg(sequence)
    print("original sequence: " + sequence)
    print("segment result: " + seg_sequence)
