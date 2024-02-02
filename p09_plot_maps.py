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
COLORS_INCOME = [COLOR1, COLOR8, COLOR5, COLOR7]

## =============================== ##
## auxiliary data

datafile = "countries.shp"
gdf_countries = gpd.read_file(os.path.join(DATAPATH, datafile))

df_area = pd.read_csv(os.path.join(DATAPATH, 'countries_landarea.csv'), sep=';')
iso2area = dict(zip(df_area['iso3'].values, df_area['Land area (sq. km)'].values))

## =============================== ##
## radiosondes

df = pd.read_csv(os.path.join(DATAPATH, 'radiosondes_1985-2020_nobs.csv'))
df = df.loc[df['year'].between(2011, 2020), :]
df = df.loc[df['nobs'] > 0., :]
df_coords = df.groupby('radiosonde_id').first().reset_index().loc[:, ['radiosonde_id', 'lon', 'lat']]
gdf = gpd.GeoDataFrame(df_coords, geometry=gpd.points_from_xy(df_coords.lon, df_coords.lat)).set_crs('EPSG:4326')

fig, ax = plt.subplots(figsize=(8,4))
gdf_countries.plot(ax=ax, alpha=1., facecolor='#f0f0f0', lw=0.5, edgecolor='k')
gdf.plot(ax=ax, alpha=1., facecolor='r', marker='o', edgecolor='none', markersize=6.)
ax.set_xlim(-130., 180.)
ax.set_ylim(-60., 75.)
ax.plot(ax.get_xlim(), [-23.5, -23.5], 'k--', linewidth=0.5)
ax.plot(ax.get_xlim(), [23.5, 23.5], 'k--', linewidth=0.5)
ax.set_xlabel(None)
ax.set_ylabel(None)
fig.savefig('./figures/map_points_radiosondes_2011-2020.png', bbox_inches='tight', dpi=400)

## =============================== ##
## stations

df = pd.read_csv(os.path.join(DATAPATH, 'stations_1985-2020_nobs.csv'))
df = df.loc[df['year'].between(1985, 2020), :]
df = df.loc[(df['slp_utc12'] > 0.) | (df['slp_utc00'] > 0.), :]
df['nobs'] = (df['slp_utc12'] + df['slp_utc00']) / 2.
df = df.loc[df['nobs'] > 0., :]

dfc = pd.read_csv(os.path.join(DATAPATH, 'stations_1985-2020_countries.csv'))
dfc = dfc.drop(columns=['lat', 'lon'])
df = df.merge(dfc, on=['station_id', 'year'], how='left')
df = df.sort_values(by=['station_id', 'year'], ascending=True)
df = df.groupby(['iso3', 'station_id']).last().reset_index()
df = (df.loc[df['year'].between(2011, 2020), :].groupby('iso3')['station_id'].count()).reset_index()

df['density_stations'] = df['station_id'] / df['iso3'].apply(lambda x: iso2area.get(x, np.nan))
df['density_stations'] = df['density_stations'] * 1.e4

gdf = gdf_countries.merge(df, on='iso3', how='left')
gdf = gdf.loc[~gdf.duplicated(), :]

cmap = plt.cm.Blues
bounds = np.arange(0., 2.2, 0.2)
norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
formatcode = '%.1f'

fig, ax = plt.subplots(figsize=(8,4))
ax2 = fig.add_axes([0.94, 0.16, 0.03, 0.68])
cb = mpl.colorbar.ColorbarBase(ax2, cmap=cmap, norm=norm,
				spacing='uniform', ticks=bounds, boundaries=bounds, format=formatcode,
				extend='max', orientation='vertical')
cb.ax.tick_params(labelsize='medium')
cb.set_label(label="Number of stations per 10,000 km2", size='medium')
gdf_countries.plot(ax=ax, alpha=1., facecolor='none', lw=0.5, edgecolor='k')
gdf.plot(ax=ax, alpha=1., column='density_stations', lw=0.2, cmap=cmap, norm=norm, edgecolor='none', markersize=1.)
ax.set_xlim(-130., 180.)
ax.set_ylim(-60., 75.)
ax.plot(ax.get_xlim(), [-23.5, -23.5], 'k--', linewidth=0.5)
ax.plot(ax.get_xlim(), [23.5, 23.5], 'k--', linewidth=0.5)
ax.set_xlabel(None)
ax.set_ylabel(None)
fig.savefig('./figures/map_density_2011-2020.png', bbox_inches='tight', dpi=400)

