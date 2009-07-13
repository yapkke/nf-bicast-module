from PyQt4.QtCore import (QDate, Qt, SIGNAL, pyqtSignature)
from PyQt4.QtGui import (QApplication, QDialog, QDialogButtonBox, QWidget, QMainWindow)
from subprocess import *
import openroad_layout
import sys, os

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
            self.bonding_ip_address = text
        self.OutputText.insertPlainText("Bonding IP Address:"+self.bonding_ip_address+"\n")
        self.updateUi()
    
    @pyqtSignature("QString")
    def on_editBondIP_nowimax_textEdited(self, text):
        if not self.wimax_enable:
            self.bonding_ip_address = text
            self.OutputText.insertPlainText("Bonding IP Address:"+self.bonding_ip_address+"\n")
        else:
            self.OutputText.insertPlainText("WiMAX is enabled. Won't use the bonding IP address:"+text+"\n")
            self.updateUi()

    @pyqtSignature("QString")
    def on_editAP1_textEdited(self, text):
        self.ap1 = text
        self.OutputText.insertPlainText("AP1:"+self.ap1+"\n")
        self.updateUi()

    @pyqtSignature("QString")
    def on_editAP2_textEdited(self, text):
        self.ap2 = text
        self.OutputText.insertPlainText("AP2:"+self.ap2+"\n")
        self.updateUi()

    @pyqtSignature("QString")
    def on_editAP3_textEdited(self, text):
        self.ap3 = text
        self.OutputText.insertPlainText("AP3:"+self.ap3+"\n")
        self.updateUi()

    @pyqtSignature("QString")
    def on_editWiFiIF1_textEdited(self, text):
        self.wifi1 = text
        self.OutputText.insertPlainText("#1 WiFi Interface:"+self.wifi1+"\n")
        self.updateUi()

    @pyqtSignature("QString")
    def on_editWiFiIF2_textEdited(self, text):
        self.wifi2 = text
        self.OutputText.insertPlainText("#2 WiFi Interface:"+self.wifi2+"\n")
        self.updateUi()

    @pyqtSignature("QString")
    def on_editWimaxIF_textEdited(self, text):
        self.wimax = text
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
        self.updateUi()

    @pyqtSignature("QString")
    def on_editGW_textEdited(self, text):
        self.gateway = text
        self.OutputText.insertPlainText("Gateway:"+self.gateway+"\n")
        self.updateUi()
    
    @pyqtSignature('')
    def on_ButtonRun_clicked(self):
        self.demo_run()
        
    #currently a useless function :p
    def updateUi(self):
        a=1
        #self.OutputText.setPlainText(self.bond_name)
    
    # os.popen is out-dated, but I haven't find out how to use subprocess
    def exe_os_cmd(self, cmd):
	#p = subprocess.Popen( cmd ,stdout=subprocess.PIPE,stderr=subprocess.PIPE) 
	#output, errors = p.communicate()
	self.OutputText.insertPlainText("Executing: "+cmd+"\n")
	try:
		stdin, stdout, stderr = os.popen3(cmd)
  		#add expr for if stdout is not empty
		self.OutputText.insertPlainText("Output: " + str(stdout.read())+"\n")
		#if stderr is not empty
		self.OutputText.insertPlainText("Error: " + str(stderr.read())+ "\n")
	except OSError:
		pass

    # Demo command-related stuff
    def interface_up_cmd(self, interface):
        return "ifconfig %s up" % interface

    def interface_down_cmd(self, interface):
        return "ifconfig %s down" % interface

    def wifi_associate_cmd(self, interface, ap):
        return "iwconfig %s essid %s" % (interface, ap)

    def wifi_dissociate_cmd(self, interface):
        return "iwconfig %s essid xxxx ap off" % interface

    def wimax_associate(self):
        self.exe_os_cmd("./wimax-bicast-up.sh")

    def wimax_dissociate(self):
        self.exe_os_cmd("./wimax-bicast-down.sh")

    def change_active_slave(self, new_active_slave):
        cmd = "./change-active-slave %s %s" % (self.bond_name, new_active_slave) 
	self.exe_os_cmd(cmd)

    def signal_quit_to_nox(self):
        ## TODO: Modify bicast_noxmsg.py so that it's parameterized with GUI's
        ## input
        pass

        
    def send_bicast_msg(self, hostmac=int("0x001cf0ee5ad1", 16), noxhost="192.168.2.254", noxport=2603):
	#hostmac = int("0x001cf0ee5ad1", 16);
	#noxhost = "192.168.2.254"
	#noxport = 2603
	#noxport = 6633
      	sock = noxmsg.NOXChannel(noxhost, noxport);
      	noxmsgtype = int("0x12",16);
      	sock.send(noxmsgtype, struct.pack("Q",noxmsg.htonll(hostmac)));
	self.OutputText.insertPlainText("Sending Bicast Message:  ")
      	self.OutputText.insertPlainText("Bicast Host : "+str(hostmac))
      	self.OutputText.insertPlainText("NOX Host : "+noxhost)
      	self.OutputText.insertPlainText("NOX Port : "+str(noxport) + "\n")

    def device_init(self):
	#cmd = "ifconfig %s down" % (self.wifi1)
	self.exe_os_cmd(self.interface_down_cmd(self.wifi1))
	#cmd = "ifconfig %s down" % (self.wifi2)
	self.exe_os_cmd(self.interface_down_cmd(self.wifi2))
	if self.wimax_enable:
		#cmd = "ifconfig %s down" % (self.wimax)
		self.exe_os_cmd(self.interface_down_cmd(self.wimax))
	#cmd = "ifconfig %s down" % (self.bond_name)
	self.exe_os_cmd(self.interface_down_cmd(self.bond_name))

	cmd = "ifconfig %s hw ether %s" % (self.bond_name, self.bonding_mac_address)
	self.exe_os_cmd(cmd)

	#cmd = "ifconfig %s up" % (self.bond_name)
	self.exe_os_cmd(self.interface_up_cmd(self.bond_name))
	#cmd = "ifconfig %s up" % (self.wifi1)
	self.exe_os_cmd(self.interface_up_cmd(self.wifi1))
	#cmd = "ifconfig %s up" % (self.wifi2)
	self.exe_os_cmd(self.interface_up_cmd(self.wifi2))
	if self.wimax_enable:
		#cmd = "ifconfig %s up" % (self.wimax)
		self.exe_os_cmd(self.interface_up_cmd(self.wimax))

	cmd = "ifconfig %s %s" % (self.bond_name, self.bonding_ip_address)
	self.exe_os_cmd(cmd)
	cmd = "ifconfig %s" % (self.bond_name)
	self.exe_os_cmd(cmd)
	cmd = "cat /proc/net/bonding/%s" % (self.bond_name)
	self.exe_os_cmd(cmd)
	cmd = "route add default gw %s" % (self.gateway)
	self.exe_os_cmd(cmd)
	self.OutputText.insertPlainText("Devices Initialized.\n");

    def associate_wifi(self, wifiIF, ap):
      	# Initialize association and active slave
	#cmd = "iwconfig %s essid %s" % (wifiIF, ap)
	self.exe_os_cmd(self.wifi_associate_cmd(wifiIF, ap))
  	time.sleep(self.wifi_association_time/1000000)	

	#cmd = "./change-active-slave %s %s" % (self.bond_name, wifiIF)
  	self.change_active_slave(self.bond_name, wifiIF)
	if wifiIF == self.wifi1:
		self.wifi_status_1.setText(ap)
	elif wifiIF == self.wifi2:
		self.wifi_status_2.setText(ap)
	self.OutputText.insertPlainText(wifiIF + " is asscociated with " +ap +"\n")

    def dissociate_wifi(self, wifiIF):
	self.exe_os_cmd(self.wifi_dissociate_cmd(wifiIF))	
	if wifiIF == self.wifi1:
                self.wifi_status_1.setText("N/A")
        elif wifiIF == self.wifi2:
                self.wifi_status_2.setText("N/A")
        self.OutputText.insertPlainText(wifiIF + " is disscociated from AP\n")

    def dissociate_devices(self):
	# Dissociate everything in the beginning
      	self.dissociate_wifi(self.wifi1)
      	self.dissociate_wifi(self.wifi2)
	if self.wimax_enable:
		self.wimax_dissociate()
	self.OutputText.insertPlainText("Dissociated all interfaces. Start Demo Now.\n");


    def demo_run(self):
	self.device_init()
	self.dissociate_devices()
	
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
		self.wimax_associate()
		time.sleep(10)
	  	self.OutputText.insertPlainText("Finished Wimax association.\n")
	
	# wimax -> ap2
	self.send_bicast_msg()
	self.dissociate_wifi(self.wifi1)
  	time.sleep(self.wifi_association_time/1000000)	
 
	self.associate_wifi(self.wifi1, self.ap2)
  	time_s = 20
	self.OutputText.insertPlainText("Sleep for "+ str(time_s) +" seconds .... \n");
	time.sleep(time_s)

	self.OutputText.insertPlainText("Switched "+self.wifi1+" from "+self.ap1+" to "+self.ap2+"\n")
  	time_s = 15
	self.OutputText.insertPlainText("Sleep for "+ str(time_s) +" seconds .... \n");
	time.sleep(time_s)

  	# ap2 -> ap1
	self.send_bicast_msg();
	self.dissociate_wifi(self.wifi2)
  	time.sleep(self.wifi_association_time/1000000)	

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
