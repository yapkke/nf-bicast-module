#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <ctype.h>
#include <string.h>
#include <errno.h>
#include <fcntl.h>
#include <getopt.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <linux/if.h>
#include <net/if_arp.h>
#include <linux/if_ether.h>
#include <linux/if_bonding.h>
#include <linux/sockios.h>

typedef unsigned long long u64;	/* hack, so we may include kernel's ethtool.h */
typedef __uint32_t u32;		/* ditto */
typedef __uint16_t u16;		/* ditto */
typedef __uint8_t u8;		/* ditto */
#include <linux/ethtool.h>

//#define SIOCBONDHOOLOCKTEST 0x899a

int main(int argc, char *argv[])
{
	/* Open a basic socket */
	int skfd = -1;
	char *bond_name;
	char *act_slave;
	if(argc <= 1) {
		printf("Need bond name!\n");
		return -1;
	}
	if(argc <= 2) {
		printf("Need the new active slave name too!\n");
		return -1;
	}
	bond_name = argv[1];
	act_slave = argv[2];
	if(strlen(bond_name) >= IFNAMSIZ) {
		printf("Shorter bond-name please!\n");
		return -1;
	}
	if(strlen(act_slave) >= IFNAMSIZ) {
		printf("Shorter slave-name please!\n");
		return -1;
	}

	if ((skfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
		printf("Failed to open socket\n");
		return -1;
	}

	struct ifreq ifr;
	strcpy(ifr.ifr_name, bond_name);
	strcpy(ifr.ifr_slave, act_slave);
	if (ioctl(skfd, SIOCBONDHOOLOCKTEST, &ifr) < 0) {
		printf("ioctl call failed :(\n");
		return -1;
	}
	
	printf("Done with ioctl-test\n");
	return 0;

}
