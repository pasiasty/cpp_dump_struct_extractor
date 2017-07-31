#include <stdint.h>
#include <stdio.h>

struct A
{
    unsigned int        a;
    unsigned int        b;
    unsigned long       c;
    unsigned long long  d;
};

struct B
{
    A              A_arr[10];
    unsigned char  byte_arr[5][4][3][2];
    unsigned short var;
};

int main()
{
    B a;

    for(int idx=0; idx < 10; idx++)
    {
         a.A_arr[idx].a = 10 * idx;
         a.A_arr[idx].b = 10 * idx + 1;
         a.A_arr[idx].c = 10 * idx + 2;
         a.A_arr[idx].d = 10 * idx + 3;
    }

    for(int a_idx=0; a_idx < (5*4*3*2); a_idx++)
    {
        ((unsigned char*)a.byte_arr)[a_idx] = (unsigned char)a_idx;
    }

    a.var = 123;

    FILE* file = fopen("out.bin", "wb");
    fwrite(&a, sizeof(B), 1, file);
    fclose(file);
}
