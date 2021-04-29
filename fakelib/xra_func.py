#!/usr/bin/env python

import rasterio as rio
import xarray as xr
import geopandas
import cartopy.crs as ccrs
from rasterio.session import AWSSession
import boto3

aws_session = AWSSession(boto3.Session(), requester_pays=True)


def get_ll_corner(aoi_geojson_file):
    
    url = aoi_geojson_file
    gdf = geopandas.read_file(url)
    bbox = (gdf['geometry'].bounds['minx'][0], gdf['geometry'].bounds['miny'][0], 
            gdf['geometry'].bounds['maxx'][0], gdf['geometry'].bounds['maxy'][0])

    print(bbox)

    crs = ccrs.epsg(5072)
    mycrs = '5070'
    crs_object  = ccrs.epsg('5070')

    ll_alb = crs_object.transform_point(bbox[0],bbox[1], ccrs.PlateCarree())
    ll_corner = ll_alb
    return(ll_corner)


def get_ur_corner(aoi_geojson_file):
    
    url = aoi_geojson_file
    gdf = geopandas.read_file(url)
    bbox = (gdf['geometry'].bounds['minx'][0], gdf['geometry'].bounds['miny'][0], 
            gdf['geometry'].bounds['maxx'][0], gdf['geometry'].bounds['maxy'][0])

    print(bbox)

    crs = ccrs.epsg(5072)
    mycrs = '5070'
    crs_object  = ccrs.epsg('5070')

    ur_alb = crs_object.transform_point(bbox[2],bbox[3], ccrs.PlateCarree())
    ur_corner=ur_alb

    return(ur_corner)



#Function used to create array from data stored in dataframe table created above
def create_dataset(row, ll_corner, ur_corner, measures , chunks = {'band': 1, 'x':2048, 'y':2048}):
    datasets = []
    with rio.Env(aws_session):
        for band in measures:
            try:
                url=row[band]
                print(url)
                # should use rioxarray.open_rasterio TONY TONY TONY
                da = xr.open_rasterio(url)

                #da = xr.open_rasterio(url, chunks = chunks)
                daSub = da.sel(x=slice(ll_corner[0], ur_corner[0]), y=slice(ur_corner[1], ll_corner[1]))
                daSub = daSub.squeeze().drop(labels='band')
                DS = daSub.to_dataset(name = band)
                datasets.append(DS)
            except:
                print('skipping band ', band);
        DS = xr.merge(datasets)
        return DS


def load_all_bands_from_df_as_array_of_dataarrays(geoj_file, df, measures):
    ldatasets = []
    ll_corner = get_ll_corner(geoj_file)
    ur_corner = get_ur_corner(geoj_file)
    for i,row in df.iterrows():
        if (i<1000):
            try:
                print('loading....', row.datetime, i)
                ds = create_dataset(row, ll_corner, ur_corner, measures)
                ldatasets.append(ds)
            except Exception as e:
                print('Error loading, skipping')
                print(e)
    return(ldatasets)




# ldatasets = load_all_bands_from_df_as_array_of_dataarrays(aoi_geojson_file, df)
