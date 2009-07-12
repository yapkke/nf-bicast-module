from PyQt4.QtCore import (QDate, Qt, SIGNAL, pyqtSignature)
from PyQt4.QtGui import (QApplication, QDialog, QDialogButtonBox, QWidget, QMainWindow)
import subprocess
import openroad_layout
import os
import sys
#for bicast_noxmsg
import noxmsg
import socket
import struct
import time

class OpenRoadClient(QMainWindow,
            openroad_layout.Ui_MainWindow):
    
    def __init__(self, parent=None):
        super(OpenRoadClient, self).__init__(parent)
        self.setupUi(self)
        self.ButtonRun.setFocus()
	# init: variables
	# APs
  	self.ap1 = self.editAP1.text()
  	self.ap2 = self.editAP2.text()
  	self.ap3 = self.editAP3.text()
	# WiFi Interfaces
  	self.wifi1 = self.editWiFiIF1.text()
  	self.wifi2 = self.editWiFiIF2.text()
  	# WiMAX
	self.wimax = self.editWimaxIF.text()
  	self.wimax_enable = self.isUseWiMax.isChecked() 
	# Bonding Drivers
        self.bond_name = self.editBondMacIF.text()
  	self.bonding_mac_address = self.editBondMac.text()
  	if self.wimax_enable:
 	 	self.bonding_ip_address = self.editBondIP.text()
  	else:
		self.bonding_ip_address = self.editBondIP_nowimax.text()
  	# General Settings
  	self.wifi_association_time = self.wifiAssoTimeSpinBox.value()
	self.gateway = self.editGW.text()
	self.updateUi()

    @pyqtSignature("QString")
    def on_editBondMacIF_textEdited(self, text):
        self.bond_name = text;
	self.OutputText.insertPlainText("Bonding InterFace:"+self.bond_name+"\n")
        self.updateUi()
    
    @pyqtSignature("QString")
    def on_editBondMac_textEdited(self, text):
        self.bonding_mac_address = text;
	self.OutputText.insertPlainText("Bonding MAC Address:"+self.bonding_mac_address+"\n")
        self.updateUi()
    
    @pyqtSignature("QString")
    def on_editBondIP_textEdited(self, text):
        if self.wimax_enable:
	        self.bonding_ip_address = text;
		self.OutputText.insertPlainText("Bonding IP Address:"+self.bonding_ip_address+"\n")
	        self.updateUi()
    
    @pyqtSignature("QString")
    def on_editBondIP_nowimax_textEdited(self, text):
        if not self.wimax_enable:
	        self.bonding_ip_address = text;
		self.OutputText.insertPlainText("Bonding IP Address:"+self.bonding_ip_address+"\n")
  	else:
		self.OutputText.insertPlainText("WiMAX is enabled. Won't use the bonding IP address:"+text+"\n")
	self.updateUi()

    @pyqtSignature("QString")
    def on_editAP1_textEdited(self, text):
        self.ap1 = text;
	self.OutputText.insertPlainText("AP1:"+self.ap1+"\n")
        self.updateUi()

    @pyqtSignature("QString")
    def on_editAP2_textEdited(self, text):
        self.ap2 = text;
	self.OutputText.insertPlainText("AP2:"+self.ap2+"\n")
        self.updateUi()

    @pyqtSignature("QString")
    def on_editAP3_textEdited(self, text):
        self.ap3 = text;
	self.OutputText.insertPlainText("AP3:"+self.ap3+"\n")
        self.updateUi()

    @pyqtSignature("QString")
    def on_editWiFiIF1_textEdited(self, text):
        self.wifi1 = text;
	self.OutputText.insertPlainText("#1 WiFi Interface:"+self.wifi1+"\n")
        self.updateUi()

    @pyqtSignature("QString")
    def on_editWiFiIF2_textEdited(self, text):
        self.wifi2 = text;
	self.OutputText.insertPlainText("#2 WiFi Interface:"+self.wifi2+"\n")
        self.updateUi()

    @pyqtSignature("QString")
    def on_editWimaxIF_textEdited(self, text):
        self.wimax = text;
	self.OutputText.insertPlainText("WiMAX Interface:"+self.wimax+"\n")
        self.updateUi()

    @pyqtSignature('bool')
    def on_isUseWiMax_toggled(self, checked):
        self.wimax_enable = checked
	if self.wimax_enable:
	       self.bonding_ip_address = self.editBondIP.text()
	else:
	       self.bonding_ip_address = self.editBondIP_nowimax.text()
	self.OutputText.insertPlainText("WiMAX Enable:"+str(self.wimax_enable)+"\n")
	self.OutputText.insertPlainText("Bonding IP Address:"+self.bonding_ip_address+"\n")
        self.updateUi()

    @pyqtSignature("int")
    def on_wifiAssoTimeSpinBox_valueChanged(self, value):
	self.wifi_association_time = value;
	self.OutputText.insertPlainText("WiFi Association Time:"+str(self.wifi_association_time)+"\n")
        self.updateUi()

    @pyqtSignature("QString")
    def on_editGW_textEdited(self, text):
        self.gateway = text;
	self.OutputText.insertPlainText("Gateway:"+self.gateway+"\n")
        self.updateUi()
    
    @pyqtSignature('')
    def on_ButtonRun_clicked(self):
              self.demo_run()
 	
    def updateUi(self):
        a=1
	#self.OutputText.setPlainText(self.bond_name)
	#amount = (self.priceSpinBox.value() *
	#          self.quantitySpinBox.value())
	#enable = not self.customerLineEdit.text().isEmpty() and amount
	#self.buttonBox.button(
	#        QDialogButtonBox.Ok).setEnabled(enable)
	#self.amountLabel.setText(str(amount))

    def exe_os_cmd(self, cmd):
	#os.system(cmd)
	#p = subprocess.Popen( cmd ,stdout=subprocess.PIPE,stderr=subprocess.PIPE) 
	#output, errors = p.communicate()
	self.OutputText.insertPlainText("Executing: "+cmd+"\n")
	try:
		stdin, stdout, stderr = os.popen3(cmd)
  		#add expr for if stdout is not empty
		self.OutputText.insertPlainText("Output: " + stdout.read()+"\n")
		#if stderr is not empty
		self.OutputText.insertPlainText("Error: " + stderr.read()+ "\n")
	except OSError:
		pass
        
    def send_bicast_msg(self):
      	hostmac = int("0x001cf0ee5ad1", 16);
      	noxhost = "192.168.2.254"
      	noxport = 2603
	#noxport = 6633
      	sock = noxmsg.NOXChannel(noxhost, noxport);
      	noxmsgtype = int("0x12",16);
      	sock.send(noxmsgtype, struct.pack("Q",noxmsg.htonll(hostmac)));
	#sock.send(noxmsgtype, noxmsg.htonll(hostmac));
	#sock.send("test");
	self.OutputText.insertPlainText("Send Bicast Message:")
      	self.OutputText.insertPlainText("Bicast Host : "+str(hostmac))
      	self.OutputText.insertPlainText("NOX Host : "+noxhost)
      	self.OutputText.insertPlainText("NOX Port : "+str(noxport))

    def device_init(self):
	cmd = "ifconfig %s down" % (self.wifi1)
	self.exe_os_cmd(cmd)
	cmd = "ifconfig %s down" % (self.wifi2)
	self.exe_os_cmd(cmd)
	if self.wimax_enable:
		cmd = "ifconfig %s down" % (self.wimax)
		self.exe_os_cmd(cmd)
	cmd = "ifconfig %s down" % (self.bond_name)
	self.exe_os_cmd(cmd)
	cmd = "ifconfig %s hw ether %s" % (self.bond_name, self.bonding_mac_address)
	self.exe_os_cmd(cmd)
	cmd = "ifconfig %s up" % (self.bond_name)
	self.exe_os_cmd(cmd)
	cmd = "ifconfig %s up" % (self.wifi1)
	self.exe_os_cmd(cmd)
	cmd = "ifconfig %s up" % (self.wifi2)
	self.exe_os_cmd(cmd)
	if self.wimax_enable:
		cmd = "ifconfig %s up" % (self.wimax)
		self.exe_os_cmd(cmd)
	cmd = "ifconfig %s %s" % (self.bond_name, self.bonding_ip_address)
	self.exe_os_cmd(cmd)
	cmd = "ifconfig %s" % (self.bond_name)
	self.exe_os_cmd(cmd)
	cmd = "cat /proc/net/bonding/%s" % (self.bond_name)
	self.exe_os_cmd(cmd)
	cmd = "route add default gw %s" % (self.gateway)
	self.exe_os_cmd(cmd)
	self.OutputText.insertPlainText("Devices Initialized.\n");

    def deassociate_devices(self):
	# Dissociate everything in the beginning
      	cmd = "iwconfig %s essid xxxx ap off" % (self.wifi1)
	self.exe_os_cmd(cmd)
      	cmd = "iwconfig %s essid xxxx ap off" % (self.wifi2)
	self.exe_os_cmd(cmd)
	if self.wimax_enable:
		cmd = "./wimax-bicast-down.sh"
		self.exe_os_cmd(cmd)
	self.OutputText.insertPlainText("Dissociated all interfaces. Start Demo Now.\n");

    def associate_wifi(self, wifiIF, ap):
      	# Initialize association and active slave
      	cmd = "iwconfig %s essid %s" % (wifiIF, ap)
	self.exe_os_cmd(cmd)
  	cmd = "./short-sleep %d" % (self.wifi_association_time)
	self.exe_os_cmd(cmd)
      	cmd = "./change-active-slave %s %s" % (self.bond_name, wifiIF)
	self.exe_os_cmd(cmd)
	if wifiIF == self.wifi1:
		self.wifi_status_1.setText(ap)
	elif wifiIF == self.wifi2:
		self.wifi_status_2.setText(ap)
	self.OutputText.insertPlainText(wifiIF + " is asscociated with " +ap +"\n")

    def demo_run(self):
	self.device_init()
	self.deassociate_devices()
	
	self.OutputText.insertPlainText("Set up Ready.\n");
	self.OutputText.insertPlainText("Bonding MAC address: "+ self.bonding_mac_address+"\n")
	self.OutputText.insertPlainText("Bonding IP address: " + self.bonding_ip_address+"\n")
	self.OutputText.insertPlainText("Starting Demo .....\n");
	
	# Sequence
	# ap1 -> ap3 -> wimax -> ap2 -> ap1
	self.associate_wifi(self.wifi1, self.ap1)	
	
  	self.send_bicast_msg(); 
	self.send_bicast_msg(); 
	self.send_bicast_msg();
	
	time_s = 30
	self.OutputText.insertPlainText("Sleep for "+ str(time_s) +" seconds .... \n");
	time.sleep(time_s)

	# ap1 -> ap3 (start bicast)
  	self.associate_wifi(self.wifi2, self.ap3)
	if self.wimax_enable:
		time_s = 20
  	else:
		time_s = 30
	self.OutputText.insertPlainText("Sleep for "+ str(time_s) +" seconds .... \n");
	time.sleep(time_s)
	
  	# ap3 -> wimax
  	if self.wimax_enable:
        	self.exe_os_cmd("./wimax-bicast-up.sh")
		time.sleep(10)
	  	self.OutputText.insertPlainText("Finished Wimax association.\n")
	
	# wimax -> ap2
	self.send_bicast_msg();
	cmd = "iwconfig %s essid xxxx ap off" % (self.wifi1) # Dissociate 
	self.exe_os_cmd(cmd)
	self.exe_os_cmd("./short-sleep 5000")
 
	self.associate_wifi(self.wifi1, self.ap2)
  	time.sleep(20)

	self.OutputText.insertPlainText("Switched "+self.wifi1+" from "+self.ap1+" to "+self.ap2+"\n")
	time.sleep(15)

  	# ap2 -> ap1
	self.send_bicast_msg();
  	cmd = "iwconfig %s essid xxxx ap off" % (self.wifi2) # Dissociate 
  	self.exe_os_cmd("./short-sleep 5000")

	self.associate_wifi(self.wifi2, self.ap1)

	self.OutputText.insertPlainText("Switched "+self.wifi2+" from "+self.ap3+" to "+self.ap1+"\n")

	time.sleep(60)
	self.OutputText.insertPlainText("Demo End!\n")

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    form = OpenRoadClient()
    form.show()
    app.exec_()
