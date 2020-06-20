#ifndef __PROTOCOL_fr12hn_H__ //避免重复包含头文件
//"https://www.cnblogs.com/skynet/archive/2010/07/10/1774964.html"
#ifdef  __cplusplus
extern "C" {		//extern "C" fun();指定fun()应该根据C的编译和连接规约来链接,用来实现C++和C的互相调用
#endif

#define VERSION "4.0"

#ifndef	_CRT_SECURE_NO_WARNINGS
#define _CRT_SECURE_NO_WARNINGS
#endif

#include <stdio.h>
#include <string.h>

#include "lprintf.h"

/* Initalization */ 
extern void protocol_init(int argc, char **argv);

/* Event Driver */
extern int wait_for_event(int *arg);

#define NETWORK_LAYER_READY  0
#define PHYSICAL_LAYER_READY 1
#define FRAME_RECEIVED       2
#define DATA_TIMEOUT         3
#define ACK_TIMEOUT          4

/* Network Layer functions */
#define PKT_LEN 256

extern void enable_network_layer(void);
extern void disable_network_layer(void);
extern int  get_packet(unsigned char *packet);
extern void put_packet(unsigned char *packet, int len);

/* Physical Layer functions */
extern int  recv_frame(unsigned char *buf, int size);
extern void send_frame(unsigned char *frame, int len);

extern int  phl_sq_len(void);

/* CRC-32 polynomium coding function */
extern unsigned int crc32(unsigned char *buf, int len);

/* Timer Management functions */
extern unsigned int get_ms(void);
extern void start_timer(unsigned int nr, unsigned int ms);
extern void stop_timer(unsigned int nr);
extern void start_ack_timer(unsigned int ms);
extern void stop_ack_timer(void);

/* Protocol Debugger */
extern char *station_name(void);

extern void dbg_event(char *fmt, ...);
extern void dbg_frame(char *fmt, ...);
extern void dbg_warning(char *fmt, ...);

#define MARK lprintf("File \"%s\" (%d)\n", __FILE__, __LINE__)

#ifdef  __cplusplus ////extern "C" fun();指定fun()应该根据C的编译和连接规约来链接,用来实现C++和C的互相调用
}
#endif

#endif
