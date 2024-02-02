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

## =============================== ##

from parameters import *

## =============================== ##
## auxiliary data

df_gdp = pd.read_csv(os.path.join(DATAPATH, 'countries_income.csv'))
df_gdp = df_gdp.loc[df_gdp['income_group_2020'].notnull(), :]
df_gdp['income_group_2020'] = pd.Categorical(df_gdp['income_group_2020'],
		categories=['Low', 'Lower middle', 'Upper middle', 'High'], ordered=True)
df_gdp = df_gdp.sort_values(by='income_group_2020', ascending=True)

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

## =============================== ##

df = pd.read_csv(os.path.join(DATAPATH, 'data_hex_res{0:0d}_subset.csv'.format(HEX_RES)))
df = df.loc[df['year'] != 2006, :]
dfc = df.groupby('iso3').sum().reset_index()
countries_drop = dfc.loc[dfc['corr_d01'] == 0., 'iso3'].unique()
df = df.loc[~df['iso3'].isin(countries_drop), :]
df = df.loc[df['corr_d01'].notnull(), :]

## =============================== ##

# weigh all hexagons by population for each country, then one country = one vote
dfg = weighted_mean(df, ['iso3', 'year'], ['corr_d01', 'corr_d02', 'corr_d03', 'corr_d04', 'corr_d05', 'corr_d06', 'corr_d07',
	'corr_analysis_d01', 'corr_analysis_d02', 'corr_analysis_d03', 'corr_analysis_d05', 'corr_analysis_d07',
	'lat', 'lon'], 'population')
dfg = dfg.merge(df_gdp, on='iso3', how='left')

dfg.to_csv(os.path.join(DATAPATH, 'data_countries_timeseries.csv'), index=False)
