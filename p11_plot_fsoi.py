#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import copy

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns

## ===================================================================== ##

# x = density of observations; y = impact per observation
xarr = [74.2628096494201, 287.785078865399, 80.3441477678689, 555.707239309828, 143.974909531427, 1377.5039824771, 23.6614000438885]
yarr = [2.29074889867841E-06, 1.60352422907489E-06, 3.59471365638767E-06, 5.81497797356828E-07, 1.74449339207048E-06, 2.81938325991189E-07, 5.11013215859031E-06]

labels = ['Africa', 'Asia', 'South America', 'North and Central America', 'Pacific', 'Europe', 'Antarctica']

fig, ax = plt.subplots(figsize=(4,4))
for i, label in enumerate(labels):
	x = xarr[i]
	y = yarr[i] / 1.e-6
	ax.plot(x, y, 'o', color='m')
	ax.annotate(text=label, xy=(x, y+0.2), xycoords='data', ha='left', va='center')
ax.set_xlabel('Number of assimilated observations\nper 1,000 km2')
ax.set_ylabel('Impact per observation\n(absolute value in 10e-6 Jkg-1)')
sns.despine(ax=ax, offset=1., right=True, top=True)
fig.savefig('./figures/scatter_fsoi_kull.pdf', bbox_inches='tight', transparent=True)

