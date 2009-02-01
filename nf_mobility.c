#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/netfilter_ipv4.h>
#include <linux/netfilter.h>

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
static unsigned int nfm_num_buffer_bytes = 0;  /* Maximum buffered bytes */
static int nfm_is_buffer_packets = 0; /* By default, buffer */
static int nfm_is_buffer_bytes = 1; 

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


static void nf_mobility_print_incoming_TCP(__be32 saddr, __be32 daddr, __be16 sport, __be16 dport)
{
	nf_mobility_print_ip(saddr);
	printk(KERN_ALERT " %u ... ", sport);
	nf_mobility_print_ip(daddr);
	printk(KERN_ALERT " %u\n", dport);
	printk(KERN_ALERT "%u    %u\n", saddr, daddr);
}

static void nf_mobility_deliver_packet(struct sk_buff* skb, int (*ref_fn)(struct sk_buff *) )
{
	ref_fn(skb);	
}

static int nf_mobility_should_deliver_buffer(struct nf_mobility_flow *flow)
{
	return !(flow->is_buffering) || (!nfm_is_buffer_packets || (flow->buffered_packets >= nfm_num_buffer_packets)) && (!nfm_is_buffer_bytes || (flow->buffered_bytes >= nfm_num_buffer_bytes));
}

static void nf_mobility_deliver_buffered_upto(struct nf_mobility_flow *flow, struct nf_mobility_buffer *stop_buffer, int (*ref_fn)(struct sk_buff *)){
	struct nf_mobility_buffer *buffer, *next_buffer;
	
	buffer = flow->buffers; 
	while(buffer != NULL && buffer != stop_buffer){
		/* Actual delivery of packet to layer 4 */
		nf_mobility_deliver_packet(buffer->skbi, ref_fn);
		next_buffer = buffer->next;
		kfree(buffer);
	}
	flow->buffers = buffer;
	
	return;
}

static unsigned int nf_mobility_try_deliver(struct nf_mobility_flow *flow, struct sk_buff *skb, int (*ref_fn)(struct sk_buff *))
{
	if(flow->is_buffering){
		/* Queue up packet */
		nf_mobility_enqueue_packet(flow, skb);
	}

	/* Check if need to deliver out-of-order packets */
	if(nf_mobility_should_deliver_buffer(flow)){
		nf_mobility_deliver_buffer_upto(flow, NULL, ref_fn);
		return NF_ACCEPT;
	}
	return NF_STOLEN;
}

static unsigned int nf_mobility_hook(unsigned int hooknum, struct sk_buff *skb, const struct net_device *in, const struct net_device *out, int (*ref_fn)(struct sk_buff *))
{
	int users = atomic_read(&(skb->users));
	//printk(KERN_ALERT "Accepting packet! skb->users = %d\n", users);
	
	struct iphdr *iph;
	__be32 saddr;
	__be32 daddr;
	struct tcphdr *tcph;
	__be16 sport;
	__be16 dport;
	__u32 start_seq;
	__u32 end_seq;
	__u32 ack_seq;
	__u32 packet_length;

        iph = ip_hdr(skb);
	if(iph->protocol != IPPROTO_TCP){
		return NF_ACCEPT;
	}

	saddr = ntohl(iph->saddr);
	daddr = ntohl(iph->daddr);
	tcph = (struct tcphdr*)(skb->data + sizeof(struct iphdr));
	sport = ntohs(tcph->source);
	dport = ntohs(tcph->dest);
	start_seq = ntohl(tcph->seq);
	end_seq = start_seq + tcph->syn + tcph->fin + skb->len - sizeof(struct iphdr) - tcph->doff * 4 - 1;
	ack_seq = ntohl(tcph->ack_seq);
	packet_length = end_seq - start_seq + 1;
	nf_mobility_print_incoming_TCP(saddr, daddr, sport, dport);
	printk(KERN_ALERT "TCP packet (%u), start_seq = %u, end_seq = %u, len = %u, ack_seq = %u\n", iph->protocol, start_seq, end_seq, packet_length, ack_seq);

	/**** Process packet ****/
	struct nf_mobility_flow *flow;
	unsigned int ret = NF_ACCEPT;
	write_lock_bh(&(nfm->flow_lock));

	/* Get flow entry, create one if necessary */
	flow = nf_mobility_get_flow(saddr, daddr, sport, dport);
	if(flow == NULL){
		nf_mobility_create_flow(saddr, daddr, sport, dport, start_seq);
	}

	/* Packet falls on head of line */
	if(start_seq == flow->head_of_line){
		head_of_line = end_seq + 1;
		ret = nf_mobility_try_deliever(flow, skb, ref_fn);
		else{
			/* Update head of line and deliver packet */
			head_of_line = end_seq+1;
			ret =  NF_ACCEPT;
		}
	}
	/* Packet behind head of line, check if it is a duplicate
	 * or a hole-filler */
	else if(start_seq < flow->head_of_line){ 
		switch(nf_mobility_match_and_fill_hole(flow, start_seq, end_seq)){
			case NF_MOBILITY_MATCH_FIRST_HOLE:
				/* Deliver this packet */
				nf_mobility_deliver_packet(skb, ref_fn);
				
				/* Check for in-order packets for delivery */
				struct nf_mobility_buffer *buffer;
				struct nf_mobility_hole *hole;
				if(flows->buffers == NULL){
					printk(KERN_ALERT "Filled first hole, but out-of-order packets already delivered.\n");
					break;
				}
				else if(flows->holes = NULL){
					printk(KERN_ALERT "Filled first (and only) hole, delivering out-of-order packets");
					nf_mobility_deliver_packets_upto(flow, NULL, ref_fn);
					break;
				}

				buffer = flow->buffers;
				hole = flow->holes;

				while(buffer != NULL){
					if(buffer->start_seq > hole->start_seq)
						break;
					buffer = buffer->next;
				}
				nf_mobility_deliver_buffer_upto(flow, buffer, ref_fn);
				break;

			case NF_MOBILITY_MATCH_OTHER_HOLE:
				/* Try to deliver out-of-order packet */
				nf_mobility_try_deliver(flow, skb, ref_fn);
				break;

			case NF_MOBILITY_MATCH_NO_HOLE:
				/* Is duplicate packet, drop it */
				ret = NF_DROP;
				break;
			default:
				printk(KERN_ALERT "ERROR in nf_mobility module: Unexpected hole-matching result!\n");
		}
		
	}
	else{	/* Packet creates a hole (behind head of line) */
		
	}

	write_unlock_bh(&(nfm->flow_lock));
	return ret;
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
		nfm_buffer_bytes = NF_MOBILITY_DEFAULT_NUM_BUFFER_BYTES;
	}

	return nf_register_hook(&nf_mobility_ops);
}

static void __exit nf_mobility_exit(void)
{
	printk(KERN_ALERT "Removing nf-mobility module\n");
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

