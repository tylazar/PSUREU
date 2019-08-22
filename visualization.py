#!/usr/bin/env python3
"""
Created on Mon Aug  5 10:14:06 2019

@author: Ty Lazarchik
"""
import matplotlib.pyplot as plt
import pandas as pd

def colorful():
    file_names = ['Main_Testing_0.csv', 'Main_Testing_05.csv', 'Main_Testing_1.csv',
                  'Main_Testing_15.csv', 'Main_Testing_2.csv', 'Main_Testing_25.csv',
                  'Main_Testing_3.csv', 'Main_Testing_35.csv', 'Main_Testing_4.csv',
                  'Main_Testing_45.csv', 'Main_Testing_5.csv']
    
    plt.figure(figsize=[12, 8])
    label_num = 0
    xlabels = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    
    for i in range(len(file_names)):
        file_name = file_names[i]
        cycle_count = 7
        
        data = pd.read_csv(file_name)
        
        step_values = [0, 0, 0, 0]
                
        for i in range(len(data)):
            if int(data.iloc[i]['Step']) == 0:
                step_values[0] += float(data.iloc[i]['Transit'])
            elif int(data.iloc[i]['Step']) == 1:
                step_values[1] += float(data.iloc[i]['Transit'])
            elif int(data.iloc[i]['Step']) == 2:
                step_values[2] += float(data.iloc[i]['Transit'])
            else:
                step_values[3] += float(data.iloc[i]['Transit'])
        
        step_values[0] = step_values[0]/cycle_count
        step_values[1] = step_values[1]/cycle_count
        step_values[2] = step_values[2]/cycle_count
        step_values[3] = step_values[3]/cycle_count
        
        plt.xlabel('Trip')
        plt.xlim((0.0, 10.0))
        plt.xticks(ticks=[0.0, 1.0, 2.0, 3.0, 4.0, 5.0], labels=xlabels)
        plt.ylabel('Transit Usage (%)')
        plt.grid(True)
        plt.plot(step_values, label='Tax = ${}0'.format(label_num))
        label_num += 0.5
    
    plt.legend()
    return


def usage_change():
    file_names = ['Main_Testing_0.csv', 'Main_Testing_05.csv', 'Main_Testing_1.csv',
                  'Main_Testing_15.csv', 'Main_Testing_2.csv', 'Main_Testing_25.csv',
                  'Main_Testing_3.csv', 'Main_Testing_35.csv', 'Main_Testing_4.csv',
                  'Main_Testing_45.csv', 'Main_Testing_5.csv']
    tax_vals = [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5]
    plt.figure(figsize=[24, 16])
    vals = []
    
    for file in file_names:
        data = pd.read_csv(file)
        vals.append(data.loc[:, 'Transit'].mean())
    
    print(vals)
    plt.xlabel('Tax Value ($)')
    plt.ylabel('Transit Usage (%)')
    plt.xticks(ticks=tax_vals, labels=tax_vals)
    plt.ylim((80, 92))
    plt.grid(False)
    plt.bar(tax_vals, vals, color='green', width=0.4)
    return

def rate_of_change():
    tax_vals = [0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5]
    rates = [0.39, 0.38, 0.33, 0.32, 0.31, 0.28, 0.28, 0.27, 0.27, 0.24] # hard coded vals
    
    plt.figure(figsize=[12, 8])
    plt.xlabel('Tax Value ($)')
    plt.ylabel('Change in Transit Usage (%)')
    plt.xticks(ticks=tax_vals, labels=tax_vals)
    plt.bar(tax_vals, rates, color='green', width=0.4)
    
    return

