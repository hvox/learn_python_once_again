#include <stdio.h>

int f(unsigned char *p1, unsigned char *p2) {
	printf("addr: %p\n", p2);
	printf("delta: %p\n", p2 - p1);
	unsigned char *p = p2;
	for (int i = 0; i < 5; i++)
		printf("array[%d] = %d\n", i, p[i]++);
}
