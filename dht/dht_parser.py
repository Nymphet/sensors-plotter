import re
import time

# This module parses the output of a DHT11 sensor.

# ---- Example Output ----

"""

DHTxx Unified Sensor Example

------------------------------------

Temperature

Sensor:       DHT11

Driver Ver:   1

Unique ID:    -1

Max Value:    50.00 *C

Min Value:    0.00 *C

Resolution:   2.00 *C

------------------------------------

------------------------------------

Humidity

Sensor:       DHT11

Driver Ver:   1

Unique ID:    -1

Max Value:    80.00%

Min Value:    20.00%

Resolution:   5.00%

------------------------------------

"""


#---- Example Data Output ----#

"""
Temperature: 24.00 *C

Humidity: 32.00%
"""

Temperature_re = re.compile(r"Temperature: (\d{2}\.\d{2}) \*C")
Humidity_re = re.compile(r"Humidity: (\d{2}\.\d{2})%")


def parse_header():
    # todo
    pass


class IllegalFormatError(Exception):
    pass


def parse_data(data_output):
    # parses a line
    # raises IllegalFormatError if the line is not data
    # returns str:data_type, float:data

    data_type = None

    if Temperature_re.match(data_output):
        data = float(Temperature_re.match(data_output).group(1))
        data_type = "t/*C"
    elif Humidity_re.match(data_output):
        data = float(Humidity_re.match(data_output).group(1))
        data_type = "RH/%"
    else:
        raise IllegalFormatError

    assert data_type != None
    return data_type, data


class ReadDataTimeoutError(Exception):
    pass


def read_data(ser):
    # ensures we get a line of data, blocking
    # raises ReadDataTimeoutError if non-data lines exceeds max_try
    # returns str:data_type, float:data, float:timestamp
    max_try = 99
    for i in range(max_try):
        buffer = ser.readline()
        data_output = buffer.decode()
        try:
            data_type, data = parse_data(data_output)
            return data_type, data, time.time()
        except IllegalFormatError:
            print("Parser: Non-data line received: ", data_output, ", retry #", i)
            pass
    raise ReadDataTimeoutError
