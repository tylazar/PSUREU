#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 10:13:39 2019

@author: Ty Lazarchik
"""

from sys import argv
import pandas as pd

from tqdm import tqdm
from modeldef import TransModel

global_counter = 0
population = 583776 # 100 for development, 583776 for tests

if len(argv) == 1:
    input_param = 0
else:
    for x in argv[1:]:
        print('Simulating with tax value {}...'.format(x))
        input_param = x
        data = pd.DataFrame(columns=['Cycle', 'Step', 'Transit', 'PfH'])
        
        for i in tqdm(range(7)): # 7 days per cycle
            model = TransModel(population, 60, 48, input_param)
            
            for j in range(4): # 4 trips per day
                model.step()
                step_data = model.data_collector.get_model_vars_dataframe()
                data.loc[global_counter] = [i, j, step_data.iloc[j]['Transit'], step_data.iloc[j]['PfH']]
                global_counter += 1

        data.to_csv('Main_Testing_{}.csv'.format(input_param))
