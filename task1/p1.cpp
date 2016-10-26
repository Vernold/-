#include <stdio.h>
#include <time.h>

#define SIZE 10000

double a[SIZE][SIZE];
int i;
double b[SIZE][SIZE];
double c[SIZE][SIZE];


int main(int argc, char **argv)
{
    int j, k=1, t = clock();
    
    for( i = 0; i < SIZE; ++i){
        for( j = 0; j < SIZE; ++j){
            a[i][j] = b[i][j] + c[i][j];
        }
    }
    printf("%f\n", (float)(clock()-t)/ CLOCKS_PER_SEC);
    return 0;
}
