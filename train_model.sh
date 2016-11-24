#!/bin/sh

python3 bigram_counter.py data/msr_training.utf8 data/pku_training.utf8

python3 segmentor.py records/bigram_counter.record data/pangu_word_table.utf8 records/model.model
