#include <iostream>

int main(int argc, const char* argv[]) {
    if (argc < 3) {
        std::cout << "Usage: ModelGeneator <train_file> <model_output_file>" << std::endl;
        return -1;
    }
    return 0;
}