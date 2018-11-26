import io

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ---- preprocess ----

def preprocess_df_time(df):
    # Convert timestamp to datetime format
    df['time'] = pd.to_datetime(df['time'], unit='s')
    # By default pandas converts timestamps to UTC time, and if we specify time zone
    # by tz_localize, bokeh would not recognize that, so we manually convert UTC time to Asia/Shanghai
    df['time'] = df['time'] + pd.Timedelta('8H')
    return df

def preprocess_csv_file(filename):
    with open(filename, 'r') as f:
        df = pd.read_csv(f, names=['RSSI', 'Ch', 'PeerMAC', 'SSID', 'time'])

    df = preprocess_df_time(df)
    return df

def preprocess_csv_string(csvstring):
    file_io = io.StringIO(csvstring)
    df = pd.read_csv(file_io, names=['RSSI', 'Ch', 'PeerMAC', 'SSID', 'time'])
    df = preprocess_df_time(df)
    return df


def get_MAC_list(df):
    # get mac list from a df
    MAC_list = list(df.PeerMAC.value_counts().keys())
    return MAC_list


def gregorian_to_timestamp(days_since_0000):
    # the matplotlib converts pandas.Timestamps to gregorians, and when we want 
    # to use it in pandas, we will need to convert it back.
    # gregorian times are days since 0000, Jan 01, 00:00
    # every day
    seconds_in_a_day = 60 * 60 * 24
    seconds_since_gregorian = days_since_0000 * seconds_in_a_day
    unix_epoch = 62135683200
    unix_timestamp = seconds_since_gregorian - unix_epoch
    return unix_timestamp