#!/usr/bin/python
#Todo: Auto mode / flush state
from PyQt4.QtCore import * #(QDate, Qt, SIGNAL, pyqtSignature)
from PyQt4.QtGui import * #(QApplication, QDialog, QDialogButtonBox, QWidget, QMainWindow, QComboBox, QPushButton, QMessageBox)
from subprocess import *
import openroad_layout
import sys, os, subprocess
import time
import noxmsg
import socket
import struct
import thread

class OpenRoadClient(QMainWindow, openroad_layout.Ui_MainWindow):
		def __init__(self, parent=None):
				global redlight
				global greenlight
				
				redlight = QPixmap("black-20.png")
				greenlight = QPixmap("red-20.png")

				super(OpenRoadClient, self).__init__(parent)
				self.setupUi(self)
				self.cbMode.setFocus()
				# init: variables
				self.startNcast = 0;
				self.leaving_ap = "N/A";
				# initialize the thread for auto mode
				self.auto_thread = AutoThreadwoWimax(self)
				self.vlc_thread = VLCThread(self)
				# AP MACs
				# for mobicom APs
				#self.ap1_dpid = int("0xdb916ee48", 16);
				#self.ap2_dpid = int("0xdb916efa4", 16);
				#self.ap3_dpid = int("0xdb916efd0", 16);				
				# for backup APs
				self.ap1_dpid = int("0xdb916f04c", 16);
				self.ap2_dpid = int("0xdb916efd4", 16);
				self.ap3_dpid = int("0xdb916f038", 16);				
				# APs
				self.ap1 = self.editAP1.text()
				self.ap2 = self.editAP2.text()
				self.ap3 = self.editAP3.text()
				self.ap_map = {'AP1': self.ap1, 'AP2': self.ap2, 'AP3': self.ap3, 'N/A': "N/A"}
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
				# NOX
				self.noxhost = self.gateway
				self.noxport = 2603 #msg port
				#Control Panel, default is auto mode
				self.cbWifi1.setEnabled(False)
				self.cbWifi2.setEnabled(False)
				#Active Wireless Interface 
				self.activeIF = "N/A"
				#The Stop Button by default is disable, enabled with the start button is pushed
				self.ButtonStop.setEnabled(False)
				self.cbWifi1.setCurrentIndex(0)
				self.cbWifi2.setCurrentIndex(3)
				#Traffic Light
				self.light_ap1.setText("1")
				self.light_ap1.setPixmap(redlight)
				self.light_ap2.setText("2")
				self.light_ap2.setPixmap(redlight)
				self.light_ap3.setText("3")
				self.light_ap3.setPixmap(redlight)

				#Initialize devices:
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
				cmd = "route add default gw %s" % (self.gateway)
				self.exe_os_cmd(cmd)
				self.dissociate_devices()
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
				#self.device_init()
				if mode == "Auto":
						self.cbWifi1.setEnabled(False)
						self.cbWifi2.setEnabled(False)
						
				else:				
						self.OutputText.insertPlainText("Changed to Manual Mode. \n")
						self.cbWifi1.setEnabled(True)						
						self.cbWifi1.setCurrentIndex(0)
						self.cbWifi2.setEnabled(True)
						# The second wifi by default set as none
						self.cbWifi2.setCurrentIndex(3)
				self.vlc_thread.stop();
				self.auto_thread.stop();
				self.startNcast = 0;
				self.ButtonStop.setEnabled(False)
				self.ButtonStart.setEnabled(True)
			
		
		def is_unicast_setting(self):
				if self.cbWifi1.currentIndex() == 3 and self.cbWifi2.currentIndex() == 3:
						return False;
				if self.cbWifi1.currentIndex() != 3 and self.cbWifi2.currentIndex() != 3:
						return False;
				else:
						return True

		def preserve_origin_index(self, origin_ap, wifiIF):
				if wifiIF == self.wifi1:
						if origin_ap == self.ap1:
								self.cbWifi1.setCurrentIndex(0)
						elif origin_ap == self.ap2:
								self.cbWifi1.setCurrentIndex(1)
						elif origin_ap == self.ap3:
								self.cbWifi1.setCurrentIndex(2)
						else:
								self.cbWifi1.setCurrentIndex(3)
				elif wifiIF == self.wifi2:
						if origin_ap == self.ap1:
								self.cbWifi2.setCurrentIndex(0)
						elif origin_ap == self.ap2:
								self.cbWifi2.setCurrentIndex(1)
						elif origin_ap == self.ap3:
								self.cbWifi2.setCurrentIndex(2)
						else:
								self.cbWifi2.setCurrentIndex(3)
		
		def enable_cbWifi(self):
				self.cbWifi1.setEnabled(True)
				self.cbWifi2.setEnabled(True)
		
		@pyqtSignature("QString")
		def on_cbWifi1_currentIndexChanged(self, ap_):
				ap = self.ap_map[str(ap_)]
				if self.cbMode.currentText() == "Auto":
						return
				#elif self.startNcast == 0:
				#		if not self.is_unicast_setting():
				#				self.cbWifi1.setCurrentIndex(3)
				#				QMessageBox.warning(self, "Warning", "Please start from Uni-casting.")
				elif ap == self.wifi_status_1.text():
						return
				elif ap == self.wifi_status_2.text():
						#select sth equal to wifi2
						if ap == "N/A":
								QMessageBox.warning(self, "Warning", "There must always be one AP associated.")
						else:
								QMessageBox.warning(self, "Warning", "This AP is already associated with the other WiFi interface.")
						#recover the previous setting
						current_ap = self.wifi_status_1.text();
						self.preserve_origin_index(current_ap, self.wifi1)
						return
				elif self.startNcast == 1 :
						# is uni/n-casting
						origin_ap = self.wifi_status_1.text();
						if ap == "N/A" and self.wifi_status_2.text() == "N/A":
							self.preserve_origin_index(origin_ap, self.wifi1)
							QMessageBox.warning(self, "Warning", "There must always be one AP associated.")
							return
						
						self.leaving_ap = origin_ap;
						self.cbWifi1.setEnabled(False)
						self.cbWifi2.setEnabled(False)

						if origin_ap != "N/A":
							self.leave_currentAP();							
						
						if ap == "N/A":
							self.dissociate_wifi(self.wifi1)
						else:
							self.associate_wifi(self.wifi1, ap)
							self.change_active_slave(self.wifi1)
						QTimer.singleShot(2000, self.enable_cbWifi);


		@pyqtSignature("QString")
		def on_cbWifi2_currentIndexChanged(self, ap_):
				ap = self.ap_map[str(ap_)]
				if self.cbMode.currentText() == "Auto":
						return
				#elif self.startNcast == 0:
				#		if not self.is_unicast_setting():
				#				self.cbWifi2.setCurrentIndex(3)
				#				QMessageBox.warning(self, "Warning", "Please start from Uni-casting.")
				elif ap == self.wifi_status_2.text():
						return
				elif ap == self.wifi_status_1.text():
						if ap == "N/A":
								QMessageBox.warning(self, "Warning", "There must always be one AP associated.")
						else:
								QMessageBox.warning(self, "Warning", "This AP is already associated with the other WiFi interface.")
						#Recover to previous setting
						current_ap = self.wifi_status_2.text();
						self.preserve_origin_index(current_ap, self.wifi2)
				elif self.startNcast == 1:
						# is uni/n-casting
						origin_ap = self.wifi_status_2.text();
						if ap == "N/A" and self.wifi_status_1.text() == "N/A":
							self.preserve_origin_index(origin_ap, self.wifi2)
							QMessageBox.warning(self, "Warning", "There must always be one AP associated.")
							return
						
						self.leaving_ap = origin_ap;
						self.cbWifi1.setEnabled(False)
						self.cbWifi2.setEnabled(False)

						if origin_ap != "N/A":
							# since origin_ap is not N/A, it is leaving an AP
							self.leave_currentAP();							
						
						if ap == "N/A":
							self.dissociate_wifi(self.wifi2)
						else:
							self.associate_wifi(self.wifi2, ap)
							self.change_active_slave(self.wifi2)

						QTimer.singleShot(2000, self.enable_cbWifi);

					#if 0:
					#	current_ap = self.wifi_status_2.text();
					#	self.leaving_ap = current_ap;
					#	self.cbWifi1.setEnabled(False)
					#	self.cbWifi2.setEnabled(False)
					#	if ap == "N/A":
					#			#wifi2 is dissociated 
					#			self.dissociate_wifi(self.wifi2)
					#			if self.activeIF == "N/A" and self.wifi_status_1.text()!= "N/A":
					#					self.change_active_slave(self.wifi1)
					#			else:
					#					QMessageBox.warning(self, "Warning", "There must always be one AP associated.")
					#					return
					#	else:
					#			self.associate_wifi(self.wifi2, ap)
					#			if self.activeIF == "N/A":
					#					self.change_active_slave(self.wifi2)
					#	if current_ap != "N/A":
					#			QTimer.singleShot(1000, self.leave_currentAP);
					#	else:
					#			self.cbWifi1.setEnabled(True)
					#			self.cbWifi2.setEnabled(True)

		@pyqtSignature('bool')
		def on_actionDetail_toggled(self, checked):
				if checked == True:
						self.resize(433, 696)
				else:
						self.resize(433, 310)


		@pyqtSignature('')
		def on_ButtonVideo_clicked(self):
				self.video_start(self)

		def video_start(self):
				#self.exe_os_cmd("killall vlc");			
				#cvlc_cmd = "cvlc --repeat rtsp://%s:8080/test.sdp &" % self.gateway
				#cmd = "su demo -c \"%s\"" % cvlc_cmd
				#subprocess.call(cmd, shell=True)
				#self.exe_os_cmd(cmd)
				self.vlc_thread.start();
		def video_stop(self):
				#self.exe_os_cmd("killall vlc");			
				self.vlc_thread.stop();

		@pyqtSignature('')
		def on_ButtonFlush_clicked(self):
				self.flush_bicast_state();
		
		@pyqtSignature('')
		def on_ButtonStop_clicked(self):		  
				self.auto_thread.stop()
				self.startNcast = 0;
				self.OutputText.insertPlainText("Stop clicked\n")
				self.ButtonStop.setEnabled(False)
				if self.cbMode.currentText() == "Auto": #and self.auto_thread.timer.isActive():
						QTimer.singleShot(3000, self.enable_ButtonStart)
				else:		
						self.ButtonStart.setEnabled(True)

		@pyqtSignature('')
		def enable_ButtonStart(self):
				self.ButtonStart.setEnabled(True)
		@pyqtSignature('')
		def on_ButtonStart_clicked(self):
				self.OutputText.insertPlainText("Start clicked\n")
				if self.cbMode.currentText() == "Auto Mode" or self.cbMode.currentText() == "Auto":
						self.cbWifi1.setCurrentIndex(3)
						self.cbWifi2.setCurrentIndex(3)
						self.OutputText.insertPlainText("Auto Mode\n")
						if self.wimax_enable:
								self.demo_auto_with_wimax()
						else:
								#self.demo_auto_without_wimax()
								self.auto_thread.start()
								self.startNcast = 1;
								self.ButtonStop.setEnabled(True)
								self.ButtonStart.setEnabled(False)
				else:
						self.OutputText.insertPlainText("Manual Mode\n")
						self.dissociate_devices()
						QTimer.singleShot(500, self.device_init)
						self.flushed = 0
						QTimer.singleShot(3500, self.demo_manual)

			
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
				#set label for traffic light
				self.label_light_ap1.setText(QApplication.translate("MainWindow", self.ap1, None, QApplication.UnicodeUTF8))
				self.label_light_ap2.setText(QApplication.translate("MainWindow", self.ap2, None, QApplication.UnicodeUTF8))
				self.label_light_ap3.setText(QApplication.translate("MainWindow", self.ap3, None, QApplication.UnicodeUTF8))
		
		#currently a useless function :p
		def updateUi(self):
				a=1
				#self.OutputText.setPlainText(self.bond_name)
		
		# os.popen is out-dated, but I haven't find out how to use subprocess
		def exe_os_cmd(self, cmd):
				#p = subprocess.Popen( cmd ,stdout=subprocess.PIPE,stderr=subprocess.PIPE) 
				#output, errors = p.communicate()
				#cmd = "sudo %s" % orig_cmd;
				self.OutputText.insertPlainText("Executing: "+cmd+"\n")
				print cmd
				try:
						#stdin, stdout, stderr = os.popen3(cmd)
						subprocess.call(cmd, shell=True);
						#print stderr.read()
						#add expr for if stdout is not empty
						#msg = str(stdout.read())
						#if msg != "":
					    #		self.OutputText.insertPlainText("Output: " + msg +"\n")
						#if stderr is not empty
						#errmsg = str(stderr.read())
						#if errmsg != "":
						#		self.OutputText.insertPlainText("Error: " + errmsg + "\n")
				except OSError, e:
						print e
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
				#cmd = "ifenslave -c %s %s" % (self.bond_name, new_active_slave) 
				self.exe_os_cmd(cmd)
				self.activeIF = new_active_slave
		
		def signal_quit_to_nox(self):
				## TODO: Modify bicast_noxmsg.py so that it's parameterized with GUI's
				## input
				pass
		
		def flush_bicast_state(self):
				#self.send_bicast_msg();
				#self.send_bicast_msg();
				#if self.wimax_enable:
				#		self.send_bicast_msg();
				self.send_bicast_leave_msg(self.ap1_dpid)
				self.send_bicast_leave_msg(self.ap2_dpid)
				self.send_bicast_leave_msg(self.ap3_dpid)
				QTimer.singleShot(1300, self.dissociate_devices)
		
		def leave_currentAP(self):
				current_ap = self.leaving_ap
				print "notifying nox the host is leaving %s" % current_ap
				try:
					if current_ap == self.ap1:
						self.send_bicast_leave_msg(self.ap1_dpid)
					elif current_ap == self.ap2:
						self.send_bicast_leave_msg(self.ap2_dpid)
					elif current_ap == self.ap3:
						self.send_bicast_leave_msg(self.ap3_dpid)						
				except socket.error, msg:
					print msg
					pass
				#finally:
				#	self.cbWifi1.setEnabled(True)
				#	self.cbWifi2.setEnabled(True)

		def leave_AP(self, ap):				
				print "notifying nox the host is leaving %s" % ap
				try:
					if ap == self.ap1:
						self.send_bicast_leave_msg(self.ap1_dpid)
					elif ap == self.ap2:
						self.send_bicast_leave_msg(self.ap2_dpid)
					elif ap == self.ap3:
						self.send_bicast_leave_msg(self.ap3_dpid)						
				except socket.error, msg:
					print msg
					pass

		def send_bicast_leave_msg(self, apdpid): #, apport=0, noxhost=self.gateway, noxport=2603):
				if self.activeIF == "N/A":
						if self.wifi_status_1.text() != "N/A":
								self.change_active_slave(self.wifi1)
						elif self.wifi_status_2.text() != "N/A":
								self.change_active_slave(self.wifi2)
						else:
								#no associated wifi, can't send
								self.OutputText.insertPlainText("There is no active interface for sending bicast msg.")
								return
				noxhost = self.noxhost
				noxport = self.noxport
				apport = 0
				mac_addr_str = "0x"+self.bonding_mac_address.replace(":","")
				hostmac = int(str(mac_addr_str), 16)
				sock = noxmsg.NOXChannel(noxhost, noxport);
				noxmsgtype = int("0x13",16);
				sock.send(noxmsgtype, struct.pack(">QQH",hostmac, apdpid, apport));


		def send_bicast_msg(self):
				noxhost = self.noxhost
				noxport = self.noxport
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
				#noxhost = self.gateway
				self.OutputText.insertPlainText("Sending Bicast Message:  ")
				self.OutputText.insertPlainText("Bicast Host : "+str(hostmac))
				self.OutputText.insertPlainText("NOX Host : "+noxhost)
				self.OutputText.insertPlainText("NOX Port : "+str(noxport) + "\n")
				
				sock = noxmsg.NOXChannel(noxhost, noxport);
				noxmsgtype = int("0x12",16);
				try:
						sock.send(noxmsgtype, struct.pack("Q",noxmsg.htonll(hostmac)));
				except socket.error, msg:
						print msg
						self.OutputText.insertPlainText("Socket Error:" + msg + "\n")
						pass
		
			
		def associate_wifi(self, wifiIF, ap):
				# Initialize association and active slave
				#cmd = "iwconfig %s essid %s" % (wifiIF, ap)
				if ap == "N/A":
						self.dissociate_wifi(wifiIF)
				else:
						self.exe_os_cmd(self.wifi_associate_cmd(wifiIF, ap))
				#time.sleep(self.wifi_association_time/1000000)

				if ap == self.ap1:
						self.light_ap1.setPixmap(greenlight)
				elif ap == self.ap2:
						self.light_ap2.setPixmap(greenlight)
				elif ap == self.ap3:
						self.light_ap3.setPixmap(greenlight)

				if wifiIF == self.wifi1:
						prev_ap = self.wifi_status_1.text();
						self.wifi_status_1.setText(ap)
						if self.cbMode.currentText() == "Auto":
								if ap == self.ap1:
										self.cbWifi1.setCurrentIndex(0)
								elif ap == self.ap2:
										self.cbWifi1.setCurrentIndex(1)
								elif ap == self.ap3:
										self.cbWifi1.setCurrentIndex(2)
								else:
										self.cbWifi1.setCurrentIndex(3)
				elif wifiIF == self.wifi2:
						prev_ap = self.wifi_status_2.text();
						self.wifi_status_2.setText(ap)
						if self.cbMode.currentText() == "Auto":
								if ap == self.ap1:
										self.cbWifi2.setCurrentIndex(0)
								elif ap == self.ap2:
										self.cbWifi2.setCurrentIndex(1)
								elif ap == self.ap3:
										self.cbWifi2.setCurrentIndex(2)
								else:
										self.cbWifi2.setCurrentIndex(3)
				if prev_ap != "N/A":
						if prev_ap == self.ap1:
								self.light_ap1.setPixmap(redlight)
						elif prev_ap == self.ap2:
								self.light_ap2.setPixmap(redlight)
						elif prev_ap == self.ap3:
								self.light_ap3.setPixmap(redlight)

				self.OutputText.insertPlainText(wifiIF + " is asscociated with " +ap +"\n")
				
		def dissociate_wifi(self, wifiIF):
				self.exe_os_cmd(self.wifi_dissociate_cmd(wifiIF))
				if wifiIF == self.wifi1:
						prev_ap = self.wifi_status_1.text();
						self.wifi_status_1.setText("N/A")
						if self.cbMode.currentText() == "Auto":
								self.cbWifi1.setCurrentIndex(3)
				elif wifiIF == self.wifi2:
						prev_ap = self.wifi_status_2.text();
						self.wifi_status_2.setText("N/A")
						if self.cbMode.currentText() == "Auto":
								self.cbWifi2.setCurrentIndex(3)

				if prev_ap != "N/A":
						if prev_ap == self.ap1:
								self.light_ap1.setPixmap(redlight)
						elif prev_ap == self.ap2:
								self.light_ap2.setPixmap(redlight)
						elif prev_ap == self.ap3:
								self.light_ap3.setPixmap(redlight)

				if self.activeIF == wifiIF:
						self.activeIF = "N/A"
				self.OutputText.insertPlainText(wifiIF + " is disscociated from AP\n")
		
		def dissociate_devices(self):
				# Dissociate everything in the beginning
				self.dissociate_wifi(self.wifi1)
				self.dissociate_wifi(self.wifi2)
				self.light_ap1.setPixmap(redlight)
				self.light_ap2.setPixmap(redlight)
				self.light_ap3.setPixmap(redlight)
				if self.wimax_enable:
						self.wimax_dissociate()
				self.flushed = 1
				self.OutputText.insertPlainText("Dissociated all interfaces. We may start now.\n");
		
		def device_init(self):
				# In order to clean nox states by sending out bicast msgs, 
				# we associate wifi1 to ap1, then dissociate everything
				self.cbWifi1.setEnabled(False)
				self.cbWifi2.setEnabled(False)

				self.associate_wifi(self.wifi1, self.ap1)
				self.change_active_slave(self.wifi1)
				self.OutputText.insertPlainText("Devices Initialized.\n");
				self.flushed = 0;
				#inside flush_bicast_state, devices will be dissociated afterwards
				QTimer.singleShot(1500, self.flush_bicast_state)
				#time.sleep(5)
		
	
		def demo_manual(self):
			if self.flushed == 1:
				self.cbWifi1.setEnabled(True)
				self.cbWifi2.setEnabled(True)
				if self.cbWifi1.currentIndex()!=3:
						#Start from wifi1
						self.associate_wifi(self.wifi1, self.ap_map[str(self.cbWifi1.currentText())])
						self.change_active_slave(self.wifi1)
						if self.cbWifi2.currentIndex()!=3:
								self.associate_wifi(self.wifi2, self.ap_map[str(self.cbWifi2.currentText())])
				elif self.cbWifi2.currentIndex()!=3:
						#Start from wifi2, wifi1 = "N/A"
						self.associate_wifi(self.wifi2, self.ap_map[str(self.cbWifi2.currentText())])
						self.change_active_slave(self.wifi2)
				self.startNcast = 1;
				self.ButtonStop.setEnabled(True)
				self.ButtonStart.setEnabled(False)
				self.video_start();
			else:
				QTimer.singleShot(1000, self.demo_manual)
				
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

class VLCThread(QThread):
		@pyqtSignature('OpenRoadClient')
		def __init__(self, orc, parent=None):
				QThread.__init__(self)
				self.orc = orc
				self.isRunning = False
		def start(self):
				self.isRunning = True
				self.run()
		def stop(self):
				self.isRunning = False
				self.orc.exe_os_cmd("killall vlc");			
		def run(self):
				self.orc.exe_os_cmd("killall vlc");			
				cvlc_cmd = "cvlc --repeat -f --video-x 1024 rtsp://%s:8080/test.sdp &" % self.orc.gateway
				cmd = "su demo -c \"%s\"" % cvlc_cmd
				self.orc.exe_os_cmd(cmd)

class AutoThreadwoWimax(QThread):
		@pyqtSignature('OpenRoadClient')
		def __init__(self, orc, parent=None):
				QThread.__init__(self)
				self.orc = orc
				self.isRunning = False
				self.handoverTime = 8000
				self.timer = QTimer(self)
		def start(self):
				if self.timer.isActive():
						self.timer.stop()
						self.timer = QTimer(self)
				self.run()
		def stop(self):
				self.isRunning = False
				self.timer.stop()
				self.orc.video_stop()

		def run(self):
				self.orc.dissociate_devices()
				self.timer.singleShot(500, self.orc.device_init)
				self.orc.OutputText.insertPlainText("Set up Ready.\n");
				self.orc.OutputText.insertPlainText("Bonding MAC address: "+ self.orc.bonding_mac_address+"\n")
				self.orc.OutputText.insertPlainText("Bonding IP address: " + self.orc.bonding_ip_address+"\n")
				self.orc.OutputText.insertPlainText("Starting Demo .....in 3 seconds\n");
				
				#QTimer.singleShot(3500, self.demo_auto_without_wimax_s0)
				self.timer.singleShot(3500, self.demo_auto_without_wimax_s0)
				# Sequence
				# previous: (ap1, N/A) -> (ap1, ap2) -> (ap3, ap2) -> (ap3, ap1) -> (N/A, ap1) -> (ap2, ap1) -> (ap2, ap3) -> (ap1, ap3) -> (ap1, N/A)
				# (ap1, N/A) -> (ap1, ap2) -> (ap3, ap2) -> (ap3, N/A) -> (ap3, ap1) -> (ap2, ap1) -> (ap2, N/A) -> (ap2, ap3) -> (ap1, ap3) -> (ap1, N/A)
		def demo_auto_without_wimax_s0(self):
				self.isRunning = True
				# wifi1: ap1, wifi2:N/A
				self.orc.associate_wifi(self.orc.wifi1, self.orc.ap1)	
				self.orc.change_active_slave(self.orc.wifi1)
				self.orc.video_start()
				#time.sleep(30)
				if self.isRunning:
					#QTimer.singleShot(self.handoverTime, self.demo_auto_without_wimax_s1)
					self.timer.singleShot(self.handoverTime, self.demo_auto_without_wimax_s1)
		
		def demo_auto_without_wimax_s1(self):
				if self.isRunning:
					# wifi1: ap1, wifi2:ap2
					self.orc.associate_wifi(self.orc.wifi2, self.orc.ap2)
					self.orc.change_active_slave(self.orc.wifi2)
				#time.sleep(30)
				if self.isRunning:
					#QTimer.singleShot(self.handoverTime, self.demo_auto_without_wimax_s2)
					self.timer.singleShot(self.handoverTime, self.demo_auto_without_wimax_s2)
				# ap1 -> ap3 (start bicast)
				
		def demo_auto_without_wimax_s2(self):
				if self.isRunning:
					# wifi1: ap3, wifi2:ap2
					#self.orc.send_bicast_msg()
					self.orc.leave_AP(self.orc.ap1)
					#self.orc.dissociate_wifi(self.orc.wifi1)
					self.orc.associate_wifi(self.orc.wifi1, self.orc.ap3)
					self.orc.change_active_slave(self.orc.wifi1)
				
				#time.sleep(30)
				if self.isRunning:
					#QTimer.singleShot(self.handoverTime, self.demo_auto_without_wimax_s3)
					self.timer.singleShot(self.handoverTime, self.demo_auto_without_wimax_s3)
	
		def demo_auto_without_wimax_s3(self):
				if self.isRunning:
					# wifi1: ap3, wifi2:N/A
					#self.orc.send_bicast_msg();
					self.orc.leave_AP(self.orc.ap2)
					self.orc.dissociate_wifi(self.orc.wifi2)
				if self.isRunning:
					#QTimer.singleShot(self.handoverTime, self.demo_auto_without_wimax_s4)
					self.timer.singleShot(self.handoverTime, self.demo_auto_without_wimax_s4)
	
		def demo_auto_without_wimax_s4(self):
				if self.isRunning:
					# wifi1: ap3, wifi2:ap1
					self.orc.associate_wifi(self.orc.wifi2, self.orc.ap1)
					self.orc.change_active_slave(self.orc.wifi2)
				#time.sleep(30)
				if self.isRunning:
					#QTimer.singleShot(self.handoverTime, self.demo_auto_without_wimax_s5)
					self.timer.singleShot(self.handoverTime, self.demo_auto_without_wimax_s5)
		
		# (ap1, N/A) -> (ap1, ap2) -> (ap3, ap2) -> (ap3, N/A) -> (ap3, ap1) -> (ap2, ap1) -> (ap2, N/A) -> (ap2, ap3) -> (ap1, ap3) -> (ap1, N/A)
		def demo_auto_without_wimax_s5(self):
				if self.isRunning:
					# wifi1: ap2, wifi2:ap1
					#self.orc.send_bicast_msg();
					self.orc.leave_AP(self.orc.ap3)
					#self.orc.dissociate_wifi(self.orc.wifi1)
					self.orc.associate_wifi(self.orc.wifi1, self.orc.ap2)
					self.orc.change_active_slave(self.orc.wifi1)
				if self.isRunning:
					#QTimer.singleShot(self.handoverTime, self.demo_auto_without_wimax_s6)
					self.timer.singleShot(self.handoverTime, self.demo_auto_without_wimax_s6)
		

		def demo_auto_without_wimax_s6(self):
				if self.isRunning:
					#wifi1: ap2, wifi2:N/A
					#self.orc.send_bicast_msg();
					self.orc.leave_AP(self.orc.ap1)
					self.orc.dissociate_wifi(self.orc.wifi2)
					#self.orc.associate_wifi(self.orc.wifi1, self.orc.ap2)
					#self.orc.change_active_slave(self.orc.wifi1)

				#time.sleep(30)
				if self.isRunning:
					#QTimer.singleShot(self.handoverTime, self.demo_auto_without_wimax_s7)
					self.timer.singleShot(self.handoverTime, self.demo_auto_without_wimax_s7)

		def demo_auto_without_wimax_s7(self):
				if self.isRunning:
					#wifi1: ap2, wifi2:ap3
					#self.orc.send_bicast_msg()
					#self.orc.dissociate_wifi(self.orc.wifi2)
					self.orc.associate_wifi(self.orc.wifi2, self.orc.ap3)
					self.orc.change_active_slave(self.orc.wifi2)
				#time.sleep(30)
				if self.isRunning:
					#QTimer.singleShot(self.handoverTime, self.demo_auto_without_wimax_s8)
					self.timer.singleShot(self.handoverTime, self.demo_auto_without_wimax_s8)

		def demo_auto_without_wimax_s8(self):
				if self.isRunning:
					#wifi1: ap1, wifi2:ap3
					#self.orc.send_bicast_msg()
					self.orc.leave_AP(self.orc.ap2)
					#self.orc.dissociate_wifi(self.orc.wifi1)
					self.orc.associate_wifi(self.orc.wifi1, self.orc.ap1)
					self.orc.change_active_slave(self.orc.wifi1)
				#time.sleep(30)
				if self.isRunning:
					#QTimer.singleShot(self.handoverTime, self.demo_auto_without_wimax_s9)
					self.timer.singleShot(self.handoverTime, self.demo_auto_without_wimax_s9)

		def demo_auto_without_wimax_s9(self):
				if self.isRunning:
					#wifi1: ap1, wifi2:N/A
					#self.orc.send_bicast_msg()
					self.orc.leave_AP(self.orc.ap3)
					self.orc.dissociate_wifi(self.orc.wifi2)
				#time.sleep(30)
				if self.isRunning:
					#QTimer.singleShot(self.handoverTime, self.demo_auto_without_wimax_s1)
					self.timer.singleShot(self.handoverTime, self.demo_auto_without_wimax_s1)
				#self.change_active_slave(self.wifi1)
				# Goto step two and repeat


if __name__ == "__main__":
		import sys
		app = QApplication(sys.argv)
		client = OpenRoadClient()
		client.resize(433, 310)
		client.show()
		app.exec_()
