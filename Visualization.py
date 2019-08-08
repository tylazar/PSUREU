#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug  5 10:14:06 2019

@author: carinnel
"""

from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule
from ModelDef import TransModel
from tqdm import tqdm

def agentPortrayal(agent):
    portrayal = {'Shape': 'circle',
                 'Filled': 'true',
                 'Layer': 0,
                 'r': 0.5}
    
    if agent.choice == 1:
        portrayal['Color'] = 'red'
    else:
        portrayal['Color'] = 'blue'
    
    return portrayal

# =============================================================================
# model = TransModel(100, 60, 48) 
# averages = []
# 
# for i in tqdm(range(10)):
#     for j in range(10):
#         model.step()
#         # print('step', j, 'round', i)
#     
#     transit = model.datacollector.get_model_vars_dataframe()
#     averages.append(transit['Percent'].mean())
# 
# print('\n')
# # =============================================================================
# # for i in range(len(averages)):
# #     print(i + 1, averages[i])
# # =============================================================================
# 
# print(round(sum(averages) / len(averages), 2))
# =============================================================================
    

grid = CanvasGrid(agentPortrayal, 60, 48, 500, 500)

chart = ChartModule([{'Label': 'Percent',
                      'Color': 'Black'}],
                    data_collector_name = 'datacollector')

server = ModularServer(TransModel,
                       [grid, chart],
                       'Transport Model',
                       {'N': 500, 'width': 60, 'height': 48})
server.port = 8521
server.launch()

