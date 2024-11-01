import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from geodatasets import get_path


from shapely.geometry import Polygon, LineString, Point
df = pd.DataFrame(
    {
        "name": ["Fox Lane Hill", "Camera", "Access Point", "CP94 Punto 1"],
        "state": ["El Escorial", "El Escorial", "El Escorial", "El Escorial"],
        "Latitude": [40.605647833333336, 40.60567016666667, 40.605838, 40.60551616666667],
        "Longitude": [-4.0631363333333335, -4.063272666666666, -4.063039833333334, -4.063137333333334],
        "rssi":[90, 70, 50, 30]
    }
)
gdf = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df.Longitude, df.Latitude),
    crs="EPSG:4326"
)

#gdf = gpd.GeoDataFrame(df, geometry=gpd.polygons_from_custom_xy_string(df["geometry"]))


gdf.to_file('./assets/fox_points.geojson', driver="GeoJSON")


# d = {'col1': ['name1', 'name2'], 'geometry': [Point(1, 2), Point(2, 1)]}
# gdf = gpd.GeoDataFrame(d, crs="EPSG:3857")

# list of coordindate pairs
coordinates = [
            [-4.063137333333334, 40.60551616666667],
            [-4.0634483333333336, 40.605663],
            [-4.063046666666667,40.6060075],
            [-4.062823, 40.605895],
            [-4.063137333333334, 40.60551616666667]
          ]      

# Create a Shapely polygon from the coordinate-tuple list
poly_coord = Polygon(coordinates)

# create a dictionary with needed attributes and required geometry column
df = {
    'name': ['Fox Lane Land'],
    'state': ['El Escorial'],
    'ref':['Fox Lane'],
    'geometry': poly_coord
    }

# Convert shapely object to a geodataframe 
poly = gpd.GeoDataFrame(df, geometry='geometry', crs ="EPSG:4326")

coordinates_2 = [
            [-4.063086666666667, 40.605846],
            [-4.063128, 40.60588416666667],
            [-4.063028666666667, 40.60596],
            [-4.062977333333333, 40.605932333333335],
            [-4.063086666666667, 40.605846]
          ]        

# Create a Shapely polygon from the coordinate-tuple list
poly_coord_2 = Polygon(coordinates_2)

df_2 = {
    'name': ['Fox Lane House'],
    'state': ['El Escorial'],
    'ref': ['Fox Lane'],
    'geometry': poly_coord_2
    }
poly_2 = gpd.GeoDataFrame(df_2, geometry='geometry', crs ="EPSG:4326")
poly = pd.concat([poly, poly_2], ignore_index=True)

poly.to_file(filename='./assets/fox_polygons.geojson', driver='GeoJSON')
