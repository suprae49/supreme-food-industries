// Supreme Food Industry — bag weight calculator (C++)
#include <iostream>
#include <cstdlib>
#include <iomanip>

int main(int argc, char **argv) {
    if (argc < 2) {
        std::cerr << "usage: " << argv[0] << " <bags> [kg_per_bag=25]\n";
        return 1;
    }
    long bags = std::strtol(argv[1], nullptr, 10);
    double kg_each = (argc >= 3) ? std::strtod(argv[2], nullptr) : 25.0;
    if (bags < 0 || kg_each <= 0) {
        std::cerr << "invalid input\n";
        return 1;
    }
    double total = bags * kg_each;
    std::cout << std::fixed << std::setprecision(2)
              << "{\"ok\":true,\"lang\":\"cpp\",\"bags\":" << bags
              << ",\"kg_per_bag\":" << kg_each
              << ",\"total_kg\":" << total
              << ",\"total_quintal\":" << std::setprecision(3) << (total / 100.0)
              << "}\n";
    return 0;
}
