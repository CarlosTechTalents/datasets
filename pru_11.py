import pandas as pd
import numpy as np
import geopandas as gpd
import requests
import plotly.graph_objects as go
import dash
from dash.dependencies import Input, Output, State
import json

# Update with host url
df_geo = gpd.GeoDataFrame.from_features(
    requests.get(
        "https://eric.clst.org/assets/wiki/uploads/Stuff/gz_2010_us_050_00_20m.json"
    ).json()
)

fig = go.Figure(
    [
        go.Choroplethmapbox(
            geojson=df_geo.set_index("GEO_ID")["geometry"].__geo_interface__,
            locations=df_geo["GEO_ID"],
            z=df_geo["CENSUSAREA"],
            autocolorscale=False,
            colorscale="Viridis",
            zmin=df_geo["CENSUSAREA"].min(),
            zmax=df_geo["CENSUSAREA"].quantile(0.95),
            marker_line_width=0,
            name="choropleth"
            # colorbar={"orientation": "h", "x": 0.5, "yanchor": "middle", "y": 0.1},
        ),
        go.Scattermapbox(
            name="scatter", marker={"size": 30, "color": "red", "opacity": 1}
        ),
    ]
)

fig.update_layout(
    mapbox_style="carto-positron",
    # mapbox_accesstoken=token,
    mapbox_zoom=3,
    mapbox_center={"lat": 37.0902, "lon": -95.7129},
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    datarevision=0,
    height=300,
    width=600,
    autosize=False,
)

# Build App
app = dash.Dash(__name__)
app.layout = dash.html.Div(
    [
        dash.dcc.Checklist(
            options=[{"label":"refesh", "value":"yes"}],
            id="refresh",
        ),
        dash.dcc.Graph(id="mapbox_fig", figure=fig),
        dash.html.Div(
            id="debug_container",
        ),
        dash.dcc.Store(
            id="points-store",
            data={
                "lat": [],
                "lon": [],
            },
        ),
    ]
)


@app.callback(
    Output("points-store", "data"),
    Output("debug_container", "children"),
    Input("mapbox_fig", "relayoutData"),
    Input("refresh","value")
)
def mapbox_cb(mapbox_cfg, refresh):
    try:
        refresh = refresh[0]=="yes"
    except Exception:
        refresh = False
    if mapbox_cfg and "mapbox.zoom" in mapbox_cfg.keys() and refresh:
        bbox = np.array(mapbox_cfg["mapbox._derived"]["coordinates"])
        # bbox = bbox * .8
        data = {
            "lon": bbox[:, 0].tolist() + [mapbox_cfg["mapbox.center"]["lon"]],
            "lat": bbox[:, 1].tolist() + [mapbox_cfg["mapbox.center"]["lat"]],
        }

        return data, [
            dash.html.Pre(json.dumps(mapbox_cfg, indent=2)),
            dash.html.Pre(json.dumps(data, indent=2)),
        ]
    else:
        raise dash.exceptions.PreventUpdate


app.clientside_callback(
    """
    function(data, fig) {
        fig.data[1]['lat'] = data['lat'];
        fig.data[1]['lon'] = data['lon'];
        fig.layout.datarevision = fig.layout.datarevision + 1;
        /* return fig; */
        return JSON.parse(JSON.stringify(fig)); 
    }
    """,
    Output("mapbox_fig", "figure"),
    Input("points-store", "data"),
    State("mapbox_fig", "figure"),
)

app.run(port= 8050, debug=True)
