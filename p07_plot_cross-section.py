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
income2color = dict(zip(['High', 'Upper middle', 'Lower middle', 'Low'], COLORS_INCOME[::-1]))

## =============================== ##

def linear_fit_predictions(dataframe, variable_y, variables_x):
	formula = '{0:s} ~ {1:s}'.format(variable_y, ' + '.join(variables_x))
	res = sm.OLS.from_formula(formula=formula, data=dataframe).fit(missing='drop').get_robustcov_results()
	pred = res.get_prediction(dataframe).summary_frame(alpha=0.05)
	pred.loc[:, variables_x] = dataframe.loc[:, variables_x].values
	dx = res.summary2(float_format="%.5f").tables[1].iloc[:, [0, 1, 3]]
	return pred, dx

## =============================== ##
## auxiliary data

datafile = "countries.shp"
gdf_countries = gpd.read_file(os.path.join(DATAPATH, datafile))
gdf_countries = gdf_countries.loc[:, ['iso3', 'geometry']]

## ============================================================== ##

# aggregated from stations
dfa = pd.read_csv(os.path.join(DATAPATH, 'data_countries_unweighted.csv'))

# aggregated from stations via a hexagonal mesh using population weights
dfw = pd.read_csv(os.path.join(DATAPATH, 'data_countries_weighted.csv'))

## ============================================================== ##
## figure 1 b, c

xvariable = 'log_gdp_pc_2011_2020'
yvariable = 'corr_d01_all'

dfr = dfw.loc[dfw.loc[:, [xvariable, yvariable]].isnull().sum(axis=1) == 0, :]
dfr = dfr.sort_values(by=[xvariable], ascending=True).set_index('iso3')

colors = COLORS_INCOME

fig, axes = plt.subplots(figsize=(6,4), ncols=2, sharey=True, gridspec_kw={'wspace': 0.1, 'width_ratios': [1., 0.3]})
for iso in dfr.index.values:
	x = dfr.loc[iso, xvariable]
	y = dfr.loc[iso, yvariable]
	axes[0].plot(x, y, 'o', markersize=1., color='none')
	axes[0].annotate(text=iso, xy=(x, y), xycoords='data', ha='center', va='center', color=income2color[dfr.loc[iso, 'income_group_2020']])
pred, dx = linear_fit_predictions(dfr, yvariable, [xvariable])
axes[0].plot(pred[xvariable], pred['mean'], '-', color='grey', label='{0:3.2f} + {1:3.2f} x'.format(\
	dx.loc['Intercept', 'Coef.'], dx.loc[xvariable, 'Coef.']), lw=2.)
axes[0].fill_between(pred[xvariable], pred['mean_ci_lower'], pred['mean_ci_upper'], color='grey', alpha=0.3)
axes[0].set_xlabel('log GDP pc PPP')
axes[0].set_ylabel('Forecast accuracy \n(correlation of anomalies)')
sns.despine(ax=axes[0], offset=1., right=True, top=True)
sns.boxplot(ax=axes[1], data=dfr, x='income_group_2020', y=yvariable, fliersize=0, palette=colors)
axes[1].set_xlabel('Income group')
axes[1].set_ylabel('')
sns.despine(ax=axes[1], offset=1., right=True, top=True)
axes[1].set_xticklabels([])
axes[0].set_ylim(0., 1.0)
fig.savefig('./figures/scatter_coloured_{0:s}_{1:s}.pdf'.format(xvariable, yvariable), bbox_inches='tight', transparent=True)

## ===========

colors = COLORS_INCOME[::-1]

markers = ['o', '^', 's', '*']
fig, ax = plt.subplots(figsize=(2,4))
for i, income_group in enumerate(dfr['income_group_2020'].unique()[::-1]):
	x = [1, 2, 3, 4, 5, 6, 7]
	y = dfr.loc[dfr['income_group_2020'] == income_group, ['corr_d{0:02d}_all'.format(d) for d in x]].median(axis=0).values
	ax.plot(x, y, '-', marker=markers[i], color=colors[i], label=income_group, markersize=6)
ax.set_ylabel('Forecast accuracy\n (correlation of anomalies)')
ax.set_xlabel('Forecast horizon\n(days ahead)')
ax.legend(fontsize='small', ncols=1, markerscale=0.5, handlelength=3, title='Income group', alignment='left')
sns.despine(ax=ax, offset=1., right=False, left=False, top=True)
ax.set_xticks(x)
ax.set_ylim(0., 1.0)
ax.tick_params(labelbottom=True, labeltop=False, labelleft=False, labelright=True,
				bottom=True, top=False, left=True, right=True)
ax.yaxis.set_label_position("right")
fig.savefig('./figures/lines_incomegroup.pdf', bbox_inches='tight', transparent=True)

## ============================================================== ##
## figure 1 a

gdf = gdf_countries.merge(dfr, on='iso3', how='left')

VARIABLE = 'corr_d01_all'

cmap = plt.cm.Greens
bounds = np.arange(0.2, 1.1, 0.1)
norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
formatcode = '%.1f'

fig, ax = plt.subplots(figsize=(8,4))
ax2 = fig.add_axes([0.94, 0.16, 0.03, 0.68])
cb = mpl.colorbar.ColorbarBase(ax2, cmap=cmap, norm=norm,
				spacing='uniform', ticks=bounds, boundaries=bounds, format=formatcode,
				extend='min', orientation='vertical')
cb.ax.tick_params(labelsize='medium')
cb.set_label(label="Forecast accuracy\n(correlation of anomalies)", size='medium')
ax.set_title(None)
gdf_countries.plot(ax=ax, alpha=1., facecolor='#e7e7e7', lw=0.5, edgecolor='k')
gdf.plot(ax=ax, alpha=1., column=VARIABLE, lw=0.2, cmap=cmap, norm=norm, edgecolor='none', markersize=1.)
gdf_countries.plot(ax=ax, alpha=1., facecolor='none', lw=0.5, edgecolor='k')
ax.set_xlim(-130., 180.)
ax.set_ylim(-60., 75.)
ax.plot(ax.get_xlim(), [-23.5, -23.5], 'k--', linewidth=0.5)
ax.plot(ax.get_xlim(), [23.5, 23.5], 'k--', linewidth=0.5)
ax.set_xlabel(None)
ax.set_ylabel(None)
ax.annotate(text='Forecast 1 day ahead versus station observations', xy=(0.9, 0.08), xycoords='axes fraction', ha='right', va='bottom', fontsize='small')
ax.annotate(text='ECMWF, 2011-2020', xy=(0.9, 0.02), xycoords='axes fraction', ha='right', va='bottom', fontsize='small')
fig.savefig('./figures/map_countries_{0:s}.png'.format(VARIABLE), bbox_inches='tight', dpi=400)

## ============================================================== ##

## other scatter plots for appendix

xvariable = 'log_gdp_pc_2011_2020'

for yvariable in ['corr_d01_all', 'corr_d01_subset']:

	for m, dfm in enumerate([dfa, dfw]):

		label = ['unweighted', 'weighted'][m]

		dfr = dfm.loc[dfm.loc[:, [xvariable, yvariable]].isnull().sum(axis=1) == 0, :]
		dfr = dfr.sort_values(by=[xvariable], ascending=True).set_index('iso3')

		fig, ax = plt.subplots(figsize=(4,4))
		for iso in dfr.index.values:
			x = dfr.loc[iso, xvariable]
			y = dfr.loc[iso, yvariable]
			ax.plot(x, y, 'bo', markersize=1.)
			ax.annotate(text=iso, xy=(x, y), xycoords='data', ha='center', va='center')
		pred, dx = linear_fit_predictions(dfr, yvariable, [xvariable])
		p = dx.loc[xvariable, 'P>|t|']
		ax.plot(pred[xvariable], pred['mean'], '-', color='grey', label='{0:3.2f} + {1:3.2f} x'.format(\
			dx.loc['Intercept', 'Coef.'], dx.loc[xvariable, 'Coef.']), lw=2.)
		ax.fill_between(pred[xvariable], pred['mean_ci_lower'], pred['mean_ci_upper'], color='grey', alpha=0.3)
		ax.set_xlabel('log GDP pc PPP')
		ax.set_ylabel('Forecast accuracy \n(correlation of anomalies)')
		sns.despine(ax=ax, offset=1., right=True, top=True)
		fig.savefig('./figures/scatter_{0:s}_{1:s}_{2:s}.pdf'.format(xvariable, yvariable, label), bbox_inches='tight', transparent=True)

