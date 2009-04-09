#!/bin/bash

################
# Run constants 
################
bond_name=bond0
bonding_mac_addr=00:1c:f0:ed:98:5a
init_interface=ath0
init_essid=cleanslatewifi1
num_essids=2
essids[0]=cleanslatewifi1
essids[1]=cleanslatewifi2
num_interfaces=2
interfaces[0]=ath0
interfaces[1]=wlan0


time_between_switches=60

# Bicast duration
hold_time=1

# Wait time between new AP association and change active slave
# (in usec)
change_active_delay=5000 

num_switches=20

cur_interface=$init_interface
cur_essid=$init_essid
next_interface=1
next_essid=1

#############
# FUNCTIONS #
#############
switch_ap()
{
	# Make new association
	iwconfig ${interfaces[$next_interface]} essid ${essids[$next_essid]}
	sleep 1
	
	# Change sending interface
	ifenslave -c $bond_name ${interfaces[$next_interface]}
	
	# Hold
	sleep $hold_time

	# Break old association
	iwconfig ${interfaces[$cur_interface]} essid "xxxx" ap off
}

########
# Init #
########

# Set MAC address of bonding driver
ifconfig $bond_name down
ifconfig $bond_name hw ether $bonding_mac_addr
ifconfig $bond_name up
ifconfig $bond_name
cat /proc/net/bonding/$bond_name

# Initialize association and active slave
iwconfig $init_interface essid $init_essid
sleep 1
iwconfig $init_interface
ifenslave -c $bond_name $init_interface

python bicast_noxmsg.py

echo "Press <ENTER> to start."
read

# Start bicast filtering in Netfilter module
echo "Starting bicast filtering..."
./nf-start-bicast

sleep $time_between_switches

cur_inteface=$init_interface
cur_essid=$init_essid

# Switching
for i in `seq 1 $num_switches`; do
	let "next_interface=($cur_interface+1)%$num_interfaces"
	let "next_essid=($cur_essid+1)%$num_essids"

	echo "Switching from ${essids[$cur_essid]} (${interfaces[$cur_interface]}) to ${essids[$next_essid]} (${interfaces[$next_interface]}), hold time = $hold_time" 

	# Make new association
	iwconfig ${interfaces[$next_interface]} essid ${essids[$next_essid]}
	#sleep $change_active_delay
	./short-sleep $change_active_delay

	# Change sending interface
	# ifenslave -c $bond_name ${interfaces[$next_interface]}
	./change-active-slave $bond_name
	
	# Hold
	#let "sleep_time=$hold_time - $change_active_delay"
	#sleep $sleep_time
	sleep $hold_time
	
	# Send stop message to Nox
	python bicast_noxmsg.py
	
	# Break old association
	iwconfig ${interfaces[$cur_interface]} essid "xxxx" ap off

	cur_interface=$next_interface
	cur_essid=$next_essid

	sleep $time_between_switches
done

# Stop bicast filtering in Netfilter module
echo "Stopping bicast filtering..."
./nf-stop-bicast

echo "Done!"

