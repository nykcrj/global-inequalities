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

dfg = pd.read_csv(os.path.join(DATAPATH, 'data_countries_timeseries.csv'))

## =============================== ##

dfg2 = dfg.groupby(['year', 'income_group_2020']).mean().reset_index()

## =============================== ##

colors = COLORS_INCOME
markers = ['o', '^', 's', '*']

ROLLING_WINDOW = 5
fig, ax = plt.subplots(figsize=(4,4))
for d in [1]:
	x = dfg2.loc[dfg2['income_group_2020'] == 'High', 'year'].rolling(ROLLING_WINDOW, center=True).mean()
	y = dfg2.loc[dfg2['income_group_2020'] == 'High', 'corr_d{0:02d}'.format(d)].rolling(ROLLING_WINDOW, center=True).mean()
	#y = y / y[x == 2000.].values * 100.
	ax.plot(x, y, '-', color=colors[3], marker=markers[0], markersize=4, label='High')#, {0:d} days ahead'.format(d))
for d in [1]:
	x = dfg2.loc[dfg2['income_group_2020'] == 'Upper middle', 'year'].rolling(ROLLING_WINDOW, center=True).mean()
	y = dfg2.loc[dfg2['income_group_2020'] == 'Upper middle', 'corr_d{0:02d}'.format(d)].rolling(ROLLING_WINDOW, center=True).mean()
	#y = y / y[x == 2000.].values * 100.
	ax.plot(x, y, '-', color=colors[2], marker=markers[1], markersize=4, label='Upper middle')#, {0:d} days ahead'.format(d))
for d in [1]:
	x = dfg2.loc[dfg2['income_group_2020'] == 'Lower middle', 'year'].rolling(ROLLING_WINDOW, center=True).mean()
	y = dfg2.loc[dfg2['income_group_2020'] == 'Lower middle', 'corr_d{0:02d}'.format(d)].rolling(ROLLING_WINDOW, center=True).mean()
	#y = y / y[x == 2000.].values * 100.
	ax.plot(x, y, '-', color=colors[1], marker=markers[2], markersize=4, label='Lower middle')#, {0:d} days ahead'.format(d))
for d in [1]:
	x = dfg2.loc[dfg2['income_group_2020'] == 'Low', 'year'].rolling(ROLLING_WINDOW, center=True).mean()
	y = dfg2.loc[dfg2['income_group_2020'] == 'Low', 'corr_d{0:02d}'.format(d)].rolling(ROLLING_WINDOW, center=True).mean()
	#y = y / y[x == 2000.].values * 100.
	ax.plot(x, y, '-', color=colors[0], marker=markers[3], markersize=4, label='Low')#, {0:d} days ahead'.format(d))
ax.set_xticks(np.arange(1985, 2020+5, 5))
ax.set_ylim(0.25, 0.75)
ax.set_ylabel('Forecast accuracy\n(correlation of anomalies)')
ax.legend(fontsize='medium', ncols=1, markerscale=0.5, handlelength=2, title='Income group',
		title_fontsize = 'medium', alignment = 'left')
sns.despine(ax=ax, offset=1., right=True, top=True)
fig.savefig('./figures/timeseries_incomegroups_runningmean.pdf', bbox_inches='tight', transparent=True)

## =============================== ##

dfg['tropics'] = 'extratropics'
dfg.loc[dfg['lat'].abs() < 23.5, 'tropics'] = 'tropics'
dfg3 = dfg.groupby(['year', 'tropics']).mean().reset_index()

## =============================== ##

dfg['tropics'] = 'extratropics'
dfg.loc[dfg['lat'].abs() < 23.5, 'tropics'] = 'tropics'
dfg['hemisphere'] = 'NH'
dfg.loc[dfg['lat'] < 0., 'hemisphere'] = 'SH'

dfg3a = dfg.loc[dfg['year'].between(1991, 2000), :].groupby('tropics').mean()
dfg3b = dfg.loc[dfg['year'].between(2001, 2010), :].groupby('tropics').mean()
dfg3c = dfg.loc[dfg['year'].between(2011, 2020), :].groupby('tropics').mean()

dfg3a_std = dfg.loc[dfg['year'].between(1991, 2000), :].groupby('tropics').std()
dfg3b_std = dfg.loc[dfg['year'].between(2001, 2010), :].groupby('tropics').std()
dfg3c_std = dfg.loc[dfg['year'].between(2011, 2020), :].groupby('tropics').std()

dfg4a = dfg.loc[dfg['year'].between(1991, 2000), :].groupby('hemisphere').mean()
dfg4b = dfg.loc[dfg['year'].between(2001, 2010), :].groupby('hemisphere').mean()
dfg4c = dfg.loc[dfg['year'].between(2011, 2020), :].groupby('hemisphere').mean()

dfg4a_std = dfg.loc[dfg['year'].between(1991, 2000), :].groupby('hemisphere').std()
dfg4b_std = dfg.loc[dfg['year'].between(2001, 2010), :].groupby('hemisphere').std()
dfg4c_std = dfg.loc[dfg['year'].between(2011, 2020), :].groupby('hemisphere').std()

dfg5a = dfg.loc[dfg['year'].between(1991, 2000), :].groupby('income_group_2020').mean()
dfg5b = dfg.loc[dfg['year'].between(2001, 2010), :].groupby('income_group_2020').mean()
dfg5c = dfg.loc[dfg['year'].between(2011, 2020), :].groupby('income_group_2020').mean()

dfg5a_std = dfg.loc[dfg['year'].between(1991, 2000), :].groupby('income_group_2020').std()
dfg5b_std = dfg.loc[dfg['year'].between(2001, 2010), :].groupby('income_group_2020').std()
dfg5c_std = dfg.loc[dfg['year'].between(2011, 2020), :].groupby('income_group_2020').std()

colors = [COLOR2, COLOR4, COLOR6]

for region in ['tropics', 'extratropics']:
	fig, ax = plt.subplots(figsize=(4,4))
	for t, dfx in enumerate([dfg3a, dfg3b, dfg3c]):
		for d in [1, 2, 3]:
			color = colors[d-1]
			y = dfx.loc[region, 'corr_d{0:02d}'.format(d)]
			if t == 1:
				ax.bar(t*4 + d, y, color=color, label='{0:d} days ahead'.format(d))
			else:
				ax.bar(t*4 + d, y, color=color)
			if t >= 0:
				delta = y - dfg3a.loc[region, 'corr_d{0:02d}'.format(d)]
				ax.annotate(text='{0:3.2f}'.format(y),
					xy=(t*4 + d, y - 0.01), xycoords='data', va='top', ha='center', color='white', rotation=90.)
	ax.set_title(region.capitalize(), ha='left', loc='left')
	ax.set_xlabel('')#'Time period')
	ax.set_ylabel('Forecast accuracy\n(correlation of anomalies)')
	ax.set_xticks([2, 6, 10])
	ax.set_xticklabels(['1991-2000', '2001-2010', '2011-2020'])
	ax.legend()
	ax.set_ylim(0., 1.0)
	sns.despine(ax=ax, offset=1., right=True, top=True)
	fig.savefig('./figures/bars_{0:s}.pdf'.format(region), bbox_inches='tight', transparent=True)

dfx_std = [dfg3a_std, dfg3b_std, dfg3c_std]
colors = [COLOR2, COLOR4, COLOR6]
fig, ax = plt.subplots(figsize=(4,4))
for t, dfx in enumerate([dfg3a, dfg3b, dfg3c]):
	d = 1
	for r, region in enumerate(['extratropics', 'tropics']):
		color = colors[r]
		y = dfx.loc[region, 'corr_d{0:02d}'.format(d)]
		if t == 1:
			ax.bar(t*3 + r, y, color=color, label='{0:s}'.format(region.capitalize()))
		else:
			ax.bar(t*3 + r, y, color=color)
		ax.errorbar(t*3 + r+0.1, y,
					dfx_std[t].loc[region, 'corr_d{0:02d}'.format(d)], capsize=4., color='grey', lw=0.5)
		if t >= 0:
			delta = y - dfg3a.loc[region, 'corr_d{0:02d}'.format(d)]
			ax.annotate(text='{0:3.2f}'.format(y),
				xy=(t*3 + r + 0.05, y - 0.01), xycoords='data', va='top', ha='right', rotation=90., color='white')
#ax.set_title(region.capitalize())
ax.set_xlabel('')#'Time period')
ax.set_ylabel('Forecast accuracy\n(correlation of anomalies)')
ax.set_xticks([0.5, 3.5, 6.5])
ax.set_xticklabels(['1991-2000', '2001-2010', '2011-2020'])
ax.legend()
ax.set_ylim(0., 1.0)
ax.tick_params(labelbottom=True, labeltop=False, labelleft=False, labelright=True,
				bottom=True, top=False, left=True, right=True)
ax.yaxis.set_label_position("right")
sns.despine(ax=ax, offset=1., right=False, top=True)
fig.savefig('./figures/bars_tropics-extratropics.pdf', bbox_inches='tight', transparent=True)

colors = [COLOR2, COLOR4, COLOR6]
for region in ['NH', 'SH']:
	fig, ax = plt.subplots(figsize=(4,4))
	for t, dfx in enumerate([dfg4a, dfg4b, dfg4c]):
		for d in [1, 2, 3]:
			color = colors[d-1]
			y = dfx.loc[region, 'corr_d{0:02d}'.format(d)]
			if t == 1:
				ax.bar(t*4 + d, y, color=color, label='{0:d} days ahead'.format(d))
			else:
				ax.bar(t*4 + d, y, color=color)
			if t >= 0:
				delta = y - dfg4a.loc[region, 'corr_d{0:02d}'.format(d)]
				ax.annotate(text='{0:3.2f}'.format(y),
					xy=(t*4 + d, y - 0.01), xycoords='data', va='top', ha='center', color='white', rotation=90.)
	ax.set_title(region.upper(), ha='left', loc='left')
	ax.set_xlabel('')#'Time period')
	ax.set_ylabel('Forecast accuracy\n(correlation of anomalies)')
	ax.set_xticks([2, 6, 10])
	ax.set_xticklabels(['1991-2000', '2001-2010', '2011-2020'])
	ax.legend()
	ax.set_ylim(0., 1.0)
	sns.despine(ax=ax, offset=1., right=True, top=True)
	fig.savefig('./figures/bars_{0:s}.pdf'.format(region), bbox_inches='tight', transparent=True)

dfx_std = [dfg4a_std, dfg4b_std, dfg4c_std]
colors = [COLOR3, COLOR6]
fig, ax = plt.subplots(figsize=(4,4))
for t, dfx in enumerate([dfg4a, dfg4b, dfg4c]):
	d = 1
	for r, region in enumerate(['NH', 'SH']):
		color = colors[r]
		y = dfx.loc[region, 'corr_d{0:02d}'.format(d)]
		if t == 1:
			ax.bar(t*3 + r, y, color=color, label='{0:s}'.format(region))
		else:
			ax.bar(t*3 + r, y, color=color)
		ax.errorbar(t*3+0.1 + r, y,
					dfx_std[t].loc[region, 'corr_d{0:02d}'.format(d)], capsize=4., color='grey', lw=0.5)
		if t >= 0:
			if r == 0:
				color='k'
			else:
				color='w'
			delta = y - dfg4a.loc[region, 'corr_d{0:02d}'.format(d)]
			ax.annotate(text='{0:3.2f}'.format(y),
				xy=(t*3 + r + 0.05, y - 0.01), xycoords='data', va='top', ha='right', rotation=90., color=color)
#ax.set_title(region.capitalize())
ax.set_xlabel('')#'Time period')
ax.set_ylabel('Forecast accuracy\n(correlation of anomalies)')
ax.set_xticks([0.5, 3.5, 6.5])
ax.set_xticklabels(['1991-2000', '2001-2010', '2011-2020'])
ax.legend()
ax.set_ylim(0., 1.0)
sns.despine(ax=ax, offset=1., right=True, top=True)
fig.savefig('./figures/bars_NH-SH.pdf', bbox_inches='tight', transparent=True)

colors = COLORS_INCOME[::-1]
dfx_std = [dfg5a_std, dfg5b_std, dfg5c_std]
fig, ax = plt.subplots(figsize=(4,4))
for t, dfx in enumerate([dfg5a, dfg5b, dfg5c]):
	#for d in [1, 2, 3]:
	d = 1
	for i, income_group in enumerate(['Low', 'Lower middle', 'Upper middle', 'High'][::-1]):
		#color = colors[d]
		color = colors[i]
		y = dfx.loc[income_group, 'corr_d{0:02d}'.format(d)]
		if t == 0:
			ax.bar(t*5 + 3-i, y, color=color, label='{0:s}'.format(income_group))
		else:
			ax.bar(t*5 + 3-i, y, color=color)
		#ax.errorbar(t*5 + 3-i, y,
		#			dfx_std[t].loc[income_group, 'corr_d{0:02d}'.format(d)], capsize=4., color='grey', lw=0.5)
		if t >= 0:
			delta = y - dfg5a.loc[income_group, 'corr_d{0:02d}'.format(d)]
			ax.annotate(text='{0:3.2f}'.format(y),
				xy=(t*5 + 3-i, y - 0.005), xycoords='data', va='top', ha='center', rotation=90.)
ax.set_xlabel('')#'Time period')
ax.set_ylabel('Forecast accuracy\n(correlation of anomalies)')
ax.set_xticks([1.5, 6.5, 11.5])
ax.set_xticklabels(['1991-2000', '2001-2010', '2011-2020'])
ax.legend(title='Income group', alignment='left')
ax.set_ylim(0.25, 0.75)
ax.tick_params(labelbottom=True, labeltop=False, labelleft=False, labelright=True,
				bottom=True, top=False, left=True, right=True)
ax.yaxis.set_label_position("right")
sns.despine(ax=ax, offset=1., right=False, top=True)
fig.savefig('./figures/bars_{0:s}.pdf'.format('income'), bbox_inches='tight', transparent=True)

y1 = dfg5c.loc['High', 'corr_d01']
y2 = dfg5c.loc['Low', 'corr_d01']
print(y1, y2, (y1-y2)/y2)
