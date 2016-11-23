#include <iostream>
#include <fstream>
#include <map>
#include <set>

#include "model.hpp"

std::set<std::string> Punctuation;

void init(const char* punctuation_file_name) {
    std::ifstream ifs = std::ifstream(punctuation_file_name);
    std::string temp;
    while (ifs >> temp){
        Punctuation.insert(temp);
    }
}

template <typename T>
void dict_count(const T& unit, std::map<T, int>& dict) {
    auto iter = dict.find(unit);
    if (iter == dict.end()) {
        dict.insert(
                std::make_pair(
                        unit, 1
                )
        );
    } else {
        *iter->second += 1;
    }
}


int main(int argc, const char* argv[]) {
    if (argc < 3) {
        std::cout << "Usage: ModelGeneator <punctuation_file> <train_file> <model_output_file>" << std::endl;
        return -1;
    }

    init(argv[1]);

    auto ifs = std::ifstream(argv[2]);
    std::string temp;

    std::string last_word;
    std::string last_last_word;
    while(ifs >> temp) {
        if (Punctuation.find(temp) != Punctuation.end()) {
            last_word = last_last_word = "🐸";
            std::cout << last_word;
            continue;
        }
        std::cout << temp;


        auto t_unit = std::make_tuple(last_last_word, last_word, temp);
        dict_count(t_unit, TrigramCounter);
        auto b_unit = std::make_tuple(last_word, temp);
        dict_count(b_unit, BigramCounter);
        auto u_unit = std::make_tuple(temp);
        dict_count(u_unit, UnigramCounter);


    }


    return 0;
}
