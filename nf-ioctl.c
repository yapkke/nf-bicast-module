/*
 * nf-ioctl.c − the process to use ioctl's to control the kernel module
 * */
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h> /* open */
#include <unistd.h> /* exit */
#include <sys/ioctl.h> /* ioctl */

#include "nf_mobility_ioctl.h"

int do_ioctl(int fd, int param){
	int ret_val;

	ret_val = ioctl(fd, NF_MOBILITY_IOCTL_SET_STATUS, param);

	if(ret_val < 0){
		fprintf(stderr, "ioctl call failed. ret_val = %d\n", ret_val);	
		exit(-1);
	}

	fprintf(stderr, "ioctl call apparently successful.\n");
	return ret_val;
}

int main(){
	int fd, ret_val;

	fd = open(NF_MOBILITY_DEVICE_FILE_NAME, 0);
	if(fd < 0){
		fprintf(stderr, "Can't open device file: %s\n", NF_MOBILITY_DEVICE_FILE_NAME);
		exit(-1);
	}

	ret_val = do_ioctl(fd, 0);

	return 0;
}

