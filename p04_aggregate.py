#!/usr/bin/env python

import os
import numpy as np
import pandas as pd
import copy

import matplotlib.pyplot as plt

import geopandas as gpd

## ==============================================================================

from parameters import *

VERIFICATION_COLUMNS = ['corr_d00', 'corr_d01', 'corr_d02', 'corr_d03', 'corr_d04', 'corr_d05', 'corr_d06', 'corr_d07',
	'corr_analysis_d01', 'corr_analysis_d02', 'corr_analysis_d03', 'corr_analysis_d05', 'corr_analysis_d07',]

SUBSET = False

## ==============================================================================

def expand_df(df, dims, values):
	df = df.set_index(dims)
	multi_index = (pd.MultiIndex.from_product(
			iterables=values,
			names=dims))
	df = df.reindex(multi_index, fill_value=np.nan).reset_index()
	df = df.sort_values(by=dims, ascending=True).reset_index(drop=True)
	return df

## ==============================================================================

index_column = 'h3_{0:02d}'.format(HEX_RES)
gdf_hex = gpd.read_file(os.path.join(DATAPATH, 'h3_hexagons', 'h3_hexagons_res{0:d}.shp'.format(HEX_RES)))
gdf_hex['lon'] = gdf_hex.geometry.centroid.x
gdf_hex['lat'] = gdf_hex.geometry.centroid.y

datafile = "countries.shp"
gdf_countries = gpd.read_file(os.path.join(DATAPATH, datafile))
gdf_countries = gdf_countries.loc[:, ['iso3', 'geometry']]

## ==============================================================================
## match verification stations to hex
## ==============================================================================

df_all = pd.DataFrame()

for year in range(1985, 2020+1, 1):

	time_utc = 12

	if SUBSET == True:
		ipath = os.path.join(DATAPATH, 'correlations_ecmwf_stations_subset')
	else:
		ipath = os.path.join(DATAPATH, 'correlations_ecmwf_stations')
	ifile = 'correlations_ecmwf_stations_{0:d}_utc{1:02d}_tmp_T5_t2m.csv'.format(year, time_utc)
	df = pd.read_csv(os.path.join(ipath, ifile))

	df['year'] = year
	df['time_utc'] = time_utc

	df_all = pd.concat([df_all, df], axis=0, ignore_index=True)

dfm = df_all.groupby('station_id').first().reset_index()

## =============

gdf = gpd.GeoDataFrame(dfm, geometry=gpd.points_from_xy(dfm.lon, dfm.lat)).set_crs('EPSG:4326')
df_merge = gdf_hex.sjoin(gdf, how='right').loc[:, ['station_id', index_column]]

df = df_all.merge(df_merge, on='station_id', how='left')
df = df.loc[:, ['year', index_column] + VERIFICATION_COLUMNS]
df_count = df.groupby(['year', index_column])[VERIFICATION_COLUMNS[0]].count().reset_index().rename(columns={VERIFICATION_COLUMNS[0]: 'verification_count'})
df = df.groupby(['year', index_column]).mean().reset_index()
df = df.merge(df_count, on=['year', index_column], how='left')

## ==============================================================================
## match countries and characteristics to hex
## ==============================================================================

datafile = "countries.shp"
gdf_countries = gpd.read_file(os.path.join(DATAPATH, datafile))
gdf_countries = gdf_countries.loc[:, ['iso3', 'geometry']]

## =============

df_iso = gdf_hex.sjoin(gdf_countries, how='left').loc[:, [index_column, 'iso3']]

## ==============================================================================
## add population of hexagons
## ==============================================================================

df_pop = pd.read_csv(os.path.join(DATAPATH, 'population', 'population_2020_h3_res{0:d}.csv'.format(HEX_RES)))

## ==============================================================================
## merge all based on hex
## ==============================================================================

units = gdf_hex[index_column].unique()
years = df['year'].unique()
df = expand_df(df, [index_column, 'year'], [units, years])

df = df.merge(df_iso, on=[index_column], how='left')
df = df.merge(gdf_hex.loc[:, [index_column, 'lat', 'lon']], on=[index_column], how='left')
df = df.merge(df_pop, on=[index_column], how='left')

if SUBSET == True:
	df.to_csv(os.path.join(DATAPATH, 'data_hex_res{0:0d}_subset.csv'.format(HEX_RES)), index=False)
else:
	df.to_csv(os.path.join(DATAPATH, 'data_hex_res{0:0d}.csv'.format(HEX_RES)), index=False)
