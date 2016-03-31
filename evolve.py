#!/usr/bin/env python3.4

from datetime import datetime
import pandas as pd
import random
import time

from fitness_function import judge_fitness
from portfolio import Portfolio

POPULATION_SIZE = 1000
PORTFOLIO_SIZE = 5
GLOBAL_START_DATE = datetime(2012, 7, 17)
GLOBAL_END_DATE = datetime(2016, 3, 15)
GENERATIONS = 2


def generate_random_portfolio():
    raw_ratios = [random.random() for _ in range(PORTFOLIO_SIZE)]
    total = sum(raw_ratios)
    normalised_ratios = [(100 * ratio) / total for ratio in raw_ratios]
    stocks = random.sample(universe, PORTFOLIO_SIZE)
    return Portfolio(list(zip(stocks, normalised_ratios)))


universe = set()

print("Reading universe of tickers")
with open("data/share_universe.csv", "r") as f:
    for line in f:
        universe.add(line.strip())
print("Read {} tickers".format(len(universe)))

print("Loading market data")
market_data = {}
for ticker in universe:
    frame = pd.read_csv("data/{}.csv".format(ticker), parse_dates=[0], index_col=0)
    frame = frame.reindex(pd.date_range(GLOBAL_START_DATE, GLOBAL_END_DATE, freq="D"), method="ffill")
    frame.fillna(method="ffill", inplace=True)
    market_data[ticker] = frame
print("Done loading, got market data for {} tickers".format(len(market_data)))


print("Generating {} initial portfolios with {} stocks in each".format(POPULATION_SIZE, PORTFOLIO_SIZE))
population = set()
for ii in range(POPULATION_SIZE):
    population.add(generate_random_portfolio())
print("Done generating, got {} portfolios".format(len(population)))


start_date = datetime(2013, 1, 1)
end_date = datetime(2013, 12, 31)
for ii in range(GENERATIONS):
    print("Judging fitness over {} to {}".format(start_date, end_date))
    start_time = time.time()
    ratings = []
    for portfolio in population:
        trace = portfolio.trace(market_data, start_date, end_date)
        ratings.append((judge_fitness(trace.frame), portfolio))
    print("Done judging, took {}s".format(time.time() - start_time))

    print("Culling...")
    new_population = set()
    # Kill weakest third plus any with zero rating
    for rating, portfolio in ratings[int(len(ratings) / 3):]:
        if rating != 0:
            new_population.add(portfolio)
    print("{} survivors ({}%)".format(len(new_population), len(new_population) * 100 / len(population)))

    new_portfolio_count = len(population) - len(new_population)
    print("Generating {} new portfolios".format(new_portfolio_count))
    for jj in range(new_portfolio_count):
        new_population.add(generate_random_portfolio())
    print("Done generating new portfolios")

    population = new_population





league_table = sorted(ratings, key=lambda element: element[0])
for fitness, portfolio in league_table:
    print("{} for {}".format(fitness, portfolio.holdings))


