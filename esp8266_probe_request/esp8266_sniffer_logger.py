# This script constantly recieves data from the sensor and logs it to a file

import serial
import datetime
import time

import esp8266_sniffer_parser


# serial_port = "/dev/ttyUSB0"
serial_port = "/dev/cu.wchusbserial1420"
baud_rate = 115200

ser = serial.Serial(serial_port, baud_rate, timeout=1)


def update_data():
    today = datetime.date.today()
    now = time.time()
    # write every 60s
    write_interval = 60
    print("[Logger]: Today is ", str(today))
    data = list()
    try:
        while True:
            if time.time() - now > write_interval:
                break
            if ser.inWaiting():
                data_dict = esp8266_sniffer_parser.read_data(ser)
                data.append((data_dict['RSSI'], data_dict['Ch'],
                             data_dict['Peer MAC'], data_dict['SSID'], data_dict['timestamp']))
            else:
                time.sleep(1)
        write_data(today, data)
    except KeyboardInterrupt:
        # save data for today if user exits
        write_data(today, data)
        print("[Logger]: KeyboardInterrupt received, exiting")
        exit(0)


def write_data(today, data):
    data_filename = "./data/data-"+str(today)+".csv"
    with open(data_filename, 'a') as f:
        writestring = "\n".join([",".join(list(map(str, i)))
                                 for i in data]) + '\n'
        print("[Logger]: Writing data for ",
              str(today), " at ", data_filename, "... ", end='')
        f.write(writestring)
        print("Done")


while True:
    update_data()
