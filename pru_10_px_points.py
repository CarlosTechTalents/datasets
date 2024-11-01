from dash import Dash, html, dcc, Output, Input, State, DiskcacheManager, dash_table, callback, set_props, callback_context, no_update, ctx
import plotly.express as px

import geopandas as gpd

print('Loading data...')

gdf = gpd.read_file('./assets/fox_points.geojson')
print (gdf.head())
gdf = gdf.to_crs(epsg=4326)
print (gdf.head())


df_car = px.data.carshare()
print (df_car.head())
print('Done!')

app = Dash(__name__)

app.layout = html.Div([
    html.Div([
                dcc.RadioItems(
                    id='radio-color_on',
                    options=[{'label': i, 'value': i} for i in ['AREA','PERIMETER']],
                    value='AREA',
                    labelStyle={'display': 'inline-block'}
                ),
    ],style={'width': '40%', 'display': 'inline-block',}),

html.Div([], style={'width':'100%'}),

    html.Div([
                dcc.Graph(id="fig")
    ],style={'width': '100%', 'display': 'inline-block', 'padding': '0 10',},),
]) 

@app.callback(
    Output("fig", "figure"), 
    [Input("radio-color_on", "value")])
def draw_choropleth(color_on):
    fig = px.scatter_mapbox(gdf,
                            lat="Latitude",
                            lon="Longitude",
                            color="rssi",
                            size="rssi",
                            # color_continuous_scale="Jet",
                            # color_continuous_scale="rainbow",
                            # color_continuous_scale="turbo",
                            # color_continuous_scale="rdylgn",
                            color_continuous_scale="spectral",
                            range_color=(0, 100),
                            mapbox_style="carto-positron",
                            zoom=18,
                            # center = {"lat":gdf.centroid.y.mean(), "lon":gdf.centroid.x.mean()},
                            center = {"lat":40.605846, "lon":-4.063128},
                            opacity=0.9,
                            )
    
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0},
                        height=700,
                        )
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)