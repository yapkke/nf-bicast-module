#!/bin/bash

################
# Run constants 
################
bond_name=bond0
# Need to use Wimax MAC
bonding_mac_addr=00:50:c2:74:d1:08
# Wimax-specific IP address
bond_ip_address=192.168.2.225
# Wimax interface is normally eth1
wimax_interface=eth1
wifi_interface=wlan0
wifi_essid=cleanslatewifi1
init_interface=eth1

wimax_up_script="./wimax-bicast-up.sh"
wimax_down_script="./wimax-bicast-down.sh"

# manually switch
# time_between_switches=60

# Bicast duration (in seconds)
#hold_time=10
DEFAULT_HOLD_TIME=10

wimax_association_time=10 # 10 seconds for Wimax association
wifi_association_time=50000 # (in usec)

num_switches=20

cur_interface=$init_interface

########
# MAIN #
########

# Set MAC address of bonding driver
ifconfig $wifi_interface down
ifconfig $wimax_interface down
ifconfig $bond_name down
ifconfig $bond_name hw ether $bonding_mac_addr
ifconfig $bond_name up
ifconfig $wifi_interface up
ifconfig $wimax_interface up
ifconfig $bond_name $bond_ip_address
ifconfig $bond_name
cat /proc/net/bonding/$bond_name

route add default gw 192.168.2.254

# Dessociate everything first in the beginning
iwconfig $wifi_interface essid xxxx ap off
$wimax_down_script
echo -e "\r\n"
sleep 5

# Initialize association and active slave
if [ "$init_interface" = "$wifi_interface" ]; then
	iwconfig $init_interface essid $wifi_essid
	sleep 1
	iwconfig $init_interface
else
	$wimax_up_script
	sleep $wimax_association_time
	echo "After Wimax association sleep time"
fi
ifenslave -c $bond_name $init_interface

echo "Before sending bicast noxmsg"
python bicast_noxmsg.py
echo "After sending bicast noxmsg"

echo "Press <ENTER> to start."
read

# Start bicast filtering in Netfilter module
echo "Starting bicast filtering..."
./nf-start-bicast

cur_inteface=$init_interface

# Switching
for i in `seq 1 $num_switches`; do
	echo "Enter hold time in seconds (default = $DEFAULT_HOLD_TIME): "
	read hold_time

	if [ "$hold_time" = "" ]; then
		hold_time=$DEFAULT_HOLD_TIME
	fi
	echo "hold time = $hold_time"

	# Get next interface to use
	if [ "$cur_interface" = "$wifi_interface" ]; then
		next_interface="$wimax_interface"
		echo "Switching from Wifi ($cur_interface) to Wimax ($next_interface), hold time = $hold_time" 

		# Associate Wimax
		$wimax_up_script
		pwd

		# Wimax needs long association time
		sleep $wimax_association_time
		echo "After wimax association sleep"
	else
		next_interface="$wifi_interface"
		echo "Switching from Wimax ($cur_interface) to Wifi ($next_interface <-> $wifi_essid), hold time = $hold_time" 

		# Make Wifi association
		iwconfig $next_interface essid $wifi_essid
	
		# Wifi needs short sleep
		./short-sleep $wifi_association_time
	fi

	# Change sending interface
	# ifenslave -c $bond_name $next_interface
	./change-active-slave $bond_name
	
	# Hold
	sleep $hold_time
	
	# Send stop message to Nox
	python bicast_noxmsg.py
	
	# Break old association
	if [ "$cur_interface" = "$wifi_interface" ]; then
		iwconfig $cur_interface essid "xxxx" ap off
	else
		$wimax_down_script
		echo -e "\r\n"
	fi

	cur_interface="$next_interface"
done

# Stop bicast filtering in Netfilter module
echo "Stopping bicast filtering..."
./nf-stop-bicast

echo "Done!"

