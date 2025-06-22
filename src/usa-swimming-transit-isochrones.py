# -*- coding: utf-8 -*-

"""
    Author: Andrew Lindstrom
    Date: 2025-04-01
    Purpose: USA Swimming Transit Isochrones
"""

import os
import sys
import json
import logging

import numpy as np
import geopandas as gpd

sys.path.append("/Users/andrewmurp/Documents/python/transit-isochrones/src")
from isochrone import Isochrone
"""TODO:
get data for the 50 largest MSAs in the US, must have at least 2 different clubs in the USA Swimming thing
New York | DONE
Los Angeles | DONE
Chicago | DONE
Dallas | DONE
Houston | DONE
Miami | DONE
DC | DONE
Atlanta | DONE
Philly | DONE
Phoenix | DONE
Boston | DONE
San Francisco | DONE
San Jose | DONE
Detroit | DONE
Seattle | DONE
Minneapolis | DONE
Tampa | DONE
San Diego | DONE
Denver | DONE
Orlando | DONE
Charlotte | DONE
Baltimore | DONE
St. Louis | DONE
San Antonio | DONE
Austin | DONE
Portland | DONE
Sacramento | DONE
Las Vegas | DONE
Cincinnati | DONE
Kansas City | DONE
Columbus | DONE
Indianapolis | DONE
Nashville | DONE
Virginia Beach | DONE
Providence | DONE
Milwaukee | DONE
Raleigh | Done
Louisville | DONE
Richmond | DONE
Fresno | DONE
"""
def main():
    """Process driver
    """
    base_path = os.path.dirname(__file__)
    base_data = gpd.read_file(
        os.path.join(base_path, "data", "usa_swimming_top_clubs_msa.geojson")
    )
    msa_file_name = "fresno"
    msa_starts_with = "Fresno"
    os.makedirs(os.path.join(base_path, "data", msa_file_name), exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        filename=os.path.join(os.path.dirname(__file__),"data","logs",f"{msa_file_name}.log")
    )
    msa = base_data[base_data["NAME"].str.startswith(msa_starts_with)]
    with open("/Users/andrewmurp/Documents/python/transit-isochrones/mapbox.env", "r") as f:
        mapbox_pk = json.load(f)['mapbox_pk']

    gtfs_files = [
        os.path.join(base_path, "gtfs", msa_file_name, f) for f in os.listdir(os.path.join(base_path, "gtfs", msa_file_name)) 
        if os.path.isdir(os.path.join(base_path, "gtfs", msa_file_name, f))
    ]
    ic = Isochrone(
        gtfs_files,
        mapbox_pk=mapbox_pk,
        mapbox_cache_path="/Users/andrewmurp/Documents/python/transit-isochrones/data/mapbox_cache"
    )
    print(f"Running data for {len(msa.index)} pools...")
    n = 0
    for pidx in msa.index:
        pool = msa.loc[pidx]
        pt = pool['geometry']
        club_name = pool['club_name']
        pool_name = pool['pool_name']
        if os.path.isfile(os.path.join(os.path.dirname(__file__),"data",msa_file_name,f"{club_name}_{pool_name}.geojson")):
            n += 1
            print(f"Data already processed for {club_name}, {pool_name}. {n} out of {len(msa.index)}")
            continue
        lat = pt.y
        lng = pt.x
        gdf = ic.transit_isochrone(
            lat = lat,
            lng = lng,
            time = 60,
            time_of_day = "18:00:00",
            transfers = 1,
            intial_walk_time = 20,
            api_behavior = 'check'
        )
        gdf["club_name"] = club_name
        gdf["pool_name"] = pool_name
        gdf = gdf[["club_name","pool_name","lat","lon","geometry"]]
        gdf.to_file(os.path.join(os.path.dirname(__file__),"data",msa_file_name,f"{club_name}_{pool_name}.geojson"))
        n += 1
        print(f"Finished data for {club_name}, {pool_name}. {n} out of {len(msa.index)}")
    return

main()
