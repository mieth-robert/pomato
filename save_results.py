# -*- coding: utf-8 -*-
"""
Created on Mon May  4 14:09:58 2020

@author: OediP
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt 

# %% Init POMATO with the options file and the dataset
from pomato import POMATO
import pickle

#datasets = ["dataset_de_no_change"]#,"dataset_de_plants","dataste_de_new","dataset_de_demand_export"]
datasets = ["dataset_de_new","dataset_de_demand_export"]
#datasets = ["dataset_de_new_2_1"]#,"dataset_de_demand_export"]

results_pickle = list(map(lambda x: "data_output/"+x+"_results.pickle",datasets))

for dataset,result_file in zip(datasets,results_pickle):
    mato = POMATO(wdir=Path.cwd(), options_file="profiles/de.json")    
    mato.load_data(r'data_input/{}.xlsx'.format(dataset))
    
    # Acess the data.
    nodes = mato.data.nodes
    lines = mato.grid.lines
    dclines = mato.data.dclines
    demand = mato.data.demand_el
    zones = mato.data.zones
    plants = mato.data.plants
    availability = mato.data.availability
    net_export = mato.data.net_export
    
    # %% Run the Market Model, including (costbased) Re-Dispatch.
    # The Market Result is determined based on the option file.
    # The Redispatrch is done to N-0 per default.
    mato.create_grid_representation()
    mato.update_market_model_data()
    mato.run_market_model()
    
    # There are two market results loaded into data.results.
    # Specify redisp and market result for analysis
    redisp_result = mato.data.results[next(r for r in list(mato.data.results) if "redispatch" in r)]
    market_result = mato.data.results[next(r for r in list(mato.data.results) if "market_result" in r)]
    
    # Check for Overloaded lines N-0, N-1 (should be non for N-0, but plenty for N-1)
    df1, df2 = redisp_result.overloaded_lines_n_1()
    df3, df4 = redisp_result.overloaded_lines_n_0()
    
    # Check for infeasibilities in market / redispatch result.
    infeas_redisp = redisp_result.infeasibility()
    infeas_market = market_result.infeasibility()
    
    # %% Examplary Result Analysis
    
    # Generation comparison between Market Result and Redispatch.
    gen = pd.merge(market_result.data.plants[["plant_type", "fuel", "tech", "g_max", "node"]],
                   market_result.G, left_index=True, right_on="p")
    
    # Redispatch Caluclation G_redispatch - G_market
    gen = pd.merge(gen, redisp_result.G, on=["p", "t"], suffixes=("_market", "_redispatch"))
    gen["delta"] = gen["G_redispatch"] - gen["G_market"]
    gen["delta_abs"] = gen["delta"].abs()
    
    # Generation Plots
#    gen[["fuel", "t", "G_market"]].groupby(["t", "fuel"]).sum().reset_index().pivot(index="t", columns="fuel", values="G_market").plot.area(stacked=True)
#    gen[["fuel", "t", "G_redispatch"]].groupby(["t", "fuel"]).sum().reset_index().pivot(index="t", columns="fuel", values="G_redispatch").plot.area(stacked=True)
#    #plt.show()

    #save data to pickle
    
    
    to_save = [mato.data,gen,df1,df2,df3,df4,infeas_redisp,infeas_market,redisp_result, market_result]
    
    with open(result_file,"wb") as f:
        for i in to_save:
            pickle.dump(i,f)

