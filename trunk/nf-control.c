/*
* nf-ioctl.c − the process to use ioctl's to control the kernel module
*/
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h> /* open */
#include <unistd.h> /* exit */
#include <sys/ioctl.h> /* ioctl */

#include "nf_mobility_ioctl.h"

int do_ioctl(int fd, int cmd, int param){
	int ret_val;

	ret_val = ioctl(fd, cmd, param);

	if(ret_val < 0){
		fprintf(stderr, "ioctl call failed. ret_val = %d\n", ret_val);	
		exit(-1);
	}

	fprintf(stderr, "ioctl call apparently successful.\n");
	return ret_val;
}

int main(){
	int fd, ret_val, timeout;
	char input[32];

	fd = open(NF_MOBILITY_DEVICE_FILE_NAME, 0);
	if(fd < 0){
		fprintf(stderr, "Can't open device file: %s\n", NF_MOBILITY_DEVICE_FILE_NAME);
		fprintf(stderr, "Try executing this first: [sudo] mknod nfm_dev c %d 0\n", NF_MOBILITY_MAJOR_NUM);
		exit(-1);
	}

	while(1){
		printf("====== Client Mobility Manager ======\n");
		printf("~~ MAIN MENU ~~\n");
		printf("1. Start bicast\n");
		printf("2. Stop bicast\n");
		printf("3. Set timeout\n");
		
		printf("\n");

		printf("Enter option (q to quit): ");
		scanf("%s", input);

		if(input[0] == 'q'){
			printf("Exiting...\n");
			break;
		}
	
		switch(input[0]){
			case '1':
				ret_val = do_ioctl(fd, NF_MOBILITY_IOCTL_SET_STATUS, NF_MOBILITY_IOCTL_START_BICAST);
				break;
			case '2':
				ret_val = do_ioctl(fd, NF_MOBILITY_IOCTL_SET_STATUS, NF_MOBILITY_IOCTL_STOP_BICAST);
				break;
			case '3':
				printf("Input timeout value in ms (integer, 0 = unchanged): ");
				scanf("%d", &timeout);
				if(timeout > 0){
					ret_val = do_ioctl(fd, NF_MOBILITY_IOCTL_SET_TIMEOUT, timeout);
				}
				else if(timeout < 0){
					fprintf(stderr, "Error: timeout value cannot be negative!\n");
					ret_val = -1;
				}
				else{
					printf("Timeout value unchanged.\n");
					ret_val = 0;
				}
				break;
			default:
				fprintf(stderr, "Unknown option!\n");
				ret_val = -2;
		}
		printf("ret_val = %d\n", ret_val);
		printf("\n");
	}
	return 0;
}

