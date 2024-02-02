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

df = pd.read_csv(os.path.join(DATAPATH, 'national_forecasts_wmo.csv'))

## =============================== ##

df_income = pd.read_csv(os.path.join(DATAPATH, 'countries_income.csv'))
code2income = dict(zip(df_income['iso3'].values, df_income['income_group_2020'].values))

## =============================== ##

df['income'] = df['iso3'].apply(lambda x: code2income.get(x, np.nan))
df = df.loc[df['income'].notnull(), :]
df['income'] = df['income'].apply(lambda x: x.replace(' income', ''))
df['income'] = pd.Categorical(df['income'],
		categories=['Low', 'Lower middle', 'Upper middle', 'High'], ordered=True)
df = df.sort_values(by='income', ascending=True)

## =============================== ##

dfg = df.groupby('income')['Forecast'].sum() / df.groupby('income')['Forecast'].count() * 100.

fig, ax = plt.subplots(figsize=(4,4))
for i, income_group in enumerate(['Low', 'Lower middle', 'Upper middle', 'High'][::-1]):
	ax.bar(3-i, dfg.loc[income_group], color=COLORS_INCOME[::-1][i], label='{0:s}'.format(income_group))
ax.set_ylabel('Percentage of countries reporting\n an official national forecast to the WMO')
ax.set_xlabel('Income group')
ax.set_xticks([0., 1., 2., 3.])
ax.set_xticklabels([l.replace('middle', 'm.') for l in dfg.index.values])
#ax.legend()
#ax.set_ylim(0., 0.8)
sns.despine(ax=ax, offset=1., right=True, top=True)
#ax.set_xticklabels(ax.get_xticklabels(), rotation=20, ha='right')
fig.savefig('./figures/bars_national_forecast_wmo.pdf', bbox_inches='tight', transparent=True)
