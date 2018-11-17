# This script constantly recieves data from the sensor and logs it to a file

import serial
import datetime
import time

import dht_parser


serial_port = "/dev/ttyUSB0"
baud_rate = 9600

ser = serial.Serial(serial_port, baud_rate, timeout=1)


def update_data():
    today = datetime.date.today()
    print("[Logger]: Today is ", str(today))
    data_temperature = list()
    data_humidity = list()
    try:
        while True:
            if datetime.date.today() != today:
                break
            if ser.inWaiting():
                data_type, data, timestamp = dht11_parser.read_data(ser)
                if data_type == "t/*C":
                    data_temperature.append((timestamp, data))
                elif data_type == "RH/%":
                    data_humidity.append((timestamp, data))
                else:
                    pass
            else:
                time.sleep(1)
        write_data(today, data_temperature, data_humidity)
    except KeyboardInterrupt:
        # save data for today if user exits
        write_data(today, data_temperature, data_humidity)
        print("[Logger]: KeyboardInterrupt received, exiting")
        exit(0)


def write_data(today, data_temperature, data_humidity):
    temperature_filename = "./data/temperature-"+str(today)+".csv"
    with open(temperature_filename, 'a') as f:
        writestring = "\n".join([",".join(list(map(str, i)))
                                 for i in data_temperature]) + '\n'
        print("[Loggger]: Writing temperature data for ",
              str(today), " at ", temperature_filename, "... ", end='')
        f.write(writestring)
        print("Done")
    humidity_filename = "./data/humidity-"+str(today)+".csv"
    with open(humidity_filename, 'a') as f:
        writestring = "\n".join([",".join(list(map(str, i)))
                                 for i in data_humidity]) + '\n'
        print("[Loggger]: Writing humidity data for ",
              str(today), " at ", humidity_filename, "... ", end='')
        f.write(writestring)
        print("Done")


while True:
    update_data()
