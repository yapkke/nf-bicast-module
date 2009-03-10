#!/usr/bin/python2.5
import noxmsg
import sys
import socket
import struct

hostmac = int("0x001cf0ed985a", 16);
noxhost = "192.168.2.254"
noxport = 2603
sock = noxmsg.NOXChannel(noxhost, noxport);
noxmsgtype = int("0x12",16);
sock.send(noxmsgtype, struct.pack("Q",noxmsg.htonll(hostmac)));
#sock.send(noxmsgtype, noxmsg.htonll(hostmac));
#sock.send("test");

print "Bicast Host : "+str(hostmac)
print "NOX Host : "+noxhost
print "NOX Port : "+str(noxport)
