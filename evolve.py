#!/usr/bin/env python3.4

import random

from portfolio import Portfolio


universe = set()

print("Reading universe of tickers")
with open("data/share_universe.csv", "r") as f:
    for line in f:
        universe.add(line.strip())
print("Read {} tickers".format(len(universe)))

POPULATION_SIZE = 5
PORTFOLIO_SIZE = 5
print("Generating {} initial portfolios with {} stocks in each".format(POPULATION_SIZE, PORTFOLIO_SIZE))
population = set()
for ii in range(POPULATION_SIZE):
    raw_ratios = [random.random() for _ in range(PORTFOLIO_SIZE)]
    total = sum(raw_ratios)
    normalised_ratios = [(100 * ratio) / total for ratio in raw_ratios]
    stocks = random.sample(universe, PORTFOLIO_SIZE)
    portfolio = Portfolio(list(zip(stocks, normalised_ratios)))




