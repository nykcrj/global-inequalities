#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

import numpy as np
import pandas as pd

import pickle
import socket

import xarray as xr
import geopandas as gpd

## ==============================================================================

from parameters import *

## ==============================================================================

# read in population data
ifile = 'gpw_v4_population_count_rev11_2020_2pt5_min.nc'
ds_pop = xr.open_dataset(os.path.join(DATAPATH, 'population', ifile)).\
						rename_dims({'lon': 'longitude', 'lat': 'latitude'}).\
							rename_vars({'lon': 'longitude', 'lat': 'latitude'})
ds_pop = ds_pop.assign_coords(longitude=(((ds_pop.longitude + 180) % 360) - 180)).sortby('longitude').sortby('latitude')
df = ds_pop.to_dataframe().reset_index()
df = df.loc[df['population'].notnull(), :]
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude)).set_crs('EPSG:4326')

## ==============================================================================

gdf_hex = gpd.read_file(os.path.join(DATAPATH, 'h3_hexagons', 'h3_hexagons_res{0:d}.shp'.format(HEX_RES)))
index_column = 'h3_{0:02d}'.format(HEX_RES)

## ==============================================================================

gdf_hex = gdf_hex.sjoin(gdf, how='left')

## ==============================================================================

dfg = gdf_hex.groupby(index_column)['population'].sum().reset_index()

dfg.to_csv(os.path.join(DATAPATH, 'population', 'population_2020_h3_res{0:d}.csv'.format(HEX_RES)), index=False)