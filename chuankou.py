import serial
import serial.tools.list_ports
import time

def list_available_ports():
    """列出可用的串口"""
    ports = serial.tools.list_ports.comports()
    for port, desc, hwid in sorted(ports):
        print("{}: {} [{}]".format(port, desc, hwid))

def main():
    list_available_ports()
    port = input("请输入要使用的串口名称: ")
    baud_rate = int(input("请输入波特率（如 9600、115200 等）: "))

    try:
        ser = serial.Serial(port, baud_rate, timeout=1)
    except serial.SerialException as e:
        print("无法打开串口: ", e)
        return

    while True:
        # 发送数据
        send_data = input("请输入要发送的数据（输入 'q' 退出）: ")
        if send_data == 'q':
            break
        ser.write(send_data.encode())

        # 接收数据
        try:
            received_data = ser.readline()
            if received_data:
                print("接收到的数据: ", received_data.decode().strip())
        except serial.SerialException as e:
            print("读取数据时出错: ", e)

    # 关闭串口
    ser.close()

if __name__ == "__main__":
    main()