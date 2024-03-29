

#ifndef _NF_MOBILITY_H_
#define _NF_MOBILITY_H_

#include <linux/types.h>
#include <linux/time.h> /* For delivery timer in bicast */

/* Default parameters */
#define NF_MOBILITY_MODE_BICAST 0x01
#define NF_MOBILITY_MODE_HOOLOCK 0x02 /* Future development */

#define NF_MOBILITY_DEFAULT_NUM_BUFFER_PACKETS 5
#define NF_MOBILITY_DEFAULT_NUM_BUFFER_BYTES 300

/* Hole-matching results */
#define NF_MOBILITY_MATCH_FIRST_HOLE 0x10
#define NF_MOBILITY_MATCH_OTHER_HOLE 0x20
#define NF_MOBILITY_MATCH_NO_HOLE    0x40

/* DEBUGGING */
#define NFM_DEBUG 0
#define NFM_DEBUG_DUPE 1
#define NFM_DEBUG_HOLE 1

// Forward declarations
struct nf_mobility_buffer;
struct nf_mobility_hole;

// Delivery timer
struct timer_list nfm_delivery_timer; 

// Info struct
struct nf_mobility{
	int mode;
	int status; // On, off, etc.
	rwlock_t flow_lock;	
};

struct nf_mobility_flow{
	struct nf_mobility_flow *prev;
	struct nf_mobility_flow *next;

	__u8 protocol; /* L4 protocol */
	__be32 saddr;
	__be32 daddr;
	__be16 sport;
	__be16 dport;
	__u32 dupe_check_start_seq; /* Starting sequence number to check for dupes */
	__u32 head_of_line; /* Latest sequence number received */

	int is_buffering;
	int buffered_packets;
	int buffered_bytes;
	struct nf_mobility_buffer *buffer_head;
	struct nf_mobility_buffer *buffer_tail;

	 /* Ordered doubly linked list */
	struct nf_mobility_hole *holes_head;
	struct nf_mobility_hole *holes_tail;
};

struct nf_mobility_buffer{
	struct nf_mobility_buffer *prev;
	struct nf_mobility_buffer *next;
	struct sk_buff* skb;
	__u32 start_seq;
	__u32 end_seq;
};

struct nf_mobility_hole{
	struct nf_mobility_hole *prev;
	struct nf_mobility_hole *next;
	__u32 start_seq;
	__u32 end_seq;
};

static void nf_mobility_remove_holes(struct nf_mobility_flow *flow);
static void nf_mobility_timer_delivery(unsigned long x);

#endif

