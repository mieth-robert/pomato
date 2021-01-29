# -*- coding: utf-8 -*-
"""
Created on Mon May  4 14:38:08 2020

@author: OediP
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt 

# %%Init POMATO with the options file and the dataset
from pomato import POMATO
import pickle

datasets = ["dataset_de_new","dataset_de_new_2","dataset_de_demand_export"]
results_pickle = list(map(lambda x: "data_output/"+x+"_results.pickle",datasets))
to_load = ["mato.data","gen","df1","df2","df3","df4","infeas_redisp","infeas_market","redisp_result","market_result"]#,mato]
for dataset,result in zip(datasets,results_pickle):
    name = dataset.split("_",2)[-1]
    exec("{} = dict()".format(name))
    with open(result,"rb") as f:
        exec("{}['mato'] = POMATO(wdir=Path.cwd(), options_file='profiles/de.json')".format(name))
        exec("{}['mato'].data = pickle.load(f)".format(name))
        for i in to_load[1:]:
            exec("{}['{}'] = pickle.load(f)".format(name,i))
        
redispatch_data = pd.read_excel("redispatch/redispatch_hourly_data.xlsx")
redispatch_data_1701 = pd.read_excel("redispatch/redispatch_de_hourly_201701.xlsx")

##plots und data
#redispatch über zeit, average jan, first day jan
#top 10 nodes new , demand
#top 10 nodes über zeit
#top 10 nodes über zeit nach fuel
# untersuchung knoten 7270
# top 3 knoten, benachbarte knoten nach summe gmax untersuchen

# indicator average daily redispatch

# dataframe scenario, total_redispatch, avg_daily_redispatch,std_daily_redispatch,avg_hourly_redispatch,std_hourly_redispatch,min,.25,.5,.75,max
# scenarios overall,1701, new,demand_export

# %%benchmark overall berechnen
redispatch_data.groupby("time")["redispatch_abs"].sum().describe()

# benchmark 1701 berechnen
redispatch_data_1701["redispatch_abs"].describe()

# demand_export
demand_export["gen"].groupby("t")["delta_abs"].sum().describe()

# new
new["gen"].groupby("t")["delta_abs"].sum().describe()

# %% plot benchmark vs. model
redispatch_comparison = pd.DataFrame()
redispatch_comparison["new"] = new["gen"].groupby("t")["delta_abs"].sum()
redispatch_comparison.reset_index(inplace=True)
demand_export_delta_abs = demand_export["gen"].groupby("t")["delta_abs"].sum()
demand_export_delta_abs = demand_export_delta_abs.reset_index()
redispatch_comparison = redispatch_comparison.merge(demand_export_delta_abs,how="outer",on="t")
new_2_delta_abs = new_2["gen"].groupby("t")["delta_abs"].sum()
new_2_delta_abs = new_2_delta_abs.reset_index()
redispatch_comparison = redispatch_comparison.merge(new_2_delta_abs,how="outer",on="t")


redispatch_data_1701["t"] = pd.DatetimeIndex(redispatch_data_1701["utc_timestamp"]).hour+1

#average hourly redispatch for first month
benchmark = redispatch_data_1701.groupby("t")["redispatch_abs"].mean()
benchmark = benchmark.reset_index()
benchmark["t"] = list(map(lambda x: "t"+str(x).zfill(4),benchmark["t"].values))
redispatch_comparison = redispatch_comparison.merge(benchmark,how="outer",on="t")

#first week only
redispatch_0101 = redispatch_data_1701[redispatch_data_1701["utc_timestamp"] < "2017-01-02"]
redispatch_0101 = redispatch_0101[["index","redispatch_abs"]]
redispatch_0101.columns = ["t","redispatch_abs"]
redispatch_comparison = redispatch_comparison.merge(redispatch_0101[["t","redispatch_abs"]],how = "outer",on="t")#    
redispatch_comparison.columns = ["t","new","demand_export","new_2","benchmark","benchmark01"]

#model nur erster tag oder gemittelt?
#alle tage gemittelt über stunde
plt.plot(redispatch_comparison[["new","demand_export","new_2","benchmark","benchmark01"]])
plt.legend(labels=["new","demand_export","new_2","benchmark","benchmark01"])
plt.show()

############
# %% total redispatch values
redispatch_comparison[["new","demand_export","benchmark"]].sum().plot()
plt.show()

##get correlations fuel
#new["gen"][["fuel","delta_abs"]].boxplot(by="fuel")
#plt.show()
#
##get correlations plant_type
#new["gen"][["plant_type","delta_abs"]].boxplot(by="plant_type")
#plt.show()
#
##get correlations tech
#new["gen"][["tech","delta_abs"]].boxplot(by="tech")
#plt.show()
#
#############
#
##get correlations fuel
#new["gen"][["fuel","delta_abs"]].groupby("fuel").sum()
#
##get correlations plant_type
#new["gen"][["plant_type","delta_abs"]].groupby("plant_type").sum()
#
##get correlations tech
#new["gen"][["tech","delta_abs"]].groupby("tech").sum()
#
# %% new
#check nodes with highest redispatch
top10 = new["gen"].groupby("node")["delta_abs"].sum().sort_values(ascending=False).head(10)
print(top10)
#top 3 sum of delta
top3 = new["gen"].groupby("node")["delta_abs"].sum().sort_values(ascending=False).head(3).sum()
top3/redispatch_comparison[["new"]].sum().values

# %% demand_export
demand_export["gen"].groupby("node")["delta_abs"].sum().sort_values(ascending=False).head(10)

# %%
#plot redispatch per node
n4630_new = new["gen"][new["gen"]["node"] == "n4630"]
plt.plot(n4630_new.groupby("t")["delta_abs"].sum())
plt.show()
#
##see degree of node
#lines_new = new["mato"].data.lines
#lines_new[lines_new["node_i"] == "n4634"]
#lines_new[lines_new["node_j"] == "n4634"]
##4634 nur eine line
#
#
#nodes_new = new["mato"].data.nodes
#degree = list()
#for i in nodes_new.index:
#    first = len(lines_new[lines_new["node_i"] == i]["node_j"].unique())
#    second = len(lines_new[lines_new["node_j"] == i]["node_i"].unique())
#    degree.append(first+second)
#nodes_new["degree"] = degree
#
#new_node_delta = new["gen"].groupby("node")["delta_abs"].sum()
#new_node_delta.index.name = "index"
#pd.merge(nodes_new["degree"],new_node_delta,how = "outer",on="index").plot.scatter(x="degree",y="delta_abs")
#plt.show()

# %% g_max per node
print(new["mato"].data.plants.groupby("node")["g_max"].sum().sort_values(ascending=False).head(10))
print(demand_export["mato"].data.plants.groupby("node")["g_max"].sum().sort_values(ascending=False).head(10))

# %%
#new 
#neighbors of top3 nodes
top3_new = top10[:3]
lines_new = new["mato"].data.lines
i_j = lines_new[np.isin(lines_new["node_i"].values,top3_new.index.values)][["node_i","node_j"]]
j_i = lines_new[np.isin(lines_new["node_j"].values,top3_new.index.values)][["node_i","node_j"]]
neighborstop3 = list(set(pd.concat([i_j,j_i]).values.flatten()))

demand_new = new["mato"].data.demand_el
demand_new = demand_new[np.isin(demand_new["node"].values,neighborstop3)]
demand_new = demand_new.groupby("node")["demand_el"].sum()
gmax_new = new["mato"].data.plants
gmax_new = gmax_new[np.isin(gmax_new["node"].values,neighborstop3)]
gmax_new = gmax_new.groupby("node")["g_max"].sum()
gmax_new.sort_index()
demand_new.sort_index()
demand_new.index.values == gmax_new.index.values
neighbors_compare = pd.DataFrame([demand_new,gmax_new]).transpose()
neighbors_compare["demand/gmax"] = neighbors_compare["demand_el"]/neighbors_compare["g_max"]


# %% 

#all plants von n4630 und n4634 distances zu n4635

from sklearn.metrics.pairwise import haversine_distances
from math import radians

new_plants = new["mato"].data.plants
new_plants = new_plants[np.isin(new_plants["node"].values,["n4630","n4634","n4635"])]

n4635_location = (radians(51.113869),radians(6.628876))
n4634_location = (radians(51.061249),radians(6.551971))
n4630_location = (radians(50.995607),radians(6.58959790990991))
new_plants["lat_rad"] = new_plants["lat"].apply(radians)
new_plants["lon_rad"] = new_plants["lon"].apply(radians)

dist = haversine_distances(new_plants[["lat_rad","lon_rad"]].values,np.array(n4635_location).reshape((1,2)))
new_plants["distance_n4635"] = dist
dist = haversine_distances(new_plants[["lat_rad","lon_rad"]].values,np.array(n4634_location).reshape((1,2)))
new_plants["distance_n4634"] = dist
dist = haversine_distances(new_plants[["lat_rad","lon_rad"]].values,np.array(n4630_location).reshape((1,2)))
new_plants["distance_n4630"] = dist

new_plants[["g_max","distance_n4635"]].groupby("distance_n4635").sum()
new_plants_compare =new_plants[["node","g_max","distance_n4635","distance_n4634","distance_n4630"]]
new_plants_compare["min_node"] = pd.Series(np.argmin(new_plants_compare[["distance_n4635","distance_n4630","distance_n4634"]].values,1)).map({0:"n4635",1:"n4630",2:"n4634"}).values
new_plants_compare = new_plants_compare.sort_values("distance_n4635")






