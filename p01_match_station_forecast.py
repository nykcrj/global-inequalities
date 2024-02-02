#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import copy

import socket
import subprocess

import numpy as np
import pandas as pd
import xarray as xr

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
SUBSET = False

## =============================== ##

ipath = os.path.join(DATAPATH, '')
if SUBSET == True:
	df_subset = pd.read_csv(os.path.join(ipath, 'stations_1985-2020_continuous.csv'))
else:
	df_subset = pd.read_csv(os.path.join(ipath, 'stations_1985-2020_nobs.csv'))
df_subset['station_id'] = df_subset['station_id'].apply(lambda x: correct_station_id(x))
stations_subset = df_subset['station_id'].unique()

#stations_subset = ['72231612958']

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
	
	opath = os.path.join(DATAPATH, 'noaa_isd_forecast_era5')
	if not os.path.exists(opath):
		os.mkdir(opath)

	for station_id in df_stations.index.values:

		print(station_id)

		#if year < 2007:
		#	time_utc = 12
		#else:
		#	time_utc = 0

		time_utc = 12

		ofile = os.path.join(opath, str(year), '{0:s}_{1:d}_utc{2:02d}_t2m.csv'.format(station_id, year, time_utc))

		## PREVENT OVERWRITING EXISTING FILES
		if os.path.exists(ofile):
			continue

		lat, lon = df_stations.loc[station_id, ['lat', 'lon']].values
		if pd.isnull(lat) or pd.isnull(lon):
			print('Station coordinates not found: ', station_id)
			continue
		
		## =========================================

		forecastdir = os.path.join(DATAPATH, 'ecmwf_utc{0:02d}'.format(time_utc))

		for d in range(0, 8+1, 1):
			
			forecastfile = 'ecmwf_{0:04d}_utc{1:02d}_d{2:02d}_t2m.nc'.format(year, time_utc, d)
			forecastfile_prior = 'ecmwf_{0:04d}_utc{1:02d}_d{2:02d}_t2m.nc'.format(year-1, time_utc, d)

			tempfile1 = 'temp_{0:d}_{1:s}_d{2:02d}.nc'.format(year, station_id, d)
			tempfile2 = 'temp_{0:d}_{1:s}_d{2:02d}_prior.nc'.format(year, station_id, d)

			cdo_command = 'cdo -O -b 32 remapnn,lon={0:f}_lat={1:f} -setgridtype,regular {2:s} {3:s}'.format(\
					lon, lat,
					os.path.join(forecastdir, forecastfile),
					tempfile1
					)
			result = subprocess.check_output(cdo_command, shell=True)
			print(result)

			if (year > 1985) & (d > 0):
				cdo_command = 'cdo -O -b 32 remapnn,lon={0:f}_lat={1:f} -setgridtype,regular -selyear,{2:04d} {3:s} {4:s}'.format(\
						lon, lat, year,
						os.path.join(forecastdir, forecastfile_prior),
						tempfile2
						)
				result = subprocess.check_output(cdo_command, shell=True)
				print(result)

				cdo_command = 'cdo -O mergetime {0:s} {1:s} {0:s}'.format(\
					tempfile1,
					tempfile2)
				result = subprocess.check_output(cdo_command, shell=True)
				print(result)

				os.remove(tempfile2)

			df = xr.open_dataset(tempfile1).to_dataframe().reset_index().drop(columns=['lon', 'lat'])
			df = df.rename(columns={'2t': 't2m_d{0:02d}'.format(d), 'var167': 't2m_d{0:02d}'.format(d)})
			if d == 0:
				df_all = df
			else:
				df_all = df_all.merge(df, on=['time'], how='outer')

			os.remove(tempfile1)
		
		## =========================================
		
		era5dir = os.path.join(DATAPATH, 'era5')
		era5file = 'era5_1991-2020_utc{0:02d}_t2m_ydaymean.nc'.format(time_utc)

		tempfile = 'temp_{0:d}_{1:s}_d{2:02d}.nc'.format(year, station_id, d)

		cdo_command = 'cdo -O -b 32 setyear,{0:d} -remapnn,lon={1:f}_lat={2:f} {3:s} {4:s}'.format(\
					year, lon, lat,
					os.path.join(era5dir, era5file),
					tempfile
					)
		result = subprocess.check_output(cdo_command, shell=True)
		print(result)

		df = xr.open_dataset(tempfile).to_dataframe().reset_index().drop(columns=['lon', 'lat'])
		df = df.rename(columns={'t2m': 't2m_era5_mean'})
		df_all = df_all.merge(df, on=['time'], how='outer')

		## ===

		era5dir = os.path.join(DATAPATH, 'era5')
		era5file = 'era5_1991-2020_utc{0:02d}_t2m_ydaystd.nc'.format(time_utc)

		cdo_command = 'cdo -O -b 32 setyear,{0:d} -remapnn,lon={1:f}_lat={2:f} {3:s} {4:s}'.format(\
					year, lon, lat,
					os.path.join(era5dir, era5file),
					tempfile
					)
		result = subprocess.check_output(cdo_command, shell=True)
		print(result)

		df = xr.open_dataset(tempfile).to_dataframe().reset_index().drop(columns=['lon', 'lat'])
		df = df.rename(columns={'t2m': 't2m_era5_std'})
		df_all = df_all.merge(df, on=['time'], how='outer')
		
		## =========================================

		df_all.to_csv(ofile, index=False)
		
		os.remove(tempfile)
