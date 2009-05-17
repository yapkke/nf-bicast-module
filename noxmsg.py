"""This module defines the messaging to and from NOX.

Copyright (C) 2009 Stanford University
Created by ykk
See src/nox/coreapps/messenger
"""
import socket
import struct

def htonll(value):
    val = struct.unpack("HHHH",struct.pack("Q",value))
    return struct.unpack("Q",struct.pack("HHHH",socket.htons(val[3]),socket.htons(val[2]),socket.htons(val[1]),socket.htons(val[0])))[0]

#def htonll(value):
#    val = struct.unpack("LL",struct.pack("Q",value))
#    return struct.unpack("Q",struct.pack("LL",socket.htonl(val[1]),socket.htonl(val[0])))[0]

class NOXMsg:
    """Base class for messages to NOX.
    If not extended provides the disconnect message.
    """
    def __init__(self):
        self.type = 0;

    def __repr__(self):
        "Provide message to send"
        return "";

class NOXChannel:
    """TCP channel to communicate to NOX with.
    """
    def __init__(self,ipAddr,portNo=2603):
        "Initialize with socket"
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((ipAddr,portNo))

    def baresend(self,cmd):
        "Send bare message"
        self.sock.send(struct.pack("H",socket.htons(len(str(cmd))+2))\
                       +str(cmd))

    def send(self,type,cmd):
        "Send message of certain type"
        self.baresend(struct.pack("B",type)+str(cmd))
        
    def sendMsg(self,msg):
        "Send message that is NOXMsg"
        if isinstance(msg, NOXMsg):
            self.send(msg.type, msg)
               
    def receive(self, recvLen):
        "Receive command"
        return self.sock.recv(recvLen)

    def __del__(self):
        "Terminate connection"
        self.sendMsg(NOXMsg())
        self.sock.shutdown(1)
        self.sock.close()

class NOXSSLChannel(NOXChannel):
    """SSL channel to communicate to NOX with.
    """
    def __init__(self, ipAddr, portNo=1304):
        "Initialize with SSL sock"
        NOXChannel.__init__(self, ipAddr, portNo)
        self.sslsock = socket.ssl(self.sock)

    def baresend(self,cmd):
        "Send bare message"
        self.sslsock.write(struct.pack("H",socket.htons(len(str(cmd))+2))\
                           +str(cmd))
