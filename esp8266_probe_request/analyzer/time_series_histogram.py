import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import esp8266_aux

def calc_nbins(df, time_window_length):
    # calculate how many bins do we need
    start_time = df['time'].min()
    end_time = df['time'].max()
    nbins = (end_time - start_time) / pd.to_timedelta(time_window_length)
    nbins = int(nbins)
    if nbins == 0:
        nbins = 1
    return nbins


def histograms_of_time(df, time_window_length='10min', first_n = 10):
    # count how many times the signal has appeared in each time_window (Histogram)

    # the default method df.hist() works great, but it is based on matplotlib and is not
    # available over internet, so we will calculate the data only, and plot it with bokeh
    # later.

    # calculate histogram for each MAC
    MAC_list = esp8266_aux.get_MAC_list(df)
    histograms = dict()

    for MAC in MAC_list[:first_n]:
        histogram = histogram_of_time(df, MAC, time_window_length='10min')
        histograms[MAC] = histogram

    return histograms


def histogram_of_time(df, MAC, time_window_length='10min'):
    nbins = calc_nbins(df, time_window_length)

    macdf = df[df['PeerMAC'] == MAC]
    n, time_bins, patches = plt.hist(macdf.time, bins=nbins)
    plt.close('all')
    histogram = pd.DataFrame()
    histogram['n'] = n
    histogram['time_bins'] = time_bins[:-1]
    # the time_bins plt.hist gives us are in gregorian days format, so we need to convert
    # them to unix timestamps first, then convert timestamps to pd.Timestamp
    histogram['time_bins'] = esp8266_aux.gregorian_to_timestamp(histogram['time_bins'])
    histogram['time_bins'] = pd.to_datetime(histogram['time_bins'], unit='s')
    return histogram


#filename = '../data/data-2018-11-25.csv'
#df = esp8266_aux.preprocess_csv_file(filename)

