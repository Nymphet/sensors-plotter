# -*- coding: utf-8 -*-

import base64
import io
import json
import logging
import os
import select
import sys
import time
import datetime

# Math
import numpy as np
from scipy import signal

# Data
import pandas as pd

# System
import serial

# Bokeh
from bokeh.layouts import column, row, widgetbox
from bokeh.models import ColumnDataSource, CustomJS
from bokeh.models.widgets import (Button, DataTable, Div, NumberEditor,
                                  NumberFormatter, RadioButtonGroup,
                                  RangeSlider, Select, Slider, TableColumn,
                                  TextInput)
from bokeh.plotting import curdoc, figure, output_file, show
from bokeh.palettes import brewer

# Tornado
from tornado import gen

def generate_spectral_color(n):
    colors = brewer['Spectral'][11]
    i = 0
    while i <= n:
        i = i + 1
        yield colors[i%11]


doc = curdoc()

filename = './data/data-2018-11-21.csv'

with open(filename, 'r') as f:
    df = pd.read_csv(f, names=['RSSI', 'Ch', 'PeerMAC', 'SSID', 'time'])

# first, we want to plot RSSI vs. timestamp for each PeerMAC, to see how distant the device is from the ESP8266 at any time.

# Convert timestamp to datetime format
df['time'] = pd.to_datetime(df['time'], unit='s')
# By default pandas converts timestamps to UTC time, and if we specify time zone
# by tz_localize, bokeh would not recognize that, so we manually convert UTC time to Asia/Shanghai
df['time'] = df['time'] + pd.Timedelta('08:00:00')

rawdata_figure = figure(
    plot_width=1280, plot_height=720, x_axis_type="datetime")

# so we split table by PeerMAC column, then plot

line_color_generator = generate_spectral_color(999)

for MAC in df.PeerMAC.value_counts().keys():
    macdf = df[df['PeerMAC'] == MAC]
    data_source = ColumnDataSource(macdf)
    rssi_time_line = rawdata_figure.line(
        'time', 'RSSI', line_width=2, source=data_source, line_color=next(line_color_generator) )

doc.add_root(rawdata_figure)
