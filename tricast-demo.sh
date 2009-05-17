#!/bin/bash

# Wifi settings
# New D-link card
bond_name=bond0
bonding_mac_address=00:1c:f0:ee:5a:d1

wifi1=wlan0
wifi2=ath1

ap1=cleanslatewifi1
ap2=cleanslatewifi4
ap3=cleanslatewifi3

wifi_association_time=50000

# WiMax settings
wimax=eth1

use_wimax=1

if [ "$use_wimax" = "1" ]; then
	bonding_ip_address=192.168.2.226
else
	bonding_ip_address=192.168.2.140
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

route add default gw 192.168.2.254

# Dissociate everything in the beginning
iwconfig $wifi1 essid xxxx ap off
iwconfig $wifi2 essid xxxx ap off
if [ "$use_wimax" = "1" ]; then
	./wimax-bicast-down.sh
fi

echo "Dissociated all interfaces. Can start now."

# Sequence
# ap1 -> ap3 -> wimax -> ap2 -> ap1


# Initialize association and active slave
iwconfig $wifi1 essid $ap1
./short-sleep $wifi_association_time
./change-active-slave $bond_name $wifi1

echo "Associated $wifi1 with $ap1"


# Clean Nox bicast state
python bicast_noxmsg.py
python bicast_noxmsg.py
python bicast_noxmsg.py

echo "Set up ready."
echo "Bonding MAC address: $bonding_mac_address"
echo "Bonding IP address: $bonding_ip_address"
echo "Press <ENTER> to start"
read

echo "Starting..."

#echo "Starting bicast filtering..."
#./nf-start-bicast

sleep 30

echo "Associating second AP ($ap3) with $wifi2"

# ap1 -> ap3 (start bicast)
iwconfig $wifi2 essid $ap3
./short-sleep $wifi_association_time
./change-active-slave $bond_name $wifi2

echo "Associated $wifi2 with $ap3"
if [ "$use_wimax" = "1" ]; then
	sleep 20
else
	sleep 30
fi

# ap3 -> wimax
if [ "$use_wimax" = "1" ]; then
	./wimax-bicast-up.sh
	sleep 10
	echo "Finished Wimax association."
fi

# wimax -> ap2
python bicast_noxmsg.py # Send quit to remove ap1 association
iwconfig $wifi1 essid xxxx ap off # Dissociate 
./short-sleep 5000

iwconfig $wifi1 essid $ap2
echo "Associated $wifi1 with $ap2"
./short-sleep $wifi_association_time
sleep 5
./change-active-slave $bond_name $wifi1

echo "Switched $wifi1 from $ap1 to $ap2"
sleep 15

# ap2 -> ap1
python bicast_noxmsg.py # Send quit to remove ap1 association
iwconfig $wifi2 essid xxxx ap off # Dissociate 
./short-sleep 5000

iwconfig $wifi2 essid $ap1
echo "Associated $wifi2 with $ap1"
./short-sleep $wifi_association_time
sleep 5
./change-active-slave $bond_name $wifi2

echo "Switched $wifi2 from $ap3 to $ap1"

sleep 60


#echo "Stopping bicast filtering..."
#./nf-stop-bicast

echo "End!"

