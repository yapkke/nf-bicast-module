# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './openroad.ui'
#
# Created: Tue Sep 15 00:24:10 2009
#      by: PyQt4 UI code generator 4.4.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(433, 696)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.settingTab = QtGui.QTabWidget(self.centralwidget)
        self.settingTab.setGeometry(QtCore.QRect(15, 310, 401, 161))
        self.settingTab.setTabPosition(QtGui.QTabWidget.North)
        self.settingTab.setTabShape(QtGui.QTabWidget.Triangular)
        self.settingTab.setObjectName("settingTab")
        self.tabAP = QtGui.QWidget()
        self.tabAP.setObjectName("tabAP")
        self.editAP1 = QtGui.QLineEdit(self.tabAP)
        self.editAP1.setGeometry(QtCore.QRect(70, 20, 113, 22))
        self.editAP1.setObjectName("editAP1")
        self.label_ap1 = QtGui.QLabel(self.tabAP)
        self.label_ap1.setGeometry(QtCore.QRect(30, 23, 31, 17))
        self.label_ap1.setObjectName("label_ap1")
        self.label_ap2 = QtGui.QLabel(self.tabAP)
        self.label_ap2.setGeometry(QtCore.QRect(30, 52, 31, 17))
        self.label_ap2.setObjectName("label_ap2")
        self.editAP2 = QtGui.QLineEdit(self.tabAP)
        self.editAP2.setGeometry(QtCore.QRect(70, 50, 113, 22))
        self.editAP2.setObjectName("editAP2")
        self.label_ap3 = QtGui.QLabel(self.tabAP)
        self.label_ap3.setGeometry(QtCore.QRect(30, 80, 31, 17))
        self.label_ap3.setObjectName("label_ap3")
        self.editAP3 = QtGui.QLineEdit(self.tabAP)
        self.editAP3.setGeometry(QtCore.QRect(70, 79, 113, 22))
        self.editAP3.setObjectName("editAP3")
        self.settingTab.addTab(self.tabAP, "")
        self.tabWiFi = QtGui.QWidget()
        self.tabWiFi.setObjectName("tabWiFi")
        self.label_wifi_if_1 = QtGui.QLabel(self.tabWiFi)
        self.label_wifi_if_1.setGeometry(QtCore.QRect(27, 21, 131, 20))
        self.label_wifi_if_1.setObjectName("label_wifi_if_1")
        self.editWiFiIF1 = QtGui.QLineEdit(self.tabWiFi)
        self.editWiFiIF1.setGeometry(QtCore.QRect(149, 20, 121, 22))
        self.editWiFiIF1.setObjectName("editWiFiIF1")
        self.editWiFiIF2 = QtGui.QLineEdit(self.tabWiFi)
        self.editWiFiIF2.setGeometry(QtCore.QRect(149, 50, 121, 22))
        self.editWiFiIF2.setObjectName("editWiFiIF2")
        self.label_wifi_if_2 = QtGui.QLabel(self.tabWiFi)
        self.label_wifi_if_2.setGeometry(QtCore.QRect(10, 51, 151, 20))
        self.label_wifi_if_2.setObjectName("label_wifi_if_2")
        self.settingTab.addTab(self.tabWiFi, "")
        self.tabBond = QtGui.QWidget()
        self.tabBond.setObjectName("tabBond")
        self.label_bond_ip = QtGui.QLabel(self.tabBond)
        self.label_bond_ip.setGeometry(QtCore.QRect(20, 10, 151, 20))
        self.label_bond_ip.setObjectName("label_bond_ip")
        self.editBondIP = QtGui.QLineEdit(self.tabBond)
        self.editBondIP.setGeometry(QtCore.QRect(180, 10, 121, 22))
        self.editBondIP.setObjectName("editBondIP")
        self.label_bond_mac = QtGui.QLabel(self.tabBond)
        self.label_bond_mac.setGeometry(QtCore.QRect(82, 70, 91, 20))
        self.label_bond_mac.setObjectName("label_bond_mac")
        self.editBondMac = QtGui.QLineEdit(self.tabBond)
        self.editBondMac.setGeometry(QtCore.QRect(180, 70, 121, 22))
        self.editBondMac.setObjectName("editBondMac")
        self.label_bond_if = QtGui.QLabel(self.tabBond)
        self.label_bond_if.setGeometry(QtCore.QRect(69, 100, 101, 20))
        self.label_bond_if.setObjectName("label_bond_if")
        self.editBondMacIF = QtGui.QLineEdit(self.tabBond)
        self.editBondMacIF.setGeometry(QtCore.QRect(180, 100, 121, 22))
        self.editBondMacIF.setObjectName("editBondMacIF")
        self.label_bond_ip_nowimax = QtGui.QLabel(self.tabBond)
        self.label_bond_ip_nowimax.setGeometry(QtCore.QRect(23, 40, 151, 20))
        self.label_bond_ip_nowimax.setObjectName("label_bond_ip_nowimax")
        self.editBondIP_nowimax = QtGui.QLineEdit(self.tabBond)
        self.editBondIP_nowimax.setGeometry(QtCore.QRect(181, 39, 121, 22))
        self.editBondIP_nowimax.setObjectName("editBondIP_nowimax")
        self.settingTab.addTab(self.tabBond, "")
        self.tabWimax = QtGui.QWidget()
        self.tabWimax.setObjectName("tabWimax")
        self.label_wimax_if = QtGui.QLabel(self.tabWimax)
        self.label_wimax_if.setGeometry(QtCore.QRect(20, 12, 131, 20))
        self.label_wimax_if.setObjectName("label_wimax_if")
        self.editWimaxIF = QtGui.QLineEdit(self.tabWimax)
        self.editWimaxIF.setGeometry(QtCore.QRect(20, 30, 113, 22))
        self.editWimaxIF.setObjectName("editWimaxIF")
        self.isUseWiMax = QtGui.QCheckBox(self.tabWimax)
        self.isUseWiMax.setGeometry(QtCore.QRect(20, 70, 101, 21))
        self.isUseWiMax.setChecked(False)
        self.isUseWiMax.setObjectName("isUseWiMax")
        self.settingTab.addTab(self.tabWimax, "")
        self.tabGeneral = QtGui.QWidget()
        self.tabGeneral.setObjectName("tabGeneral")
        self.wifiAssoTimeSpinBox = QtGui.QSpinBox(self.tabGeneral)
        self.wifiAssoTimeSpinBox.setGeometry(QtCore.QRect(20, 30, 91, 21))
        self.wifiAssoTimeSpinBox.setMaximum(100000)
        self.wifiAssoTimeSpinBox.setSingleStep(1000)
        self.wifiAssoTimeSpinBox.setProperty("value", QtCore.QVariant(50000))
        self.wifiAssoTimeSpinBox.setObjectName("wifiAssoTimeSpinBox")
        self.label_WifiAssocTime = QtGui.QLabel(self.tabGeneral)
        self.label_WifiAssocTime.setGeometry(QtCore.QRect(20, 10, 211, 20))
        self.label_WifiAssocTime.setObjectName("label_WifiAssocTime")
        self.label_gw = QtGui.QLabel(self.tabGeneral)
        self.label_gw.setGeometry(QtCore.QRect(20, 50, 61, 20))
        self.label_gw.setObjectName("label_gw")
        self.editGW = QtGui.QLineEdit(self.tabGeneral)
        self.editGW.setGeometry(QtCore.QRect(20, 70, 121, 22))
        self.editGW.setObjectName("editGW")
        self.settingTab.addTab(self.tabGeneral, "")
        self.line_2 = QtGui.QFrame(self.centralwidget)
        self.line_2.setGeometry(QtCore.QRect(-5, 510, 441, 20))
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.label_output = QtGui.QLabel(self.centralwidget)
        self.label_output.setGeometry(QtCore.QRect(165, 520, 111, 30))
        self.label_output.setObjectName("label_output")
        self.label_settings = QtGui.QLabel(self.centralwidget)
        self.label_settings.setGeometry(QtCore.QRect(184, 280, 111, 30))
        self.label_settings.setObjectName("label_settings")
        self.line_3 = QtGui.QFrame(self.centralwidget)
        self.line_3.setGeometry(QtCore.QRect(0, 150, 421, 20))
        self.line_3.setFrameShape(QtGui.QFrame.HLine)
        self.line_3.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.label_wifi_status_1 = QtGui.QLabel(self.centralwidget)
        self.label_wifi_status_1.setGeometry(QtCore.QRect(145, 203, 71, 21))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label_wifi_status_1.setFont(font)
        self.label_wifi_status_1.setScaledContents(False)
        self.label_wifi_status_1.setObjectName("label_wifi_status_1")
        self.label_wifi_status_2 = QtGui.QLabel(self.centralwidget)
        self.label_wifi_status_2.setGeometry(QtCore.QRect(145, 232, 71, 20))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label_wifi_status_2.setFont(font)
        self.label_wifi_status_2.setObjectName("label_wifi_status_2")
        self.label_wimax_status = QtGui.QLabel(self.centralwidget)
        self.label_wimax_status.setGeometry(QtCore.QRect(146, 261, 61, 17))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label_wimax_status.setFont(font)
        self.label_wimax_status.setObjectName("label_wimax_status")
        self.wifi_status_1 = QtGui.QLabel(self.centralwidget)
        self.wifi_status_1.setGeometry(QtCore.QRect(235, 204, 111, 20))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.wifi_status_1.setFont(font)
        self.wifi_status_1.setObjectName("wifi_status_1")
        self.wifi_status_2 = QtGui.QLabel(self.centralwidget)
        self.wifi_status_2.setGeometry(QtCore.QRect(235, 232, 121, 20))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.wifi_status_2.setFont(font)
        self.wifi_status_2.setObjectName("wifi_status_2")
        self.wimax_status = QtGui.QLabel(self.centralwidget)
        self.wimax_status.setGeometry(QtCore.QRect(236, 262, 131, 17))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.wimax_status.setFont(font)
        self.wimax_status.setObjectName("wimax_status")
        self.OutputText = QtGui.QPlainTextEdit(self.centralwidget)
        self.OutputText.setGeometry(QtCore.QRect(15, 550, 401, 101))
        self.OutputText.setTabChangesFocus(True)
        self.OutputText.setReadOnly(True)
        self.OutputText.setCenterOnScroll(True)
        self.OutputText.setObjectName("OutputText")
        self.line_4 = QtGui.QFrame(self.centralwidget)
        self.line_4.setGeometry(QtCore.QRect(-5, 275, 421, 20))
        self.line_4.setFrameShape(QtGui.QFrame.HLine)
        self.line_4.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_4.setObjectName("line_4")
        self.cbMode = QtGui.QComboBox(self.centralwidget)
        self.cbMode.setGeometry(QtCore.QRect(150, 10, 131, 27))
        font = QtGui.QFont()
        font.setFamily("Nice")
        font.setPointSize(14)
        self.cbMode.setFont(font)
        self.cbMode.setObjectName("cbMode")
        self.cbMode.addItem("")
        self.cbMode.addItem("")
        self.label_control_wifi1 = QtGui.QLabel(self.centralwidget)
        self.label_control_wifi1.setGeometry(QtCore.QRect(90, 49, 81, 20))
        font = QtGui.QFont()
        font.setFamily("Rehan")
        font.setPointSize(14)
        self.label_control_wifi1.setFont(font)
        self.label_control_wifi1.setObjectName("label_control_wifi1")
        self.cbWifi1 = QtGui.QComboBox(self.centralwidget)
        self.cbWifi1.setGeometry(QtCore.QRect(60, 70, 111, 27))
        font = QtGui.QFont()
        font.setFamily("Nice")
        font.setPointSize(14)
        self.cbWifi1.setFont(font)
        self.cbWifi1.setObjectName("cbWifi1")
        self.cbWifi1.addItem("")
        self.cbWifi1.addItem("")
        self.cbWifi1.addItem("")
        self.cbWifi1.addItem("")
        self.label_control_wifi2 = QtGui.QLabel(self.centralwidget)
        self.label_control_wifi2.setGeometry(QtCore.QRect(260, 49, 91, 20))
        font = QtGui.QFont()
        font.setFamily("Rehan")
        font.setPointSize(14)
        self.label_control_wifi2.setFont(font)
        self.label_control_wifi2.setObjectName("label_control_wifi2")
        self.cbWifi2 = QtGui.QComboBox(self.centralwidget)
        self.cbWifi2.setGeometry(QtCore.QRect(250, 70, 111, 27))
        font = QtGui.QFont()
        font.setFamily("Nice")
        font.setPointSize(14)
        self.cbWifi2.setFont(font)
        self.cbWifi2.setObjectName("cbWifi2")
        self.cbWifi2.addItem("")
        self.cbWifi2.addItem("")
        self.cbWifi2.addItem("")
        self.cbWifi2.addItem("")
        self.ButtonStop = QtGui.QPushButton(self.centralwidget)
        self.ButtonStop.setGeometry(QtCore.QRect(221, 112, 80, 30))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.ButtonStop.setFont(font)
        self.ButtonStop.setObjectName("ButtonStop")
        self.ButtonSet = QtGui.QPushButton(self.centralwidget)
        self.ButtonSet.setGeometry(QtCore.QRect(190, 480, 80, 28))
        self.ButtonSet.setObjectName("ButtonSet")
        self.ButtonStart = QtGui.QPushButton(self.centralwidget)
        self.ButtonStart.setGeometry(QtCore.QRect(121, 112, 80, 30))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.ButtonStart.setFont(font)
        self.ButtonStart.setObjectName("ButtonStart")
        self.light_ap1 = QtGui.QLabel(self.centralwidget)
        self.light_ap1.setGeometry(QtCore.QRect(106, 170, 21, 21))
        self.light_ap1.setObjectName("light_ap1")
        self.light_ap2 = QtGui.QLabel(self.centralwidget)
        self.light_ap2.setGeometry(QtCore.QRect(196, 170, 21, 21))
        self.light_ap2.setObjectName("light_ap2")
        self.light_ap3 = QtGui.QLabel(self.centralwidget)
        self.light_ap3.setGeometry(QtCore.QRect(286, 170, 21, 21))
        self.light_ap3.setObjectName("light_ap3")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 433, 26))
        self.menubar.setObjectName("menubar")
        self.menuSettings = QtGui.QMenu(self.menubar)
        self.menuSettings.setObjectName("menuSettings")
        MainWindow.setMenuBar(self.menubar)
        self.actionDetail = QtGui.QAction(MainWindow)
        self.actionDetail.setCheckable(True)
        self.actionDetail.setObjectName("actionDetail")
        self.actionWiFi_Interfaces = QtGui.QAction(MainWindow)
        self.actionWiFi_Interfaces.setObjectName("actionWiFi_Interfaces")
        self.actionBonding_Drivers = QtGui.QAction(MainWindow)
        self.actionBonding_Drivers.setObjectName("actionBonding_Drivers")
        self.actionWiMAX = QtGui.QAction(MainWindow)
        self.actionWiMAX.setObjectName("actionWiMAX")
        self.actionAaa = QtGui.QAction(MainWindow)
        self.actionAaa.setCheckable(True)
        self.actionAaa.setObjectName("actionAaa")
        self.menuSettings.addAction(self.actionDetail)
        self.menubar.addAction(self.menuSettings.menuAction())

        self.retranslateUi(MainWindow)
        self.settingTab.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "OpenRoad Tricast Demo", None, QtGui.QApplication.UnicodeUTF8))
        self.editAP1.setText(QtGui.QApplication.translate("MainWindow", "ordemo1", None, QtGui.QApplication.UnicodeUTF8))
        self.label_ap1.setText(QtGui.QApplication.translate("MainWindow", "AP1", None, QtGui.QApplication.UnicodeUTF8))
        self.label_ap2.setText(QtGui.QApplication.translate("MainWindow", "AP2", None, QtGui.QApplication.UnicodeUTF8))
        self.editAP2.setText(QtGui.QApplication.translate("MainWindow", "ordemo2", None, QtGui.QApplication.UnicodeUTF8))
        self.label_ap3.setText(QtGui.QApplication.translate("MainWindow", "AP3", None, QtGui.QApplication.UnicodeUTF8))
        self.editAP3.setText(QtGui.QApplication.translate("MainWindow", "ordemo3", None, QtGui.QApplication.UnicodeUTF8))
        self.settingTab.setTabText(self.settingTab.indexOf(self.tabAP), QtGui.QApplication.translate("MainWindow", "AP", None, QtGui.QApplication.UnicodeUTF8))
        self.label_wifi_if_1.setText(QtGui.QApplication.translate("MainWindow", "First InterFace Name", None, QtGui.QApplication.UnicodeUTF8))
        self.editWiFiIF1.setText(QtGui.QApplication.translate("MainWindow", "wlan0", None, QtGui.QApplication.UnicodeUTF8))
        self.editWiFiIF2.setText(QtGui.QApplication.translate("MainWindow", "ath0", None, QtGui.QApplication.UnicodeUTF8))
        self.label_wifi_if_2.setText(QtGui.QApplication.translate("MainWindow", "Second InterFace Name", None, QtGui.QApplication.UnicodeUTF8))
        self.settingTab.setTabText(self.settingTab.indexOf(self.tabWiFi), QtGui.QApplication.translate("MainWindow", "WiFi Interface", None, QtGui.QApplication.UnicodeUTF8))
        self.label_bond_ip.setText(QtGui.QApplication.translate("MainWindow", "IP Address with WiMAX", None, QtGui.QApplication.UnicodeUTF8))
        self.editBondIP.setText(QtGui.QApplication.translate("MainWindow", "10.79.1.242", None, QtGui.QApplication.UnicodeUTF8))
        self.label_bond_mac.setText(QtGui.QApplication.translate("MainWindow", "MAC Address ", None, QtGui.QApplication.UnicodeUTF8))
        self.editBondMac.setText(QtGui.QApplication.translate("MainWindow", "00:1c:f0:ed:98:5a", None, QtGui.QApplication.UnicodeUTF8))
        self.label_bond_if.setText(QtGui.QApplication.translate("MainWindow", "InterFace Name", None, QtGui.QApplication.UnicodeUTF8))
        self.editBondMacIF.setText(QtGui.QApplication.translate("MainWindow", "bond0", None, QtGui.QApplication.UnicodeUTF8))
        self.label_bond_ip_nowimax.setText(QtGui.QApplication.translate("MainWindow", "IP Address w/o WiMAX", None, QtGui.QApplication.UnicodeUTF8))
        self.editBondIP_nowimax.setText(QtGui.QApplication.translate("MainWindow", "10.79.1.242", None, QtGui.QApplication.UnicodeUTF8))
        self.settingTab.setTabText(self.settingTab.indexOf(self.tabBond), QtGui.QApplication.translate("MainWindow", "Bonding Driver", None, QtGui.QApplication.UnicodeUTF8))
        self.label_wimax_if.setText(QtGui.QApplication.translate("MainWindow", "WiMAX Interface Name", None, QtGui.QApplication.UnicodeUTF8))
        self.editWimaxIF.setText(QtGui.QApplication.translate("MainWindow", "eth1", None, QtGui.QApplication.UnicodeUTF8))
        self.isUseWiMax.setText(QtGui.QApplication.translate("MainWindow", "Use WiMAX", None, QtGui.QApplication.UnicodeUTF8))
        self.settingTab.setTabText(self.settingTab.indexOf(self.tabWimax), QtGui.QApplication.translate("MainWindow", "WiMAX", None, QtGui.QApplication.UnicodeUTF8))
        self.label_WifiAssocTime.setText(QtGui.QApplication.translate("MainWindow", "WiFi Association Time (micro second)", None, QtGui.QApplication.UnicodeUTF8))
        self.label_gw.setText(QtGui.QApplication.translate("MainWindow", "Gateway ", None, QtGui.QApplication.UnicodeUTF8))
        self.editGW.setText(QtGui.QApplication.translate("MainWindow", "10.79.1.105", None, QtGui.QApplication.UnicodeUTF8))
        self.settingTab.setTabText(self.settingTab.indexOf(self.tabGeneral), QtGui.QApplication.translate("MainWindow", "General", None, QtGui.QApplication.UnicodeUTF8))
        self.label_output.setText(QtGui.QApplication.translate("MainWindow", "Output Message", None, QtGui.QApplication.UnicodeUTF8))
        self.label_settings.setText(QtGui.QApplication.translate("MainWindow", "Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.label_wifi_status_1.setText(QtGui.QApplication.translate("MainWindow", "WiFi #1", None, QtGui.QApplication.UnicodeUTF8))
        self.label_wifi_status_2.setText(QtGui.QApplication.translate("MainWindow", "WiFi #2", None, QtGui.QApplication.UnicodeUTF8))
        self.label_wimax_status.setText(QtGui.QApplication.translate("MainWindow", "WiMax", None, QtGui.QApplication.UnicodeUTF8))
        self.wifi_status_1.setText(QtGui.QApplication.translate("MainWindow", "N/A", None, QtGui.QApplication.UnicodeUTF8))
        self.wifi_status_2.setText(QtGui.QApplication.translate("MainWindow", "N/A", None, QtGui.QApplication.UnicodeUTF8))
        self.wimax_status.setText(QtGui.QApplication.translate("MainWindow", "N/A", None, QtGui.QApplication.UnicodeUTF8))
        self.cbMode.setItemText(0, QtGui.QApplication.translate("MainWindow", "Auto Mode", None, QtGui.QApplication.UnicodeUTF8))
        self.cbMode.setItemText(1, QtGui.QApplication.translate("MainWindow", "Manual Mode", None, QtGui.QApplication.UnicodeUTF8))
        self.label_control_wifi1.setText(QtGui.QApplication.translate("MainWindow", "WiFi  #1", None, QtGui.QApplication.UnicodeUTF8))
        self.cbWifi1.setItemText(0, QtGui.QApplication.translate("MainWindow", "ordemo1", None, QtGui.QApplication.UnicodeUTF8))
        self.cbWifi1.setItemText(1, QtGui.QApplication.translate("MainWindow", "ordemo2", None, QtGui.QApplication.UnicodeUTF8))
        self.cbWifi1.setItemText(2, QtGui.QApplication.translate("MainWindow", "ordemo3", None, QtGui.QApplication.UnicodeUTF8))
        self.cbWifi1.setItemText(3, QtGui.QApplication.translate("MainWindow", "N/A", None, QtGui.QApplication.UnicodeUTF8))
        self.label_control_wifi2.setText(QtGui.QApplication.translate("MainWindow", "WiFi  #2", None, QtGui.QApplication.UnicodeUTF8))
        self.cbWifi2.setItemText(0, QtGui.QApplication.translate("MainWindow", "ordemo1", None, QtGui.QApplication.UnicodeUTF8))
        self.cbWifi2.setItemText(1, QtGui.QApplication.translate("MainWindow", "ordemo2", None, QtGui.QApplication.UnicodeUTF8))
        self.cbWifi2.setItemText(2, QtGui.QApplication.translate("MainWindow", "ordemo3", None, QtGui.QApplication.UnicodeUTF8))
        self.cbWifi2.setItemText(3, QtGui.QApplication.translate("MainWindow", "N/A", None, QtGui.QApplication.UnicodeUTF8))
        self.ButtonStop.setText(QtGui.QApplication.translate("MainWindow", "Stop", None, QtGui.QApplication.UnicodeUTF8))
        self.ButtonSet.setText(QtGui.QApplication.translate("MainWindow", "Set", None, QtGui.QApplication.UnicodeUTF8))
        self.ButtonStart.setText(QtGui.QApplication.translate("MainWindow", "Start", None, QtGui.QApplication.UnicodeUTF8))
        self.menuSettings.setTitle(QtGui.QApplication.translate("MainWindow", "Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.actionDetail.setText(QtGui.QApplication.translate("MainWindow", "Show Detail", None, QtGui.QApplication.UnicodeUTF8))
        self.actionWiFi_Interfaces.setText(QtGui.QApplication.translate("MainWindow", "Show Setting", None, QtGui.QApplication.UnicodeUTF8))
        self.actionBonding_Drivers.setText(QtGui.QApplication.translate("MainWindow", "Bonding Driver", None, QtGui.QApplication.UnicodeUTF8))
        self.actionWiMAX.setText(QtGui.QApplication.translate("MainWindow", "WiMAX", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAaa.setText(QtGui.QApplication.translate("MainWindow", "aaa", None, QtGui.QApplication.UnicodeUTF8))

