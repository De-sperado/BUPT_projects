#include <stdio.h>
#include <string.h>
int main()
{
	char buffer[8][128];
	char bu[128];
	printf("%lu\n%lu", sizeof buffer[2], sizeof bu);
	memcpy(bu, buffer[2], 128);
	memcpy(buffer[2], bu, 128);
	return 0;
}