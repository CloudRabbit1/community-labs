/* SUID root file reader — demonstrates SUID privilege escalation */
#include <stdio.h>
int main(int argc, char *argv[]) {
    if (argc < 2) { fprintf(stderr, "usage: readfile <path>\n"); return 1; }
    FILE *f = fopen(argv[1], "r");
    if (!f) { perror(argv[1]); return 1; }
    int c;
    while ((c = fgetc(f)) != EOF) putchar(c);
    fclose(f);
    return 0;
}
