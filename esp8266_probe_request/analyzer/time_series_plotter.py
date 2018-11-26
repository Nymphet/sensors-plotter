# -*- coding: utf-8 -*-

# this is a bokeh app, run it with 
# $ bokeh serve --show thisfile

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


import esp8266_aux

# ------ some aux functions here


def generate_spectral_color(n):
    # different color for each line
    colors = brewer['Spectral'][11]
    i = 0
    while i <= n:
        i = i + 1
        yield colors[i % 11]


# ------ save current doc

doc = curdoc()

# ------ import and preprocess data

filename = '../data/esp8266-dlzziio-2018-11-26.csv'
df = esp8266_aux.preprocess_csv_file(filename)

# ------ prepare a empty figure and start to draw

rawdata_figure = figure(
    plot_width=1280, plot_height=720, x_axis_type="datetime")

# so we split table by PeerMAC column, then plot


def draw_RSSI_vs_time(df):
    line_color_generator = generate_spectral_color(999)

    for MAC in df.PeerMAC.value_counts().keys():
        macdf = df[df['PeerMAC'] == MAC]
        data_source = ColumnDataSource(macdf)
        rssi_time_line = rawdata_figure.line(
            'time', 'RSSI', line_width=2, source=data_source, line_color=next(line_color_generator))

draw_RSSI_vs_time(df)

doc.add_root(rawdata_figure)


