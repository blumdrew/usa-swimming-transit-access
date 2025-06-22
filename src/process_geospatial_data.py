# -*- coding: utf-8 -*-

"""
    Author: Andrew Lindstrom
    Date: 2025-04-06
    Purpose: Process geospatial data made by fetch script into usable data to
    upload to mapbox
"""

import geopandas as gpd
import pandas as pd
import os

DATA_PATH = "/Users/andrewmurp/Documents/python/usa-swimming-transit/data"


def main():
    """process driver, sketchy code, etc.
    """
    cbsa_map = {
        "nyc":"New York-Newark-Jersey City, NY-NJ",
        "la":"Los Angeles-Long Beach-Anaheim, CA",
        "chicago":"Chicago-Naperville-Elgin, IL-IN",
        "dallas":"Dallas-Fort Worth-Arlington, TX",
        "houston":"Houston-Pasadena-The Woodlands, TX",
        "miami":"Miami-Fort Lauderdale-West Palm Beach, FL",
        "dc":"Washington-Arlington-Alexandria, DC-VA-MD-WV",
        "atlanta":"Atlanta-Sandy Springs-Roswell, GA",
        "philly":"Philadelphia-Camden-Wilmington, PA-NJ-DE-MD",
        "phoenix":"Phoenix-Mesa-Chandler, AZ",
        "boston":"Boston-Cambridge-Newton, MA-NH",
        "san francisco":"San Francisco-Oakland-Fremont, CA",
        "san jose":"San Jose-Sunnyvale-Santa Clara, CA",
        "detroit":"Detroit-Warren-Dearborn, MI",
        "seattle":"Seattle-Tacoma-Bellevue, WA",
        "minneapolis":"Minneapolis-St. Paul-Bloomington, MN-WI",
        "tampa":"Tampa-St. Petersburg-Clearwater, FL",
        "san diego":"San Diego-Chula Vista-Carlsbad, CA",
        "denver":"Denver-Aurora-Centennial, CO",
        "orlando":"Orlando-Kissimmee-Sanford, FL",
        "charlotte":"Charlotte-Concord-Gastonia, NC-SC",
        "baltimore":"Baltimore-Columbia-Towson, MD",
        "st louis":"St. Louis, MO-IL",
        "san antonio":"San Antonio-New Braunfels, TX",
        "austin":"Austin-Round Rock-San Marcos, TX",
        "portland":"Portland-Vancouver-Hillsboro, OR-WA",
        "sacramento":"Sacramento-Roseville-Folsom, CA",
        "las vegas":"Las Vegas-Henderson-North Las Vegas, NV",
        "cincinnati":"Cincinnati, OH-KY-IN",
        "kansas city":"Kansas City, MO-KS",
        "columbus":"Columbus, OH",
        "indy":"Indianapolis-Carmel-Greenwood, IN",
        "nashville":"Nashville-Davidson--Murfreesboro--Franklin, TN",
        "virginia beach":"Virginia Beach-Chesapeake-Norfolk, VA-NC",
        "providence":"Providence-Warwick, RI-MA",
        "milwaukee":"Milwaukee-Waukesha, WI",
        "raleigh":"Raleigh-Cary, NC",
        "louisville":"Louisville/Jefferson County, KY-IN",
        "richmond":"Richmond, VA",
        "fresno":"Fresno, CA"
    }
    cbsa_mhi_data = {
        "nyc":97_334,
        "la":93_525,
        "chicago":88_850,
        "dallas":87_155,
        "houston":80_458,
        "miami":73_481,
        "dc":123_896,
        "atlanta":86_338,
        "philly":89_273,
        "phoenix":84_703,
        "boston":110_697,
        "san francisco":127792,
        "san jose":153202,
        "detroit":72574,
        "seattle":112_594,
        "minneapolis":95102,
        "tampa":72743,
        "san diego":103674,
        "denver":103055,
        "orlando":77378,
        "charlotte":81262,
        "baltimore":94289,
        "st louis":78224,
        "san antonio":73195,
        "austin":98508,
        "portland":94925,
        "sacramento":94992,
        "las vegas":75065,
        "cincinnati":77844,
        "kansas city":79842,
        "columbus":77390,
        "indy":77947,
        "nashville":84685,
        "virginia beach":79325,
        "providence":83330,
        "milwaukee":76_404,
        "raleigh":96096,
        "louisville":68921,
        "richmond":84332,
        "fresno":71140
    }

    tract_data = gpd.read_file(os.path.join(DATA_PATH, "tracts", "msa_tracts.geojson"))
    tract_data.to_crs("EPSG:4326",inplace=True)

    all_data = []
    for cbsa in cbsa_map.keys():
        try:
            cbsa_title_simple = cbsa_map[cbsa][:cbsa_map[cbsa].index("-")]
        except ValueError:
            cbsa_title_simple = cbsa.capitalize()
        if cbsa == "st louis":
            cbsa_title_simple = "St. Louis"
        elif cbsa == "cincinnati":
            cbsa_title_simple = "Cincinnati"
        elif cbsa == "kansas city":
            cbsa_title_simple = "Kansas City"
        elif cbsa == "louisville":
            cbsa_title_simple = "Louisville"
        # get population totals for MSA
        cbsa_population = tract_data[tract_data["CBSA_title"] == cbsa_map[cbsa]]["population"].sum()
        cbsa_population_white = tract_data[tract_data["CBSA_title"] == cbsa_map[cbsa]]["population_white"].sum()
        cbsa_population_black = tract_data[tract_data["CBSA_title"] == cbsa_map[cbsa]]["population_black"].sum()
        cbsa_population_latino = tract_data[tract_data["CBSA_title"] == cbsa_map[cbsa]]["population_hispanic_latino"].sum()
        cbsa_mhi = cbsa_mhi_data[cbsa]
        cbsa_path = os.path.join(DATA_PATH, cbsa)
        cbsa_data_pool = gpd.GeoDataFrame(pd.concat(
            [gpd.read_file(os.path.join(cbsa_path, f)) for f in os.listdir(cbsa_path) if f.endswith("geojson")]
        ), crs="EPSG:4326")
        cbsa_data = cbsa_data_pool.dissolve()
        cbsa_data_club = cbsa_data_pool.dissolve(by="club_name",as_index=False)
        # add population data for overall
        cbsa_tract_data = gpd.GeoDataFrame(tract_data.clip(cbsa_data))
        # add cbsa racial demographics, since we need to reference this somehow in the map itself
        
        # calculate proportion of tract left after clip to estimate each population number
        cbsa_tract_data.to_crs(cbsa_tract_data.estimate_utm_crs(),inplace=True)
        cbsa_tract_data["population_est"] = (
            cbsa_tract_data["population"]
            * (cbsa_tract_data.area / cbsa_tract_data["ALAND"])
        ).round()
        cbsa_tract_data["population_white_est"] = (
            cbsa_tract_data["population_white"]
            * (cbsa_tract_data.area / cbsa_tract_data["ALAND"])
        ).round()
        cbsa_tract_data["population_black_est"] = (
            cbsa_tract_data["population_black"]
            * (cbsa_tract_data.area / cbsa_tract_data["ALAND"])
        ).round()
        cbsa_tract_data["population_latino_est"] = (
            cbsa_tract_data["population_hispanic_latino"]
            * (cbsa_tract_data.area / cbsa_tract_data["ALAND"])
        ).round()
        cbsa_tract_data["population_est"] = cbsa_tract_data[["population","population_est"]].min(axis=1)
        cbsa_tract_data["population_white_est"] = cbsa_tract_data[["population_white","population_white_est"]].min(axis=1)
        cbsa_tract_data["population_black_est"] = cbsa_tract_data[["population_black","population_black_est"]].min(axis=1)
        cbsa_tract_data["population_latino_est"] = cbsa_tract_data[["population_hispanic_latino","population_latino_est"]].min(axis=1)
        # mhi specifics.. population weighted
        cbsa_tract_data["above_cbsa_mhi"] = (cbsa_tract_data["median_household_income"] > cbsa_mhi).astype(int)
        cbsa_tract_data["population_mhi_weight"] = cbsa_tract_data["population_est"] * cbsa_tract_data["above_cbsa_mhi"]
        # recovert to lat/lng
        cbsa_tract_data.to_crs("EPSG:4326",inplace=True)

        cbsa_data_agg = cbsa_tract_data[[
            "population_est", "population_white_est","population_black_est",
            "population_latino_est", "population_mhi_weight"
        ]].sum()
        cbsa_data["population_est"] = cbsa_data_agg["population_est"]
        cbsa_data["population_pct"] = (100 * (cbsa_data["population_est"] / cbsa_population)).round(2)
        # all racial demographics are relative to cbsa
        cbsa_data["population_white_est"] = cbsa_data_agg["population_white_est"]
        cbsa_data["population_white_pct"] = (100 * (cbsa_data["population_white_est"] / cbsa_population_white)).round(2)
        cbsa_data["population_black_est"] = cbsa_data_agg["population_black_est"]
        cbsa_data["population_black_pct"] = (100 * (cbsa_data["population_black_est"] / cbsa_population_black)).round(2)
        cbsa_data["population_latino_est"] = cbsa_data_agg["population_latino_est"]
        cbsa_data["population_latino_pct"] = (100 * (cbsa_data["population_latino_est"] / cbsa_population_latino)).round(2)
        #
        cbsa_data["pct_over_cbsa_mhi"] = (100 * cbsa_data_agg["population_mhi_weight"] / cbsa_data_agg["population_est"]).round(2)

        cbsa_data["club_name"] = None
        cbsa_data["pool_name"] = None
        cbsa_data["layer_name"] = "cbsa"
        cbsa_data["cbsa_name"] = cbsa_title_simple
        cbsa_data["cbsa_mhi"] = cbsa_mhi
        cbsa_data = cbsa_data[[
            "cbsa_name","layer_name","pool_name","club_name","cbsa_mhi",
            "population_est","population_pct",
            "population_white_est","population_white_pct",
            "population_black_est","population_black_pct",
            "population_latino_est","population_latino_pct",
            "pct_over_cbsa_mhi",
            "geometry"
        ]]
        # add population data for club
        cbsa_data_club_sjoin = gpd.sjoin(cbsa_data_club, cbsa_tract_data, how="left")
        cbsa_data_club = cbsa_data_club_sjoin.groupby(
            by="club_name",
            as_index=False
        ).agg({
            "geometry":"first",
            "population_est":"sum",
            "population_white_est":"sum",
            "population_black_est":"sum",
            "population_latino_est":"sum",
            "population_mhi_weight":"sum",
        })
        cbsa_data_club["population_pct"] = (100 * (cbsa_data_club["population_est"] / cbsa_population)).round(2)
        cbsa_data_club["population_white_pct"] = (100 * (cbsa_data_club["population_white_est"] / cbsa_population_white)).round(2)
        cbsa_data_club["population_black_pct"] = (100 * (cbsa_data_club["population_black_est"] / cbsa_population_black)).round(2)
        cbsa_data_club["population_latino_pct"] = (100 * (cbsa_data_club["population_latino_est"] / cbsa_population_latino)).round(2)
        cbsa_data_club["pct_over_cbsa_mhi"] = (100 * cbsa_data_club["population_mhi_weight"] / cbsa_data_club["population_est"]).round(2)
        cbsa_data_club = gpd.GeoDataFrame(cbsa_data_club, geometry="geometry", crs="EPSG:4326")
        cbsa_data_club["pool_name"] = None
        cbsa_data_club["layer_name"] = "club"
        cbsa_data_club["cbsa_name"] = cbsa_title_simple
        cbsa_data_club["cbsa_mhi"] = cbsa_mhi
        cbsa_data_club = cbsa_data_club[[
            "cbsa_name","layer_name","pool_name","club_name","cbsa_mhi",
            "population_est","population_pct",
            "population_white_est","population_white_pct",
            "population_black_est","population_black_pct",
            "population_latino_est","population_latino_pct",
            "pct_over_cbsa_mhi",
            "geometry"
        ]]

        # add population data for pools
        cbsa_data_pool_sjoin = gpd.sjoin(cbsa_data_pool, cbsa_tract_data, how="left")
        cbsa_data_pool = cbsa_data_pool_sjoin.groupby(
            by=["club_name","pool_name"],
            as_index=False
        ).agg({
            "geometry":"first",
            "population_est":"sum",
            "population_white_est":"sum",
            "population_black_est":"sum",
            "population_latino_est":"sum",
            "population_mhi_weight":"sum",
        })
        cbsa_data_pool["population_pct"] = (100 * (cbsa_data_pool["population_est"] / cbsa_population)).round(2)
        cbsa_data_pool["population_white_pct"] = (100 * (cbsa_data_pool["population_white_est"] / cbsa_population_white)).round(2)
        cbsa_data_pool["population_black_pct"] = (100 * (cbsa_data_pool["population_black_est"] / cbsa_population_black)).round(2)
        cbsa_data_pool["population_latino_pct"] = (100 * (cbsa_data_pool["population_latino_est"] / cbsa_population_latino)).round(2)
        cbsa_data_pool["pct_over_cbsa_mhi"] = (100 * cbsa_data_pool["population_mhi_weight"] / cbsa_data_pool["population_est"]).round(2)
        cbsa_data_pool = gpd.GeoDataFrame(cbsa_data_pool, geometry="geometry", crs="EPSG:4326")
        
        cbsa_data_pool["layer_name"] = "pool"
        cbsa_data_pool["cbsa_name"] = cbsa_title_simple
        cbsa_data_pool["cbsa_mhi"] = cbsa_mhi
        cbsa_data_pool = cbsa_data_pool[[
            "cbsa_name","layer_name","pool_name","club_name","cbsa_mhi",
            "population_est","population_pct",
            "population_white_est","population_white_pct",
            "population_black_est","population_black_pct",
            "population_latino_est","population_latino_pct",
            "pct_over_cbsa_mhi",
            "geometry"
        ]]
        all_data.append(cbsa_data)
        all_data.append(cbsa_data_club)
        all_data.append(cbsa_data_pool)

    gdf = gpd.GeoDataFrame(
        pd.concat(all_data),
        crs="EPSG:4326"
    )
    gdf.to_file(
        os.path.join(os.path.dirname(os.path.dirname(__file__)),"data","full_cbsa_data.geojson")
    )
    gdf.drop("geometry",axis=1,inplace=True)
    gdf.to_csv(
        os.path.join(os.path.dirname(os.path.dirname(__file__)),"data","data_no_geoms.csv"),
        index=False
    )
    gdf.fillna("",inplace=True)
    # TODO: future versions may want more than just the below data included in map
    # but since this json is copy/pasted into the .html, want it to be as short as possible
    html_cols_used = ["layer_name","club_name","pool_name","cbsa_name","population_pct"]
    pd.DataFrame(gdf)[html_cols_used].to_json(
        os.path.join(os.path.dirname(os.path.dirname(__file__)),"data","data_no_geoms.json"),
        orient="records"
    )

main()