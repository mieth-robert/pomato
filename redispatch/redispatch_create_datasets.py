# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 12:25:59 2020

@author: OediP
"""
import numpy as np
import pandas as pd

# data from https://www.netztransparenz.de/EnWG/Redispatch
redispatch = pd.read_csv("redispatch_daten.csv",sep=";")

# combine start date and time
redispatch["start"] = redispatch["BEGINN_DATUM"] +"_"+ redispatch["BEGINN_UHRZEIT"] 
redispatch["start"] = pd.to_datetime(redispatch["start"],format =  "%d.%m.%Y_%H:%M")
redispatch["end"] = redispatch["ENDE_DATUM"] +"_"+ redispatch["ENDE_UHRZEIT"] 
#time zone A alpha, B bravo
redispatch.loc[10892,"end"] = '25.10.2015_02:00'
redispatch.loc[26017,"end"] = '28.10.2018_02:15'
redispatch["end"] = pd.to_datetime(redispatch["end"],format =  "%d.%m.%Y_%H:%M")
redispatch["duration"] = (redispatch["end"] - redispatch["start"]).astype("timedelta64[m]") / 60
redispatch = redispatch[redispatch["end"].values > redispatch["start"].values]
redispatch["MITTLERE_LEISTUNG_MW"] =  redispatch["MITTLERE_LEISTUNG_MW"].str.replace(",",".")

#spreads the total redispatch on all hours between start and end
def create_hour(row):
    row = pd.Series(row._asdict())
    row.drop(["BEGINN_UHRZEIT","BEGINN_DATUM","ENDE_UHRZEIT","ENDE_DATUM","GESAMTE_ARBEIT_MWH"],inplace=True)
    duration = int(np.ceil(row["duration"]))
    weights = np.ones(duration)
    start_time = row["start"]
    if start_time.minute != 0:            
        weights[0] = start_time.minute / 60
    start_time = start_time.floor("h")
    end_time = row["end"]
    if end_time.minute != 0:            
        weights[-1] = row["end"].minute/60
    if row["RICHTUNG"] == "Wirkleistungseinspeisung reduzieren":
        weights = weights * -1
    hours = pd.to_timedelta(range(duration),unit="h")
    hours = hours + start_time
    redispatch = weights * float(row["MITTLERE_LEISTUNG_MW"])
    data = pd.DataFrame({"time":hours,"redispatch":redispatch, "redispatch_abs":np.abs(redispatch)})
    row.drop(["start","end","duration"],inplace=True)
    metadata = [row for i in weights]
    metadata = pd.DataFrame(metadata)
    return pd.concat([data,metadata],1)


redispatch_map = map(create_hour,redispatch.itertuples(index=False))
redispatch_hourly = pd.concat(list(redispatch_map),0)
redispatch_hourly.to_excel("redispatch_hourly_data.xlsx")

#create aggregated hourly dataset for 2017-01 with index t0xyz
redispatch_hourly  =  pd.read_excel("redispatch_hourly_data.xlsx")
redisptach_hourly_201701 = redispatch_hourly[(redispatch_hourly["time"] >= "2017-01-01") & (redispatch_hourly["time"] < "2017-01-31")] 
redispatch_hourly_201701 = redisptach_hourly_201701[["time","redispatch","redispatch_abs"]]    
redispatch_hourly_201701 = redispatch_hourly_201701.groupby("time").sum()
redispatch_hourly_201701["time_diff"] = redispatch_hourly_201701.index - pd.Timestamp("2017-01-01")
redispatch_hourly_201701["time_diff"] =  list(map(lambda x: x.astype("timedelta64[h]").astype(int),redispatch_hourly_201701["time_diff"].values))
redispatch_hourly_201701["index"] = list(map(lambda x: "t"+str(x+1).zfill(4),redispatch_hourly_201701["time_diff"].values))
redispatch_hourly_201701.reset_index(inplace=True)
redispatch_hourly_201701 = redispatch_hourly_201701[["index","redispatch","redispatch_abs","time"]]
redispatch_hourly_201701.columns = ["index","redispatch","redispatch_abs","utc_timestamp"]
redispatch_hourly_201701.to_excel("redispatch_de_hourly_201701.xlsx")