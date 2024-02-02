#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import copy

import numpy as np
import pandas as pd

import geopandas as gpd

import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns

import statsmodels.api as sm

## =============================== ##

from parameters import *
COLORS_INCOME = [COLOR1, COLOR8, COLOR5, COLOR7]

## =============================== ##
## auxiliary data

datafile = "countries.shp"
gdf_countries = gpd.read_file(os.path.join(DATAPATH, datafile))
gdf_countries = gdf_countries.loc[:, ['iso3', 'geometry']]

df_gdp = pd.read_csv(os.path.join(DATAPATH, 'countries_income.csv'))
df_gdp = df_gdp.loc[df_gdp['income_group_2020'].notnull(), :]
df_gdp['income_group_2020'] = pd.Categorical(df_gdp['income_group_2020'],
		categories=['Low', 'Lower middle', 'Upper middle', 'High'], ordered=True)
df_gdp = df_gdp.sort_values(by='income_group_2020', ascending=True)
df_gdp['log_gdp_pc_2011_2020'] = np.log(df_gdp['gdp_pc_2011_2020']).replace([-np.inf, np.inf], np.nan)

## =============================== ##

def weighted_mean(df, columns_groups, columns_values, column_weights):
	columns_weighted = []
	for col in columns_values:
		df[col + '_w'] = df[col].values * df[column_weights].values
		columns_weighted.append(col + '_w')
	dfg = df.groupby(columns_groups).sum().reset_index()
	for col in columns_weighted:
		dfg[col] = dfg[col].values / dfg[column_weights].values
	dfg = dfg.drop(columns=columns_values).rename(columns=dict(zip(columns_weighted, columns_values)))
	dfg = dfg.loc[:, columns_groups + columns_values]
	return dfg

## ============================================================== ##
## hex with population weights
## ============================================================== ##

## stations all
df = pd.read_csv(os.path.join(DATAPATH, 'data_hex_res{0:0d}.csv'.format(3)))
dfc = df.groupby('iso3').count().reset_index()
countries_drop = dfc.loc[dfc['corr_d01'] == 0., 'iso3'].unique()
df = df.loc[~df['iso3'].isin(countries_drop), :]
df = df.loc[df['corr_d01'].notnull(), :]

dfg = weighted_mean(df, ['iso3', 'year'], ['corr_d01', 'corr_d02', 'corr_d03', 'corr_d04', 'corr_d05', 'corr_d06', 'corr_d07', 'lat', 'lon'], 'population')
dfw1 = dfg.loc[dfg['year'].between(2011, 2020), :].groupby('iso3').mean().reset_index()

## =============================== ##

## stations subset
df = pd.read_csv(os.path.join(DATAPATH, 'data_hex_res{0:0d}_subset.csv'.format(3)))
dfc = df.groupby('iso3').count().reset_index()
countries_drop = dfc.loc[dfc['corr_d01'] == 0., 'iso3'].unique()
df = df.loc[~df['iso3'].isin(countries_drop), :]
df = df.loc[df['corr_d01'].notnull(), :]

dfg = weighted_mean(df, ['iso3', 'year'], ['corr_d01', 'corr_d02', 'corr_d03', 'corr_d04', 'corr_d05', 'corr_d06', 'corr_d07', 'lat', 'lon'], 'population')
dfw2 = dfg.loc[dfg['year'].between(2011, 2020), :].groupby('iso3').mean().reset_index()

## =============================== ##

dfw = dfw1.merge(dfw2.drop(columns=['lon', 'lat']), on=['iso3'], how='outer', suffixes=['_all', '_subset'])
dfw = dfw.merge(df_gdp, on='iso3', how='left')

dfw.to_csv(os.path.join(DATAPATH, 'data_countries_weighted.csv'), index=False)

## ============================================================== ##
## individual stations, no weights
## ============================================================== ##

## stations all
df_all = pd.DataFrame()
for year in range(2011, 2020+1, 1):
	time_utc = 12
	ipath = os.path.join(DATAPATH, 'correlations_ecmwf_stations')
	ifile = 'correlations_ecmwf_stations_{0:d}_utc{1:02d}_tmp_T5_t2m.csv'.format(year, time_utc)
	df = pd.read_csv(os.path.join(ipath, ifile))
	df['year'] = year
	df['time_utc'] = time_utc
	df_all = pd.concat([df_all, df], axis=0, ignore_index=True)
dfm = df_all.groupby('station_id').first().reset_index()
gdf = gpd.GeoDataFrame(dfm, geometry=gpd.points_from_xy(dfm.lon, dfm.lat)).set_crs('EPSG:4326')
df_merge = gdf_countries.sjoin(gdf, how='right').loc[:, ['station_id', 'iso3']]
dfa1 = df_all.merge(df_merge, on='station_id', how='left')
dfa1 = dfa1.loc[dfa1['year'].between(2011, 2020), :].groupby('iso3').mean().reset_index()

## =============================== ##

## stations subset
df_all = pd.DataFrame()
for year in range(2011, 2020+1, 1):
	time_utc = 12
	ipath = os.path.join(DATAPATH, 'correlations_ecmwf_stations_subset')
	ifile = 'correlations_ecmwf_stations_{0:d}_utc{1:02d}_tmp_T5_t2m.csv'.format(year, time_utc)
	df = pd.read_csv(os.path.join(ipath, ifile))
	df['year'] = year
	df['time_utc'] = time_utc
	df_all = pd.concat([df_all, df], axis=0, ignore_index=True)
dfm = df_all.groupby('station_id').first().reset_index()
gdf = gpd.GeoDataFrame(dfm, geometry=gpd.points_from_xy(dfm.lon, dfm.lat)).set_crs('EPSG:4326')
df_merge = gdf_countries.sjoin(gdf, how='right').loc[:, ['station_id', 'iso3']]
dfa2 = df_all.merge(df_merge, on='station_id', how='left')
dfa2 = dfa2.loc[dfa2['year'].between(2011, 2020), :].groupby('iso3').mean().reset_index()

## =============================== ##

dfa = dfa1.merge(dfa2.drop(columns=['lon', 'lat', 'nobs', 'year', 'time_utc']), on=['iso3'], how='outer', suffixes=['_all', '_subset'])
dfa = dfa.merge(df_gdp, on='iso3', how='left')

dfa.to_csv(os.path.join(DATAPATH, 'data_countries_unweighted.csv'), index=False)