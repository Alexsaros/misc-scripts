#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>
#include <windows.h>

int main()
{
    srand(time(NULL));
    int alive = 1;
    int line, row, counter_line, counter_row;
    int snake = 505;
    int snakex, snakey;
    while (alive == 1) {
        for (line = 1; counter_line <= 10; counter_line++) {
            snakey = snake/100;
            snakex = snake-(snakey*100);
            for (row = 1; counter_row <= 10; counter_row++) {
                if (snakey == line && snakex == row) {
                    printf("O");
                }
                else {
                    printf("X");
                }
                counter_row = counter_row + 1;
            }
            printf("\n");
        }
        Sleep(500);
        printf("\n\n\n\n\n\n\n\n\n\n\n");
    }
    printf("You died.");
    return 0;
}
