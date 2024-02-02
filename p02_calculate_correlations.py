#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import copy

import socket
import subprocess

import numpy as np
import pandas as pd
import datetime

## =============================== ##

from parameters import *

## =============================== ##

def correct_station_id(x):
	if isinstance(x, int):
		return '{0:011d}'.format(x)
	else:
		try:
			return '{0:011d}'.format(int(x))
		except:
			return str(x)

## =============================== ##

YEARS = range(1985, 2020+1, 1)

THRESHOLD = 5
COLUMN = 'tmp'

SUBSET = False

## =============================== ##

ipath = os.path.join(DATAPATH, 'noaa_isd')
if SUBSET == True:
	df_subset = pd.read_csv(os.path.join(ipath, 'stations_1985-2020_continuous.csv'))
else:
	df_subset = pd.read_csv(os.path.join(ipath, 'stations_1985-2020_nobs.csv'))
df_subset['station_id'] = df_subset['station_id'].apply(lambda x: correct_station_id(x))
stations_subset = df_subset['station_id'].unique()

## =============================== ##

for year in YEARS:

	print(year)

	year_str = str(year)

	ipath = os.path.join(DATAPATH, 'noaa_isd', year_str)
	df_stations = pd.read_csv(os.path.join(ipath, 'station_locations.csv'))

	df_stations['station_id'] = df_stations['station_id'].apply(lambda x: correct_station_id(x))
	df_stations = df_stations.set_index('station_id')
	df_stations = df_stations.sort_index()

	# subset of stations
	df_stations = df_stations.loc[stations_subset, :]
	df_stations = df_stations.sort_index()

	#if year < 2007:
	#	time_utc = 12
	#else:
	#	time_utc = 0

	time_utc = 12

	if SUBSET == True:
		opath = os.path.join(DATAPATH, 'correlations_ecmwf_stations_subset')
	else:
		opath = os.path.join(DATAPATH, 'correlations_ecmwf_stations')
	ofile = 'correlations_ecmwf_stations_{0:d}_utc{1:02d}_{2:s}_T{3:d}_t2m.csv'.format(year, time_utc, COLUMN, THRESHOLD)

	#if os.path.exists(os.path.join(opath, ofile)):
	#	continue

	for i, station_id in enumerate(df_stations.index.values):

		#print(station_id)

		lat, lon = df_stations.loc[station_id, ['lat', 'lon']].values

		ipath = os.path.join(DATAPATH, 'noaa_isd', year_str)
		ifile = os.path.join(ipath, '{0:s}.csv'.format(station_id))
		if os.path.exists(ifile):
			df1 = pd.read_csv(ifile)
		else:
			print('Station files not found for: ', station_id)
			continue

		ipath = os.path.join(DATAPATH, 'noaa_isd_forecast_era5', str(year))
		ifile = os.path.join(ipath, '{0:s}_{1:d}_utc{2:02d}_t2m.csv'.format(station_id, year, time_utc))
		if os.path.exists(ifile):
			df2 = pd.read_csv(ifile)
		else:
			print('Extracted forecast files not found for: ', station_id)
			continue
		## if no hour information in file yet:
		if ' ' not in df2['time'].values[0]:
			df2['time'] = df2['time'].apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d').strftime('%Y-%m-%d {0:02d}:00:00'.format(time_utc)))

		df1 = df1.loc[:, ['datetime', COLUMN]].rename(columns={'datetime': 'time'})
		## if no hour information in file yet:
		if ' ' not in df1['time'].values[0]:
			df1['time'] = df1['time'].apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d').strftime('%Y-%m-%d {0:02d}:00:00'.format(time_utc)))

		df1[COLUMN] = df1[COLUMN] + 273.15
		df = df1.merge(df2, on='time', how='right')

		## =========================================

		df_duplicates = pd.read_csv(os.path.join(DATAPATH, 'duplicates_utc{0:02d}_d00.csv'.format(time_utc)))
		df_duplicates['time'] = df_duplicates['time'].astype(str)
		df['time'] = df['time'].astype(str)
		df = df.loc[~df['time'].isin(df_duplicates['time'].unique()), :]

		## =========================================

		df['dev'] = (df[COLUMN] - df['t2m_era5_mean']).abs() / df['t2m_era5_std']
		df.loc[df['dev'] > THRESHOLD, COLUMN] = np.nan
		nobs = df[COLUMN].count()
		df_stations.loc[station_id, 'nobs'] = nobs

		df['anomaly_obs'] = df[COLUMN] - df['t2m_era5_mean']
		for d in range(0, 8+1, 1):
			df['anomaly_model'] = df['t2m_d{0:02d}'.format(d)] - df['t2m_era5_mean']
			df_stations.loc[station_id, 'corr_d{0:02d}'.format(d)] = \
					df.loc[:, ['anomaly_obs', 'anomaly_model']].corr().iloc[0, 1]

			if d > 0:
				df['anomaly_d00'] = df['t2m_d00'] - df['t2m_era5_mean']
				df_stations.loc[station_id, 'corr_analysis_d{0:02d}'.format(d)] = \
						df.loc[:, ['anomaly_d00', 'anomaly_model']].corr().iloc[0, 1]

			indices_valid = df[COLUMN].notnull()
			df_stations.loc[station_id, 'diff_d{0:02d}'.format(d)] = \
					((df['t2m_d{0:02d}'.format(d)] - df.loc[indices_valid, 't2m_d{0:02d}'.format(d)].mean()) -\
					(df[COLUMN] - df.loc[indices_valid, COLUMN].mean())).abs().mean()

	df_stations.to_csv(os.path.join(opath, ofile))
