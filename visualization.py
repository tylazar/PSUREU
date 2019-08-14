#!/usr/bin/env python3
"""
Created on Mon Aug  5 10:14:06 2019

@author: Ty Lazarchik
"""

from sys import argv

from tqdm import tqdm
from modeldef import TransModel

transits = []
pfhs = []
times = []
moneys = []

for j in tqdm(range(30)): # 30 cycles, i.e. 30 days
    if len(argv) > 1:
        input_param = argv[1]
    else:
        input_param = 0
        
    # run the model
    model = TransModel(583776, 60, 48, input_param) # testing population = 100; final population = 583776
    for i in range(4): # 4 steps, i.e. 4 trips per day
        model.step()
    
    percs = model.data_collector.get_model_vars_dataframe()
    agentVals = model.data_collector.get_agent_vars_dataframe()
    transits.append(percs['Transit'][1:].mean())
    pfhs.append(percs['PfH'][1:].mean())
    times.append(agentVals['Time'][1:].mean())
    moneys.append(agentVals['Money'][1:].mean())

# to be later changed to write to a file
print('\n')
print('percent taking transit:', round(sum(transits) / len(transits), 2))
print('percent taking pfh:', round(sum(pfhs) / len(pfhs), 2))

# =============================================================================
# print('avg time left:', round(sum(times) / len(times), 2))
# print('avg money left:', round(sum(moneys)  / len(moneys), 2))
# print('you typed:', input_param)
# =============================================================================
    