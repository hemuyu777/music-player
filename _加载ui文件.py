import sys
import time
import serial
from PyQt5 import uic
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *

class Mywindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.ui = uic.loadUi("chuankou.ui")
        self.init()


    #Pyqt5_Serial
    # 初始化程序
    def init(self):
        # super(Mywindow, self).__init__()

        # self.setupUi(self)
        # self.init()

        self.ser = serial.Serial()
        self.port_check()

        # 设置Logo和标题
        # self.setWindowIcon(QIcon('Com.png'))
        self.setWindowTitle("串口助手")
        # 设置禁止拉伸窗口大小
        self.setFixedSize(self.width(), self.height())

        # 发送数据和接收数据数目置零
        self.data_num_sended = 0
        self.lineEdit_2.setText(str(self.data_num_sended))
        self.data_num_received = 0
        self.lineEdit_3.setText(str(self.data_num_received))

        # 串口关闭按钮使能关闭
        self.pushButton_3.setEnabled(False)

        # 发送框、文本框清除
        self.textEdit.setText("")
        self.textBrowser.setText("")

    # 建立控件信号与槽关系
    # def init(self):
        # 串口检测按钮
        self.pushButton.clicked.connect(self.port_check)
        # 串口打开按钮
        self.pushButton_2.clicked.connect(self.port_open)
        # 串口关闭按钮
        self.pushButton_3.clicked.connect(self.port_close)

        # 定时发送数据
        self.timer_send = QTimer()
        self.timer_send.timeout.connect(self.data_send)
        self.checkBox_7.stateChanged.connect(self.data_send_timer)

        # 发送数据按钮
        self.pushButton_6.clicked.connect(self.data_send)

        # 保存日志
        self.pushButton_4.clicked.connect(self.savefiles)
        # 加载日志
        self.pushButton_5.clicked.connect(self.openfiles)

        # 清除发送按钮
        self.pushButton_7.clicked.connect(self.send_data_clear)

        # 清除接收按钮
        self.pushButton_8.clicked.connect(self.receive_data_clear)
    #
    #     # 串口检测
    def port_check(self):
        # 检测所有存在的串口，将信息存储在字典中
        self.Com_Dict = {}
        port_list = list(serial.tools.list_ports.comports())

        self.comboBox.clear()
        for port in port_list:
            self.Com_Dict["%s" % port[0]] = "%s" % port[1]
            self.comboBox.addItem(port[0])

        # 无串口判断
        if len(self.Com_Dict) == 0:
            self.comboBox.addItem("无串口")

    # 打开串口
    def port_open(self):
        self.ser.port        = self.comboBox.currentText()      # 串口号
        self.ser.baudrate    = int(self.comboBox_2.currentText())  # 波特率

        flag_data = int(self.comboBox_3.currentText())  # 数据位
        if flag_data == 5:
            self.ser.bytesize = serial.FIVEBITS
        elif flag_data == 6:
            self.ser.bytesize = serial.SIXBITS
        elif flag_data == 7:
            self.ser.bytesize = serial.SEVENBITS
        else:
            self.ser.bytesize = serial.EIGHTBITS

        flag_data = self.comboBox_4.currentText()  # 校验位
        if flag_data == "None":
            self.ser.parity = serial.PARITY_NONE
        elif flag_data == "Odd":
            self.ser.parity = serial.PARITY_ODD
        else:
            self.ser.parity = serial.PARITY_EVEN

        flag_data = int(self.comboBox_5.currentText())  # 停止位
        if flag_data == 1:
            self.ser.stopbits = serial.STOPBITS_ONE
        else:
            self.ser.stopbits = serial.STOPBITS_TWO

        flag_data = self.comboBox_6.currentText()  # 流控
        if flag_data == "No Ctrl Flow":
            self.ser.xonxoff = False  #软件流控
            self.ser.dsrdtr  = False  #硬件流控 DTR
            self.ser.rtscts  = False  #硬件流控 RTS
        elif flag_data == "SW Ctrl Flow":
            self.ser.xonxoff = True  #软件流控
        else:
            if self.checkBox_3.isChecked():
                self.ser.dsrdtr = True  #硬件流控 DTR
            if self.checkBox_4.isChecked():
                self.ser.rtscts = True  #硬件流控 RTS
        try:
            time.sleep(0.1)
            self.ser.open()
        except:
            QMessageBox.critical(self, "串口异常", "此串口不能被打开！")
            return None

        # 串口打开后，切换开关串口按钮使能状态，防止失误操作
        if self.ser.isOpen():
            self.pushButton.setEnabled(False)
            self.pushButton_3.setEnabled(True)
            self.formGroupBox1.setTitle("串口状态（开启）")

        # 定时器接收数据
        self.timer = QTimer()
        self.timer.timeout.connect(self.data_receive)
        # 打开串口接收定时器，周期为1ms
        self.timer.start(1)

    # 定时发送数据
    def data_send_timer(self):
        try:
            if 1<= int(self.lineEdit.text()) <= 30000:  # 定时时间1ms~30s内
                if self.checkBox_7.ischecked():
                    self.timer_send.start(int(self.lineEdit.text()))
                    self.lineEdit.setEnabled(False)
                else:
                    self.timer_send.stop()
                    self.lineEdit.setEnabled(True)
            else:
                QMessageBox.critical(self, '定时发送数据异常', '定时发送数据周期仅可设置在30秒内！')
        except:
            QMessageBox.critical(self, '定时发送数据异常', '请设置正确的数值类型！')

    # 接收数据
    def data_receive(self):
        try:
            num = self.ser.inWaiting()

            if num > 0:
                time.sleep(0.1)
                num = self.ser.inWaiting()  # 延时，再读一次数据，确保数据完整性
        except:
            QMessageBox.critical(self, '串口异常', '串口接收数据异常，请重新连接设备！')
            self.port_close()
            return None

        if num > 0:
            data = self.ser.read(num)
            num = len(data)

            # 时间显示
            if self.checkBox_5.ischecked():
                self.textBrowser.insertPlainText((time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + " ")

            # HEX显示数据
            if self.checkBox_2.checkState():
                out_s = ''
                for i in range(0, len(data)):
                    out_s = out_s + '{:02X}'.format(data[i]) + ' '

                self.textBrowser.insertPlainText(out_s)
            # ASCII显示数据
            else:
                self.textBrowser.insertPlainText(data.decode('utf-8'))

            # 接收换行
            if self.checkBox_6.ischecked():
                self.textBrowser.insertPlainText('\r\n')

            # 获取到text光标
            textCursor = self.textBrowser.textCursor()
            # 滚动到底部
            textCursor.movePosition(textCursor.End)
            # 设置光标到text中去
            self.textBrowser.setTextCursor(textCursor)

            # 统计接收字符的数量
            self.data_num_received += num
            self.lineEdit_3.setText(str(self.data_num_received))
        else:
            pass

    # 保存日志
    def savefiles(self):
        dlg = QFileDialog()
        filenames = dlg.getSaveFileName(None, "保存日志文件", None, "Txt files(*.txt)")

        try:
            with open(file = filenames[0], mode='w', encoding='utf-8') as file:
                file.write(self.textBrowser.toPlainText())
        except:
            QMessageBox.critical(self, '日志异常', '保存日志文件失败！')

    # 加载日志
    def openfiles(self):
        dlg = QFileDialog()
        filenames = dlg.getOpenFileName(None, "加载日志文件", None, "Txt files(*.txt)")

        try:
            with open(file = filenames[0], mode='r', encoding='utf-8') as file:
                self.textEdit.setPlainText(file.read())
        except:
            QMessageBox.critical(self, '日志异常', '加载日志文件失败！')

    # 清除发送数据显示
    def send_data_clear(self):
        self.textEdit.setText("")

        self.data_num_sended = 0
        self.lineEdit_2.setText(str(self.data_num_sended))

    # 清除接收数据显示
    def receive_data_clear(self):
        self.testBrowser.setText("")

        self.data_num_received = 0
        self.lineEdit_3.setText(str(self.data_num_received))

    # 关闭串口
    def port_close(self):
        try:
            self.timer.stop()
            self.timer_send.stop()

            self.ser.close()
        except:
            QMessageBox.critical(self, '串口异常', '关闭串口失败，请重启程序！')
            return None

        # 切换开关串口按钮使能状态和定时发送使能状态
        self.pushButton.setEnabled(True)
        self.pushButton_3.setEnabled(False)
        self.lineEdit.setEnabled(True)

        # 发送数据和接收数据数目置零
        self.data_num_sended = 0
        self.lineEdit_2.setText(str(self.data_num_sended))
        self.data_num_received = 0
        self.lineEdit_3.setText(str(self.data_num_received))

        self.formGroupBox_1.setTitle("串口状态（关闭）")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Mywindow()
    w.show()
    app.exec_()
