#include "model.hpp"

auto TrigramCounter =
        std::map<std::tuple<std::string, std::string, std::string>, int>();
auto BigramCounter =
        std::map<std::tuple<std::string, std::string>, int>();
auto UnigramCounter =
        std::map<std::tuple<std::string>, int>();
