import requests
import pandas as pd
import geopandas
import xarray as xr

from ks_cool_stac import ks_filter_stacquery, ks_filter_ascending, ks_convert_llurl
from fm_map import Fmap
from xra_func import load_all_bands_from_df_as_array_of_dataarrays


def get_bbox_from_geojson(geojson_file):
	url = geojson_file
	gdf = geopandas.read_file(url)
	bbox = (gdf['geometry'].bounds['minx'][0], gdf['geometry'].bounds['miny'][0], 
        	gdf['geometry'].bounds['maxx'][0], gdf['geometry'].bounds['maxy'][0])
	return(bbox)

def get_my_alber_scenes(dates, bbox,min_clouds=0, max_clouds=90):

    clouds = max_clouds
    filtered = ks_filter_stacquery({
        'bbox': bbox,
        'limit': 500,
        'time': dates,
        # this did not work'collection': 'landsat-c2l2-sr',
        'query': {'eo:cloud_cover': {'lt': clouds},
                  'eo:instrument': {'eq': 'OLI_TIRS'},
                 'collection': {'eq': 'landsat-c2l2alb-bt'}}},
        filters=ks_filter_ascending)
    return(filtered)

import json

def get_href_url_for_asset(assets, asset_band):
   try:
            jstr = assets[asset_band]
            href = jstr['href']
   except:
            jstr='NotAvail'
            href = None
   return ks_convert_llurl(href)

def get_measurement_band_assets(assets):
    asset_dict = {}
    for key in assets.keys():
        if 'SR_' in key:
            # print('ASSET', key)
            asset_dict[key] = get_href_url_for_asset(assets, key)
    # print(asset_dict)
    return asset_dict
    


def create_simple_df_instead(meas_dict, my_scenes):
    dict_list=[]
    print(len(my_scenes), 'LENGTH')
    print(my_scenes[0].keys())
    for scene in my_scenes:
        prop_df = pd.DataFrame(scene['properties'])
        prune_list = ['datetime', 'eo:cloud_cover', 'eo:platform', 'eo:instrument', 'landsat:wrs_path', 'landsat:wrs_row', 'landsat:scene_id']
        prune_prop_df = prop_df[prune_list]
        #print(prune_prop_df)
        prune_prop_df.reset_index(drop=True, inplace=True)
        my_dict = prune_prop_df.to_dict('records')
        s_dict = my_dict[0]

        asset_dict = get_measurement_band_assets(scene['assets'])
        for akey in meas_dict:
            try:
                print(meas_dict[akey])
                s_dict[akey] = asset_dict[meas_dict[akey]]
            except:
                print('key error', scene['assets'])
        
        dict_list.append(s_dict)
    my_df = pd.DataFrame(dict_list)
    #print(my_df)
    return(my_df)

class NR():

  def __init__(self):
    self.sat_api_url = "https://landsatlook.usgs.gov/sat-api"
    print("creating Nathan Roberts Class")
    self.verify_api()
    self.set_measurements()

  def verify_api(self):
    satAPI = requests.post(self.sat_api_url)
    if satAPI.status_code == 200:
        print('Sat-API is Available')
    else:
        print('Sat-API is not Available')
        sys.exit()

  def set_measurements(self):
    # this could be done from a yml
    self.measures = { 
                        'coastal':'SR_B1.TIF', 
                        'red':'SR_B2.TIF', 
                        'green':'SR_B3.TIF', 
                        'blue':'SR_B4.TIF', 
                        'nir':'SR_B5.TIF', 
                        'swir1':'SR_B6.TIF', 
                        'swir2':'SR_B7.TIF',
                        'pixqa':'SR_QA_AEROSOL.TIF', }

  def measurements(self):
    display_measures = pd.DataFrame(self.measures, index=[0])
    return(display_measures)

  def collections(self):
    satAPICollections = requests.post('https://landsatlook.usgs.gov/sat-api/collections')
    sat_collections = satAPICollections.json()
    my_df = pd.DataFrame(sat_collections['collections'])
    s_df = my_df[['id','title','description']]
    pd.set_option('display.max_colwidth', None)  ### Keeps pandas from truncating text
    return(s_df)


  def search(self, geoj_file, date_min, date_max, min_cloud, max_cloud, requested_measures, sort_date=False):
    print(geoj_file, date_min, date_max, min_cloud, max_cloud, requested_measures)
    bbox = get_bbox_from_geojson(geoj_file)
    dates = f'{date_min}/{date_max}'
    my_scenes = get_my_alber_scenes(dates, bbox, min_cloud, max_cloud)
    simple_df = create_simple_df_instead(self.measures, my_scenes)
    #print(simple_df)
    simple_df['datetime'] = pd.to_datetime(simple_df['datetime'])
    try:
        simple_df = simple_df[simple_df['red'].notna()]
    except:
        pass
    if sort_date:
        simple_df = simple_df.sort_values(by=['datetime'])

    return(my_scenes, simple_df)

  def load(self, aoi_geojson_file, work_df, my_measures='ALL'):
    
    if 'ALL' in my_measures:
        my_measures = self.measures.keys()
    ldatasets = load_all_bands_from_df_as_array_of_dataarrays(aoi_geojson_file, work_df, my_measures)
    from datetime import datetime

    my_text_list=[]
    my_list = work_df.datetime.tolist()
    for dt in my_list:
        str_dt = dt.strftime('%Y-%m-%d')
        my_text_list.append(str_dt)
    DS = xr.concat(ldatasets, dim= pd.DatetimeIndex(my_text_list, name='time'))
    return DS
    

  def map(self, geoj):
    fm=Fmap()
    return(fm.map_geojson(geoj))

  def sat(self, geoj):
    fm=Fmap()
    return(fm.sat_geojson(geoj))
