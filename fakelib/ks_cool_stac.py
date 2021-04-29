'''
these functions were borrowed from Kelcy Smith's Notebook
'''
from functools import lru_cache
from typing import Union
from cytoolz import pipe
from typing import List, Callable
import requests

_stac = 'https://landsatlook.usgs.gov/sat-api/stac'

def get_json(url: str, params: Union[list, dict, None] = None) -> Union[list, dict]:
    """
    Perform a GET request to a REST API endpoint, assume the response is a JSON
    """
    resp = requests.get(url, params=params)
    
    if not resp.ok:
        resp.raise_for_status()

    return resp.json()

def post_json(url: str, data: Union[list, dict]) -> Union[list, dict]:
    """
    Send a POST request to the resource with the payload as JSON
    """
    resp = requests.post(url, json=data)
    
    if not resp.ok:
        resp.raise_for_status()
        
    return resp.json()

@lru_cache()
def search_endpoint(endpoint: str = _stac) -> str:
    """
    Get the search endpoint for STAC
    """
    resp = get_json(endpoint)
    
    for item in resp['links']:
        if item['rel'] == 'search':
            return item['href']

def ks_stac_search(params: dict, endpoint: str = _stac) -> Union[list, dict]:
    """
    Simple search against STAC-API
    """
    return get_json(search_endpoint(endpoint),
                    params=params)

def ks_stac_query(data: dict, endpoint: str = _stac) -> Union[list, dict]:
    """
    Perform a more complex query against the STAC-API
    """
    return post_json(search_endpoint(endpoint),
                     data=data)

def ks_filter_ascending(features: List[dict]) -> List[dict]:
    """
    Filter out ascending path/rows from a STAC query
    """
    return [f for f in features
            if int(f['properties']['landsat:wrs_path']) < 100
               and int(f['properties']['landsat:wrs_row']) < 100]

def ks_filter_stacquery(data: dict, filters: Union[List[Callable], Callable], endpoint: str = _stac) -> List[dict]:
    """
    Conduct a STAC query, then apply some filters to the results
    """
    items = ks_stac_query(data, endpoint)

    if isinstance(filters, Callable):
        return filters(items['features'])
    else:
        return pipe(items['features'], *filters)

import rasterio
def ks_convert_llurl(ll_url: str) -> str:
    """
    Convert a landsat look url to an S3 url
    """
    return ll_url.replace('https://landsatlook.usgs.gov/data', 's3://usgs-landsat')

def ks_open_dateset(ll_url: str):
    """
    Open a file with gdal
    """
    with rasterio.open(ks_convert_llurl(ll_url)) as f:
        return f
#     return gdal.Open(path, gdal.ReadOnly)
