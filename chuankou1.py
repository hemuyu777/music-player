import serial
import serial.tools.list_ports
import threading
import time
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class SerialPortAssistant(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.serial = None
        self.thread = None
        self.receive_data = ''

    def initUI(self):
        self.setWindowTitle('串口助手')
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        # 串口列表下拉框
        self.comPortComboBox = QComboBox()
        self.comPortComboBox.addItems(["无串口", "COM3", "COM4", "COM5"])
        # self.updateComPortList()
        layout.addWidget(self.comPortComboBox)

        # 波特率下拉框
        self.baudRateComboBox = QComboBox()
        self.baudRateComboBox.addItems(["9600", "115200", "460800"])
        layout.addWidget(self.baudRateComboBox)

        # 打开/关闭串口按钮
        self.openCloseButton = QPushButton('打开串口')
        self.openCloseButton.clicked.connect(self.toggleSerialPort)
        layout.addWidget(self.openCloseButton)

        # 发送数据输入框
        self.sendDataLineEdit = QLineEdit()
        layout.addWidget(self.sendDataLineEdit)

        # 发送按钮
        self.sendButton = QPushButton('发送')
        self.sendButton.clicked.connect(self.sendData)
        layout.addWidget(self.sendButton)

        # 接收数据显示框
        self.receiveDataTextEdit = QTextEdit()
        self.receiveDataTextEdit.setReadOnly(True)
        layout.addWidget(self.receiveDataTextEdit)

        self.setLayout(layout)

    def updateComPortList(self):
        """更新可用串口列表"""
        port_list = [port.device for port in serial.tools.list_ports.comports()]
        self.comPortComboBox.clear()
        self.comPortComboBox.addItems(port_list)

    def toggleSerialPort(self):
        """打开或关闭串口"""
        if self.openCloseButton.text() == '打开串口':
            port = self.comPortComboBox.currentText()
            baud_rate = int(self.baudRateComboBox.currentText())
            try:
                self.serial = serial.Serial(port, baud_rate)
                self.openCloseButton.setText('关闭串口')
                self.thread = threading.Thread(target=self.receiveDataThread)
                self.thread.start()
            except serial.SerialException as e:
                QMessageBox.critical(self, "错误", f"无法打开串口: {e}")
        else:
            if self.serial and self.serial.is_open:
                self.serial.close()
                self.openCloseButton.setText('打开串口')
                self.thread.join()

    def receiveDataThread(self):
        """接收数据的线程函数"""
        while self.serial.is_open:
            try:
                received_data = self.serial.readline()
                if received_data:
                    data = received_data.decode('utf-8').strip()
                    self.receive_data += data + '\n'
                    QMetaObject.invokeMethod(self.receiveDataTextEdit, "setText", Qt.QueuedConnection, Q_ARG(str, self.receive_data))
            except serial.SerialException as e:
                QMessageBox.critical(self, "错误", f"接收数据时出错: {e}")

    def sendData(self):
        """发送数据"""
        if self.serial and self.serial.is_open:
            data = self.sendDataLineEdit.text()
            self.serial.write(data.encode())

if __name__ == '__main__':
    app = QApplication([])
    window = SerialPortAssistant()
    window.show()
    app.exec_()