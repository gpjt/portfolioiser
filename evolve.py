#!/usr/bin/env python3.4

from datetime import datetime
import numpy as np
import pandas as pd
import random
import time

from fitness_function import judge_fitness
from portfolio import Portfolio

POPULATION_SIZE = 1000
PORTFOLIO_SIZE = 8
GLOBAL_START_DATE = datetime(2012, 7, 17)
GLOBAL_END_DATE = datetime(2016, 3, 15)
GENERATIONS = 50


def generate_random_portfolio():
    raw_ratios = [random.random() for _ in range(PORTFOLIO_SIZE)]
    total = sum(raw_ratios)
    normalised_ratios = [(100 * ratio) / total for ratio in raw_ratios]
    stocks = random.sample(universe, PORTFOLIO_SIZE)
    return Portfolio(list(zip(stocks, normalised_ratios)))


def mutate(portfolio):
    holdings = list(portfolio.holdings)
    change_holding_index = random.randint(0, len(portfolio.holdings) - 1)
    if random.random() < 0.5:
        # Change the stock
        holdings[change_holding_index] = (random.choice(list(universe)), holdings[change_holding_index][1])
    else:
        # Adjust size
        new_ratios = [weight for holding, weight in holdings]
        new_ratios[change_holding_index] = new_ratios[change_holding_index] + (new_ratios[change_holding_index] * (random.random() - 0.5))
        if new_ratios[change_holding_index] < 0:
            raise Exception()
        total = sum(new_ratios)
        normalised_ratios = [(100 * ratio) / total for ratio in new_ratios]
        holdings = list(zip([holding for (holding, _) in holdings], normalised_ratios))
    return Portfolio(holdings)


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
for generation in range(GENERATIONS):
    print()
    print("*" * 80)
    print("Generation {}".format(generation))
    print("*" * 80)
    print()
    print("Judging fitness over {} to {}".format(start_date, end_date))
    start_time = time.time()
    metrics_portfolios = []
    for portfolio in population:
        trace = portfolio.trace(market_data, start_date, end_date)
        fitness, calmness, return_over_period = judge_fitness(trace.frame)
        metrics_portfolios.append((fitness, calmness, return_over_period, portfolio))
    metrics_portfolios = sorted(metrics_portfolios, key=lambda element: element[0])
    print("Done collating fitness, took {}s".format(time.time() - start_time))

    print("Finished generation {}. Stats (min / max / average)".format(generation))
    fitnesses = [fitness for (fitness, _, _, _) in metrics_portfolios]
    print("Fitness: {} / {} / {}".format(min(fitnesses), max(fitnesses), np.mean(fitnesses)))
    calmnesses  = [calmness for (_, calmness, _, _) in metrics_portfolios]
    print("Calmness: {} / {} / {}".format(min(calmnesses), max(calmnesses), np.mean(calmnesses)))
    returns_over_period  = [return_over_period for (_, _, return_over_period, _) in metrics_portfolios]
    print("Returns: {} / {} / {}".format(min(returns_over_period), max(returns_over_period), np.mean(returns_over_period)))
    winner_fitness, winner_calmness, winner_returns_over_period, winner_porfolio = metrics_portfolios[-1]
    print("Winner fitness {}".format(winner_fitness))
    print("Winner calmness {}".format(winner_calmness))
    print("Winner return {}".format(winner_returns_over_period))
    print("Winner holdings {}".format(winner_porfolio.holdings))

    if generation < GENERATIONS - 1:
        print("Culling...")
        new_population = set()
        # Kill weakest half plus any with zero rating
        for rating, _, _, portfolio in metrics_portfolios[int(len(metrics_portfolios) / 2):]:
            if rating != 0:
                new_population.add(portfolio)
        print("{} survivors ({}%)".format(len(new_population), len(new_population) * 100 / len(population)))

        new_portfolio_count = len(population) - len(new_population)
        print("Need {} new portfolios".format(new_portfolio_count))

        print("Creating 90% mutated portfolios weighting reproduction chances to highest-ranked")
        reproducing_population = [portfolio for (_, _, _, portfolio) in metrics_portfolios]
        reproduction_chance_unnormalised = range(len(reproducing_population))
        normalisation_factor = sum(reproduction_chance_unnormalised)
        reproduction_chance = [v / normalisation_factor for v in reproduction_chance_unnormalised]
        for jj in range(int(new_portfolio_count * 0.9)):
            new_population.add(mutate(np.random.choice(reproducing_population, None, p=reproduction_chance)))
        print("New population is now {}".format(len(new_population)))

        to_fill = POPULATION_SIZE - len(new_population)
        print("Generating {} new random portfolios".format(to_fill))
        for jj in range(to_fill):
            new_population.add(generate_random_portfolio())
        print("Done generating new random portfolios")

        population = new_population




