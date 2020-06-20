#include <stdio.h>
#include <string.h>
#include "protocol.h"
#include "datalink.h"

typedef enum { false, true }bool;
typedef unsigned char seq_nr;
typedef struct {
	unsigned char info[PKT_LEN];
}packet;

static int phl_ready = 0;
bool no_nak = true;

typedef struct FRAME
{
	unsigned char kind;   
	seq_nr ack;           
	seq_nr  seq;          
	packet data;          
	unsigned int  padding;
}Frame;

static bool between(seq_nr a, seq_nr b, seq_nr c)
{
	if ((a <= b && b < c) || (c < a && a <= b) || (b < c && c < a)) return true;
	else return false;
}

static void put_frame(unsigned char *frame, int len)
{
	*(unsigned int *)(frame + len) = crc32(frame, len);/* generate the check sum for the data in buffer */
	send_frame(frame, len + 4); /* send the data after generating the check sum */
	phl_ready = 0;       /* let the physical layer stay in unready */
}

static void send_data(unsigned char fk, seq_nr frame_nr, seq_nr frame_expected, packet buffer[])
{
	Frame s;   
	s.kind = fk; 
	s.seq = frame_nr; 
	s.ack = (frame_expected + MAX_SEQ) % (MAX_SEQ + 1);

	if (fk == FRAME_DATA)
	{
		memcpy(s.data.info, buffer[frame_nr%NR_BUFS].info, PKT_LEN);
		dbg_frame("Send DATA %d %d,ID %d\n", s.seq, s.ack, *(short*)&(s.data).info);

		put_frame((unsigned char *)&s, 3 + PKT_LEN); 
		start_timer(frame_nr%NR_BUFS, DATA_TIMER); 
	}

	if (fk == FRAME_NAK)
	{
		dbg_frame("Send NAK %d\n", s.ack);
		no_nak = false;   
		put_frame((unsigned char *)&s, 2);
	}

	if (fk == FRAME_ACK)
	{
		dbg_frame("Send ACK %d\n", s.ack);
		put_frame((unsigned char *)&s, 2);
	}
	stop_ack_timer(); 
}

int main(int argc, char **argv)
{
	seq_nr next_frame_to_send;  /* upper edge of sender's window+1 */
	seq_nr ack_expected;        /* lower edge of sender's window */
	seq_nr frame_expected;      /* lower edge of receiver's window */
	seq_nr too_far;             /* upper edge of receiver's window+1 */
	int arg, length = 0;
	int i;                      /* index into buffer pool */

	Frame r;                    /* scratch variable */
	seq_nr nbuffered;           /* the number of output buffers currently used */
	packet out_buf[NR_BUFS];    /* buffers for outbound stream */
	packet in_buf[NR_BUFS];     /* buffers for inbound stream */
	bool arrived[NR_BUFS];      /* inbound bit map */
	int event;

	enable_network_layer();     /* initialize */

	ack_expected = 0;           /* next ack expected on the inbound stream */
	next_frame_to_send = 0;     /* number of next putgoing frame */
	frame_expected = 0;         /* the number expected to receive */
	too_far = NR_BUFS;
	nbuffered = 0;              /* initially no packets are buffered */

	for (i = 0; i < NR_BUFS; i++)
	{
		arrived[i] = false; /* the i of receiver's window can receive data */
	}

	protocol_init(argc, argv);  /* the initializatio of the protocol's environment */
	lprintf("Designed by 6v, build: " __DATE__"  "__TIME__"\n");

	for (; ; )
	{
		event = wait_for_event(&arg);/* five possibilities */

		switch (event)
		{
		case NETWORK_LAYER_READY:
			nbuffered++;     /* expand the window */
			get_packet(out_buf[next_frame_to_send%NR_BUFS].info);            /* fetch the new packet */
			send_data(FRAME_DATA, next_frame_to_send, frame_expected, out_buf); /* transmit the packet */
			inc(next_frame_to_send);  /* advance upper window edge */
			break;

		case PHYSICAL_LAYER_READY:
			phl_ready = 1;
			break;

		case FRAME_RECEIVED:
			length = recv_frame((unsigned char *)&r, sizeof r);

			if (length < 5 || crc32((unsigned char *)&r, length) != 0)
			{
				dbg_event("**** Receiver Error, Bad CRC ******\n");
				if (no_nak)
				{
					send_data(FRAME_NAK, 0, frame_expected, out_buf);/* send a nak */
				}
				break;
			}

			if (r.kind == FRAME_DATA)
			{
				if ((r.seq != frame_expected) && no_nak)
					send_data(FRAME_NAK, 0, frame_expected, out_buf);
				else
					start_ack_timer(ACK_TIMER);
				if (between(frame_expected, r.seq, too_far) && (arrived[r.seq%NR_BUFS] == false))
				{
					dbg_frame("Recv DATA %d %d,ID %d\n",r.seq,r.ack,*(short*)&(r.data).info);
					arrived[r.seq%NR_BUFS] = true; /* set the buffer '1' */
					in_buf[r.seq%NR_BUFS] = r.data;/* storage the data into the in_buff */
					while (arrived[frame_expected%NR_BUFS])
					{
						put_packet(in_buf[frame_expected%NR_BUFS].info, length - 7);
						no_nak = true;
						arrived[frame_expected%NR_BUFS] = false;/* set the i of receiver's window can receive frame */
						inc(frame_expected);
						inc(too_far);
						start_ack_timer(ACK_TIMER);   /* set the timer of ack */
					}
				}
			}
			if ((r.kind == FRAME_NAK) && between(ack_expected, (r.ack + 1) % (MAX_SEQ + 1), next_frame_to_send))
				send_data(FRAME_DATA, (r.ack + 1) % (MAX_SEQ + 1), frame_expected, out_buf);
			
			while (between(ack_expected, r.ack, next_frame_to_send))
			{
				nbuffered--; /* handle piggybacked ack */
				stop_timer(ack_expected%NR_BUFS);/* frame arrived intact */
				inc(ack_expected); /* advance lower edge of sender's window */
			}
			break;

		case ACK_TIMEOUT:
			dbg_event("******** ACK %d timeout *********\n", arg);
			send_data(FRAME_ACK, 0, frame_expected, out_buf);
			break;

		case DATA_TIMEOUT:
			dbg_event("******** DATA %d timeout **********\n", arg);
			if (!between(ack_expected, arg, next_frame_to_send))
				arg = arg + NR_BUFS;
			send_data(FRAME_DATA, arg, frame_expected, out_buf);
			break;
		}
		if (nbuffered < NR_BUFS&& phl_ready)
			enable_network_layer();
		else
			disable_network_layer();
	}
}

