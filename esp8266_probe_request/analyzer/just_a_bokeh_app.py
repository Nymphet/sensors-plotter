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


# this module

import esp8266_aux
import time_series_histogram

### -------------- get things ready --------------- ###

# system
__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

# --- Bokeh related
# Save current Bokeh document for later use
doc = curdoc()

# prepare empty figures
spectrum_tools = "box_select,box_zoom,lasso_select,pan,poly_select,tap,wheel_zoom,undo,redo,reset,save,crosshair,hover"

histogram = figure(plot_width=1280, plot_height=720,
                   tools=spectrum_tools, x_axis_type="datetime")

# just a string for init
init_filename = '../data/data-2018-11-25.csv'
raw_df = esp8266_aux.preprocess_csv_file(init_filename)
MAC_list = esp8266_aux.get_MAC_list(raw_df)
hist_df = time_series_histogram.histograms_of_time(raw_df)[MAC_list[0]]

histogram_data_source = ColumnDataSource(hist_df)

histogram_line = histogram.line(
    'time_bins', 'n', line_width=1, source=histogram_data_source)

### -------------- get things ready --------------- ###


### -------------- define callbacks --------------- ###

# --- load local file
file_source = ColumnDataSource({'file_contents': [], 'file_name': []})


def file_callback(attr, old, new):
    global raw_df, hist_df
    loaded_file_div.text = '<font color=#006699>' + "Loaded file" + ': </font>' + \
        file_source.data['file_name'][0]
    raw_contents = file_source.data['file_contents'][0]
    # # remove the prefix that JS adds
    prefix, b64_contents = raw_contents.split(",", 1)
    file_contents = base64.b64decode(b64_contents).decode()
    raw_df = esp8266_aux.preprocess_csv_string(file_contents)
    MAC_list = esp8266_aux.get_MAC_list(raw_df)
    hist_df = time_series_histogram.histograms_of_time(raw_df)[MAC_list[0]]
    histogram_line.data_source = ColumnDataSource(hist_df)


file_source.on_change('data', file_callback)



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



# --- Layouts

input_widgets = column(
    load_file_button,
    loaded_file_div
)


figure_widgets = column(histogram)

column1 = row(figure_widgets, input_widgets)


# put the button and plot in a layout and add to the document
doc.add_root(column1)

### -------------- make the document -------------- ###
