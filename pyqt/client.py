#!/usr/bin/python
#Todo: Auto mode / flush state
from PyQt4.QtCore import * #(QDate, Qt, SIGNAL, pyqtSignature)
from PyQt4.QtGui import * #(QApplication, QDialog, QDialogButtonBox, QWidget, QMainWindow, QComboBox, QPushButton, QMessageBox)
from subprocess import *
import openroad_layout
import sys, os
import time
import noxmsg
import socket
import struct
import thread

class OpenRoadClient(QMainWindow, openroad_layout.Ui_MainWindow):
		def __init__(self, parent=None):
				super(OpenRoadClient, self).__init__(parent)
				self.setupUi(self)
				self.cbMode.setFocus()
				# init: variables
				self.startNcast = 0;
				self.handoverTime = 30000
				self.auto_pid = 0;
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

				#Control Panel, default is auto mode
				self.cbWifi1.setEnabled(False)
				self.cbWifi2.setEnabled(False)
				#Active Wireless Interface 
				self.activeIF = "N/A"
				#The Stop Button by default is disable, enabled with the start button is pushed
				self.ButtonStop.setEnabled(False)
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
		
		@pyqtSignature("QString")
		def on_cbMode_currentIndexChanged(self, mode):
				self.device_init()
				if mode == "Auto":
						self.cbWifi1.setEnabled(False)
						self.cbWifi2.setEnabled(False)
				else:				
						self.OutputText.insertPlainText("Changed to Manual Mode. \n")
						self.cbWifi1.setEnabled(True)						
						self.cbWifi2.setCurrentIndex(0)
						self.cbWifi2.setEnabled(True)
						# The second wifi by default set as none
						self.cbWifi2.setCurrentIndex(3)
						self.auto_pid = 0;
				self.ButtonStop.setEnabled(False)
				self.ButtonStart.setEnabled(True)
			
		
		def is_unicast_setting(self):
				if self.cbWifi1.currentIndex() != 3 and self.cbWifi2.currentIndex() != 3:
						return False;
				else:
						return True


		
		@pyqtSignature("QString")
		def on_cbWifi1_currentIndexChanged(self, ap):
				if self.startNcast == 0:
						if not self.is_unicast_setting():
								self.cbWifi1.setCurrentIndex(3)
								QMessageBox.warning(self, "Warning", "Please start from Uni-casting.")								
				elif ap == self.wifi_status_2.text():
						current_ap = self.wifi_status_1.text();
						if current_ap == self.ap1:
								self.cbWifi1.setCurrentIndex(0)
						elif current_ap == self.ap2:
								self.cbWifi1.setCurrentIndex(1)
						elif current_ap == self.ap3:
								self.cbWifi1.setCurrentIndex(2)
						else:
								self.cbWifi1.setCurrentIndex(3)
						QMessageBox.warning(self, "Warning", "This AP is already associated with the other WiFi interface.")
				else:
						# is uni/n-casting
						if self.wifi_status_1.text()!="N/A":
								#leaving an AP, send message
								self.send_bicast_msg()
								self.dissociate.wifi(self.wifi1)
						self.associate_wifi(self.wifi1, ap);
						if self.activeIF == "N/A" or self.wifi_status_2.text()=="N/A":
								self.change_active_slave(self.wifi1)

		@pyqtSignature("QString")
		def on_cbWifi2_currentIndexChanged(self, ap):
				if self.startNcast == 0:
						if not self.is_unicast_setting():
								self.cbWifi2.setCurrentIndex(3)
								QMessageBox.warning(self, "Warning", "Please start from Uni-casting.")
				elif ap == self.wifi_status_1.text():
						current_ap = self.wifi_status_2.text();
						if current_ap == self.ap1:
								self.cbWifi2.setCurrentIndex(0)
						elif current_ap == self.ap2:
								self.cbWifi2.setCurrentIndex(1)
						elif current_ap == self.ap3:
								self.cbWifi2.setCurrentIndex(2)
						else:
								self.cbWifi2.setCurrentIndex(3)
						QMessageBox.warning(self, "Warning", "This AP is already associated with the other WiFi interface.")
				else:
						# is uni/n-casting
						if self.wifi_status_2.text()!="N/A":
								self.send_bicast_msg()
								self.dissociate.wifi(self.wifi2)
						self.associate_wifi(self.wifi2, ap);
						if self.activeIF == "N/A" or self.wifi_status_2.text()=="N/A":
								self.change_active_slave(self.wifi2)

		@pyqtSignature('')
		def on_ButtonFlush_clicked(self):
				self.flush_bicast_state();

		@pyqtSignature('')
		def on_ButtonStop_clicked(self):		  
				self.startNcast = 0;
				self.OutputText.insertPlainText("Stop clicked\n")
				if self.auto_pid != 0:
					os.popen("kill -9 "+str(self.auto_pid))
					self.auto_pid =0;
				self.ButtonStop.setEnabled(False)
				self.ButtonStart.setEnabled(True)  

		
		@pyqtSignature('')
		def on_ButtonStart_clicked(self):
				self.startNcast = 1;
				self.ButtonStop.setEnabled(True)
				self.ButtonStart.setEnabled(False)
				self.OutputText.insertPlainText("Start clicked\n")
				if self.cbMode.currentText() == "Auto":
						self.OutputText.insertPlainText("Auto Mode\n")
						if self.wimax_enable:
								self.demo_auto_with_wimax()
						else:
								thread.start_new_thread(self.demo_auto_without_wimax())
								#self.demo_auto_without_wimax()
				else:
						self.OutputText.insertPlainText("Manual Mode\n")
						self.demo_manual();

			
		@pyqtSignature('')
		def on_ButtonSet_clicked(self):
				self.ap1 = self.editAP1.text()
				self.ap2 = self.editAP2.text()
				self.ap3 = self.editAP3.text()
				#comboBox Wifi1
				self.cbWifi1.setItemText(0, QApplication.translate("MainWindow", self.ap1, None, QApplication.UnicodeUTF8))
				self.cbWifi1.setItemText(1, QApplication.translate("MainWindow", self.ap2, None, QApplication.UnicodeUTF8))				
				self.cbWifi1.setItemText(2, QApplication.translate("MainWindow", self.ap3, None, QApplication.UnicodeUTF8))
				self.cbWifi1.setItemText(3, QApplication.translate("MainWindow", "N/A", None, QApplication.UnicodeUTF8))
				#comboBox Wifi2
				self.cbWifi2.setItemText(0, QApplication.translate("MainWindow", self.ap1, None, QApplication.UnicodeUTF8))
				self.cbWifi2.setItemText(1, QApplication.translate("MainWindow", self.ap2, None, QApplication.UnicodeUTF8))
				self.cbWifi2.setItemText(2, QApplication.translate("MainWindow", self.ap3, None, QApplication.UnicodeUTF8))
				self.cbWifi2.setItemText(3, QApplication.translate("MainWindow", "N/A", None, QApplication.UnicodeUTF8))
				#set Interface#1
				self.label_control_wifi1.setText(QApplication.translate("MainWindow", self.wifi1, None, QApplication.UnicodeUTF8))
				self.label_wifi_status_1.setText(QApplication.translate("MainWindow", self.wifi1, None, QApplication.UnicodeUTF8))
				#set Interface#2
				self.label_control_wifi2.setText(QApplication.translate("MainWindow", self.wifi2, None, QApplication.UnicodeUTF8))
				self.label_wifi_status_2.setText(QApplication.translate("MainWindow", self.wifi2, None, QApplication.UnicodeUTF8))		
		
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
						#msg = str(stdout.read())
						#if msg != "":
					    #		self.OutputText.insertPlainText("Output: " + msg +"\n")
						#if stderr is not empty
						#errmsg = str(stderr.read())
						#if errmsg != "":
						#		self.OutputText.insertPlainText("Error: " + errmsg + "\n")
				except OSError, e:
						if e.errno == 13: #permission error
								self.OutputText.insertPlainText("Permission problem with \""+cmd+"\"\n")
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
				self.activeIF = new_active_slave
		
		def signal_quit_to_nox(self):
				## TODO: Modify bicast_noxmsg.py so that it's parameterized with GUI's
				## input
				pass
		
		def flush_bicast_state(self):
				self.send_bicast_msg();
				self.send_bicast_msg();
				if self.wimax_enable:
						self.send_bicast_msg();


		def send_bicast_msg(self, hostmac=int("0x001cf0ed985a", 16), noxhost="10.79.1.105", noxport=2603):
				# Check if there is an active_slave working
				if self.activeIF == "N/A":
						if self.wifi_status_1.text() != "N/A":
								self.change_active_slave(self.wifi1)
						elif self.wifi_status_2.text() != "N/A":
								 self.change_active_slave(self.wifi2)
						else:
								#no associated wifi, can't send
								self.OutputText.insertPlainText("There is no active interface for sending bicast msg.")
								return

				# Change "00:1c:f0:ed:98:5a" to "0x001cf0ed985a", then change to integer in Hex
				mac_addr_str = "0x"+self.bonding_mac_address.replace(":","")
				hostmac = int(str(mac_addr_str), 16)
				noxhost = self.gateway
				self.OutputText.insertPlainText("Sending Bicast Message:  ")
				self.OutputText.insertPlainText("Bicast Host : "+str(hostmac))
				self.OutputText.insertPlainText("NOX Host : "+noxhost)
				self.OutputText.insertPlainText("NOX Port : "+str(noxport) + "\n")
				
				sock = noxmsg.NOXChannel(noxhost, noxport);
				noxmsgtype = int("0x12",16);
				try:
						sock.send(noxmsgtype, struct.pack("Q",noxmsg.htonll(hostmac)));
				except socket.error, msg:
						self.OutputText.insertPlainText("Socket Error:" + msg + "\n")
						pass
		
			
		def associate_wifi(self, wifiIF, ap):
				# Initialize association and active slave
				#cmd = "iwconfig %s essid %s" % (wifiIF, ap)
				self.exe_os_cmd(self.wifi_associate_cmd(wifiIF, ap))
				time.sleep(self.wifi_association_time/1000000)	
				
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

				if self.activeIF == wifiIF:
						self.activeIF = "N/A"
				self.OutputText.insertPlainText(wifiIF + " is disscociated from AP\n")
		
		def dissociate_devices(self):
				# Dissociate everything in the beginning
				self.dissociate_wifi(self.wifi1)
				self.dissociate_wifi(self.wifi2)
				if self.wimax_enable:
						self.wimax_dissociate()
				self.OutputText.insertPlainText("Dissociated all interfaces. We may start now.\n");
		
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
				#cmd = "ifconfig %s" % (self.bond_name)				
				#self.exe_os_cmd(cmd)
				#cmd = "cat /proc/net/bonding/%s" % (self.bond_name)
				#self.exe_os_cmd(cmd)
				cmd = "route add default gw %s" % (self.gateway)
				self.exe_os_cmd(cmd)
				self.OutputText.insertPlainText("Devices Initialized.\n");
				# In order to clean nox states by sending out bicast msgs, 
				# we associate wifi1 to ap1, then dissociate everything
				#self.associate_wifi(self.wifi1, self.ap1)
				#self.change_active_slave(self.wifi1)
				#self.flush_bicast_state()
				#time.sleep(5)
				self.dissociate_devices()
		
	
		def demo_manual(self):
				self.device_init()
				if self.cbWifi1.currentIndex()!=3:
						#Start from wifi1
						self.associate_wifi(self.wifi1, self.cbWifi1.currentText())
						self.change_active_slave(self.wifi1)
				elif self.cbwifi2.currentIndex()!=3:
						#Start from wifi2
						self.associate_wifi(self.wifi2, self.cbWifi2.currentText())
						self.change_active_slave(self.wifi2)
				
		def sleep_between_handover(self, time_s):
				self.OutputText.insertPlainText("Sleep for "+ str(time_s) +" seconds .... \n");
				time.sleep(time_s)
		
		def demo_auto_with_wimax(self):
				self.device_init()
				self.OutputText.insertPlainText("Set up Ready.\n");
				self.OutputText.insertPlainText("Bonding MAC address: "+ self.bonding_mac_address+"\n")
				self.OutputText.insertPlainText("Bonding IP address: " + self.bonding_ip_address+"\n")
				self.OutputText.insertPlainText("Starting Demo .....\n");
				
				# Sequence
				# ap1 -> ap3 -> wimax -> ap2 -> ap1
				self.associate_wifi(self.wifi1, self.ap1)	
				self.change_active_slave(self.wifi1)

				self.sleep_between_handover(30)
				
				# ap1 -> ap3 (start bicast)
				self.associate_wifi(self.wifi2, self.ap3)
				self.sleep_between_handover(30)
				
				# ap3 -> wimax(tricast)
				if self.wimax_enable:
						self.wimax_associate()
						time.sleep(10)
						self.OutputText.insertPlainText("Finished Wimax association.\n")
				
				# wimax -> ap2 (back to bicast)
				self.send_bicast_msg()
				self.dissociate_wifi(self.wifi1)
				
				self.associate_wifi(self.wifi1, self.ap2)
				self.sleep_between_handover(30)
				
				# ap2 -> ap1
				self.send_bicast_msg();
				self.dissociate_wifi(self.wifi2)
				
				self.associate_wifi(self.wifi2, self.ap1)
				self.OutputText.insertPlainText("Switched "+self.wifi2+" from "+self.ap3+" to "+self.ap1+"\n")
				self.sleep_between_handover(60)
				self.OutputText.insertPlainText("Demo End!\n")

		def demo_auto_without_wimax(self):
				self.device_init()
				self.OutputText.insertPlainText("Set up Ready.\n");
				self.OutputText.insertPlainText("Bonding MAC address: "+ self.bonding_mac_address+"\n")
				self.OutputText.insertPlainText("Bonding IP address: " + self.bonding_ip_address+"\n")
				self.OutputText.insertPlainText("Starting Demo .....\n");

				self.auto_pid = os.getpid()
				
				# Sequence
				# (ap1, N/A) -> (ap1, ap2) -> (ap3, ap2) -> (ap3, ap1) -> (ap2, ap1) -> (ap2, ap3) -> (ap1, ap3) -> (ap1, N/A)

				# wifi1: ap1, wifi2:N/A
				self.associate_wifi(self.wifi1, self.ap1)	
				self.change_active_slave(self.wifi1)

				QTimer.singleShot(self.handoverTime, self.demo_auto_without_wimax_s1)
		
		def demo_auto_without_wimax_s1(self):
				# wifi1: ap1, wifi2:ap2
				self.associate_wifi(self.wifi2, self.ap2)
				self.change_active_slave(self.wifi2)
				QTimer.singleShot(self.handoverTime, self.demo_auto_without_wimax_s2)
				# ap1 -> ap3 (start bicast)
				#self.sleep_between_handover(30)
				
		def demo_auto_without_wimax_s2(self):
				# wifi1: ap3, wifi2:ap2
				self.send_bicast_msg()
				self.dissociate_wifi(self.wifi1)
				self.associate_wifi(self.wifi1, self.ap3)
				self.change_active_slave(self.wifi1)
				
				#self.sleep_between_handover(30)
				QTimer.singleShot(self.handoverTime, self.demo_auto_without_wimax_s3)
		
		def demo_auto_without_wimax_s3(self):
				# wifi1: ap3, wifi2:ap1
				self.send_bicast_msg();
				self.dissociate_wifi(self.wifi2)
				self.associate_wifi(self.wifi2, self.ap1)
				self.change_active_slave(self.wifi2)
				#self.sleep_between_handover(30)
				QTimer.singleShot(self.handoverTime, self.demo_auto_without_wimax_s4)

		def demo_auto_without_wimax_s4(self):
				#wifi1: ap2, wifi2:ap1
				self.send_bicast_msg()
				self.dissociate_wifi(self.wifi1)
				self.associate_wifi(self.wifi1, self.ap2)
				self.change_active_slave(self.wifi1)
				#self.sleep_between_handover(30)
				QTimer.singleShot(self.handoverTime, self.demo_auto_without_wimax_s5)

				
		def demo_auto_without_wimax_s5(self):
				#wifi1: ap2, wifi2:ap3
				self.send_bicast_msg()
				self.dissociate_wifi(self.wifi2)
				self.associate_wifi(self.wifi2, self.ap3)
				self.change_active_slave(self.wifi2)
				#self.sleep_between_handover(30)
				QTimer.singleShot(self.handoverTime, self.demo_auto_without_wimax_s6)

		def demo_auto_without_wimax_s6(self):
				#wifi1: ap1, wifi2:ap3
				self.send_bicast_msg()
				self.dissociate_wifi(self.wifi1)
				self.associate_wifi(self.wifi1, self.ap1)
				self.change_active_slave(self.wifi1)
				QTimer.singleShot(self.handoverTime, self.demo_auto_without_wimax_s7)
				#self.sleep_between_handover(30)

		def demo_auto_without_wimax_s7(self):
				#wifi1: ap1, wifi2:N/A
				self.send_bicast_msg()
				self.dissociate_wifi(self.wifi2)
				QTimer.singleShot(self.handoverTime, self.demo_auto_without_wimax_s1)
				#self.change_active_slave(self.wifi1)
				#self.sleep_between_handover(60)
				# Goto step two and repeat


if __name__ == "__main__":
		import sys
		app = QApplication(sys.argv)
		client = OpenRoadClient()
		client.show()
		app.exec_()
