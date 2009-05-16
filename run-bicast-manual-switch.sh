#!/bin/bash

################
# Run constants 
################
bond_name=bond0
# Old D-link card
#bonding_mac_addr=00:1c:f0:ed:98:5a
# New D-link card
bonding_mac_addr=00:1c:f0:ee:5a:d1
bonding_ip_address=192.168.2.140
num_interfaces=2
interfaces[0]=wlan0
interfaces[1]=ath1
num_essids=2
essids[0]=cleanslatewifi1
essids[1]=cleanslatewifi3
# Init interfaces are array indices into the essids and interfaces arrays
init_interface=0
init_essid=0

# manually switch
# time_between_switches=60

# Bicast duration (in seconds)
#hold_time=10
DEFAULT_HOLD_TIME=10

# Wait time between new AP association and change active slave
# (in usec)
change_active_delay=500000 

num_switches=20

(( x=$num_interfaces-1 ))

########
# MAIN #
########

# Set MAC address of bonding driver
for i in `seq 0 $x`; do
		cmd="ifconfig ${interfaces[$i]} down"
		echo $cmd
		$cmd
done
ifconfig $bond_name down
ifconfig $bond_name hw ether $bonding_mac_addr
ifconfig $bond_name up
for i in `seq 0 $x`; do
		cmd="ifconfig ${interfaces[$i]} up"
		echo $cmd
		$cmd
done
ifconfig $bond_name $bonding_ip_address
ifconfig $bond_name
cat /proc/net/bonding/$bond_name

route add default gw 192.168.2.254

# Dessociate everything in the beginning
for i in `seq 0 $x`; do
		cmd="iwconfig ${interfaces[$i]} essid xxxx ap off"
		echo $cmd
		$cmd
done

# Initialize association and active slave
iwconfig ${interfaces[$init_interface]} essid ${essids[$init_essid]}
sleep 1
iwconfig ${interfaces[$init_interface]}
ifenslave -c $bond_name ${interfaces[$init_interface]}

python bicast_noxmsg.py

echo "Press <ENTER> to start."
read

# Start bicast filtering in Netfilter module
echo "Starting bicast filtering..."
./nf-start-bicast

cur_interface=$init_interface
cur_essid=$init_essid

echo $cur_interface
let "next_interface=($cur_interface+1)%$num_interfaces"
echo $next_interface

# Switching
for i in `seq 1 $num_switches`; do
	echo "Enter hold time in seconds (default = $DEFAULT_HOLD_TIME): "
	read hold_time

	if [ "$hold_time" = "" ]; then
		hold_time=$DEFAULT_HOLD_TIME
	fi
	echo "hold time = $hold_time"

	let "next_interface=($cur_interface+1)%$num_interfaces"
	let "next_essid=($cur_essid+1)%$num_essids"

	echo "Switching from ${essids[$cur_essid]} (${interfaces[$cur_interface]}) to ${essids[$next_essid]} (${interfaces[$next_interface]}), hold time = $hold_time" 

	# Make new association
	iwconfig ${interfaces[$next_interface]} essid ${essids[$next_essid]}
	#sleep $change_active_delay
	./short-sleep $change_active_delay

	# Change sending interface
	# ifenslave -c $bond_name ${interfaces[$next_interface]}
	./change-active-slave $bond_name ${interfaces[$next_interface]}
	
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
done

# Stop bicast filtering in Netfilter module
echo "Stopping bicast filtering..."
./nf-stop-bicast

echo "Done!"

