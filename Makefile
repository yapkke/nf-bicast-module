# For ncast-netfilter module
obj-m += nf_mobility.o

CC = gcc
INCLUDE = -I/usr/src/linux-headers-$(shell uname -r)/include
client-prog-list = nf-control nf-ioctl nf-start-bicast nf-stop-bicast short-sleep change-active-slave

all: ncast-netfilter-module client-progs

ncast-netfilter-module: 
	make -C /lib/modules/$(shell uname -r)/build M=$(shell pwd) modules

client-progs: $(client-prog-list)

$(client-prog-list): %: %.c
	$(CC) -o $@ $< $(INCLUDE) 

clean:
	make -C /lib/modules/$(shell uname -r)/build M=$(shell pwd) clean
	rm -f *.o $(client-prog-list)
