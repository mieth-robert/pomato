# -*- coding: utf-8 -*-
"""
Created on Sun Apr 19 21:25:13 2020

@author: OediP
"""

from bokeh.models import ColumnDataSource, Select, Band,HoverTool
from bokeh.plotting import figure,show,reset_output
from bokeh.layouts import row, gridplot,column, WidgetBox
from bokeh.models.widgets import Tabs, Panel
from bokeh.io import output_file,curdoc
import pandas as pd
import numpy as np

reset_output()
level = "hour"
#loaddata
print("reading in data")
data = pd.read_csv("redispatch_hourly_plot.csv",index_col="time")
data.index = pd.to_datetime(data.index)
print("finished reading data")
#dropdown
menu = ["hour","day","week","month"]
dropdown = Select(title="Level", options=menu,value="hour")

name_freq_map = {"hour":"H","day":"D","week":"W","month":"M"}


def make_dataset_timeline(level = "hour"):
    plot_data = data.copy()
    plot_data.index = plot_data.index.to_period(name_freq_map[level]).to_timestamp()
    plot_data = plot_data.groupby(plot_data.index).sum()
    return ColumnDataSource(plot_data)


def make_dataset_timeavg(src,level = "hour"):
    plot_data = src.to_df().set_index("time")
    plot_data.index = eval("plot_data.index.{}".format(level))
    grouped = plot_data.groupby(plot_data.index)[["redispatch_abs"]]
    plot_data = grouped.mean()
    standard_dev = grouped.std()["redispatch_abs"]
    plot_data["lower"] = plot_data["redispatch_abs"].values - standard_dev.values 
    plot_data["upper"] = plot_data["redispatch_abs"].values + standard_dev.values
    return ColumnDataSource(plot_data)

def make_dataset_histogram(src):
    plot_data = src.to_df()
    arr_hist,edges = np.histogram(plot_data["redispatch_abs"].values)
    histogram_data = pd.DataFrame({"count":arr_hist,"left":edges[:-1],"right":edges[1:]})
    histogram_data["freq"] = histogram_data["count"] / histogram_data["count"].sum() *100 
    return ColumnDataSource(histogram_data)

def make_timeline(src):
    p = figure(plot_width=500,
               plot_height = 300,
               x_axis_type="datetime",
               title="Redispatch over Time",
               y_axis_label = "Redispatch in MW",
               x_axis_label = "Time")
    hover = HoverTool(tooltips = [("Time","@time{%F}"),("Redispatch in MW","@redispatch_abs")],formatters={'@time': 'datetime'})
    p.line("time","redispatch_abs",source=src)
    p.title.align="center"
    p.add_tools(hover)
    return p

def make_timeavg(src):
    p = figure(plot_width=500,
               plot_height = 300,
               title="Average Redispatch in MW",
               y_axis_label = "Avg. Redispatch in MW",  
               x_axis_label = "Time".format(level))
    hover = HoverTool(tooltips = [("Time","@time"),
                                  ("Redispatch in MW","@redispatch_abs"),
                                  ("Lower Bound","@lower"),
                                  ("Upper Bound","@upper")])
    p.line("time","redispatch_abs",source=src)
    band = Band(base='time', lower='lower', upper='upper', source=src, level='underlay',
            fill_alpha=0.0, line_width=1, line_color='black')
    p.add_layout(band)
    p.title.align="center"
    p.add_tools(hover)
    return p

def make_histogram(src):
    print(level)
    p = figure(plot_width=500,
               plot_height = 300,
               title="Distribution of Redispatch in MW",
               y_axis_label = "count",
               x_axis_label = "Redispatch in MW")
    p.quad(bottom=0,top="count",left = "left",right="right",source=src)
    hover = HoverTool(tooltips=[("count","@count"),("fequency in %","@freq")])
    p.title.align="center"
    p.add_tools(hover)
    return p



def update(attr,old,new):
    level = dropdown.value
    print(level)
    new_src = make_dataset_timeline(level)
    src.data.update(new_src.data)
    new_src2 = make_dataset_timeavg(src,level)
    src2.data.update(new_src2.data)
    new_src3 = make_dataset_histogram(src)
    src3.data.update(new_src3.data)
    print("updated")
    
src = make_dataset_timeline()
src2 = make_dataset_timeavg(src=src)
src3 = make_dataset_histogram(src)
p = make_timeline(src)
p2 = make_timeavg(src2) 
p3 = make_histogram(src3)
dropdown.on_change("value",update)
#dropdown.on_click(update)

controls = WidgetBox(dropdown)

layout = column(controls,p,p2,p3)
tab = Panel(child=layout,title="Redispatch Germany")
tabs = Tabs(tabs=[tab])

curdoc().add_root(tabs)