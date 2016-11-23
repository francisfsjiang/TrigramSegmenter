#ifndef TRIGRAMSEGMENTER_MODEL_HPP
#define TRIGRAMSEGMENTER_MODEL_HPP

#include <map>


extern std::map<std::tuple<std::string, std::string, std::string>, int> TrigramCounter;
extern std::map<std::tuple<std::string, std::string>, int> BigramCounter;
extern std::map<std::tuple<std::string>, int> UnigramCounter;


#endif //TRIGRAMSEGMENTER_MODEL_HPP
