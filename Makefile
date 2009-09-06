# For ncast-netfilter module
obj-m += nf_mobility.o

CC=gcc
client-progs = nf-control nf-ioctl nf-start-bicast nf-stop-bicast short-sleep

all: ncast-netfilter-module $(client-progs)

ncast-netfilter-module:
	make -C /lib/modules/$(shell uname -r)/build M=$(shell pwd) modules

$(client-progs): %: %.c
	$(CC) -o $@ $< 

clean:
	make -C /lib/modules/$(shell uname -r)/build M=$(shell pwd) clean
	rm -f *.o $(client-progs)
