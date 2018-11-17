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

# Tornado
from tornado import gen

### -------------- get things ready --------------- ###

# system
__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

# --- Bokeh related
# Save current Bokeh document for later use
doc = curdoc()

# prepare empty figures
spectrum_tools = "box_select,box_zoom,lasso_select,pan,poly_select,tap,wheel_zoom,undo,redo,reset,save,crosshair,hover"

rawdata_figure = figure(plot_width=1280, plot_height=720,
                        tools=spectrum_tools, x_axis_type="datetime")

rolling_mean_figure = figure(
    plot_width=1280, plot_height=720, tools=spectrum_tools, x_axis_type="datetime")


rolling_mean_window_size = 600

### -------------- get things ready --------------- ###


### -------------- define callbacks --------------- ###

# --- load local file
file_source = ColumnDataSource({'file_contents': [], 'file_name': []})


def file_callback(attr, old, new):
    global rolling_mean_window_size
    loaded_file_div.text = '<font color=#006699>' + "Loaded file" + ': </font>' + \
        file_source.data['file_name'][0]
    raw_contents = file_source.data['file_contents'][0]
    # # remove the prefix that JS adds
    prefix, b64_contents = raw_contents.split(",", 1)
    file_contents = base64.b64decode(b64_contents).decode()
    file_io = io.StringIO(file_contents)

    df = pd.read_csv(file_io, names=['time', 'data'])
    df['time'] = pd.to_datetime(df['time'], unit='s')
    # By default pandas converts timestamps to UTC time, and if we specify time zone
    # by tz_localize, bokeh would not recognize that, so we manually convert UTC time to Asia/Shanghai
    df['time'] = df['time'] + pd.Timedelta('08:00:00')
    df['data_rolling_mean'] = df['data'].rolling(rolling_mean_window_size).mean()

    waveform_data_source = ColumnDataSource(df)
    # draw the lines
    rawdata_waveform = rawdata_figure.line('time', 'data',
                                           line_width=1, source=waveform_data_source)
    rolling_mean_waveform = rolling_mean_figure.line(
        'time', 'data_rolling_mean', line_width=1, source=waveform_data_source)


file_source.on_change('data', file_callback)


def callback_rolling_mean_window_text_input(attr, old, new):
    global rolling_mean_window_size
    try:
        rolling_mean_window_size = int(
            rolling_mean_window_text_input.value)
    except Exception as inst:
        print(type(inst), inst.args)


### -------------- define callbacks --------------- ###

### -------------- make the document -------------- ###


# Load file button

load_file_js = """
function read_file(filename) {
    var reader = new FileReader();
    reader.onload = load_handler;
    reader.onerror = error_handler;
    // readAsDataURL represents the file's data as a base64 encoded string
    reader.readAsDataURL(filename);
}

function load_handler(event) {
    var b64string = event.target.result;
    file_source.data = {'file_contents' : [
        b64string], 'file_name':[input.files[0].name]};
    file_source.trigger("change");
}

function error_handler(evt) {
    if(evt.target.error.name == "NotReadableError") {
        alert("Can't read file!");
    }
}

var input = document.createElement('input');
input.setAttribute('type', 'file');
input.onchange = function(){
    if (window.FileReader) {
        read_file(input.files[0]);
    } else {
        alert('FileReader is not supported in this browser');
    }
}
input.click();
"""

load_file_button = Button(label="Load Data From CSV File", button_type='success', callback=CustomJS(
    args=dict(file_source=file_source), code=load_file_js))

loaded_file_div = Div(text="Loaded file: None")


rolling_mean_window_text_input = TextInput(
    title="Rolling Mean Window Size", value=str(rolling_mean_window_size))
rolling_mean_window_text_input.on_change(
    'value', callback_rolling_mean_window_text_input)



# --- Layouts

input_widgets = column(
    load_file_button,
    loaded_file_div,
    rolling_mean_window_text_input
)


figure_widgets = column(rawdata_figure, rolling_mean_figure)

column1 = row(figure_widgets, input_widgets)


# put the button and plot in a layout and add to the document
doc.add_root(column1)

### -------------- make the document -------------- ###
