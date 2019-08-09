#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug  5 10:14:06 2019

@author: Ty Lazarchik
"""
from ModelDef import TransModel
from tqdm import tqdm

transits = []
pfhs = []
times = []
moneys = []

for j in tqdm(range(10)):
    # run the model
    model = TransModel(100, 60, 48) 
    for i in range(6):
        model.step()
    
    percs = model.datacollector.get_model_vars_dataframe()
    agentVals = model.datacollector.get_agent_vars_dataframe()
    transits.append(percs['Transit'][1:].mean())
    pfhs.append(percs['PfH'][1:].mean())
    times.append(agentVals['Time'][1:].mean())
    moneys.append(agentVals['Money'][1:].mean())

# to be later changed to write to a file
print('\n')
print('percent taking transit:', round(sum(transits) / len(transits), 2))
print('percent taking pfh:', round(sum(pfhs) / len(pfhs), 2))
print('avg time left:', round(sum(times) / len(times), 2))
print('avg money left:', round(sum(moneys)  / len(moneys), 2))

