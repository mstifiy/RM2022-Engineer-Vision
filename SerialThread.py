import serial
import Globla
import logging

def DOpenPort(portx, bps, timeout):         #开
    try:
        ser = serial.Serial(portx, bps, timeout=timeout)
        if(False == ser.is_open):
           ser = -1
    except Exception as e:
        print("---异常---：", e)

    return ser

def DColsePort(ser):                      #关
    ser.close()

def DReadPort(ser):                       #读
    readstr = ""
    if ser.in_waiting:
        readbuf = ser.read(ser.in_waiting)
        if readbuf[0] == 0x55 and readbuf[1] == 0xaa:
            readstr = readbuf
        else:
            readstr = readstr + readbuf

def DWritePort(ser, data):                #写
    result = ser.write(data)  # 写数据
    return result

def Serial():
    #DOpenPort()
    while Globla.run:
        #DReadPort()
        #DWritePort()
        print("运行中")
    #DColsePort()
    print("已结束")