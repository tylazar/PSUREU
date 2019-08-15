#!/usr/bin/env python3
"""
Created on Mon Aug  5 09:38:22 2019

@author: Ty Lazarchik
"""

from math import sqrt
from random import randint, uniform

from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector


def compute_aggregate(agent, p, q, mode, steps, time_weight, cost_weight):
    """Return the aggregate value, time, cost, and inconvenience."""
    dist = (sqrt(sum([(a - b) ** 2 for a, b in zip(p, q)]))) / 4

    if mode == 1: # formula for transit
        if steps % 2 == 1: # rush hour access
            access = randint(14, 28)
        else:
            access = randint(7, 21)

        time = compute_transit_time(dist, access)
        incon = access + (time // 45)
        cost = compute_transit_cost(agent, time)
    else: # formula for PfH
        if steps % 2 == 1: # rush hour access
            access = randint(6, 12)
        else:
            access = randint(3, 9)

        time = compute_pfh_time(dist, access)
        incon = access
        cost = compute_pfh_cost(agent, time, dist)

    if time_weight > 0:
        if cost_weight > 0:
            return [
                ((time * time_weight) + (cost * cost_weight)),
                time, cost, incon
                ]
        return [
            (time * time_weight),
            time, cost, incon
                ]
    if cost_weight > 0:
        return [
            (cost * cost_weight),
            time, cost, incon
            ]
    return [0, time, cost, incon]


def compute_transit_time(distance, access):
    """Return the time to travel distance by transit."""
    time = (distance * 15) + access
    return time + ((time / 45) * 6)


def compute_pfh_time(distance, access):
    """Return the time to travel distance by PfH."""
    return ((distance / 23) * 60) + access


def compute_transit_cost(agent, time):
    """Return the cost to travel for time by transit."""
    if agent.day_pass:
            cost = 0
    else:
        if time <= 150:
            cost = 2.5
        else:
            cost = 5
            agent.day_pass = True
    return cost


def compute_pfh_cost(agent, time, distance):
    """Return the cost to travel for time by PfH."""
    rate = 1.25 + (0.32 * time) + (0.94 * distance) + 2.30
    if agent.taxable:
        rate += agent.model.tax_value
    tip = rate + 0.15 # add tip
    cost = (rate + tip)
    if cost < 5:
        cost = 5
    elif cost > 400:
        cost = 400
    return cost


def transit_percent(model):
    """Return the percentage of agents taking transit."""
    transit_agents = [agent.choice for agent in model.schedule.agents if agent.choice == 1]
    return (len(transit_agents) / model.num_agents) * 100


def pfh_percent(model):
    """Return the percentage of agents taking PfH."""
    pfh_agents = [agent.choice for agent in model.schedule.agents if agent.choice == 2]
    return (len(pfh_agents) / model.num_agents) * 100


class TransModel(Model):

    def __init__(self, N, width, height, tax_val):
        self.num_agents = N
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
        self.running = True
        self.steps = 0
        self.tax_value = float(tax_val)
        
        # create agents
        for i in range(self.num_agents):
            agent = TransAgent(i, self)
            self.schedule.add(agent)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(agent, (x, y))

        # create data collector
        self.data_collector = DataCollector(model_reporters={
            'Transit': transit_percent,
            'PfH': pfh_percent},
                                            agent_reporters={
                                                'Time': 'time',
                                                'Money': 'money'})

    def step(self):
        """Adance the model by one tick."""
        self.steps += 1
        self.schedule.step()
        self.data_collector.collect(self)


# agents operating in the world
class TransAgent(Agent):

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.choice = 0
        self.time = uniform(91, 207)
        self.money = uniform(5, 39)
        self.transit_prob = 1
        self.pfh_prob = 1
        self.conv_weight = uniform(0, 1)
        self.day_pass = False
        self.taxable = False

    def pick_mode(self, p, q):
        """Decide to take transit or PfH."""
        time_weight = 0.1
        cost_weight = 1.0
        model_steps = self.model.steps

        # compute aggregate values
        transit_agg = compute_aggregate(self, p, q, 1,
                                        model_steps, time_weight, cost_weight)
        pfh_agg = compute_aggregate(self, p, q, 2,
                                    model_steps, time_weight, cost_weight)

        # change probabilities based on factors
        self.check_agg(transit_agg[0], pfh_agg[0])
        self.check_time(transit_agg[1], pfh_agg[1])
        self.check_money(transit_agg[2], pfh_agg[2])
        self.check_inconvenience(transit_agg[3], pfh_agg[3])

        # pick mode with highest probability - equal defaults to transit
        if self.transit_prob >= self.pfh_prob:
            self.choice = 1
            self.time -= transit_agg[1]
            self.money -= transit_agg[2]
        else:
            self.choice = 2
            self.time -= pfh_agg[1]
            self.money -= pfh_agg[2]

    def check_agg(self, transit_agg, pfh_agg):
        """Decrease probabilities based on aggregate values."""
        diff = abs(transit_agg - pfh_agg)

        if transit_agg <= pfh_agg:
            self.pfh_prob -= diff / 10
        else:
            self.transit_prob -= diff / 10

    def check_time(self, transit_time, pfh_time):
        """Decrease probabilities based on time used."""
        if transit_time >= self.time:
            self.transit_prob -= self.transit_prob / 2
        if pfh_time >= self.time:
            self.pfh_prob -= self.pfh_prob / 2

        self.transit_prob -= transit_time / self.time
        self.pfh_prob -= pfh_time / self.time

    def check_money(self, transit_money, pfh_money):
        """Decrease probabilities based on money used."""
        if transit_money >= self.money:
            self.transit_prob -= self.transit_prob / 2
        if pfh_money >= self.money:
            self.pfh_prob -= self.pfh_prob / 2

        self.transit_prob -= transit_money / self.money
        self.pfh_prob -= pfh_money / self.money

    def check_inconvenience(self, transit_incon, pfh_incon):
        """Decrease probabilities based on inconvenience."""
        self.transit_prob -= self.conv_weight / transit_incon
        self.pfh_prob -= self.conv_weight / pfh_incon

    def reset(self):
        """Reset probabilities."""
        self.transit_prob = 1
        self.pfh_prob = 1
        self.taxable = False

    def move(self):
        """Move from the current cell to a random cell."""
        # select random destination on grid
        possible_steps = [(i, j) for i in range(self.model.grid.width)
                          for j in range(self.model.grid.height)]
        possible_steps.remove(self.pos)
        new_pos = self.random.choice(possible_steps)

        # reset probabilities, pick transportation method and move
        self.reset()
            
        # check if origin or destination are within taxable area
        # note: (0,0) is bottom left corner of grid
        if (12 <= self.pos[0] <= 37
                or 12 <= new_pos[0] <= 37
                or 12 <= self.pos[1] <= 39
                or 12 <= new_pos[1] <= 39):
            self.taxable = True
        
        self.pick_mode(self.pos, new_pos)
        self.model.grid.move_agent(self, new_pos)

    def step(self):
        """Move on each step in the simulation cycle."""
        self.move()
        