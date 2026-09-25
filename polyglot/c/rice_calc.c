/* Supreme Food Industry — bag weight calculator (C) */
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "usage: %s <bags> [kg_per_bag=25]\n", argv[0]);
        return 1;
    }
    long bags = strtol(argv[1], NULL, 10);
    double kg_each = (argc >= 3) ? strtod(argv[2], NULL) : 25.0;
    if (bags < 0 || kg_each <= 0) {
        fprintf(stderr, "invalid input\n");
        return 1;
    }
    printf("{\"ok\":true,\"lang\":\"c\",\"bags\":%ld,\"kg_per_bag\":%.2f,\"total_kg\":%.2f,\"total_quintal\":%.3f}\n",
           bags, kg_each, bags * kg_each, (bags * kg_each) / 100.0);
    return 0;
}
