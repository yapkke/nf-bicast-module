#ifndef _NF_MOBILITY_IOCTL_H_
#define _NF_MOBILITY_IOCTL_H_

/* IOCTL stuff */
#define NF_MOBILITY_MAJOR_NUM 100

// IOCTL definition
#define NF_MOBILITY_IOCTL_COMMAND _IOR(NF_MOBILITY_MAJOR_NUM, 0, unsigned long)

// Parameters of ioctl command
#define NF_MOBILITY_IOCTL_START_BICAST	10
#define NF_MOBILITY_IOCTL_STOP_BICAST	11
#define NF_MOBILITY_IOCTL_CLEANUP		400

// Name of device
#define NF_MOBILITY_DEVICE_FILE_NAME "nfm_dev"

#endif

