CC=gcc
CFLAGS=-O2
all:
	gcc datalink.c protocol.c lprintf.c crc32.c -c

datalink: datalink.h datalink.o protocol.o lprintf.o crc32.o 
	gcc datalink.o protocol.o lprintf.o crc32.o -o datalink -lm

clean:
	${RM} *.o datalink *.log

