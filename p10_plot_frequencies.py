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

df_gdp = pd.read_csv(os.path.join(DATAPATH, 'countries_income.csv'))
df_gdp = df_gdp.loc[df_gdp['income_group_2020'].notnull(), :]
df_gdp['income_group_2020'] = pd.Categorical(df_gdp['income_group_2020'],
		categories=['Low', 'Lower middle', 'Upper middle', 'High'], ordered=True)

## =============================== ##
## stations

df = pd.read_csv(os.path.join(DATAPATH, 'stations_1985-2020_nobs.csv'))
df = df.loc[df['year'].between(1985, 2020), :]
df = df.loc[(df['slp_utc12'] > 0.) | (df['slp_utc00'] > 0.), :]
df['nobs'] = (df['slp_utc12'] + df['slp_utc00']) / 2.

dfc = pd.read_csv(os.path.join(DATAPATH, 'stations_1985-2020_countries.csv'))
dfc = dfc.drop(columns=['lat', 'lon'])
df = df.merge(dfc, on=['station_id', 'year'], how='left')

dfg1 = (df.loc[df['year'].between(2011, 2020), :].groupby('iso3')['nobs'].sum() / 365.).reset_index()
dfg2 = (df.loc[df['year'].between(2011, 2020), :].groupby('iso3')['station_id'].count()).reset_index()
dfg = dfg1.merge(dfg2, on='iso3')
dfg['frequency_nobs'] = dfg['nobs'] / dfg['station_id']

dfm = dfg.merge(df_gdp, on='iso3', how='left')
dfm = dfm.loc[dfm['income_group_2020'].notnull(), :]
dfm = dfm.sort_values(by='income_group_2020', ascending=True)
dfm = dfm.loc[~dfm.duplicated(), :]

colors = COLORS_INCOME

fig, ax = plt.subplots(figsize=(4,4))
sns.violinplot(ax=ax, data=dfm, x='income_group_2020', y='frequency_nobs', fliersize=0, showfliers=False, palette=colors, cut=0)
ax.set_ylabel('Number of observations\nper reporting time (12 UTC, 0 UTC)')
ax.set_xlabel('Income group')
ax.set_xticklabels(dfm['income_group_2020'].apply(lambda x: x.replace('middle', 'm.')).unique())
sns.despine(ax=ax, offset=1., right=True, top=True)
fig.savefig('./figures/violins_incomegroup_2011-2020_stations_frequency.pdf', bbox_inches='tight', transparent=True)

## =============================== ##
## radiosondes

df = pd.read_csv(os.path.join(DATAPATH, 'radiosondes_1985-2020_nobs.csv'))
df = df.loc[df['year'].between(1985, 2020), :]
df_iso = pd.read_csv(os.path.join(DATAPATH, 'radiosondes_1985-2020.csv'))
df_iso = df_iso.loc[:, ['radiosonde_id', 'iso3']]
df = df.merge(df_iso, on='radiosonde_id', how='left')

df = df.loc[df['iso3'].notnull(), :]
df = df.drop(columns=['year_first', 'year_last'])

dfg1 = (df.loc[df['year'].between(2011, 2020), :].groupby('iso3')['nobs'].sum() / 365.).reset_index()
dfg2 = (df.loc[df['year'].between(2011, 2020), :].groupby('iso3')['radiosonde_id'].count()).reset_index()
dfg = dfg1.merge(dfg2, on='iso3')
dfg['frequency_nobs'] = dfg['nobs'] / dfg['radiosonde_id']

dfm = dfg.merge(df_gdp, on='iso3', how='left')
dfm = dfm.loc[dfm['income_group_2020'].notnull(), :]
dfm = dfm.sort_values(by='income_group_2020', ascending=True)
dfm = dfm.loc[~dfm.duplicated(), :]

colors = COLORS_INCOME

fig, ax = plt.subplots(figsize=(4,4))
sns.violinplot(ax=ax, data=dfm, x='income_group_2020', y='frequency_nobs', fliersize=0, showfliers=False, palette=colors, cut=0)
ax.set_ylabel('Number of reports per day')
ax.set_xlabel('Income group')
ax.set_xticklabels(dfm['income_group_2020'].apply(lambda x: x.replace('middle', 'm.')).unique())
sns.despine(ax=ax, offset=1., right=True, top=True)
fig.savefig('./figures/violins_incomegroup_2011-2020_radiosondes_frequency.pdf', bbox_inches='tight', transparent=True)

## =============================== ##

