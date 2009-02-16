#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/netfilter_ipv4.h>
#include <linux/netfilter.h>

/**
 * Backward compatibility for kernels before 2.6.25-rc1
 * Remove when compiling with later kernels
 */
#define NF_INET_LOCAL_IN NF_IP_LOCAL_IN

#include <net/ip.h>
#include <linux/ip.h>
#include <linux/tcp.h>

#include "nf_mobility.h"

#define NF_MOBILITY_AUTHOR "Michael Chan <mcfchan@stanford.edu>"
#define NF_MOBILITY_DESC   "Netfilter module for bicast"

/**
 * Module parameters
 */
static unsigned int nfm_num_buffer_packets = 0; /* Maximum buffered packets */
static unsigned int nfm_num_buffer_bytes = 3000;  /* Maximum buffered bytes */
static int nfm_is_buffer_packets = 0; /* By default, buffer */
static int nfm_is_buffer_bytes = 1; 

// Debugging
static unsigned int nfm_pc = 0;
static unsigned int nfm_dupe_count = 0;

/**
 * Variables used only in this module
 *
 * Initialization in module init function
 */
static struct nf_mobility *nfm;
static struct nf_mobility_flow *nfm_flows;

static void nf_mobility_print_ip(__be32 ip)
{
	printk(KERN_ALERT "%u.%u.%u.%u", ip>>24, (ip>>16)&255, (ip>>8)&255, ip&255);
}

static void nf_mobility_print_incoming_TCP(__be32 saddr, __be32 daddr, __be16 sport, __be16 dport)
{
	nf_mobility_print_ip(saddr);
	printk(KERN_ALERT " %u ... ", sport);
	nf_mobility_print_ip(daddr);
	printk(KERN_ALERT " %u\n", dport);
	printk(KERN_ALERT "%u    %u\n", saddr, daddr);
}

/* -------- Flow manipulation -------- */
static struct nf_mobility_flow * nf_mobility_get_flow(__u8 protocol, __be32 saddr, __be32 daddr, __be16 sport, __be16 dport)
{
	struct nf_mobility_flow *flow;
	
	for(flow = nfm_flows; flow != NULL; flow = flow->next){
		if(flow->protocol == protocol &&
		   flow->saddr == saddr && flow->daddr == daddr && 
		   flow->sport == sport && flow->dport == dport)
			return flow;
	}
	return NULL;
}

static struct nf_mobility_flow * nf_mobility_create_flow(__u8 protocol, __be32 saddr, __be32 daddr, __be16 sport, __be16 dport, __u32 start_seq)
{
	struct nf_mobility_flow *flow;

	flow = (struct nf_mobility_flow *) kmalloc(sizeof(struct nf_mobility_flow), GFP_ATOMIC);

	
	if(flow == NULL){
		printk(KERN_ALERT "CRITICAL: Cannot allocate flow in nf_mobility module!");
		return NULL;
	}
	/* Initialize flow control information */
	flow->protocol = protocol;
	flow->saddr = saddr;
	flow->daddr = daddr;
	flow->sport = sport;
	flow->dport = dport;
	flow->dupe_check_start_seq = start_seq;
	flow->head_of_line = start_seq;

	flow->is_buffering = 0;
	flow->buffered_packets = 0;
	flow->buffered_bytes = 0;
	flow->buffer_head = NULL;
	flow->buffer_tail = NULL;

	flow->holes_head = NULL;
	flow->holes_tail = NULL;

	/* Link up with nfm_flows (put in beginning) */
	flow->prev = NULL;
	flow->next = nfm_flows;
	if(nfm_flows != NULL)
		nfm_flows->prev = flow;
	nfm_flows = flow;

	return flow;
}

/**
 * Enqueues a packet to the buffer list
 * Order in increasing sequence number
 *
 * Assumption:
 * No overlapping packets - this could happen if there are timeouts
 * Delivering partially overlapped packets would not do good to 
 * some layer 4 protocols like TCP since it may trigger duplicate ACKs
 * and hence unnecessary congestion control. However, for simplicity, 
 * we do not include this checking in this version. This functionality 
 * may be added in a future version should the need arise.
 */
static struct nf_mobility_buffer * nf_mobility_enqueue_packet(struct nf_mobility_flow *flow, __u32 start_seq, __u32 end_seq, struct sk_buff * skb)
{
	struct nf_mobility_buffer *new_buffer, *buffer;

	new_buffer = (struct nf_mobility_buffer *) kmalloc(sizeof(struct nf_mobility_buffer), GFP_ATOMIC);
	if(new_buffer == NULL){
		printk(KERN_ALERT "CRITICAL: Cannot allocate buffer in nf_mobility module!");
		return NULL;
	}

	(flow->buffered_packets)++;
	flow->buffered_bytes += end_seq - start_seq + 1;

if(NFM_DEBUG_HOLE)
printk(KERN_ALERT "Buffered packets = %d, bytes = %d, newest = (%d, %d)\n", flow->buffered_packets, flow->buffered_bytes, start_seq, end_seq);

	new_buffer->skb = skb;
	new_buffer->start_seq = start_seq;
	new_buffer->end_seq = end_seq;

	/* Insert new buffer into ordered linked list (by start_seq) */
	if(flow->buffer_head == NULL){ /* && flow->buffer_tail == NULL */
		flow->buffer_head = flow->buffer_tail = new_buffer;
		new_buffer->prev = new_buffer->next = NULL;
	}
	else{ /* Both buffer_head and buffer_tail of flow not NULL */
		// Reverse traversal seems more efficient since packets are coming 
		// in a generally increasing order in sequence number
		for(buffer = flow->buffer_tail; buffer != NULL; buffer = buffer->prev){
			if(buffer->start_seq < new_buffer->start_seq)
				break;
		}

		if(buffer == flow->buffer_tail){ // This looks like the most likely case
			new_buffer->next = NULL;
			new_buffer->prev = buffer;
			buffer->next = new_buffer;
			flow->buffer_tail = new_buffer;
		}
		else if(buffer != NULL){ // Insert in middle of list
			new_buffer->prev = buffer;
			new_buffer->next = buffer->next;
			buffer->next->prev = new_buffer;
			buffer->next = new_buffer;	
		}
		else{ //if(buffer == NULL){ /* Insert at head */
			new_buffer->prev = NULL;
			new_buffer->next = flow->buffer_head;
			flow->buffer_head->prev = new_buffer;
			flow->buffer_head = new_buffer;
		}
	}

	return new_buffer;
}

/* -------- Hole manipulation -------- */
/**
 * Create a hole with specified starting and ending sequence numbers
 */
static struct nf_mobility_hole * nf_mobility_create_hole(__u32 hole_start_seq, __u32 hole_end_seq)
{
	struct nf_mobility_hole *new_hole;

	/* Create hole */	
	new_hole = (struct nf_mobility_hole *) kmalloc(sizeof(struct nf_mobility_hole), GFP_ATOMIC);
	if(new_hole == NULL){
		printk(KERN_ALERT "CRITICAL: Cannot allocate hole in nf_mobility module!");
		return NULL;
	}
	
	new_hole->start_seq = hole_start_seq;
	new_hole->end_seq = hole_end_seq;
	return new_hole;
}

/**
 * Creates and appends hole to given flow with specified starting and ending sequence numbers
 */
static struct nf_mobility_hole * nf_mobility_create_and_append_hole(struct nf_mobility_flow *flow, __u32 hole_start_seq, __u32 hole_end_seq)
{
	struct nf_mobility_hole *new_hole;
	new_hole = nf_mobility_create_hole(hole_start_seq, hole_end_seq);

	if(new_hole == NULL)
		return NULL;

	/* Append hole to end of list */
	new_hole->next = NULL;
	new_hole->prev = flow->holes_tail;
	if(flow->holes_tail != NULL) /* && flow->holes_head != NULL */
		flow->holes_tail->next = new_hole;
	else /* Only hole in list */
		flow->holes_head = new_hole;
	flow->holes_tail = new_hole;

	return new_hole;
}

/**
 * Remove a hole from flow
 *
 * Hole pointer must be pointing to some hole in given flow
 */
static void nf_mobility_remove_hole(struct nf_mobility_flow *flow, struct nf_mobility_hole *hole)
{
	if(flow->holes_head == NULL){
		printk(KERN_ALERT "WARNING: Trying to remove hole from empty list.\n");
		return;
	}
	
	// Different positions of hole to be removed
	if(flow->holes_head == hole && flow->holes_tail == hole){
		// Only hole in the list
		flow->holes_head = flow->holes_tail = NULL;
	}
	else if(flow->holes_head == hole){
		// At list head
		hole->next->prev = NULL;
		flow->holes_head = hole->next;
	}
	else if(flow->holes_tail == hole){
		// At list tail
		hole->prev->next = NULL;
		flow->holes_tail = hole->prev;
	}
	else{
		// In the middle
		hole->prev->next = hole->next;
		hole->next->prev = hole->prev;
	}
	kfree(hole);
}

/**
 * Given the start and end sequences of a packet and corresponding flow, 
 * try to match holes. A match means any overlap between the packet 
 * sequence number range and the hole's sequence number range. In case 
 * of a match, the hole may be subject to one of these three actions:
 *
 * 1. Removed (complete overlap or packet's range contains hole's range)
 * 2. Shrunk from either side (partial overlap from the sides)
 * 3. Split into two (hole's range contains packet's range)
 */
static int nf_mobility_match_and_fill_holes(struct nf_mobility_flow *flow, __u32 start_seq, __u32 end_seq)
{
	struct nf_mobility_hole *hole, *next_hole, *new_hole, *holes_head;
	int matched_first;

	holes_head = flow->holes_head;

if(NFM_DEBUG_HOLE)
printk(KERN_ALERT "Start hole match for packet (%d, %d).\n", start_seq, end_seq);
	/* No hole to match against */
	if(holes_head == NULL){
if(NFM_DEBUG_HOLE)
printk(KERN_ALERT "No hole, returning.\n");
		return NF_MOBILITY_MATCH_NO_HOLE;
	}

	/* Packet's range is outside (before or after) all possible hole ranges */
	if(holes_head->start_seq > end_seq || flow->holes_tail->end_seq < start_seq){
if(NFM_DEBUG_HOLE)
printk(KERN_ALERT "Packet out of range, returning.\n");
		return NF_MOBILITY_MATCH_NO_HOLE;
}

	/* Preprocess the match_first indicator 
	 * i.e., check if the first hole in the list will match the packet */
	if(holes_head->start_seq >= start_seq)
		matched_first = 1;
	else matched_first = 0;

	/* Find the first hole that may match packet (skip all the holes 
	 * that are entirely to the left of the packet's starting sequence number */
	for(hole = holes_head; hole != NULL; hole = hole->next){
		if(hole->end_seq >= start_seq)
			break;
	}

	/* No match if packet is between two holes */
	if(hole->start_seq > end_seq)
		return NF_MOBILITY_MATCH_NO_HOLE;

	/* Check if the hole contains packet but not with completely same range */
	if(hole->start_seq < start_seq && hole->end_seq > end_seq){
if(NFM_DEBUG_HOLE)
printk(KERN_ALERT "Spliting hole, (%d, %d) -> (%d, %d) + (%d, %d) ,then returning.\n", hole->start_seq, hole->end_seq, hole->start_seq, start_seq - 1, end_seq + 1, hole->end_seq);
		/* Split hole into two by
		 * 1. Shrinking left portion
		 * 2. Create new hole for right portion */
		hole->end_seq = start_seq - 1;
		new_hole = nf_mobility_create_hole(end_seq + 1, hole->end_seq);
		
		/* Link-up stuff */
		new_hole->prev = hole;
		new_hole->next = hole->next;
		if(hole != flow->holes_tail)
			hole->next->prev = new_hole;
		else flow->holes_tail = new_hole;
		hole->next = new_hole;
		
		/* This is the only hole that'll match the packet */
		return NF_MOBILITY_MATCH_OTHER_HOLE;
	}

if(NFM_DEBUG_HOLE)
printk(KERN_ALERT "Checking for packet-from-right overlap.\n");
	/* Possible partial overlap from the right (beginning of packet overlaps 
	 * ending of hole) */
	if(hole->start_seq < start_seq){
if(NFM_DEBUG_HOLE)
printk(KERN_ALERT "Shrink hole (%d, %d) -> (%d, %d)\n", hole->start_seq, hole->end_seq, hole->start_seq, start_seq-1);
		/* Shrink hole */
		hole->end_seq = start_seq - 1;
		hole = hole->next; /* This hole already processed */	
	}

if(NFM_DEBUG_HOLE){
if(hole != NULL) printk(KERN_ALERT "Before checking complete overlap, cur hole = (%d, %d).\n", hole->start_seq, hole->end_seq);
else printk(KERN_ALERT "Before checking complete overlap, no more holes.\n"); 
}
	/* Process holes whose ranges are contained within packet's range
	 * 
	 * Note: At this point, all remaining holes have the property
	 *
	 * 	hole->start_seq >= start_seq
	 */
	for( ; hole != NULL; hole = next_hole){
 		/* Save the next hole since the current one may be removed */
		next_hole = hole->next;
		if(hole->end_seq > end_seq){ /* No more complete overlap or containment */
			break;
		}
		/* Remove completely overlapped hole (links updated automatically) */
		nf_mobility_remove_hole(flow, hole);
	}

if(NFM_DEBUG_HOLE){
if(hole != NULL) printk(KERN_ALERT "After checking complete overlap, cur hole = (%d, %d).\n", hole->start_seq, hole->end_seq);
else  printk(KERN_ALERT "After checking complete overlap, no more holes.\n");
}
	/* Possible partial overlap from the left (ending of packet overlaps 
	 * beginning of hole) */
	if(hole != NULL && hole->start_seq <= end_seq){
if(NFM_DEBUG_HOLE)
printk(KERN_ALERT "Shrinking hole from left (%d, %d) -> (%d, %d)", hole->start_seq, hole->end_seq, end_seq + 1, hole->end_seq);
		/* Shrink hole */
		hole->start_seq = end_seq + 1;
	}

	return (matched_first ? NF_MOBILITY_MATCH_FIRST_HOLE : NF_MOBILITY_MATCH_OTHER_HOLE);
}

/* -------- Packet delivery -------- */

static void nf_mobility_deliver_packet(struct sk_buff* skb, int (*ref_fn)(struct sk_buff *) )
{
	ref_fn(skb); // call the reference function passed to this hook (ip_local_deliver_finish() in this version)	
}

static int nf_mobility_should_deliver_buffer(struct nf_mobility_flow *flow)
{
	// Conditions that merit delivering a buffered packet:
	//
	// Either one of the two:
	// 1. The flow is not buffering packets (either due to no holes or an explicit policy)
	// 2. Buffering packets, and either or both of :
	//     a) We're counting buffers by packets and number of buffered packets exceeded threshold
	//     b) We're counting buffers by bytes and number of buffered bytes exceeded threshold
	//
	return !(flow->is_buffering) || 
		((!nfm_is_buffer_packets || (flow->buffered_packets >= nfm_num_buffer_packets)) && 
		 (!nfm_is_buffer_bytes || (flow->buffered_bytes >= nfm_num_buffer_bytes))
		);
}


static void nf_mobility_deliver_buffer_upto(struct nf_mobility_flow *flow, struct nf_mobility_buffer *stop_buffer, int (*ref_fn)(struct sk_buff *)){
	struct nf_mobility_buffer *buffer, *next_buffer;
	
	buffer = flow->buffer_head; 
	while(buffer != NULL && buffer != stop_buffer){
		/* Actual delivery of packet to layer 4 */
		nf_mobility_deliver_packet(buffer->skb, ref_fn);
		next_buffer = buffer->next;
		kfree(buffer); // Free memory used by buffer structure
		buffer = next_buffer;
	}
	
	// Update buffer list head
	flow->buffer_head = buffer;
 
	// If there are no buffers left...
	if(flow->buffer_head == NULL){
		flow->buffer_tail = NULL;
	}
	
	return;
}

static unsigned int nf_mobility_try_deliver(struct nf_mobility_flow *flow, __u32 start_seq, __u32 end_seq, struct sk_buff *skb, int (*ref_fn)(struct sk_buff *))
{
	if(flow->is_buffering){
		/* Queue up packet */
		/* TODO: What if queueing failed (memory shortage)?
		 * Need to do something more than just simply returning NF_ACCEPT
		 * e.g. may have to deliver buffered packets too */
		if(nf_mobility_enqueue_packet(flow, start_seq, end_seq, skb) == NULL){
			printk(KERN_ALERT "WaRNING: Cannot enqueue packet, accepting it.\n");
			return NF_ACCEPT;
		}
	}
	else{
if(NFM_DEBUG && (nfm_pc % 10 == 0))
printk(KERN_ALERT "Delivering received packet in nf_mobility_try_deliver()\n");
		nf_mobility_deliver_packet(skb, ref_fn);
	}

	/* Check if need to deliver out-of-order packets */
	if(nf_mobility_should_deliver_buffer(flow)){
//printk(KERN_ALERT "Delivering all buffered packets in nf_mobility_try_deliver()\n");
		nf_mobility_deliver_buffer_upto(flow, NULL, ref_fn);
		
		// Turn off buffering and
		// ignore existing holes - can't do reordering perfectly
		// TCP will handle the (rare) incoming out-of-order packets even after buffering
		flow->is_buffering = 0;
		flow->buffered_packets = 0;
		flow->buffered_bytes = 0;
		// Remove holes
		nf_mobility_remove_holes(flow);
		// Update start seq for checking dupes
		flow->dupe_check_start_seq = flow->head_of_line;
	}
	// NF_STOLEN is used to make sure the Netfilter framework doesn't 
	// process the packet
	return NF_STOLEN;
}


/* -------- Netfilter hook (main function) -------- */
static unsigned int nf_mobility_hook(unsigned int hooknum, struct sk_buff *skb, const struct net_device *in, const struct net_device *out, int (*ref_fn)(struct sk_buff *))
{
	//int users = atomic_read(&(skb->users));
	//printk(KERN_ALERT "Accepting packet! skb->users = %d\n", users);
	
	struct iphdr *iph;
	__be32 saddr, daddr;
	struct tcphdr *tcph;
	__be16 sport, dport;
	__u32 start_seq, end_seq, ack_seq, packet_length;
	__u8 protocol;

	// Processing variables
	struct nf_mobility_flow *flow;
	unsigned int ret;
	struct nf_mobility_buffer *buffer;
	struct nf_mobility_hole *hole;

	// For now, we support only TCP connections - not sure how to work with UDP-based flows - we can still do 
	// duplicate removal, but reordering will be difficult due to possible random IP numbers
        iph = ip_hdr(skb);
	protocol = iph->protocol;
	if(protocol != IPPROTO_TCP){
		return NF_ACCEPT;
	}

	/* ---- Get packet info ---- */
	saddr = ntohl(iph->saddr);
	daddr = ntohl(iph->daddr);
	tcph = (struct tcphdr*)(skb->data + sizeof(struct iphdr));
	sport = ntohs(tcph->source);
	dport = ntohs(tcph->dest);
	start_seq = ntohl(tcph->seq);
	end_seq = start_seq + tcph->syn + tcph->fin + skb->len - sizeof(struct iphdr) - tcph->doff * 4 - 1;
	ack_seq = ntohl(tcph->ack_seq);
	packet_length = end_seq - start_seq + 1;
	//nf_mobility_print_incoming_TCP(saddr, daddr, sport, dport); // Debugging purposes
//nfm_pc++;
//if(nfm_pc % 10 == 0)
//	printk(KERN_ALERT "TCP packet (%u), start_seq = %u, end_seq = %u, len = %u, ack_seq = %u\n", iph->protocol, start_seq, end_seq, packet_length, ack_seq);

	if(packet_length <= 0) /* Packet without data, e.g. FIN packet */
		return NF_ACCEPT;

	/* ---- Process packet ---- */
	ret = NF_ACCEPT;
	write_lock_bh(&(nfm->flow_lock));

	/* Get flow entry, create one if necessary */
	flow = nf_mobility_get_flow(protocol, saddr, daddr, sport, dport);
	if(flow == NULL){
		flow = nf_mobility_create_flow(protocol, saddr, daddr, sport, dport, start_seq);
		if(flow == NULL){ // Something wrong with flow creation - ignore packet
			ret = NF_ACCEPT;
			goto nfm_unlock;
		}
		printk(KERN_ALERT "New flow: ");
		nf_mobility_print_incoming_TCP(flow->saddr, flow->daddr, flow->sport, flow->dport);
		printk(KERN_ALERT "HOL = %u\n", flow->head_of_line);
	}


	/* Packet falls on head of line */
	if(start_seq == flow->head_of_line){
		flow->head_of_line = end_seq + 1; // Update head of line
		// Try to deliver buffered packets (holes might have held up packets)
		ret = nf_mobility_try_deliver(flow, start_seq, end_seq, skb, ref_fn);
	}
	/* Old packet - let TCP handle it */
	else if(end_seq < flow->dupe_check_start_seq){
printk(KERN_ALERT "Old packet, let TCP handle\n");
		ret = NF_ACCEPT;
	}
	/* Packet behind head of line, check if it is a duplicate
	 * or a hole-filler */
	else if(start_seq < flow->head_of_line){ 
printk(KERN_ALERT "About to call nf_mobility_match_and_fill_holes()\n");
		switch(nf_mobility_match_and_fill_holes(flow, start_seq, end_seq)){
			case NF_MOBILITY_MATCH_FIRST_HOLE:
				/* Deliver this packet */
				nf_mobility_deliver_packet(skb, ref_fn);
				ret = NF_STOLEN; // Ask Netfilter framework to ignore this packet

				/* Check for in-order packets for delivery */
				if(flow->buffer_head == NULL){
					printk(KERN_ALERT "Filled first hole, but out-of-order packets already delivered.\n");
					break;
				}
				else if(flow->holes_head == NULL){
					printk(KERN_ALERT "Filled first (and only) hole, delivering out-of-order packets\n");
					nf_mobility_deliver_buffer_upto(flow, NULL, ref_fn);
					break;
				}

				buffer = flow->buffer_head;
				hole = flow->holes_head;

				while(buffer != NULL){
					if(buffer->start_seq > hole->start_seq)
						break;
					buffer = buffer->next;
				}
				nf_mobility_deliver_buffer_upto(flow, buffer, ref_fn);
				break;

			case NF_MOBILITY_MATCH_OTHER_HOLE:
				/* Try to deliver out-of-order packet */
				ret = nf_mobility_try_deliver(flow, start_seq, end_seq, skb, ref_fn);
				break;

			case NF_MOBILITY_MATCH_NO_HOLE:
				/* Is duplicate packet, drop it */
//printk(KERN_ALERT "Dropping duplicate\n");
if(NFM_DEBUG_DUPE){
nfm_dupe_count++;
if(nfm_dupe_count % 50 == 0)
printk(KERN_ALERT "Dropped %d duplicates\n", nfm_dupe_count);
}

				ret = NF_DROP;
				break;
			default:
				printk(KERN_ALERT "ERROR in nf_mobility module: Unexpected hole-matching result!\n");
		}
		
	}
/*
else{
if(NFM_DEBUG_HOLE) printk(KERN_ALERT "Delivering hole packet\n");
nf_mobility_deliver_packet(skb, ref_fn);
if(NFM_DEBUG_HOLE) printk(KERN_ALERT "After delivery\n");
}
write_unlock_bh(&(nfm->flow_lock));
	return NF_STOLEN;

	if(false){}
*/	
	else{	/* Packet creates a hole after head of line (i.e. start_seq > flow->head_of_line) */
		// Hole spans sequence numbers from head of line up to the byte before the packet's
		// starting sequence number
		if(nf_mobility_create_and_append_hole(flow, flow->head_of_line, start_seq-1) != NULL){
			flow->is_buffering = 1; /* Turn on buffering due to hole */
			ret = nf_mobility_try_deliver(flow, start_seq, end_seq, skb, ref_fn);
		}
		flow->head_of_line = end_seq + 1; /* Update head of line */
	}
nfm_unlock:
	write_unlock_bh(&(nfm->flow_lock));
	return ret;
}


/**
 * Clears all holes of a given flow
 */
void nf_mobility_remove_holes(struct nf_mobility_flow *flow){
	struct nf_mobility_hole *hole, *next_hole;
	/* For each hole */
	for(hole = flow->holes_head; hole != NULL; hole = next_hole){
		next_hole = hole->next;
		kfree(hole);
	}
	/* Reset head and tail pointers */
	flow->holes_head = flow->holes_tail = NULL;
}

/**
 * Cleans up all memory used by the module
 */
static void nf_mobility_cleanup(void)
{
	struct nf_mobility_flow *flow, *next_flow;
	struct nf_mobility_buffer *buffer, *next_buffer;

	printk(KERN_ALERT "Freeing memory...\n");
	write_lock_bh(&(nfm->flow_lock));	
	/* For each flow */
	for(flow = nfm_flows; flow != NULL; flow = next_flow){
		next_flow = flow->next;
		/* For each buffer */
		for(buffer = flow->buffer_head; buffer != NULL; buffer = next_buffer){
			next_buffer = buffer->next;
			kfree(buffer);
		}
		nf_mobility_remove_holes(flow);
		kfree(flow);
	}
	write_unlock_bh(&(nfm->flow_lock));

	kfree(nfm);

	printk(KERN_ALERT "Done!\n");
}


static struct nf_hook_ops nf_mobility_ops __read_mostly =
{
	.pf = PF_INET,
	.priority = 1,
	.hooknum = NF_INET_LOCAL_IN,
	.hook = nf_mobility_hook
};

static int __init nf_mobility_init(void)
{
	printk(KERN_ALERT "Initializing nf-mobility module\n");
	printk(KERN_ALERT "Size of struct iphdr = %d\n", sizeof(struct iphdr));
	
	printk(KERN_ALERT "Initializing nf_mobility and nf_mobility_flow structures\n");
	nfm = (struct nf_mobility *) kmalloc(sizeof(struct nf_mobility), GFP_ATOMIC);
	nfm->mode = NF_MOBILITY_MODE_BICAST;
	rwlock_init(&(nfm->flow_lock));
	nfm_flows = NULL;

	if(nfm_num_buffer_packets > 0){
		nfm_is_buffer_packets = 1;
	}
	else if(nfm_num_buffer_bytes > 0){
		nfm_is_buffer_bytes = 1;
	}
	else{
		nfm_is_buffer_bytes = 1;
		nfm_num_buffer_bytes = NF_MOBILITY_DEFAULT_NUM_BUFFER_BYTES;
	}
	
	printk(KERN_ALERT " Buffering: packets = %d, bytes = %d\n", nfm_is_buffer_packets, nfm_is_buffer_bytes);
	printk(KERN_ALERT "Thresholds: packets = %d, bytes = %d\n", nfm_num_buffer_packets, nfm_num_buffer_bytes);

	return nf_register_hook(&nf_mobility_ops);
}

static void __exit nf_mobility_exit(void)
{
	printk(KERN_ALERT "Removing nf-mobility module\n");
	// Free memory
	nf_mobility_cleanup();
	nf_unregister_hook(&nf_mobility_ops);
}

/* Read module parameters from command line arguments */
module_param(nfm_num_buffer_packets, int, 0);
module_param(nfm_num_buffer_bytes, int, 0);

module_init(nf_mobility_init);
module_exit(nf_mobility_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR(NF_MOBILITY_AUTHOR);
MODULE_DESCRIPTION(NF_MOBILITY_DESC);

