.PHONY: figures clean

figures:
	python3 ./p07_plot_cross-section.py
	python3 ./p08_plot_time-series.py
	python3 ./p09_plot_maps.py
	python3 ./p10_plot_frequencies.py
	python3 ./p11_plot_fsoi.py
	python3 ./p12_plot_national_forecasts_wmo.py

all:
	make clean
	make figures

clean:
	rm ./figures/*