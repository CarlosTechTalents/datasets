import os
import json
from io import StringIO
from pathlib import Path

from dash import Dash, html, dcc, Output, Input, State, DiskcacheManager, dash_table, callback, set_props, callback_context, no_update, ctx
from dash.exceptions import PreventUpdate
import dash_daq as daq
import diskcache
from dash_iconify import DashIconify
import dash_bootstrap_components as dbc
from dash_extensions.javascript import arrow_function
from dash_extensions.javascript import assign

import plotly.express as px
import plotly.graph_objects as go

import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash_extensions.javascript import Namespace

import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon, LineString, Point
import numpy as np


from time import sleep
from time import time
import datetime
from datetime import datetime as dt

import serial
# serial.tools is part of the pyserial library
from serial.tools import list_ports

from gps import Gps
from wifi import Wifi
import wifi

# Some shapes.
# Some tile urls.
keys = ["toner", "terrain"]
url_template = "http://{{s}}.tile.stamen.com/{}/{{z}}/{{x}}/{{y}}.png"
attribution = 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, ' \
              '<a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> &mdash; Map data ' \
              '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              

#
# *** MAPAS ***
#

CP94 = dlx.dicts_to_geojson([dict(lat=40.605837666666666, lon=-4.063023, popup="Access Point CP94")])
colorscale = ['red', 'yellow', 'green', 'blue', 'purple']  # rainbow
vmin = 0
vmax = 100

# Client side callbacks

# *** POIS ***
# Geojson rendering logic, must be JavaScript as it is executed in clientside.

on_each_feature = assign("""function(feature, layer, context){
    layer.bindTooltip(`${feature.properties.name} (${feature.properties.rssi})`)
}""")

point_to_layer = assign("""function(feature, latlng, context){
    const {min, max, colorscale, circleOptions, colorProp} = context.hideout;
    const csc = chroma.scale(colorscale).domain([min, max]);  // chroma lib to construct colorscale
    circleOptions.fillColor = csc(feature.properties[colorProp]);  // set color based on color prop
    return L.circleMarker(latlng, circleOptions);  // render a simple circle marker
}""")

# Polygons ***
# Color selected polygons in red.
style_handle = assign("""function(feature, context){
    const {selected} = context.hideout;
    if(selected.includes(feature.properties.name)){
        return {fillColor: 'red', color: 'grey'}
    }
    return {fillColor: 'grey', color: 'grey'}
}""")
              

              
# Create app.
app = Dash()
app.layout = html.Div([
    dl.Map(
        zoom = 7,
        center = (56, 10),
        style = {'height': '80vh'},
        children=[
            dl.LayersControl(
                id="lc",
                children = 
                    [dl.BaseLayer(
                        dl.TileLayer(url=url_template.format(key),
                                     attribution=attribution),
                          name=key,
                          checked=key == "toner") for key in keys
                    ] +
                    [dl.Overlay(
                        name="markers",
                        checked=True,
                        children=[
                            dl.LayerGroup([
                                
                                dl.GeoJSON(
                                    id="geojson_polygons",
                                    url="/assets/fox_polygons.geojson",
                                    zoomToBounds=True,
                                    zoomToBoundsOnClick=True,
                                    superClusterOptions={"radius": 100},
                                    hideout=dict(selected=[]),
                                    style=style_handle,
                                    hoverStyle=arrow_function(dict(weight=5, color='#666', dashArray=''))                                            
                                    ),                                
                                ])
                            ]
                        ),
                    dl.Overlay(
                        name="polygon",
                        checked=True,
                        children=[
                            dl.LayerGroup([
                                
                                dl.GeoJSON(
                                    id="geojson_points",
                                    url="/assets/fox_points.geojson",
                                    zoomToBounds=True,  # when true, zooms to bounds when data changes
                                    pointToLayer=point_to_layer,  # how to draw points
                                    onEachFeature=on_each_feature,  # add (custom) tooltip
                                    hideout=dict(colorProp='rssi',
                                                circleOptions=dict(fillOpacity=1, stroke=False, radius=5),
                                                min=vmin,
                                                max=vmax,
                                                colorscale=colorscale)
                                    ),
                                ])
                            ]
                        )
                    ],
            )
        ]
    ),
    html.Div(id="log")
])

@app.callback(Output("log", "children"), Input("lc", "baseLayer"),
              Input("lc", "overlays"), prevent_initial_call=True)
def log(base_layer, overlays):
    return f"Base layer is {base_layer}, selected overlay(s): {json.dumps(overlays)}"

if __name__ == '__main__':
    app.run_server()