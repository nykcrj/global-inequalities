Overview
--------

The code in this replication package conducts the statistical analysis and produces the results presented in the manuscript. The package consists of several scripts written in Python 3.

Data Availability
----------------------------

All original data are publicly available at no cost.

See the section in the manuscript `Data availability` for more information.

Computational requirements
---------------------------

### Software Requirements

- Python 3.10.9
  - `numpy` 1.23.4
  - `pandas` 1.5.1
  - `scipy` 1.10.0
  - `statsmodels` 0.13.5
  - `geopandas` 0.12.0
  - `xarray` 2022.10.0
  - `matplotlib` 3.6.1
  - `seaborn` 0.12.0

The file `requirements.txt` lists these dependencies, please run `pip install -r requirements.txt` as the first step. See [https://pip.readthedocs.io/en/1.1/requirements.html](https://pip.readthedocs.io/en/1.1/requirements.html) for further instructions on using the `requirements.txt` file.

### Memory and Runtime Requirements

The analysis and visualisation of the processed data requires less than 1 hour on a standard (2024) desktop machine. The processing of the weather forecast and station observation data is not possible on a standard desktop machine. It was done over several weeks on a high performance computer.

Instructions to Replicators
---------------------------

Replication of all figures:
- The file `parameters.py` includes some parameters that can be chosen by the user prior to executing the scripts. These include the file to the data (default: `./data/`) and the colors for the figures.
- The replication is facilitated with a Makefile that runs the scripts in the correct order (`make clean; make all`).
- Note that the name of each script also indicates its relative position in the intended order of execution (i.e. `p01`, `p02`, `p03`, ...).
- Note that scripts with numbers `p01` to `p06` require the original data which can be accessed from the sources listed in the `Data availability` section. Sample files are included in this replication package.
- Some of the scripts store intermediate data in the folder `data`.
- Once all scripts have finished, all figures can be found in the folder `figures`.

For the replication of specific figures, see the following list:
- Figure 1: `p07_plot_cross-section.py`
- Figure 2: `p08_plot_time-series.py`
- Figure 3: `p09_plot_maps.py`
- Figure 4: `p10_plot_frequencies.py`, `p11_plot_fsoi.py`, `p12_plot_national_forecasts_wmo.py`

### License for Code and Data

The code in this repository is provided only for the purpose of replicating the results for peer-review. All other uses of the code or data are strictly prohibited.