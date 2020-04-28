datasets:

1. redispatch_date.csv 
	-raw data downloaded from https://www.netztransparenz.de/EnWG/Redispatch	
	-total redispatch quantities per plant per period
	-start and end timestamp specified for periods
2. redispatch_hourly_data.xlsx
	-redispatch quantities spread over hourly timeframe
3. redispatch_hourly_plot.csv
	-subset of redispatch_hourly_data.xlsx
	-faster reading for visualization usage
4. redispatch_hourly_201701.xlsx
	-total redispatch quantities per hour
	-timeframe: 2017-01 (corresponding to dataset_de)
	-index t0xyz

Visualizations


to start visualization app on local host use (command line):

bokeh serve --show redispatchApp.py

app starts automatically in browser