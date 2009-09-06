#!/bin/bash

# Wifi settings
# New D-link card
bond_name=bond0
bonding_mac_address=00:1c:f0:ed:98:5a

wifi1=wlan0
wifi2=ath0

ap1=ordemo3
ap2=ordemo1
ap3=ordemo2

wifi_association_time=50000

# WiMax settings
wimax=eth1

use_wimax=0

if [ "$use_wimax" = "1" ]; then
	bonding_ip_address=10.79.1.242
else
	bonding_ip_address=10.79.1.242
fi

#(( x=$num_interfaces-1 ))

########
# MAIN #
########

# Set MAC address of bonding driver
ifconfig $wifi1 down
ifconfig $wifi2 down
if [ "$use_wimax" = "1" ]; then
	ifconfig $wimax down
fi
ifconfig $bond_name down
ifconfig $bond_name hw ether $bonding_mac_address
ifconfig $bond_name up
ifconfig $wifi1 up
ifconfig $wifi2 up
if [ "$use_wimax" = "1" ]; then
	ifconfig $wimax up
fi
ifconfig $bond_name $bonding_ip_address
ifconfig $bond_name
cat /proc/net/bonding/$bond_name

route add default gw 10.79.1.105

# Dissociate everything in the beginning
iwconfig $wifi1 essid xxxx ap off
iwconfig $wifi2 essid xxxx ap off
if [ "$use_wimax" = "1" ]; then
	./wimax-bicast-down.sh
fi

echo "Dissociated all interfaces. Can start now."

# Sequence
# ap1 -> ap3 -> wimax -> ap2 -> ap1

# Clean Nox bicast state
#python bicast_noxmsg.py
#python bicast_noxmsg.py
#python bicast_noxmsg.py

# Initialize association and active slave
iwconfig $wifi1 essid $ap1
./short-sleep $wifi_association_time
./change-active-slave $bond_name $wifi1

echo "Associated $wifi1 with $ap1"

echo "Set up ready."
echo "Bonding MAC address: $bonding_mac_address"
echo "Bonding IP address: $bonding_ip_address"
echo "Press <ENTER> to start"
read

echo "Starting..."

#echo "Starting bicast filtering..."
#./nf-start-bicast

echo "Press <ENTER> to start bicasting"
read

echo "Associating second AP ($ap3) with $wifi2"

# ap1 -> ap3 (start bicast)
iwconfig $wifi2 essid $ap3
./short-sleep $wifi_association_time
./change-active-slave $bond_name $wifi2

echo "Associated $wifi2 with $ap3"
#if [ "$use_wimax" = "1" ]; then
##	sleep 20
#else
#	sleep 30
#fi
echo "Press <ENTER> to start tricasting"
read

# ap3 -> wimax
if [ "$use_wimax" = "1" ]; then
	./wimax-bicast-up.sh
	sleep 10
	echo "Finished Wimax association."
fi

echo "Press <ENTER> to fin"
read

