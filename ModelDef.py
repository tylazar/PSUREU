#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug  5 09:38:22 2019

@author: Ty Lazarchik
"""

from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
import math

# ========== UNIVERSAL STANDARD ========== #
# Mode 1 = transit
# Mode 2 = PfH
# ======================================== #

# computes the travel time in minutes and cost in USD from p to q
# returns list of aggregate value, time, and cost
# p and q are 2D arrays
def computeAgg(p, q, mode, timeWeight, costWeight):
    dist = (math.sqrt(sum([(a - b) ** 2 for a, b in zip(p, q)]))) / 4
    
    if mode == 1: # formula for transit
        time = (dist * 15) + 9 # 15 mins per mile, plus 9 min wait time
        time = time + ((time / 45) * 6) # 6 add mins for transfers for every 45 mins
        if time <= 150:
            cost = 2.5
        else:
            cost = 5
    else: # formula for PfH
        time = ((dist / 23) * 60) + 6 # assumed speed of 23MPH, plus 6 mins wait time
        rate = 1.25 + (0.32 * time) + (0.94 * dist) + 2.30 # base date + time rate + dist rate + add fee
        tip = rate + 0.15 # add tip
        cost = (rate + tip)
        if cost < 5: # minimum fare of $5 for all trips
            cost = 5
        elif cost > 400:
            cost = 400
        
    if timeWeight > 0:
        if costWeight > 0:
            return [((time * timeWeight) + (cost * costWeight)), time, cost] # time > 0, cost > 0 - care about both
        else:
            return [(time * timeWeight), time, cost] # time > 0, cost = 0 - dont care about cost
    else:
        if costWeight > 0:
            return [(cost * costWeight), time, cost] # time = 0, cost > 0 - dont care about time
        else:
            return [0, time, cost] # time = 0, cost = 0 - dont care about anything
        


def transitPercent(model):
    transitAgents = [agent.choice for agent in model.schedule.agents if agent.choice == 1]
    return (len(transitAgents) / model.num_agents) * 100


def pfhPercent(model):
    pfhAgents = [agent.choice for agent in model.schedule.agents if agent.choice == 2]
    return (len(pfhAgents) / model.num_agents) * 100


# the world on which agents operate
class TransModel(Model):
    # constructor for grid of width x height with N agents
    def __init__(self, N, width, height):
        self.num_agents = N
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
        self.running = True
        
        # create agents
        for i in range(self.num_agents):
            a = TransAgent(i, self)
            self.schedule.add(a)
            
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))
        
        # create data collector
        self.datacollector = DataCollector(
                model_reporters = {'Transit': transitPercent, 
                                   'PfH': pfhPercent},
                agent_reporters = {'Time': 'time', 
                                   'Money': 'money'})
    
    # advance the model by one tick
    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
    
    
# agents operating in the world
class TransAgent(Agent):
    # constructor for agent with ID uniqueID on world model
    def __init__(self, uniqueID, model):
        super().__init__(uniqueID, model)
        self.choice = 0
        self.time = 60
        self.money = 40
        self.transitProb = 1
        self.pfhProb = 1
    
    # decide to take transit or pfh
    def pickMode(self, p, q):
        # compute aggregate values
        timeWeight = 0.2
        costWeight = 0.6
    
        transitAgg = computeAgg(p, q, 1, timeWeight, costWeight)
        pfhAgg = computeAgg(p, q, 2, timeWeight, costWeight)
        
        # change probabilities based on factors
        self.checkAgg(transitAgg[0], pfhAgg[0]) 
        self.checkTime(transitAgg[1], pfhAgg[1])
        self.checkMoney(transitAgg[2], pfhAgg[2])
        
        # pick mode with highest probability
        if self.transitProb >= self.pfhProb:
            self.choice = 1
            self.time -= transitAgg[1]
            self.money -= transitAgg[2]
        else:
            self.choice = 2
            self.time -= pfhAgg[1]
            self.money -= pfhAgg[2]
        
        return
    
    # decrease probabilities based on aggregate values
    def checkAgg(self, transitAgg, pfhAgg):
        diff = abs(transitAgg - pfhAgg)
        
        if transitAgg <= pfhAgg:
            self.pfhProb -= diff / 10
        else:
            self.transitProb -= diff / 10
        
        return
    
    # decrease probabilities based on time used
    def checkTime(self, transitTime, pfhTime):
        # significant dock if not enough resources
        if transitTime >= self.time:
            self.transitProb -= self.transitProb / 2
        if pfhTime >= self.time:
            self.pfhProb -= self.pfhProb / 2
            
        self.transitProb -= transitTime / self.time
        self.pfhProb -= pfhTime / self.time
            
        return
      
    # decrease probabilities based on money used
    def checkMoney(self, transitMon, pfhMon):
        # significant dock if not enough resources
        if transitMon >= self.money:
            self.transitProb -= self.transitProb / 2
        if pfhMon >= self.money:
            self.pfhProb -= self.pfhProb / 2
        
        self.transitProb -= transitMon / self.money
        self.pfhProb -= pfhMon / self.money
        
        return
    
    # reset mode probabilities
    def reset(self):
        self.transitProb = 1
        self.pfhProb = 1
        
    # move from current cell to a random cell
    def move(self):
        # get all cells in the grid, minus the agent's current position
        possibleSteps = [(i, j) for i in range(self.model.grid.width) for j in range(self.model.grid.height)]
        possibleSteps.remove(self.pos)
        
        # move to a randomly selected cell from the list
        newPos = self.random.choice(possibleSteps)
        
        # reset probabilities, pick transportation method and move
        self.reset()
        self.pickMode(self.pos, newPos)
        self.model.grid.move_agent(self, newPos)
    
    def step(self):
        self.move()
        
        
        