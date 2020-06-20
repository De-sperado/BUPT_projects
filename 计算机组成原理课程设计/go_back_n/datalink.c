#include <stdio.h>
#include <string.h>
#include <stdbool.h>

#include "protocol.h"
#include "datalink.h"

#define DATA_TIMER_MS 2000
#define ACK_TIMER_MS 1000
#define MAX_SEQ 0x06 /*win = MAX_SEQ*/

struct FRAME {
	unsigned char kind; /* FRAME_DATA */
	unsigned char ack;
	unsigned char seq;
	unsigned char data[PKT_LEN];
	unsigned int padding;
};

static unsigned char frame_nr = 0, buffer[PKT_LEN], nbuffered;
static unsigned char frame_expected = 0;
static unsigned char ack_expected = 0;
static int phl_ready = 0;

static void put_frame(unsigned char *frame, int len)
{
	*(unsigned int *)(frame + len) = crc32(frame, len);
	send_frame(frame, len + 4);
	phl_ready = 0;
}
static void send_kind_frame(unsigned char kind)
{
	struct FRAME s;
	s.kind = kind;
	s.ack = (frame_expected + MAX_SEQ) % (MAX_SEQ + 1);
	switch (kind) {
	case FRAME_DATA:
		s.seq = frame_nr;
		memcpy(s.data, buffer, PKT_LEN);

		dbg_frame("Send DATA %d %d, ID %d\n", s.seq, s.ack,
			  *(short *)s.data);

		put_frame((unsigned char *)&s, 3 + PKT_LEN);
		start_timer(frame_nr, DATA_TIMER_MS);
		stop_ack_timer(); /*do not need an ack frame*/
		break;
	case FRAME_ACK:

		dbg_frame("Send ACK    %d\n", s.ack);

		put_frame((unsigned char *)&s, 2);
		break;
	case FRAME_NAK:
		dbg_frame("Send NCK    %d\n", s.ack);

		put_frame((unsigned char *)&s, 2);
		break;
	default:
		break;
	}
}
static bool between(unsigned char a, unsigned char b, unsigned char c)
{
	if ((a <= b && b < c) || (c < a && a <= b) || (b < c && c < a))
		return true;
	else
		return false;
}

int main(int argc, char **argv)
{
	int event, arg;
	struct FRAME f;
	int len = 0;

	unsigned char out_buffer[MAX_SEQ + 1][PKT_LEN];

	protocol_init(argc, argv);
	lprintf("Designed by Jiang Yanjun, build: " __DATE__ "  " __TIME__
		"\n");

	disable_network_layer();

	for (;;) {
		event = wait_for_event(&arg);

		switch (event) {
		case NETWORK_LAYER_READY: /*fetch and send*/
			get_packet(buffer);
			nbuffered++;
			send_kind_frame(FRAME_DATA);
			memcpy(out_buffer[frame_nr], buffer, PKT_LEN);
			frame_nr = (frame_nr + 1) % (MAX_SEQ + 1);
			break;

		case PHYSICAL_LAYER_READY:
			phl_ready = 1;
			break;

		case FRAME_RECEIVED:
			len = recv_frame((unsigned char *)&f, sizeof f);
			if (len < 5 || crc32((unsigned char *)&f, len) != 0) {
				dbg_event(
					"**** Receiver Error, Bad CRC Checksum\n");
				send_kind_frame(FRAME_NAK);
				break;
			}
			dbg_event("ack_expected=%d, f.ack=%d, frame_nr=%d\n",
				  ack_expected, f.ack, frame_nr);
			while (between(ack_expected, f.ack, frame_nr)) { /*ack*/
				stop_timer(ack_expected);
				nbuffered--;
				ack_expected =
					(ack_expected + 1) % (MAX_SEQ + 1);
			}
			if (f.kind == FRAME_ACK)
				dbg_frame("Recv ACK    %d\n", f.ack);
			if (f.kind == FRAME_DATA) {
				dbg_frame("Recv DATA %d %d, ID %d\n", f.seq,
					  f.ack, *(short *)f.data);
				if (f.seq == frame_expected) {
					put_packet(f.data, len - 7); /*upper*/
					frame_expected = (frame_expected + 1) %
							 (MAX_SEQ + 1);
					start_ack_timer(ACK_TIMER_MS);
				}
			}
			if (f.kind == FRAME_NAK) {
				dbg_frame("Recv NCK    %d\n", f.ack);
				frame_nr = ack_expected;
				for (int i = 0; i < nbuffered; i++) {
					memcpy(buffer, out_buffer[frame_nr],
					       PKT_LEN);
					send_kind_frame(FRAME_DATA);
					frame_nr =
						(frame_nr + 1) % (MAX_SEQ + 1);
				}
			}
			break;

		case DATA_TIMEOUT:
			dbg_event("---- DATA %d timeout\n", arg);
			frame_nr = ack_expected;
			for (int i = 0; i < nbuffered; i++) {
				memcpy(buffer, out_buffer[frame_nr], PKT_LEN);
				send_kind_frame(FRAME_DATA);
				frame_nr = (frame_nr + 1) % (MAX_SEQ + 1);
			}
			break;

		case ACK_TIMEOUT:
			send_kind_frame(FRAME_ACK);
		}
		dbg_event("nbuffered=%d", nbuffered);
		if (nbuffered < MAX_SEQ && phl_ready) {
			enable_network_layer();
			dbg_event("next\n");
		} else {
			disable_network_layer();
			dbg_event("wait window\n");
		}
	}
}