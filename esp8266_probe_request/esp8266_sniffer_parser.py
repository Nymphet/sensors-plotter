import re
import time


# example output
# RSSI: -79 Ch: 13 Peer MAC: 28:6c:07:1c:7f:1c SSID: Flying
# RSSI: -78 Ch: 13 Peer MAC: da:a1:11:7f:49:11 SSID: AndroidAP


output_re = re.compile(r"RSSI: -(\d{1,3}) Ch: (\d{1,2}) Peer MAC: (.{2}:.{2}:.{2}:.{2}:.{2}:.{2}) SSID:(.*)")


def parse_header():
    # there is no header to parse
    pass


class IllegalFormatError(Exception):
    pass


def parse_data(data_output):
    # parses a line
    # raises IllegalFormatError if the line is not data
    # returns data_dict:dict - 
    #           RSSI:       int
    #           Ch:         int
    #           Peer MAC:   str
    #           SSID:       str (may be empty)

    data_dict = dict()

    if output_re.match(data_output):
        data_dict['RSSI'] = 0 - int(output_re.match(data_output).group(1))
        data_dict['Ch'] = int(output_re.match(data_output).group(2))
        data_dict['Peer MAC'] = str(output_re.match(data_output).group(3))
        data_dict['SSID'] = str(output_re.match(data_output).group(4)).strip()
    else:
        raise IllegalFormatError

    assert len(data_dict) != 0 
    return data_dict


class ReadDataTimeoutError(Exception):
    pass


def read_data(ser):
    # ensures we get a line of data, blocking
    # raises ReadDataTimeoutError if non-data lines exceeds max_try
    # returns data_dict:dict - 
    #           RSSI:       int
    #           Ch:         int
    #           Peer MAC:   str
    #           SSID:       str (may be empty)
    #           timestamp:  float
    max_try = 99
    for i in range(max_try):
        buffer = ser.readline()
        try:
            data_output = buffer.decode()
        except UnicodeDecodeError:
            print("Malform data line received, retry", i)
            continue
        try:
            data_dict = parse_data(data_output)
            data_dict['timestamp'] = time.time()
            return data_dict
        except IllegalFormatError:
            print("Parser: Non-data line received: ", data_output, ", retry #", i)
            pass
    raise ReadDataTimeoutError
