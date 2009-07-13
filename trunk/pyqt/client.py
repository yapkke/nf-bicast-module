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
      try:
      	retcode = call(cmd)
      	if retcode < 0:
      		print >>sys.stderr, "Child was terminated by signal", -retcode
      	else:
      		print >>sys.stderr, "Child returned", retcode
      except OSError, e:
      	print >>sys.stderr, "Execution failed:", e

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
        os.system("./wimax-bicast-up.sh")

    def wimax_dissociate(self):
        os.system("./wimax-bicast-down.sh")

    def change_active_slave(self, new_active_slave):
        cmd = "./change-active-slave %s %s" % (self.bond_name, new_active_slave) 

    def signal_quit_to_nox(self):
        ## TODO: Modify bicast_noxmsg.py so that it's parameterized with GUI's
        ## input
        pass


    def demo_init(self):
	    cmd = "ifconfig %s down" % (self.wifi1)
	    #self.OutputText.insertPlainText(os.popen(cmd).read());
	    os.system(cmd)

    def demo_run(self):
	    self.demo_init();


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    form = OpenRoadClient()
    form.show()
    app.exec_()
